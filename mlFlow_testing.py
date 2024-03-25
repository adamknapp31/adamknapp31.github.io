 # The data set used in this example is from http://archive.ics.uci.edu/ml/datasets/Wine+Quality
# P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis.
# Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.
import itertools
import os
import warnings

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import os
import mlflow.sklearn

np.random.seed(40)




def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

def load_env_variables(env_file=".env"):
    with open(env_file, "r") as file:
        for line in file:
            if line.startswith('#') or not line.strip():
                continue
            # Assuming each line is var=value
            # Strip spaces from key and value separately
            key, value = map(str.strip, line.strip().split('=', 1))
            os.environ[key] = value

# Load the .env file
load_env_variables()

# Now you can access the environment variables using os.environ
MLFLOW_TRACKING_TOKEN = os.environ.get("MLFLOW_TRACKING_TOKEN")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")

# Use the variables as needed
print("MLFLOW_TRACKING_TOKEN:", MLFLOW_TRACKING_TOKEN)
print("MLFLOW_TRACKING_URI:", MLFLOW_TRACKING_URI)


# Read the wine-quality csv file (make sure you're running this from the root of MLflow!)
data = pd.read_csv("wine-quality.csv")

# Split the data into training and test sets. (0.75, 0.25) split.
train, test = train_test_split(data)

# The predicted column is "quality" which is a scalar from [3, 9]
train_x = train.drop(["quality"], axis=1)
test_x = test.drop(["quality"], axis=1)
train_y = train[["quality"]]
test_y = test[["quality"]]

mlflow.set_experiment(experiment_name=f"Demo 9")

alphas = [.1, .2, .3]
l1_ratios = [0.1, 0.2, 0.3]

combinations = itertools.product(alphas, l1_ratios)

for index, [alpha, l1_ratio] in enumerate(combinations):
    with mlflow.start_run(run_name=f"Candidate {index}"):
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)

        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha , l1_ratio))
        print("  RMSE: %s" % rmse)
        print("  MAE: %s" % mae)
        print("  R2: %s" % r2)

        #mlflow.log_param("alpha", alpha / 10.0)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)
        mlflow.log_artifact("requirements.txt")