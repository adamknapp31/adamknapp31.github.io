from flask import Flask
from flask import abort
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ML_model import bubba_ML

app = Flask(__name__)
predict = bubba_ML.Model()
movies = bubba_ML.Movies()
users = bubba_ML.Users()


# 1. http get request is called at http://<address-of-your-virtual-machine>:8082/recommend/<userid>
# 2. user id is captured and parsed to ML function
# 3. return from ML function is JSON
# 4. JSON is returned to GET request

# http://<address-of-your-virtual-machine>:8082/recommend/<userid>


@app.route('/recommend/<int:userid>')
def hello_world(userid):  # put application's code here
    # print(f"User #{userid} has requested recommendations.")

    if userid < 1 or userid > 1000000:
        abort(400)
    # insert function call to model here and return - expect JSON format to place in return statement
    prediction = ','.join(predict.predictTopMovies(userid, movies, users))

    return prediction


@app.route('/')
def test():  # put application's code here
    print("This is a test that the default / home page is reachable")

    return "This is a test that the default / home page is reachable"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082)
