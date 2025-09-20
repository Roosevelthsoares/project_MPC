import logging
import os
from typing import Tuple
import numpy
import json
import joblib
from pathlib import Path
from domain.entities.predictor import Predictor

class ClassificationService:

    def __init__(self, predictor: Predictor):
        self.__gating_strategy = os.getenv("GATING_METHOD", 'soft')
        self.predictor = predictor
        preprocessor_path = Path("data/models/preprocessor/pipeline.pkl")
        if not preprocessor_path.exists():
            raise RuntimeError("Preprocessor not found. Please build the Predictor first.")

        self.__scaler = joblib.load(preprocessor_path)

        
        try: self.predictor.build()
        except RuntimeError: pass    

    def pre_processing(self, message: dict) -> Tuple[str, numpy.ndarray]:
        try:
            data = json.loads(message)
            ip = data["IP Src"]
            features = data["features"]
            X = numpy.array([features], dtype=float)
            return ip, self.__scaler.transform(X)
        except Exception as e:
            logging.error(f"Classification Service could not pre-process message: {message}, with error:")
            logging.error(e.with_traceback())
            raise e

    def classification(self, input_data: numpy.ndarray) -> list[Tuple[str, float]]:
        return self.predictor.predict(input_data, strategy=self.__gating_strategy)

    