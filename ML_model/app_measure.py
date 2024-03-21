from flask import Flask, request, jsonify, abort
from ML_model import bubba_ML
from time import time
import hashlib

app = Flask(__name__)
predict = bubba_ML.Model()
movies = bubba_ML.Movies()
users = bubba_ML.Users()

REQUESTS_1000 = 1000 # testing with 1000 requests
REQUESTS_2000 = 2000 # testing with 2000 requests
REQUESTS_5000 = 5000 # testing with 5000 requests

# 1. http get request is called at http://<address-of-your-virtual-machine>:8082/recommend/<userid>
# 2. user id is captured and parsed to ML function
# 3. return from ML function is JSON
# 4. JSON is returned to GET request

# http://<address-of-your-virtual-machine>:8082/recommend/<userid>

invalid_responses = 0
total_requests = 0
unique_response_hashes = set()

def limit_reach_output_file(limit):
    # Write global variables to output file
    path = f"/home/team24/Desktop/group-project-s24-bubba-gump-ai/output_{limit}.txt"
    with open(path, "w") as file:
        file.write(f"Number of Invalid Responses: {invalid_responses}\n")
        file.write(f"Number of Unique Responses: {len(unique_response_hashes)}\n")
        file.write(f"Unique Responses Rate: {(len(unique_response_hashes)) / (total_requests - invalid_responses)}\n")
        file.write(f"Total Number of Requests: {total_requests}\n")


@app.before_request
def limit_requests():
    global total_requests
    if total_requests == REQUESTS_1000:
        limit_reach_output_file(REQUESTS_1000)
    if total_requests == REQUESTS_2000:
        limit_reach_output_file(REQUESTS_2000)
    if total_requests == REQUESTS_5000:
        limit_reach_output_file(REQUESTS_5000)


@app.after_request
def after_request(response):
    global total_requests, invalid_responses, unique_response_hashes
    
    total_requests += 1

    if response.status_code != 200:
        invalid_responses += 1
    else:
        # Create a hash of the response data for uniqueness tracking
        response_hash = hashlib.sha256(response.get_data()).hexdigest()
        unique_response_hashes.add(response_hash)
    return response

@app.route('/recommend/<int:userid>')
def recommend(userid):  # put application's code here
    # print(f"User #{userid} has requested recommendations.")

    # insert function call to model here and return - expect JSON format to place in return statement

    return ','.join(predict.predictTopMovies(user_ID=userid, movies=movies, users=users))


@app.route('/')
def test():  # put application's code here
    print("This is a test that the default / home page is reachable")

    return "This is a test that the default / home page is reachable"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082)

