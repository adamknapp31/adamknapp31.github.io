import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os
from data_drift_detector import DataDriftDetector

# Need to log the recommendation requests, GET data requests, and the GET rate requests
USERNAME = os.getenv('DB_USER')
PASSWORD = os.getenv('PASSWORD')
DB_NAME = "movie_recommendation_system"
COUNT = 0

# Variables for MongoDB connection
SERVER = "127.0.0.1:27017"
DATABASE_NAME = "movie_recommendation_system"

def setup_mongo_connection():
    try:
        client = MongoClient(f"mongodb://root:{PASSWORD}@{SERVER}/{DATABASE_NAME}", serverSelectionTimeoutMS=5000)
        return client
    except Exception as e:
        print(f"Failed to connect to MongoDB. Error: {e}")
        return None

#args: the kafka csv stream file path (str)
#returns: three df- one for each type of entry
def process_csv(file_path):
    """
    Processes the kafka data stream into the three types of data in that stream.
    The watch data, the rating data, and the reccomendation data

    -args: the kafka csv stream file path (str)
    -returns: three df- one for each type of entry
    """
    # Initialize lists to store different types of data
    user_watch_data = []
    user_rating_data = []
    recommendation_request = []

    # Open the CSV file for reading
    with open(file_path, 'r') as file:
        for line in file:
            # Assume the file uses commas as delimiters
            columns = line.strip().split(',')

            # Separate rows based on the number of columns
            if len(columns) == 3:
                # Further separate based on the type of GET request
                if '/data/' in columns[2]:
                    user_watch_data.append(columns)
                elif '/rate/' in columns[2]:
                    user_rating_data.append(columns)
            elif len(columns) == 6:
                recommendation_request.append(columns)

    # Convert the watch data list into a DataFrame
    user_watch_data_df = pd.DataFrame(user_watch_data, columns=['timestamp', 'user_id', 'GetRequest'])

    # Process watch data to extract relevant information
    user_watch_data_df['movieid'] = user_watch_data_df['GetRequest'].apply(
        lambda x: x.split('/m/')[1].rsplit('/', 1)[0].replace('+', ' '))
    user_watch_data_df['File'] = user_watch_data_df['GetRequest'].apply(
        lambda x: x.rsplit('/', 1)[1])
    user_watch_data_df['minute'] = user_watch_data_df['File'].apply(
        lambda x: x.rsplit('.', 1)[0])

    # Drop the 'GetRequest' column as its data has been extracted
    user_watch_data_df.drop('GetRequest', axis=1, inplace=True)

    # Convert the rating data list into a DataFrame
    user_rating_data_df = pd.DataFrame(user_rating_data, columns=['timestamp', 'user_id', 'GetRequest'])

    # Process rating data to extract relevant information
    user_rating_data_df['movieid'] = user_rating_data_df['GetRequest'].apply(
        lambda x: x.split('=')[0].split('/rate/')[1].replace('+', ' '))
    user_rating_data_df['rating'] = user_rating_data_df['GetRequest'].apply(
        lambda x: x.split('=')[1])

    # Drop the 'GetRequest' column as its data has been extracted
    user_rating_data_df.drop('GetRequest', axis=1, inplace=True)

    user_rating_data_df = user_rating_data_df[['user_id', 'movieid', 'rating']]
    user_rating_data_df['rating'] = user_rating_data_df['rating'].astype('int')

    # Convert the recommendation request list into a DataFrame
    recommendation_request_df = pd.DataFrame(recommendation_request, columns=[
        'TimeStamp', 'UserID', 'Request', 'Status', 'Result', 'Latency'])

    return user_watch_data_df, user_rating_data_df, recommendation_request_df

# load in the historical data used to train the model
def load_historical_data(training_file_path):
    user_watch_df, user_rating_df, _ = process_csv(training_file_path)

    return user_watch_df[['user_id', 'movieid', 'minute']], user_rating_df

def load_incoming_watch_data(client):
    db = client.movie_recommendation_system
    collection = db.user_watch_history

    # Step 1: Retrieve the last 100,000 rows added to the collection
    pipeline = [
        {"$sort": {"timestamp": -1}},  # Sort by timestamp in descending order
        {"$limit": 100000},             # Limit to the last 100,000 documents
        {"$sample": {"size": 7500}}    # Step 2: Randomly sample 10,000 rows
    ]

    sampled_documents = list(collection.aggregate(pipeline))
    df = pd.DataFrame(sampled_documents)
    df = df[['user_id', 'movieid', 'minute']]
    return df

def load_incoming_rating_data(client):
    db = client.movie_recommendation_system
    collection = db.user_ratings

    # Step 1: Retrieve the last 100,000 rows added to the collection
    pipeline = [
        {"$sort": {"timestamp": -1}},  # Sort by timestamp in descending order
        {"$limit": 5000},             # Limit to the last 100,000 documents
        {"$sample": {"size": 75}}    # Step 2: Randomly sample 10,000 rows
    ]

    sampled_documents = list(collection.aggregate(pipeline))
    df = pd.DataFrame(sampled_documents)
    df = df[['user_id', 'movieid', 'rating']]
    return df

def most_popular_movies(user_watch_df, k):
    # Group by 'Title' and count the unique 'UserID's for each 'Title'
    unique_user_counts = user_watch_df.groupby('movieid')['user_id'].nunique()

    # Sort the counts in descending order to get the most popular movie at the top
    most_popular_movies = unique_user_counts.sort_values(ascending=False)

    most_popular_movies_df = most_popular_movies.reset_index(name='UniqueUserCount')

    # Now 'most_popular_movies_df' is a DataFrame with 'Title' and 'UniqueUserCount'
    return set(most_popular_movies_df["movieid"][0:k])

def get_user_info_df(user_database, user_watch_df):

    user_watch_df["user_id"] = user_watch_df["user_id"].astype('int')
    user_df = pd.merge(user_database, user_watch_df, on='user_id', how='left')
    user_df = user_df[['age', 'occupation', 'gender']]

    return user_df

def check_drift_metrics(prior_df, post_df):
    detector = DataDriftDetector(df_prior = prior_df,
                                 df_post = post_df)
    drift_metrics = detector.calculate_drift()

    categorical_metrics = drift_metrics["categorical"]
    numerical_metrics = drift_metrics["numerical"]

    for c_key in categorical_metrics.keys():
        if categorical_metrics[c_key]['chi_square_test_p_value'] < 0.05:
            print(f"Data drift detected in {c_key}...")
        else:
            print(f"Distribution for {c_key} is similar")
    
    for n_key in numerical_metrics.keys():
        if numerical_metrics[n_key]['ks_2sample_test_p_value'] < 0.05:
            print(f"Data drift detected in {n_key}...")
        else:
            print(f"Distribution for {n_key} is similar")


if __name__ == "__main__":
    client = setup_mongo_connection()

    incoming_user_watch_df = load_incoming_watch_data(client)
    incoming_user_rating_df = load_incoming_rating_data(client)

    user_database = pd.read_csv('training_data/user_database.csv')
    user_watch_df, user_rating_df = load_historical_data('training_data/training_data.csv')

    user_prior_df = get_user_info_df(user_database, user_watch_df)
    user_post_df = get_user_info_df(user_database, incoming_user_watch_df)

    # initialize detector
    check_drift_metrics(pd.DataFrame(user_rating_df['rating']), pd.DataFrame(incoming_user_rating_df['rating']))
    check_drift_metrics(user_prior_df, user_post_df)
    
