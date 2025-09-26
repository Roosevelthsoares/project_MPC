import gc
import logging
import os
from pathlib import Path
from domain.entities.loggers.metrics import PrometheusPushLogger, Timer
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Tuple
from moe.src.moe.predictors import MoEPredictor
from moe.src.moe.calibration import GateCalibrator
from moe.src.data_preprocessing import DataProcessor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split



class PathModelConfig(BaseModel):
    base_path: str = Field(..., description="Base directory where all models are stored.")
    gate_model_path: str = Field(..., description="Path to the gate model.", exclude=True)
    experts_models_path: Dict[str, str] = Field({}, description="Mapping of attack types to expert model paths.", exclude=True)

    @model_validator(mode="before")
    @classmethod
    def validate_and_load_paths(cls, values):
        """Automatically discover models based on directory structure."""
        base_path = Path(values["base_path"]).resolve()

        if not base_path.is_dir():
            raise ValueError(f"Base path does not exist or is not a directory: {base_path}")

        # Gate Model
        gate_dir = base_path / "gate"
        gate_model_path = next(gate_dir.glob("*.h5"), None) if gate_dir.exists() else None
        if not gate_model_path:
            raise ValueError(f"Gate model not found in: {gate_dir}")
        values["gate_model_path"] = str(gate_model_path)

        # Experts Models
        experts_dir = base_path / "experts"
        experts_models = {}
        if experts_dir.exists():
            for expert_subdir in experts_dir.iterdir():
                if expert_subdir.is_dir():
                    model_path = next(expert_subdir.glob("*.h5"), None)
                    if model_path:
                        experts_models[expert_subdir.name] = str(model_path)
                    else:
                        raise ValueError(f"Expert model missing in: {expert_subdir}")
        if not experts_models:
            raise ValueError("No expert models found in the experts directory.")
        values["experts_models_path"] = experts_models

        return values
    
class MLFlowModelConfig(BaseModel):
    pass

class Predictor:
    def __init__(self, config: PathModelConfig|MLFlowModelConfig=PathModelConfig(base_path='data/models')):
        self._config = config  # Store the validated config
        self._built = False  # Track if models have been loaded
        self.id2lbl = {}
        self.lbl2id = {}
        self.experts: List = []
        self.gate_model = None
        self._logger = PrometheusPushLogger()

    @property
    def config(self) -> PathModelConfig:
        """Read-only config property."""
        return self._config

    def build(self) -> 'Predictor':
        if self._built:
            raise RuntimeError("Predictor is already built.")
        self._built = True
        
        if isinstance(self._config, PathModelConfig):
            self._build_from_dir()
        elif isinstance(self._config, MLFlowModelConfig):
            self._load_mlflow_model()
        
        return self
            
    def _load_mlflow_model(self):
        pass
    
    def _build_label_maps(self):
        self.id2lbl = {i: attack for i, attack in enumerate(self._config.experts_models_path.keys())}
        self.lbl2id = {attack: i for i, attack in enumerate(self._config.experts_models_path.keys())}
        self.classes = list(self.lbl2id.keys())
        
    def _load_from_dir(self):
        self.experts = [load_model(path) for path in self._config.experts_models_path.values()]
        self.gate_model = load_model(self._config.gate_model_path)

    def _load_data_from_dir(self) -> tuple[np.ndarray, np.ndarray]:
        calibration_data_path = Path(self._config.base_path) / "calibrate" / "CICIDS2018_preprocessed_test_reduced.parquet"

        if not calibration_data_path.exists():
            raise FileNotFoundError(f"Calibration data file not found: {calibration_data_path}")
        
        processor = DataProcessor(data_path=calibration_data_path)
        processor.load_and_preprocess_data()

        processor.label_dict = self.lbl2id
        processor.y = processor.y.map(self.lbl2id).astype(np.uint8)
        
        X = processor.X.astype(np.float32)
        y = processor.y
        del processor
        gc.collect()
        return X, y
    
    def _load_preprocessor_from_dir(self, X: np.ndarray, y: np.ndarray):
        preprocessor_path = Path(self._config.base_path) / "preprocessor" / "pipeline.pkl"
        preprocessor_path.parent.mkdir(parents=True, exist_ok=True)


        if preprocessor_path.exists():
            scaler = joblib.load(preprocessor_path)
        else:
            _, X_sample, _, _ = train_test_split(
                X, y, test_size=0.1, stratify=y, random_state=42
            )
            logging.debug(f"new reduced calibration data shape: {X_sample.shape}")
            scaler = StandardScaler().fit(X_sample)
            joblib.dump(scaler, preprocessor_path)
        
        return scaler
                
    def _import_calibration_data(self) -> tuple:
        """
        Import calibration data from a CSV file.

        Returns:
            tuple: Tuple containing features and labels for calibration.
        """
        X, y = self._load_data_from_dir()
        scaler = self._load_preprocessor_from_dir(X, y)

        X_calibrate = scaler.transform(X)
        y_calibrate = y.to_numpy()
        return X_calibrate, y_calibrate
    
    def _save_on_mlflow(self):
        pass
    
    def _build_from_dir(self):
        """Load models only if they haven't been built yet."""
        self._build_label_maps()

        self._load_from_dir()
        
        X_calibrate, y_calibrate = self._import_calibration_data()
        
        self._calibrator = GateCalibrator(self.gate_model, self.classes, method=os.getenv("CALIBRATION_METHOD", 'isotonic').lower()).calibrate(X_calibrate, y_calibrate)
        
        del X_calibrate, y_calibrate
        gc.collect()        
        
        self.predictor = MoEPredictor(self._calibrator, {cls: expert for cls, expert in zip(self.classes, self.experts)}, self.classes)
        
        self._save_on_mlflow()
        
        return self

    def predict(self, X_input: np.ndarray, strategy: str = 'soft', id:str|None=None, threshold: float = 0.1, batch_size: int = 32, **kwargs) -> List[Tuple[str, float]]:
        """
        Predict using the Mixture of Experts (MoE) approach.

        Args:
            X_input (np.ndarray): Input data for prediction.
            strategy (str): The gating strategy to use ('hard', 'soft', 'top_k').
            threshold (float): Threshold for the soft gating strategy.
            batch_size (int): Number of samples to process at once.
            kwargs: Additional arguments, such as 'k' for top_k strategy.

        Returns:
            List[str]: Predicted classes.
        """
        if not self._built:
            raise RuntimeError("Model is not built. Call `build()` first.")

        with Timer() as timer:
            preds = self.predictor.predict(X_input, strategy, threshold, batch_size, **kwargs)
        
        self._logger.log(input_data=X_input, latency=timer.elapsed_time,
                         variant=strategy, prediction=preds, metrics={'threshold': threshold, 'batch_size': batch_size}, id=id)
        return preds

