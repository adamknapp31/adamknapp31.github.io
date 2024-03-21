import unittest
# Add the ML_model directory to the sys.path so we can import the app
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ML_model.app import app

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_recommendation_endpoint(self):
        # Example user ID to test
        test_user_id = 123
        # Make a GET request to the recommend endpoint
        response = self.app.get(f'/recommend/{test_user_id}')
        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Further checks as necessary...

    def test_recommendation_bad_user_id(self):
        # Example user ID to test
        test_user_id = 0
        # Make a GET request to the recommend endpoint
        response = self.app.get(f'/recommend/{test_user_id}')
        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 400)
        # Further checks as necessary...

if __name__ == '__main__':
    unittest.main()