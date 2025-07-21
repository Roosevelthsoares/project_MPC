import gc
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from pydantic import BaseModel, Field, model_validator
from typing import Dict, List
# from moe.predictors import MoEPredictor
# from moe.calibration import GateCalibrator
from moe.src.moe.predictors import MoEPredictor
from moe.src.moe.calibration import GateCalibrator
# from data_preprocessing import DataProcessor
from moe.src.data_preprocessing import DataProcessor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split



class ModelConfig(BaseModel):
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

class Predictor:
    def __init__(self, config: ModelConfig=ModelConfig(base_path='data/models')):
        self._config = config  # Store the validated config
        self._built = False  # Track if models have been loaded
        self.id2lbl = {}
        self.lbl2id = {}
        self.experts: List = []
        self.gate_model = None

    @property
    def config(self) -> ModelConfig:
        """Read-only config property."""
        return self._config

    def build(self):
        """Load models only if they haven't been built yet."""
        if self._built:
            raise RuntimeError("Predictor is already built.")

        self.id2lbl = {i: attack for i, attack in enumerate(self._config.experts_models_path.keys())}
        self.lbl2id = {attack: i for i, attack in enumerate(self._config.experts_models_path.keys())}
        self.classes = list(self.lbl2id.keys())

        # Load models
        self.experts = [load_model(path) for path in self._config.experts_models_path.values()]
        self.gate_model = load_model(self._config.gate_model_path)

        self._built = True
        
        X_calibrate, y_calibrate = self._import_calibration_data()
        
        self._calibrator = GateCalibrator(self.gate_model, self.classes).calibrate(X_calibrate, y_calibrate)
        del X_calibrate, y_calibrate
        gc.collect()        
        self.predictor = MoEPredictor(self._calibrator, {cls: expert for cls, expert in zip(self.classes, self.experts)}, self.classes)
        
        return self
    
    
    # def _import_calibration_data(self) -> tuple:
    #     """
    #     Import calibration data from a CSV file.

    #     Returns:
    #         tuple: Tuple containing features and labels for calibration.
    #     """
    #     calibration_data_path = Path(self._config.base_path) / "calibrate" / "CICIDS2018_preprocessed_test.parquet"

    #     if not calibration_data_path.exists():
    #         raise FileNotFoundError(f"Calibration data file not found: {calibration_data_path}")
        
    #     processor = DataProcessor(data_path=calibration_data_path)
    #     processor.load_and_preprocess_data()

    #     # Apply external label mapping from Predictor
    #     processor.label_dict = self.lbl2id
    #     processor.y = processor.y.map(self.lbl2id).astype(np.uint8)

    #     # Prepare for scaler persistence
    #     preprocessor_path = Path(self._config.base_path) / "preprocessor" / "scaler.joblib"
    #     preprocessor_path.parent.mkdir(parents=True, exist_ok=True)

    #     if preprocessor_path.exists():
    #         scaler = joblib.load(preprocessor_path)
    #         del processor
    #         gc.collect()
    #     else:
    #         X, y = processor.X, processor.y
    #         del processor
    #         gc.collect()

    #         one_per_class_idx = [y[y == label].index[0] for label in np.unique(y)]
    #         total_target_size = int(len(X) * 0.2)

    #         remaining_indices = y.index.difference(one_per_class_idx)
    #         remaining_needed = max(total_target_size - len(one_per_class_idx), 0)
    #         additional_indices = (
    #             remaining_indices.to_series()
    #             .sample(n=remaining_needed, random_state=42)
    #             .index if remaining_needed > 0 else []
    #         )

    #         final_indices = one_per_class_idx + list(additional_indices)
    #         sample = X.loc[final_indices].astype(np.float32)

    #         scaler = StandardScaler().fit(sample)
    #         joblib.dump(scaler, preprocessor_path)

    #         X_calibrate = scaler.transform(X.astype(np.float32))
    #         y_calibrate = y.to_numpy()
    #         return X_calibrate, y_calibrate
    
    def _import_calibration_data(self) -> tuple:
        """
        Import calibration data from a CSV file.

        Returns:
            tuple: Tuple containing features and labels for calibration.
        """
        calibration_data_path = Path(self._config.base_path) / "calibrate" / "CICIDS2018_preprocessed_test.parquet"

        if not calibration_data_path.exists():
            raise FileNotFoundError(f"Calibration data file not found: {calibration_data_path}")
        
        processor = DataProcessor(data_path=calibration_data_path)
        processor.load_and_preprocess_data()

        # Apply label mapping
        processor.label_dict = self.lbl2id
        processor.y = processor.y.map(self.lbl2id).astype(np.uint8)

        # Set up preprocessor path
        preprocessor_path = Path(self._config.base_path) / "preprocessor" / "scaler.joblib"
        preprocessor_path.parent.mkdir(parents=True, exist_ok=True)

        X = processor.X.astype(np.float32)
        y = processor.y
        del processor
        gc.collect()

        if preprocessor_path.exists():
            scaler = joblib.load(preprocessor_path)
        else:
            # Stratified sampling: keep 20% of original data stratified by class
            _, X_sample, _, _ = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )
            print(X_sample.shape)
            scaler = StandardScaler().fit(X_sample)
            joblib.dump(scaler, preprocessor_path)

        X_calibrate = scaler.transform(X)
        y_calibrate = y.to_numpy()
        return X_calibrate, y_calibrate
    

    def predict(self, X_input: np.ndarray, strategy: str = 'soft', threshold: float = 0.1, batch_size: int = 32, **kwargs) -> List[str]:
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

        return self.predictor.predict(X_input, strategy, threshold, batch_size, **kwargs)

