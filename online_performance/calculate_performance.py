from datetime import datetime, timedelta
from pymongo import MongoClient

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)

from utilities import setup_mongo_connection


def fetch_recommendations(date, db):
    """
        Retrieves a list of recommendations from the database that were made on a specific date.

        Args:
            date (datetime): The date for which recommendations are to be fetched. The function searches for recommendations made within this date, from the start of the day to the end of the day.
            db: The database connection object used to query the recommendations. This object must have a `recommendations` collection or equivalent that stores recommendation records.

        Returns:
            pymongo.cursor.Cursor: A cursor to the list of recommendation records found in the database that match the query criteria. This cursor can be iterated over to access the individual recommendations. Each recommendation is expected to be a dictionary-like object containing at least the timestamp of when the recommendation was made.

    """
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = start_of_day + timedelta(days=1)
    return db.recommendations.find({
        "timestamp": {"$gte": start_of_day, "$lt": end_of_day}
    })


def find_next_movie_watched(user_id, recommendation_time, db):
    """
        Finds the first movie a user watched after a specified recommendation time.

        Args:
            user_id (str): The ID of the user whose watch history is being queried.
            recommendation_time (datetime): The timestamp after which the search for the next watched movie is conducted. Movies watched before this time are not considered.
            db: The database connection object used to query the user's watch history. This object must have a `user_watch_history` collection or equivalent that stores watch history records.

        Returns:
            dict or None: If a movie watched after the recommendation time is found, returns a dictionary containing:
                - 'movieid': The ID of the next movie watched by the user after the recommendation time.
                - 'watched_at': The timestamp when the movie was watched.
            If no movie was watched after the recommendation time, returns None.
        """
    # Query the user's watch history to find the first movie watched after recommendation_time
    next_watched_movie = db.user_watch_history.find_one({
        "user_id": user_id,
        "timestamp": {"$gt": recommendation_time}
    }, sort=[("timestamp",
              1)])  # Sort by timestamp in ascending order to get the earliest watch event after recommendation_time

    # Check if a movie was found
    if next_watched_movie:
        # Return the movie ID and the watch timestamp of the next movie watched
        return {
            "movieid": next_watched_movie["movieid"],
            "watched_at": next_watched_movie["timestamp"]
        }
    else:
        # Return None or an appropriate response if no movie was watched after the recommendation time
        return None


def find_next_movie_rating(user_id, recommendation_time, watched_movie_id, db):
    """
        Finds the next movie rating for a user from a certain time

        Args:
        user_id (str): The ID of the user whose rating history is being queried.
        recommendation_time (datetime): The timestamp serving as the starting point for searching the next watched movie. Ratings for movies watched before this time are not considered.
        watched_movie_id (str): The ID of the movie for which the rating is sought.
        db: The database connection object used to query the user's ratings. This object must have a `user_ratings` collection or equivalent that stores rating records.

        Returns:
            dict or None: If a rating for the specified movie watched after the recommendation time is found, returns a dictionary containing:
                - 'movie_rating': The rating given by the user to the next movie watched.
                - 'watched_at': The timestamp when the rating was recorded.
            Returns None if no rating was found for the specified conditions, indicating either the movie was not watched or rated after the given time.

        Note:
            The function relies on the 'user_ratings' collection having documents with fields 'user_id', 'movieid', 'timestamp', and 'rating'.
    """
    rated_movie = db.user_ratings.find_one({
        "user_id": user_id,
        "timestamp": {"$gt": recommendation_time},
        "movieid": watched_movie_id,
    }, sort=[("timestamp",
              1)])  # Sort by timestamp in ascending order to get the earliest watch event after recommendation_time
    # Check if a movie was found

    if rated_movie:
        # Return the movie ID and the watch timestamp of the next movie watched
        return {
            "movie_rating": rated_movie["rating"],
            "watched_at": rated_movie["timestamp"]
        }
    else:
        # Return None or an appropriate response if no movie was watched after the recommendation time
        return None


def calculate_metric_for_day(date, db):
    """
        Calculates the average rating of movies recommended on a specific day.

        This function iterates through all movie recommendations made on the given date, determines whether each recommended movie was watched and rated by the user after the recommendation, and calculates the average rating of these movies. If a movie was watched but not rated, it is excluded from the calculation. If a movie was not watched, a poor rating (1) is assumed.

        Args:
            date (datetime): The date for which to calculate the average rating of recommended movies. This date is used to fetch recommendations from the database.
            db: The database connection object used to access the recommendations and ratings stored in the database. This object must have `recommendations`, `user_watch_history`, and `user_ratings` collections or equivalents.

        Returns:
            float or None: The average rating of movies recommended on the specified date. If there are no recommendations for the given date or if no recommended movies were watched, the function returns None to indicate that an average rating cannot be calculated.

        The calculation of the average rating includes assigning a poor rating of 1 to recommended movies that were not watched. This approach ensures that the metric reflects the user's engagement with the recommended content.
        """
    recommendations = fetch_recommendations(date, db)  # This returns a cursor
    all_ratings = []

    for recommendation in recommendations:  # Correctly iterate over the cursor

        user_id = recommendation['user_id']
        recommended_movie_ids = recommendation['recommended_movies']
        recommendation_time = recommendation['timestamp']

        # Find the next movie watched after the recommendation
        watched_movie = find_next_movie_watched(user_id, recommendation_time, db)

        # Ensure watched_movie is not None before proceeding
        if watched_movie and watched_movie['movieid'] in recommended_movie_ids:
            watched_movie_rating = find_next_movie_rating(user_id=user_id, recommendation_time=recommendation_time,
                                                          watched_movie_id=watched_movie['movieid'], db=db)
            # Only account if movie was rated
            if watched_movie_rating:
                all_ratings.append(watched_movie_rating["movie_rating"])
        else:
            all_ratings.append(1)

    # Calculate average rating including the poor rating if movie is not watched
    if all_ratings:
        return sum(all_ratings) / len(all_ratings)
    else:
        return None


def war_day(Day, Month, Year):
    """
    Weighted Average Rating 
        Args:
            Day (int): The day of the month (1-31) for which to evaluate recommendations.
            Month (int): The month (1-12) for which to evaluate recommendations.
            Year (int): The year (e.g., 2024) for which to evaluate recommendations.

        Returns:
            None

        Prints:
            Average Model Rating for Date: 1.0

        From cmd Line: python -c 'from calculate_performance import war_day; war_day(15, 3, 2024)'
    """
    date_input = datetime(Year, Month, Day)
    client = setup_mongo_connection()
    db = client.movie_recommendation_system
    average_rating = calculate_metric_for_day(date_input, db=db)
    print(f"Average Model Rating for {date_input.date()}: {average_rating}")
    return

def war_over_period(start_day, start_month, start_year, end_day, end_month, end_year):
    """
    Computes the Weighted Average Ratings over a period of time.

        Args:
        start_day (int): The starting day of the month (1-31) for the period.
        start_month (int): The starting month (1-12) for the period.
        start_year (int): The starting year (e.g., 2024) for the period.
        end_day (int): The ending day of the month (1-31) for the period.
        end_month (int): The ending month (1-12) for the period.
        end_year (int): The ending year (e.g., 2024) for the period.

        Returns:
            None

        This function iterates through each day in the specified period, calculates the WAR for each day using a database query, and then calculates and prints the minimum, maximum, and average WAR over the entire period. The WAR is assumed to be a measure of the effectiveness of recommendations on a given day, weighted by some criteria (e.g., user engagement or satisfaction).

        Prints:
            - Average Model Rating for each day in the format: "Average Model Rating for YYYY-MM-DD: X.X"
            - Minimum Rating over the period: X.X
            - Maximum Rating over the period: X.X
            - Average Rating over the period: X.X

        Usage example (from the command line):
            python -c 'from calculate_performance import war_over_period; war_over_period(17, 3, 2024, 18, 3, 2024)'
    
    """
    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    current_date = start_date
    ratings = []

    client = setup_mongo_connection()
    db = client.movie_recommendation_system

    while current_date <= end_date:
        average_rating = calculate_metric_for_day(current_date, db=db)
        if not average_rating:
            average_rating = 0
        print(f"Average Model Rating for {current_date.date()}: {average_rating}")
        ratings.append(average_rating)
        current_date += timedelta(days=1)
    
    if ratings:
        min_rating = min(ratings)
        max_rating = max(ratings)
        avg_rating = sum(ratings) / len(ratings)
        print(f"Minimum Rating over the period: {min_rating}")
        print(f"Maximum Rating over the period: {max_rating}")
        print(f"Average Rating over the period: {avg_rating}")
    else:
        print("No ratings found for the specified period.")
