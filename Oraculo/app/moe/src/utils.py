from tensorflow.keras import backend as K
import tensorflow as tf 
import glob
import os
from tensorflow.keras.models import load_model
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np
import pandas as pd



class KerasGateWrapper(BaseEstimator, ClassifierMixin):
    """Wrapper for Keras models to be scikit-learn compatible"""
    def __init__(self, model, classes):
        self.model = model
        self.classes_ = classes  # Critical for scikit-learn compatibility
    
    def fit(self, X, y):
        # No-op for pre-trained models
        return self
    
    def predict_proba(self, X):
        return self.model.predict(X)
    
    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

def load_expert_models(model_dir, classes):
    expert_models = {}
    for cls in classes:
        pattern = os.path.join(model_dir, f"model_*_{cls}.h5")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            raise ValueError(f"No model file found for class: {cls}")
        elif len(matching_files) > 1:
            raise ValueError(f"Multiple model files found for class: {cls}. Files: {matching_files}")
        
        model_path = matching_files[0]
        expert_models[cls] = load_model(model_path)
        print(f"Loaded model for class '{cls}' from: {model_path}")
    
    return expert_models

def f2_score(y_true, y_pred):
    beta = 2
    y_pred = K.round(y_pred)
    # Cast y_true and y_pred to float32
    y_true = K.cast(y_true, 'float32')
    y_pred = K.cast(y_pred, 'float32')
    tp = K.sum(y_true * y_pred)
    fp = K.sum((1 - y_true) * y_pred)
    fn = K.sum(y_true * (1 - y_pred))
    precision = tp / (tp + fp + K.epsilon())
    recall = tp / (tp + fn + K.epsilon())
    beta_squared = beta ** 2
    f2 = (1 + beta_squared) * (precision * recall) / (beta_squared * precision + recall + K.epsilon())
    return f2

def multi_f2_score(y_true, y_pred):
    beta = 2
    # Ensure y_true is rank 1 (squeeze if it's shape [batch, 1])
    if len(y_true.shape) == 2 and y_true.shape[-1] == 1:
        y_true = tf.squeeze(y_true, axis=-1)

    # Convert y_true to one-hot encoding
    y_true = tf.cast(y_true, 'int32')
    num_classes = tf.shape(y_pred)[-1]
    y_true = tf.one_hot(y_true, depth=num_classes)

    # Convert y_pred to binary predictions
    y_pred = tf.argmax(y_pred, axis=-1)
    y_pred = tf.one_hot(y_pred, depth=num_classes)

    y_true = tf.cast(y_true, 'float32')
    y_pred = tf.cast(y_pred, 'float32')

    # Calculate true positives, false positives, false negatives
    tp = K.sum(y_true * y_pred, axis=0)
    fp = K.sum((1 - y_true) * y_pred, axis=0)
    fn = K.sum(y_true * (1 - y_pred), axis=0)

    # Calculate precision and recall
    precision = tp / (tp + fp + K.epsilon())
    recall = tp / (tp + fn + K.epsilon())

    beta_squared = beta ** 2
    f2 = (1 + beta_squared) * (precision * recall) / (beta_squared * precision + recall + K.epsilon())

    # Compute mean F2 across all classes
    f2 = K.mean(f2)
    return f2


def reduce_mem_usage(df):
    start_mem = df.memory_usage(deep=True).sum() / 1024**2
    print(f'Initial memory usage: {start_mem:.2f} MB')

    for col in df.columns:
        col_type = df[col].dtype
        if col_type.kind in ['i', 'u', 'f']:
            c_min = df[col].min()
            c_max = df[col].max()
            if pd.api.types.is_integer_dtype(col_type):
                if c_min >= np.iinfo(np.int8).min and c_max <= np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min >= np.iinfo(np.int16).min and c_max <= np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min >= np.iinfo(np.int32).min and c_max <= np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
            else:
                if c_min >= np.finfo(np.float16).min and c_max <= np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min >= np.finfo(np.float32).min and c_max <= np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
        else:
            if df[col].dtype == 'object' and df[col].nunique() / len(df[col]) < 0.5:
                df[col] = df[col].astype('category')

    end_mem = df.memory_usage(deep=True).sum() / 1024**2
    print(f'Optimized memory usage: {end_mem:.2f} MB')
    print(f'Reduced by {(start_mem - end_mem) / start_mem * 100:.1f}%')

    return df
