from pymongo import MongoClient
from datetime import datetime
import os

import sys

sys.path.append('../')
from utilities import setup_mongo_connection

"""
Identify the type of request that is being logged
"""


def identify_request_type(message):
    # message is for user watching a movie
    if len(message) == 3 and '/data/' in message[2]:
        return "DATA"
    # message is for user rating a movie
    elif len(message) == 3 and '/rate/' in message[2]:
        return "RATE"
    # message is for a user sending a request
    elif 'recommendation' in message[2]:
        return "RECOMMENDATION"
    # failed data-preprocessing, should log this
    return "INVALID"


"""
Convert the user watch information into document format
"""


def process_user_watch_info(message):
    timestamp_str, user_id, movie_info = message
    movieid, minute = movie_info.split('/')[-2:]
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')

    # Prepare document
    document = {
        'user_id': user_id,
        'movieid': movieid,
        'timestamp': timestamp,
        'minute': int(minute.split('.')[0])  # Extract minute without file extension
    }

    return document


"""
Convert the user watch information into document format
"""


def process_user_rating_info(message):
    timestamp_str, user_id, movie_info = message
    movieid, rating = (movie_info.split('/')[-1]).split('=')
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')

    # Prepare document
    document = {
        'user_id': user_id,
        'movieid': movieid,
        'timestamp': timestamp,
        'rating': int(rating)  # Extract rating
    }

    return document


def process_recommendation_info(message):
    timestamp_str, user_id = message[0], message[1]
    movies = message[4: 24]
    timestamp = datetime.fromisoformat(timestamp_str)

    document = {
        'user_id': user_id,
        'recommended_movies': movies,
        'timestamp': timestamp,

    }

    return document


def log_stream_line(client, collection, document):
    collection.insert_one(document)


"""
Input: List with the values from the stream. Assumed that any
        from here is valid
Output: Log the data to the correct file
"""


def log_data(preprocessed_data):
    request_type = identify_request_type(preprocessed_data)
    client = setup_mongo_connection()
    db = client.movie_recommendation_system
    if client and request_type == "DATA":
        doc = process_user_watch_info(preprocessed_data)
        if client:
            log_stream_line(client, db.user_watch_history, doc)
        else:
            print("Failed to connect to MongoDB. Cannot log data.")
    elif client and request_type == "RATE":
        doc = process_user_rating_info(preprocessed_data)
        if client:
            log_stream_line(client, db.user_ratings, doc)
        else:
            print("Failed to connect to MongoDB. Cannot log data.")
    elif request_type == "RECOMMENDATION":
        doc = process_recommendation_info(preprocessed_data)
        if client:
            log_stream_line(client, db.recommendations, doc)
        else:
            print("Failed to connect to MongoDB. Cannot log data.")