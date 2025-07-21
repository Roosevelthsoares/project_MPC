import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight

from .utils import reduce_mem_usage

class DataProcessor:
    """Handles data loading and preprocessing."""
    def __init__(self, data_path, test_data_path=None):
        self.data_path = data_path
        self.test_data_path = test_data_path
        self.df = None
        self.test_df = None
        self.X = None
        self.y = None
        self.X_test_external = None
        self.y_test_external = None
        self.unique_labels = None
        self.label_dict = None
        self.num_classes = None

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

        # Load external test data if provided
        if self.test_data_path:
            test_df = pd.read_parquet(self.test_data_path)
            test_df = preprocess(test_df)
            self.test_df = test_df

        # Print label distribution
        print(df['Label'].value_counts())
        self.unique_labels = df['Label'].unique()
        print(f'Unique labels in dataset: {self.unique_labels}')

        # Separate Features (X)
        self.X = df.drop(columns=['Label'])
        self.y = df['Label']

        # If external test set exists, store it separately
        if self.test_df is not None:
            self.X_test_external = self.test_df.drop(columns=['Label'])
            self.y_test_external = self.test_df['Label']

    def encode_labels(self):
        labels = self.y.unique()
        label_dict = {label: i for i, label in enumerate(labels)}
        self.label_dict = label_dict
        print(self.label_dict)

        self.y = self.y.map(label_dict).astype(np.uint8)
        print(self.y.value_counts())
        self.num_classes = len(labels)

        if self.y_test_external is not None:
            self.y_test_external = self.y_test_external.map(label_dict).astype(np.uint8)

        print(f'Unique labels after encoding: {np.unique(self.y)}')
        print(f"'y' dtype: {self.y.dtype}")

    def split_data(self, test_size=0.2, random_state=42):
        scaler = StandardScaler()

        if self.X_test_external is not None and self.y_test_external is not None:
            # Use provided external test set
            X_train = scaler.fit_transform(self.X)
            X_test = scaler.transform(self.X_test_external)

            y_train = self.y.to_numpy()
            y_test = self.y_test_external.to_numpy()

        else:
            # Random split
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, self.y, test_size=test_size, random_state=random_state, stratify=self.y
            )

            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            y_train = y_train.to_numpy()
            y_test = y_test.to_numpy()

        print(f'Unique labels in y_train: {np.unique(y_train)}')

        return X_train, X_test, y_train, y_test

    def compute_class_weights(self, y_train):
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weight_dict = dict(zip(np.unique(y_train), class_weights))
        print(f'Initial class weights: {class_weight_dict}')
        return class_weight_dict
