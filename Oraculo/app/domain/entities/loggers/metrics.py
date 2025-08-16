import mlflow
from mlflow.tracking import MlflowClient

from interfaces.extensions.loggers.metrics import MetricLoggingExtension


class MLFlowLogger(MetricLoggingExtension):
    def __init__(self, tracking_uri: str = None):
        self.client = MlflowClient()
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)

    def new_experiment(self, experiment_name: str):
        mlflow.set_experiment(experiment_name)

    def log(self, model_name: str, model_version: str, input_data: dict, prediction: float, latency: float,
            deployment_experiment_id: str, variant: str = None, wait_time: int | None = None, inference_time: int | None = None):
        run = self.client.get_latest_versions(model_name, stages=["Production"])[0]
        run_id = run.run_id

        with mlflow.start_run(run_id=run_id, nested=True):
            mlflow.log_params(input_data)
            mlflow.log_metric("prediction", float(prediction))
            mlflow.log_metric("latency_microsecond", latency * 1000)
            mlflow.set_tag("model_version", model_version)
            mlflow.set_tag("deployment_experiment_id", deployment_experiment_id)
            if variant:
                mlflow.set_tag("variant", variant)
            if wait_time is not None:
                mlflow.log_metric("wait_time_microsecond", wait_time * 1000)
            if inference_time is not None:
                mlflow.log_metric("inference_time_microsecond", inference_time * 1000)