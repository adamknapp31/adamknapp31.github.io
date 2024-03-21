# Bubba Gump AI
Machine Learning in Production (CMU)


## Team memebers:
- Daniel Hales
- Natasha Joseph
- Adam Knapp
- Yan Lou
- Shaurya Singh
- Nora Xia

## Status:
- Milestone 1: complete
- Milestone 2: ongoing

## Runnning the code:

### Dependencies:
- Python version ???
- Install requirements.txt (pip install -r requirements.txt)
- Local MongoDB database version 6.0 (can be installed at https://www.mongodb.com/try/download/community)
- Input the .env into root for database info (found in team drive Folder: https://drive.google.com/file/d/1rf10RmxvmgPL7jOh6Zu4nlDjXrAi0lx9/view?usp=drive_link)

### Serving Recommendations
- In ML_model folder (cd ML_model)
- Run app.py (python app.py)

## Kafka Stream
- Connect to Kafka Stream (ssh -o ServerAliveInterval=60 -L 9092:localhost:9092 tunnel@128.2.204.215 -NTf   || password: seaitunnel)

## Collecting Telemetry
- cd data_collection
- Run collect_stream (python collect_stream.py)

## Calculate Online model Performance 
- In ML_model folder (cd online_performance)
- call war_day with date for evaluation:
    Example for 15March 2024: 
        python -c 'from calculate_performance import war_day; war_day(18, 3, 2024)'
- Call war_over_period to evaluate model over deployment:
    Example for 17-18March2024:
        python -c 'from calculate_performance import war_over_period; war_over_period(17, 3, 2024, 18, 3, 2024)'
