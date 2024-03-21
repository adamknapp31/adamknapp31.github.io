#example.py
# Description: example of calling ML model
import bubba_ML



if __name__ == "__main__":
    # Load movie data
    movies = bubba_ML.Movies("movies_list_v1.2.pkl")

    # Load user data
    users = bubba_ML.Users("user_list_v1.pkl")

    # Load model
    model = bubba_ML.Model("svd_model_v1.2.pkl")

    # Specify user ID for which you want recommendations
    #user_id = 99788  # Actual user ID
    user_id = 123 # Unknown User

    # Get recommendations
    recommendations = model.predictTopMovies(user_id, movies, users)

    # Print recommendations
    print("Top 20 movie recommendations:")
    for movie in recommendations:
        print(movie)

#in cmd: python example.py