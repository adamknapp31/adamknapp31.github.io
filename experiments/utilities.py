from dotenv import load_dotenv
import mlflow
import pandas as pd
import os


def load_env_variables():

    load_dotenv()
    MLFLOW_TRACKING_TOKEN = os.environ.get("MLFLOW_TRACKING_TOKEN")
    MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")

    return MLFLOW_TRACKING_TOKEN, MLFLOW_TRACKING_URI

def start_mlflow_experiment(experiment_name, run_name=None):
    mlflow.set_experiment(experiment_name=experiment_name)
    return mlflow.start_run(run_name=run_name)

def log_parameters(params):
    for key, value in params.items():
        mlflow.log_param(key, value)

def log_metrics(metrics):
    for key, value in metrics.items():
        mlflow.log_metric(key, value)

def log_artifact(file_path):
    mlflow.log_artifact(file_path)

def end_mlflow_run():
    mlflow.end_run()


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
    user_watch_data_df = pd.DataFrame(user_watch_data, columns=['TimeStamp', 'UserID', 'GetRequest'])

    # Process watch data to extract relevant information
    user_watch_data_df['Title'] = user_watch_data_df['GetRequest'].apply(
        lambda x: x.split('/m/')[1].rsplit('/', 1)[0].replace('+', '+'))
    user_watch_data_df['File'] = user_watch_data_df['GetRequest'].apply(
        lambda x: x.rsplit('/', 1)[1])

    # Drop the 'GetRequest' column as its data has been extracted
    user_watch_data_df.drop('GetRequest', axis=1, inplace=True)

    # Convert the rating data list into a DataFrame
    user_rating_data_df = pd.DataFrame(user_rating_data, columns=['TimeStamp', 'UserID', 'GetRequest'])

    # Process rating data to extract relevant information
    user_rating_data_df['Title'] = user_rating_data_df['GetRequest'].apply(
        lambda x: x.split('=')[0].split('/rate/')[1].replace('+', '+'))
    user_rating_data_df['Rating'] = user_rating_data_df['GetRequest'].apply(
        lambda x: x.split('=')[1])

    # Drop the 'GetRequest' column as its data has been extracted
    user_rating_data_df.drop('GetRequest', axis=1, inplace=True)

    # Convert the recommendation request list into a DataFrame
    recommendation_request_df = pd.DataFrame(recommendation_request, columns=[
        'TimeStamp', 'UserID', 'Request', 'Status', 'Result', 'Latency'])

    return user_watch_data_df, user_rating_data_df, recommendation_request_df
