import numpy
import json
import joblib
from pathlib import Path
from domain.entities.predictor import Predictor

class ClassificationService:

    def __init__(self, predictor: Predictor):
        self.__predictor = predictor
        preprocessor_path = Path("data/models/preprocessor/scaler.joblib")
        if not preprocessor_path.exists():
            raise RuntimeError("Preprocessor not found. Please build the Predictor first.")

        self.__scaler = joblib.load(preprocessor_path)

        
        try: self.__predictor.build()
        except RuntimeError: pass    

    def pre_processing(self, message):
        try:
            data = json.loads(message)
            # temp = list(data.values())
            # return temp[0], self.__scaler.transform(numpy.array([temp[1:]]))


            ### -------------- MODIFICADO ----------------------------------- ###    
            # extraia o IP  
            ip = data["IP Src"]

            # pegue só o vetor de floats que já montamos lá no producer  
            features = data["features"]

            # crie a matriz 2D (1, n_features) corretamente  
            X = numpy.array([features], dtype=float)

            # e devolva ip + dados escalados  
            return ip, self.__scaler.transform(X)
            ### ------------------------------------------------------------- ###             
            
        
        except Exception:
            raise



    def classification(self, input_data):
        return self.__predictor.predict(input_data)

    