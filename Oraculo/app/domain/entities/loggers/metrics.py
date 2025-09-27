import os
import time
from typing import Any, Dict, List, Optional

import numpy as np
import requests
import mlflow
from mlflow.tracking import MlflowClient

from interfaces.extensions.loggers.metrics import MetricLoggingExtension


class Timer:
    def __init__(self):
        pass
    
    def __enter__(self):
        self.start_time = time.perf_counter_ns()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.perf_counter_ns()
        self.elapsed_time = self.end_time - self.start_time
        return False


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
           
     
class PrometheusPushLogger(MetricLoggingExtension):
    """
    MLFlow-like interface, but pushes metrics to Prometheus Pushgateway
    in one shot (single HTTP PUT), suitable for Grafana via Prometheus.

    - Keeps the same method names/signature you showed.
    - Converts latency/wait_time/inference_time to microseconds (to match your example).
    - Sends your own dict of metrics as-is (numeric -> gauges).
    - Adds useful labels (model_name, version, etc.), plus optional static labels.
    """

    def __init__(
        self,
        job: str = "inference",
        instance: Optional[str] = None,
        static_labels: Optional[Dict[str, str]] = None,
        timeout_sec: float = 3.0,
    ):
        self.gateway_url = os.getenv("PUSHGATEWAY_URL", "http://pushgateway:9091")
        self.job = job
        self.instance = instance or self._default_instance()
        self.static_labels = static_labels or {}
        self.timeout_sec = timeout_sec
        self._experiment_name: Optional[str] = None


    def new_experiment(self, experiment_name: str):
        # Not used by Prometheus, but we keep it for compatibility
        # and include it as a label on every metric.
        self._experiment_name = experiment_name

    def log(
        self,
        id: str,
        # input_data: np.ndarray,
        # prediction: List[str],
        latency: float,
        ids_version: str = "Oraculo",
        variant: str | None = None,
        wait_time: int | None = None,
        metrics: Dict[str, float] | None = None,
    ):
        """
        Push a batch of metrics in one request.

        Args:
            input_data: np.ndarray, numeric inputs. Flattened into input_0, input_1, ...
            prediction: list of strings, logged as labels prediction_0="...", prediction_1="..."
            latency: latency in milliseconds (converted to microseconds internally).
            ids_version: version tag (default "Oraculo").
            variant: optional variant tag.
            wait_time: optional wait time in milliseconds (converted to microseconds).
            metrics: optional dict of extra numeric metrics.
        """
        # Base labels
        base_labels = {"ids_version": ids_version}
        if variant:
            base_labels["variant"] = variant
        if self._experiment_name:
            base_labels["experiment"] = self._experiment_name
        base_labels.update(self.static_labels)

        # # Convert input_data (ndarray) into numeric metrics
        # input_numeric: Dict[str, float] = {}
        # if input_data is not None:
        #     arr = np.array(input_data).flatten()
        #     for i, val in enumerate(arr):
        #         input_numeric[f"{i}"] = float(val)

        # # Convert prediction (list[str]) into labels
        # prediction_labels: Dict[str, str] = {}
        # if prediction:
        #     for i, val in enumerate(prediction):
        #         prediction_labels[f"prediction_{i}"] = str(val)

        # Build Prometheus exposition text format
        lines: list[str] = []

        def add_metric(name: str, value: float, extra_labels: Optional[Dict[str, str]] = None):
            mname = self._sanitize_metric_name(name)
            all_labels = {**base_labels}#, **prediction_labels}
            if extra_labels:
                all_labels.update(extra_labels)
            label_s = ",".join(f'{k}="{self._escape_label(v)}"' for k, v in sorted(all_labels.items()))
            # TYPE line (harmless if repeated)
            lines.append(f"# TYPE {mname} gauge")
            if label_s:
                lines.append(f"{mname}{{{label_s}}} {self._fmt_float(value)}")
            else:
                lines.append(f"{mname} {self._fmt_float(value)}")

        # Core metrics
        add_metric("latency_microsecond", float(latency) * 1000.0)
        if wait_time is not None:
            add_metric("wait_time_microsecond", float(wait_time) * 1000.0)

        # Numeric input metrics
        # for k, v in input_numeric.items():
        #     add_metric(f"input_{k}", v)

        # Extra metrics
        if metrics:
            for k, v in metrics.items():
                add_metric(k, float(v))

        # Final newline per Prometheus format
        body = "\n".join(lines) + "\n"

        # Push to Pushgateway
        url = f"{self.gateway_url}/metrics/job/{self._url_seg(self.job)}/instance/{self._url_seg(self.instance)}"
        try:
            r = requests.put(url, data=body.encode("utf-8"), timeout=self.timeout_sec)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[PrometheusPushLogger] push failed: {e}")

    def clear_group(self):
        """Delete the current job/instance group from Pushgateway."""
        url = f"{self.gateway_url}/metrics/job/{self._url_seg(self.job)}/instance/{self._url_seg(self.instance)}"
        try:
            r = requests.delete(url, timeout=self.timeout_sec)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[PrometheusPushLogger] clear failed: {e}")

    @staticmethod
    def _default_instance() -> str:
        # Keep it simple; override if you want pod/container id etc.
        return str(int(time.time()))

    @staticmethod
    def _sanitize_metric_name(name: str) -> str:
        # Prometheus metric name: [a-zA-Z_:][a-zA-Z0-9_:]*
        safe = []
        for i, ch in enumerate(name):
            if (ch.isalnum() or ch in ":_") and not (i == 0 and ch.isdigit()):
                safe.append(ch)
            else:
                safe.append("_")
        res = "".join(safe)
        if res[0].isdigit():
            res = "_" + res
        return res

    @staticmethod
    def _escape_label(v: str) -> str:
        return str(v).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')

    @staticmethod
    def _fmt_float(x: float) -> str:
        # Compact but precise enough for typical metrics
        return f"{x:.10g}"

    @staticmethod
    def _url_seg(s: str) -> str:
        # path segs in Pushgateway are not URL-encoded by requests, keep simple
        return "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in str(s))

    @staticmethod
    def _partition_input(d: Dict[str, Any]) -> tuple[Dict[str, str], Dict[str, float]]:
        labels: Dict[str, str] = {}
        numeric: Dict[str, float] = {}
        for k, v in (d or {}).items():
            key = "".join(ch if ch.isalnum() or ch in "_:" else "_" for ch in str(k))
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                numeric[key] = float(v)
            else:
                # stringify strings/enums/bools to labels (watch your cardinality!)
                labels[key] = str(v)
        return labels, numeric