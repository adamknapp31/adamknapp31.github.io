import unittest
from datetime import datetime
from data_collection.collect_telemetry import identify_request_type, process_user_watch_info, process_user_rating_info, process_recommendation_info

class TestIdentifyRequestType(unittest.TestCase):

    def test_identify_request_type(self):
        # Test for user watching a movie request
        watch_message = ["2024-03-15T13:23:19.104304", "user123", "/data/movie/1234/5.mp4"]
        self.assertEqual(identify_request_type(watch_message), "DATA")

        # Test for user rating a movie request
        rating_message = ["2024-03-15T13:23:19.104304", "user456", "/rate/movie/5678=4"]
        self.assertEqual(identify_request_type(rating_message), "RATE")

        # Test for user sending a recommendation request
        recommend_message = ["2024-03-15T13:23:19.104304", "user789", "/recommendation"]
        self.assertEqual(identify_request_type(recommend_message), "RECOMMENDATION")

        # Test for invalid request
        invalid_message = ["2024-03-15T13:23:19.104304", "user789", 'rate', 'longer']
        self.assertEqual(identify_request_type(invalid_message), "INVALID")

class TestProcessUserWatchInfo(unittest.TestCase):

    def test_process_user_watch_info(self):

        # Test case 1: User watch information with different timestamp format
        message = ("2024-03-15T13:23:19", "user456", "/data/movie/5678/10.mp4")
        expected_document = {
            'user_id': "user456",
            'movieid': "5678",
            'timestamp': datetime(2024, 3, 15, 13, 23, 19),
            'minute': 10
        }
        self.assertEqual(process_user_watch_info(message), expected_document)

class TestProcessUserRatingInfo(unittest.TestCase):

    def test_process_user_rating_info(self):
        # Test case 1: User rating information with valid message
        message = ("2024-03-15T13:23:19", "user123", "/rate/movie/1234=4")
        expected_document = {
            'user_id': "user123",
            'movieid': "1234",
            'timestamp': datetime(2024, 3, 15, 13, 23, 19),
            'rating': 4
        }
        self.assertEqual(process_user_rating_info(message), expected_document)

        # Test case 2: User rating information with different rating
        message = ("2024-03-15T13:23:19", "user456", "/rate/movie/5678=5")
        expected_document = {
            'user_id': "user456",
            'movieid': "5678",
            'timestamp': datetime(2024, 3, 15, 13, 23, 19),
            'rating': 5
        }
        self.assertEqual(process_user_rating_info(message), expected_document)

class TestProcessRecommendationInfo(unittest.TestCase):

    def test_process_recommendation_info(self):
        # Test case 1: Recommendation information with valid message
        message = ["2024-03-15T13:23:19", "user123", 'server' ,'200'] + [f"movie{i}" for i in range(1, 21)]
        expected_document = {
            'user_id': "user123",
            'recommended_movies': [f"movie{i}" for i in range(1, 21)],
            'timestamp': datetime(2024, 3, 15, 13, 23, 19)
        }
        self.assertEqual(process_recommendation_info(message), expected_document)

if __name__ == '__main__':
    unittest.main()