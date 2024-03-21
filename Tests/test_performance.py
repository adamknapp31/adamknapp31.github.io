import unittest
from datetime import datetime, timezone
from pymongo import MongoClient
import mongomock



from online_performance.calculate_performance import calculate_metric_for_day, fetch_recommendations, find_next_movie_watched,  find_next_movie_rating  # Adjust import as necessary

class UnitTestPerformanceFunctions(unittest.TestCase):
    @mongomock.patch(servers=(('localhost', 27017),))
    def test_fetch_recommendations_on_date_with_data(self):
        """
            Testing fetch_recommendations for correct date and data on one item
        
        """
        
        client = mongomock.MongoClient('localhost') #mock up the mongoDB database
        db = client['movie_recommendation_system0']
        
        # Prepopulate the mock database
        recommendations_data = [
                                    {'user_id': 'user123',
                                     'recommended_movies': ['movie1', 'movie2', 'movie3', 'movie4', 'movie5',
                                    'movie6', 'movie7', 'movie8', 'movie9', 'movie10','movie11', 'movie12', 'movie13', 'movie14', 'movie15',
                                    'movie16', 'movie17', 'movie18', 'movie19', 'movie20'],
                                    'timestamp': datetime(2025, 3, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
                                    },
                                    {'user_id': 'user1234',
                                     'recommended_movies': ['movie1', 'movie2', 'movie3', 'movie4', 'movie5',
                                    'movie6', 'movie7', 'movie8', 'movie9', 'movie10','movie11', 'movie12', 'movie13', 'movie14', 'movie15',
                                    'movie16', 'movie17', 'movie18', 'movie19', 'movie20'],
                                    'timestamp': datetime(2025, 3, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
                                    }
                                ]
        db.recommendations.insert_many(recommendations_data)
        
        # Example test: fetch recommendations on a specific date
        date = datetime(2025, 3, 15)  # Corrected to match the inserted data
        recommendations = fetch_recommendations(date, db)
        fetched_data = list(recommendations)
        
        
        self.assertEqual(len(fetched_data), 2)  # check number of items
        self.assertEqual(fetched_data[0]['user_id'], 'user123') #correct user for first item
        self.assertEqual(fetched_data[0]['recommended_movies'][0],'movie1') 
        self.assertEqual(len(fetched_data[0]['recommended_movies']), 20)  # Corrected to expect 20 movies
    
    def test_find_next_movie_watched(self):
        client = mongomock.MongoClient('localhost')
        db = client['movie_recommendation_system1']
        
        # Prepopulate the mock database
        watch_history_data = [
                                    #user123 watching different movies for 40 mins
                                    {'user_id': 'user123',
                                     'movieid': 'movie1',
                                    'timestamp': datetime(2025, 3, 15, 22, 16, 42, tzinfo=timezone.utc),
                                    'minute': 10},
                                    {'user_id': 'user123',
                                     'movieid': 'movie2',
                                    'timestamp': datetime(2025, 3, 15, 22,26 , 42, tzinfo=timezone.utc),
                                    'minute': 20},
                                    {'user_id': 'user123',
                                     'movieid': 'movie3',
                                    'timestamp': datetime(2025, 3, 15, 22,36 , 42, tzinfo=timezone.utc),
                                    'minute': 30},
                                    {'user_id': 'user123',
                                     'movieid': 'movie4',
                                    'timestamp': datetime(2025, 3, 15, 22,46 , 42, tzinfo=timezone.utc),
                                    'minute': 40},

                                    ##user123 change movie
                                    {'user_id': 'user123',
                                     'movieid': 'movie2',
                                    'timestamp': datetime(2025, 3, 15, 22,47 , 42, tzinfo=timezone.utc),
                                    'minute': 0},

                                    #user1234 watch for 20 mins 
                                    {'user_id': 'user1234',
                                     'movieid': 'movie1',
                                    'timestamp': datetime(2025, 3, 15, 22,16 , 42, tzinfo=timezone.utc),
                                    'minute': 0},
                                    {'user_id': 'user1234',
                                     'movieid': 'movie1',
                                    'timestamp': datetime(2025, 3, 15, 22,26 , 42, tzinfo=timezone.utc),
                                    'minute': 10}
                                ]
        db.user_watch_history.insert_many(watch_history_data)

        recommendation_time = datetime(2025, 3, 15, 22,30 , 42, tzinfo=timezone.utc) 
        watched_movie = find_next_movie_watched(user_id ='user123', recommendation_time = recommendation_time, db =db)

        #Different movies watched every iteration
        self.assertEqual(watched_movie['movieid'], 'movie3')
        self.assertEqual(watched_movie['watched_at'], datetime(2025, 3, 15, 22,36 , 42))

        #No movies watched
        recommendation_time = datetime(2025, 3, 15, 22,30 , 42, tzinfo=timezone.utc) 
        watched_movie = find_next_movie_watched(user_id ='user1234', recommendation_time = recommendation_time, db =db)
        self.assertEqual(watched_movie, None)

    def test_find_next_movie_rating(self):
        client = mongomock.MongoClient('localhost')
        db = client['movie_recommendation_system2']
        


        # Prepopulate the mock database
        user_ratings_data = [
                                    #user123 rating different movies for 40 mins
                                    {'user_id': 'user123',
                                     'movieid': 'movie1',
                                    'timestamp': datetime(2025, 3, 15, 22, 16, 42, tzinfo=timezone.utc),
                                    'rating': 5},
                                    {'user_id': 'user123',
                                     'movieid': 'movie2',
                                    'timestamp': datetime(2025, 3, 15, 22, 20, 42, tzinfo=timezone.utc),
                                    'rating': 4},
                                    {'user_id': 'user123',
                                     'movieid': 'movie1',
                                    'timestamp': datetime(2025, 3, 15, 22, 27, 42, tzinfo=timezone.utc),
                                    'rating': 3},
                                    {'user_id': 'user123',
                                     'movieid': 'movie1',
                                    'timestamp': datetime(2025, 3, 15, 22, 35, 42, tzinfo=timezone.utc),
                                    'rating': 2},
                                    {'user_id': 'user123',
                                     'movieid': 'movie3',
                                    'timestamp': datetime(2025, 3, 15, 22, 35, 42, tzinfo=timezone.utc),
                                    'rating': 3},

                                    {'user_id': 'user1234',
                                     'movieid': 'movie3',
                                    'timestamp': datetime(2025, 3, 15, 22, 20, 42, tzinfo=timezone.utc),
                                    'rating': 3},
                                    {'user_id': 'user1234',
                                     'movieid': 'movie2',
                                    'timestamp': datetime(2025, 3, 15, 22, 27, 42, tzinfo=timezone.utc),
                                    'rating': 4}

                                    
                                    
                                ]
        db.user_ratings.insert_many(user_ratings_data)

        recommendation_time = datetime(2025, 3, 15, 22, 25, 42, tzinfo=timezone.utc)
        watched_movie_rating = find_next_movie_rating(user_id = 'user123', recommendation_time = recommendation_time, watched_movie_id = 'movie1', db=db)

        #specific movie rating with different before and after
        self.assertEqual(watched_movie_rating["movie_rating"], 3)
        self.assertEqual(watched_movie_rating['watched_at'], datetime(2025, 3, 15, 22, 27, 42))

        #No user rating
        recommendation_time = datetime(2025, 3, 15, 22,30 , 42, tzinfo=timezone.utc) 
        watched_movie = find_next_movie_watched(user_id ='user12345', recommendation_time = recommendation_time, db =db)
        self.assertEqual(watched_movie, None)

    def test_calculate_metric_for_day(self):
        client = mongomock.MongoClient('localhost')
        db = client['movie_recommendation_system3']

        # Prepopulate the mock database

        user_ratings_data = [
            # Always rated
            {'user_id': 'user123',
             'movieid': 'movie1',
             'timestamp': datetime(2022, 3, 15, 22, 30, 42, tzinfo=timezone.utc),
             'rating': 5},
            {'user_id': 'user1234',
             'movieid': 'movie2',
             'timestamp': datetime(2022, 3, 15, 22, 20, 42, tzinfo=timezone.utc),
             'rating': 3},

            # watched but rated in the future
            {'user_id': 'user1',
             'movieid': 'movie2',
             'timestamp': datetime(2022, 4, 20, 22, 20, 42, tzinfo=timezone.utc),
             'rating': 3},

            # Mix of never watched, ratings, and future rating
            {'user_id': 'user20',
             'movieid': 'movie22',
             'timestamp': datetime(2022, 6, 20, 15, 8, 42, tzinfo=timezone.utc),
             'rating': 5},
            {'user_id': 'user40',
             'movieid': 'movie42',
             'timestamp': datetime(2022, 6, 20, 17, 8, 42, tzinfo=timezone.utc),
             'rating': 3}

        ]
        db.user_ratings.delete_many({})
        print(f"Number of documents in 'user_ratings' collection: {db.user_ratings.count_documents({})}")
        db.user_ratings.insert_many(user_ratings_data)

        watch_history_data = [
            # Always rated
            {'user_id': 'user123',
             'movieid': 'movie1',
             'timestamp': datetime(2022, 3, 15, 22, 18, 42, tzinfo=timezone.utc),
             'minute': 10},
            {'user_id': 'user123',
             'movieid': 'movie1',
             'timestamp': datetime(2022, 3, 15, 22, 28, 42, tzinfo=timezone.utc),
             'minute': 20},
            {'user_id': 'user1234',
             'movieid': 'movie2',
             'timestamp': datetime(2022, 3, 15, 22, 28, 42, tzinfo=timezone.utc),
             'minute': 20},

            # watched but rated in the future
            {'user_id': 'user1',
             'movieid': 'movie2',
             'timestamp': datetime(2022, 4, 15, 22, 33, 42, tzinfo=timezone.utc),
             'minute': 20},

            # Mix of never watched, ratings, and future rating

            {'user_id': 'user20',
             'movieid': 'movie22',
             'timestamp': datetime(2022, 6, 15, 5, 33, 42, tzinfo=timezone.utc),
             'minute': 20},
            {'user_id': 'user40',
             'movieid': 'movie42',
             'timestamp': datetime(2022, 6, 15, 5, 33, 42, tzinfo=timezone.utc),
             'minute': 20},
            {'user_id': 'user50',
             'movieid': 'movie52',
             'timestamp': datetime(2022, 6, 15, 5, 33, 42, tzinfo=timezone.utc),
             'minute': 20}

        ]
        db.user_watch_history.delete_many({})
        print(
            f"Number of documents in 'user_watch_history' collection: {db.user_watch_history.count_documents({})}")
        db.user_watch_history.insert_many(watch_history_data)

        # Prepopulate the mock database
        recommendations_data = [
            # Never Watched
            {'user_id': 'user123',
             'recommended_movies': [f'movie{i}' for i in range(71, 91)],
             'timestamp': datetime(2020, 3, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
             },
            {'user_id': 'user1234',
             'recommended_movies': [f'movie{i}' for i in range(71, 91)],
             'timestamp': datetime(2020, 3, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
             },

            # Always rated
            {'user_id': 'user123',
             'recommended_movies': ['movie1', 'movie2', 'movie3', 'movie4', 'movie5',
                                    'movie6', 'movie7', 'movie8', 'movie9', 'movie10', 'movie11', 'movie12',
                                    'movie13', 'movie14', 'movie15',
                                    'movie16', 'movie17', 'movie18', 'movie19', 'movie20'],
             'timestamp': datetime(2022, 3, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
             },
            {'user_id': 'user1234',
             'recommended_movies': ['movie1', 'movie2', 'movie3', 'movie4', 'movie5',
                                    'movie6', 'movie7', 'movie8', 'movie9', 'movie10', 'movie11', 'movie12',
                                    'movie13', 'movie14', 'movie15',
                                    'movie16', 'movie17', 'movie18', 'movie19', 'movie20'],
             'timestamp': datetime(2022, 3, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
             },

            # watched but rated in the future
            {'user_id': 'user1',
             'recommended_movies': ['movie1', 'movie2', 'movie3', 'movie4', 'movie5',
                                    'movie6', 'movie7', 'movie8', 'movie9', 'movie10', 'movie11', 'movie12',
                                    'movie13', 'movie14', 'movie15',
                                    'movie16', 'movie17', 'movie18', 'movie19', 'movie20'],
             'timestamp': datetime(2022, 4, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
             },

            # Mix of never watched, ratings, and future rating
            {'user_id': 'user20',
             'recommended_movies': [f'movie{i}' for i in range(20, 41)],
             'timestamp': datetime(2020, 6, 15, 0, 16, 42, 363000, tzinfo=timezone.utc)
             },
            {'user_id': 'user30',
             'recommended_movies': [f'movie{i}' for i in range(30, 51)],
             'timestamp': datetime(2020, 6, 15, 10, 16, 42, 363000, tzinfo=timezone.utc)
             },
            {'user_id': 'user40',
             'recommended_movies': [f'movie{i}' for i in range(40, 61)],
             'timestamp': datetime(2020, 6, 15, 15, 16, 42, 363000, tzinfo=timezone.utc)
             },
            {'user_id': 'user50',
             'recommended_movies': [f'movie{i}' for i in range(50, 71)],
             'timestamp': datetime(2020, 6, 15, 22, 16, 42, 363000, tzinfo=timezone.utc)
             },

        ]
        db.recommendations.delete_many({})
        print(f"Number of documents in 'recommendations' collection: {db.recommendations.count_documents({})}")
        db.recommendations.insert_many(recommendations_data)

        # Movies never watched
        average_rating = calculate_metric_for_day(datetime(2020, 3, 15), db=db)
        self.assertEqual(average_rating, 1)

        # Just ratings from users
        average_rating = calculate_metric_for_day(datetime(2022, 3, 15), db=db)
        self.assertEqual(average_rating, 4)

        # Watched but rated later
        average_rating = calculate_metric_for_day(datetime(2022, 4, 15), db=db)
        self.assertEqual(average_rating, 3)

        # Mix of never watched, watched but not rated, watched and rated, and future rating
        average_rating = calculate_metric_for_day(datetime(2020, 6, 15), db=db)
        self.assertEqual(average_rating, 3)


if __name__ == '__main__':
    unittest.main()
