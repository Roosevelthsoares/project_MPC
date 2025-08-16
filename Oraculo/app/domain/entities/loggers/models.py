import os
import mlflow
from mlflow.tracking import MlflowClient


def init_mlflow():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment(os.getenv("EXPERIMENT_STAGE", "development"))

def log_model_to_mlflow_and_register(model, preprocessor, model_name, version, stage="Production", extra_tags=None):
    with mlflow.start_run(run_name=f"register_{model_name}_{version}") as run:
        run_id = run.info.run_id

        # Log preprocessor and model separately
        mlflow.sklearn.log_model(preprocessor, artifact_path="preprocessor")
        mlflow.sklearn.log_model(model, artifact_path="model")

        # Optionally tag run
        if extra_tags:
            for k, v in extra_tags.items():
                mlflow.set_tag(k, v)

        # Register the model (the actual predictor, not the preprocessor)
        model_uri = f"runs:/{run_id}/model"
        registered_model = mlflow.register_model(model_uri, model_name)

        # Set the stage
        client = MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=registered_model.version,
            stage=stage,
            archive_existing_versions=True
        )

    return registered_model.version, run_id