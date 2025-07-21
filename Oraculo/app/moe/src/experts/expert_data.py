import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight

from src.utils import reduce_mem_usage

class ExpertDataProcessor:
    """Handles data loading and preprocessing for expert models."""
    def __init__(self, data_path, test_data_path=None):
        self.data_path = data_path
        self.test_data_path = test_data_path
        self.df = None
        self.test_df = None
        self.X_scaled = None
        self.y = None
        self.X_test_scaled = None
        self.y_test = None
        self.unique_labels = None

    def load_and_preprocess_data(self):
        def preprocess(df):
            if 'label' in df.columns:
                df = df.rename(columns={'label': 'Label'})
            if 'Timestamp' in df.columns:
                df = df.drop(columns=['Timestamp'])
            df = reduce_mem_usage(df)
            if 'Label' in df['Label'].unique():
                df = df[df['Label'] != 'Label']
            return df

        # Load training data
        df = pd.read_parquet(self.data_path)
        df = preprocess(df)
        self.df = df
        self.unique_labels = df['Label'].unique()
        print(f'Unique labels in dataset: {self.unique_labels}')
        print(df['Label'].value_counts())

        scaler = StandardScaler()
        X = df.drop(columns=['Label'])

        # Load and preprocess test data if available
        if self.test_data_path:
            test_df = pd.read_parquet(self.test_data_path)
            test_df = preprocess(test_df)
            self.test_df = test_df

            X_test = test_df.drop(columns=['Label'])

            # Fit scaler on training data only, apply to both
            self.X_scaled = scaler.fit_transform(X)
            self.X_test_scaled = scaler.transform(X_test)
        else:
            self.X_scaled = scaler.fit_transform(X)

    def binarize_labels(self, binarize_on_label):
        self.y = (self.df['Label'] == binarize_on_label).astype(np.uint8)
        print(self.y.value_counts())
        print(f'Unique labels after binarization: {self.y.unique()}')
        print(f"'y' dtype: {self.y.dtype}")

        if self.test_df is not None:
            self.y_test = (self.test_df['Label'] == binarize_on_label).astype(np.uint8)

    def split_data(self, test_size=0.2, random_state=42):
        if self.X_test_scaled is not None and self.y_test is not None:
            # Use external test set
            X_train = self.X_scaled
            y_train = self.y.values.reshape(-1, 1)
            X_test = self.X_test_scaled
            y_test = self.y_test.values.reshape(-1, 1)
        else:
            # Do train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                self.X_scaled, self.y, test_size=test_size,
                random_state=random_state, stratify=self.y
            )
            y_train = y_train.values.reshape(-1, 1)
            y_test = y_test.values.reshape(-1, 1)

        print(f'Unique labels in y_train: {np.unique(y_train)}')
        return X_train, X_test, y_train, y_test

    def compute_class_weights(self, y_train):
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y_train),
            y=y_train.ravel()
        )
        class_weight_dict = dict(zip(np.unique(y_train), class_weights))
        print(f'Initial class weights: {class_weight_dict}')
        return class_weight_dict
