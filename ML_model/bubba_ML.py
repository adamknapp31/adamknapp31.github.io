# bubba_ML.py
# Description: Module to call ML model to get a specific user movie recommandations
# Model Version: 3 (Wrapped the code of SVD model V1.1)



from surprise import Dataset, Reader
from surprise import SVD
import pickle
import random


class Movies:
    def __init__(self, file_path="ML_model/movies_list_v1.2.pkl"):
        """
        Initializes a movie object
        Args:
            file_path (str): path to the saved movies file
        Returns:
            None
        """
        self.path = file_path
        try:
            self.data = pickle.load(open(self.path, 'rb'))
        except FileNotFoundError:
            self.data = None
            print(f"Movies file '{self.path}' not found.")


class Users:
    def __init__(self, file_path="ML_model/user_list_v1.pkl"):
        """
        Initializes a user object
        Args:
            file_path (str): path to the saved users file
        Returns:
            None
        """
        self.path = file_path
        try:
            self.data = pickle.load(open(self.path, 'rb'))
        except FileNotFoundError:
            self.data = None
            print(f"Users file '{self.path}' not found.")



class Model:
    def __init__(self, file_path="ML_model/svd_model_v1.2.pkl"):
        """
        Initializes a model object
        Args:
            file_path (str): path to the saved model file
        Returns:
            None
        """

        self.path = file_path
        try:
            self.model = pickle.load(open(self.path, "rb"))
        except FileNotFoundError:
            self.model = None
            print(f"Model file ' {self.path} ' not found.")

    
    def predictTopMovies(self, user_ID: int, movies: Movies, users: Users) -> list:
        """
        Finds prediction for a userID
        Args:
            user_ID (str): user id to predict movies for
            movies (Movies): object containing movie data
            users (Users): object containing user data
        Returns:
            top_recommendations (list): list of top 20 movies (str)
        """

        # Raise error if movie data has not been loaded
        if movies.data is None:
            raise TypeError("Movie data is required.")
        
        # Raise error if movie data has not been loaded
        if users.data is None:
            raise TypeError("User data is required.")

        # Generate predictions
        predictions = []

        
        if user_ID in users.data: #If you have a known user-> use model

            for movie_title in movies.data:
                predicted_rating = self.model.predict(str(user_ID), movie_title).est
                predictions.append(("+".join(movie_title.split()), predicted_rating))
            
            # Sort movies in descending order of ratings
            predictions.sort(key=lambda x: x[1], reverse=True)

            # Return top 20 recommendations
            top_recommendations = [movie for movie, _ in predictions[:20]]

        else: #Else (you have an unknown user)-> random top 500 movies
            top_recommendations = random.sample(movies.data, 20)
        return top_recommendations
    

