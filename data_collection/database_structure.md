## Setup

Login Information
`username`: `root`
`password`: `12345`

Command to login from the terminal
`mongosh mongodb://root:12345@127.0.0.1:27017/movie_recommendation_system`

## Database Information
Database: `movie_recommendation_system`

Collections
1. `user_watch_history` - Contains information about the movies that users are watching in the incoming stream.

Document format
```
document = {
    'user_id': ID of the user watching the movie,
    'movieid': ID of the movie being watched,
    'timestamp': timestamp,
    'minute': Minute of the movie they are watching
    }
```
2. `user_ratings` - Contains information about the ratings that users are giving movies.

Document format
```
document = {
    'user_id': ID of the user watching the movie,
    'movieid': ID of the movie being watched,
    'timestamp': timestamp,
    'rating': Integer from 1-5
    }
```
    
3. `recommendations` - Movies that were recommended to the user by the system

Document format
```
document = {
    'user_id': ID of the user watching the movie,
    'recommended_movies': List of 20 movie IDs that were recommended to the user,
    'timestamp': timestamp,
    }
```
