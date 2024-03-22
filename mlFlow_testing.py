import mlflow

# Hard-coding environment variables
MLFLOW_TRACKING_URI = 'https://gitlab.com/mlinprod/movie-recommendations/api/v4/projects/56020467/ml/mlflow'
MLFLOW_TRACKING_TOKEN = 'glpat-qLC7cLvyz8hPqFyM8eRj'

# Setting the MLflow tracking URI and token
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Your Experiment Name Here")

# Authentication with the MLflow server (in this case, GitLab)
def set_mlflow_token():
    import mlflow
    mlflow.set_registry_uri(MLFLOW_TRACKING_URI)
    mlflow.tracking._tracking_service.utils._HANDLERS['http'].set_default_header("Authorization", f"Bearer {MLFLOW_TRACKING_TOKEN}")

set_mlflow_token()

index = 0  # Example index, adjust as needed

with mlflow.start_run(run_name=f"Candidate {index}"):
    # Your training code here

    # Log a parameter as an example
    mlflow.log_param("param_name", "param_value")

    # Log a metric as an example
    mlflow.log_metric("metric_name", 0.85)

    # No GitLab CI-specific tags since we're not in a GitLab CI environment
    # However, you can set other tags as needed
    mlflow.set_tag("example_tag", "value")

    # Example of logging an artifact - ensure the file exists
    # mlflow.log_artifact("path/to/your/file", "artifact_folder")
