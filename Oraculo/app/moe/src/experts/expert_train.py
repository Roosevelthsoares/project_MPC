import gc
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    fbeta_score,
    precision_score,
    recall_score,
)

from src.models import ModelBuilderExpert
from src.utils import f2_score
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import pandas as pd

class ExpertModelTrainer:
    """Handles model compilation, training, evaluation, and saving."""
    def __init__(self, model):
        self.model = model

    def compile_model(self, strategy, learning_rate=5e-3):
        with strategy.scope():
            optimizer = Adam(learning_rate=learning_rate)
            self.model.compile(
                optimizer=optimizer,
                loss='binary_crossentropy',
                metrics=[f2_score],
            )

    def train_model_per_epoch(self, X_train, y_train, X_val, y_val, class_weight_dict, epochs=10, batch_size=8704):
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=3,
            min_delta=0.01,
            restore_best_weights=True,
        )
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_delta=0.05,
            min_lr=1e-6,
            verbose=1,
        )
        history_per_epoch = {'epoch': [], 'loss': [], 'val_loss': [], 'f2_score': [], 'val_f2_score': []}
        for epoch in range(epochs):
            print(f"\nEpoch {epoch+1}/{epochs}")
            if epoch == 0:
                class_weight_epoch = class_weight_dict
            else:
                y_train_pred_probs = self.model.predict(X_train, batch_size=batch_size)
                y_train_pred = (y_train_pred_probs >= 0.5).astype(np.uint8).flatten()
                f2_scores_train = fbeta_score(y_train, y_train_pred, beta=2, average=None, labels=[0,1])
                epsilon = 1e-3
                class_weight_epoch = {}
                for cls_idx, cls in enumerate([0, 1]):
                    f2_cls = f2_scores_train[cls_idx]
                    class_weight_epoch[cls] = 1.0 / (f2_cls + epsilon)
                total_weight = sum(class_weight_epoch.values())
                class_weight_epoch = {k: v / total_weight * len(class_weight_epoch) for k, v in class_weight_epoch.items()}
                print(f"Updated class weights: {class_weight_epoch}")
            history = self.model.fit(
                X_train,
                y_train,
                validation_data=(X_val, y_val),
                epochs=1,
                batch_size=batch_size,
                verbose=1,
                class_weight=class_weight_epoch,
                callbacks=[early_stopping, reduce_lr] if epoch == 0 else [],
            )
            history_per_epoch['epoch'].append(epoch + 1)
            history_per_epoch['loss'].append(history.history['loss'][0])
            history_per_epoch['val_loss'].append(history.history['val_loss'][0])
            history_per_epoch['f2_score'].append(history.history['f2_score'][0])
            history_per_epoch['val_f2_score'].append(history.history['val_f2_score'][0])
            if early_stopping.stopped_epoch > 0:
                print("Early stopping triggered.")
                break
        self.history_per_epoch = history_per_epoch

    def evaluate_model(self, X_test, y_test, batch_size=8704):
        y_pred_probs = self.model.predict(X_test, batch_size=batch_size)
        y_pred = (y_pred_probs >= 0.5).astype(np.uint8).flatten()
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f2 = fbeta_score(y_test, y_pred, beta=2, zero_division=0)
        print(f'Accuracy:  {accuracy * 100:.2f}%')
        print(f'Precision: {precision * 100:.2f}%')
        print(f'Recall:    {recall * 100:.2f}%')
        print(f'F2 Score:  {f2 * 100:.2f}%\n')
        print('Classification Report:')
        report = classification_report(y_test, y_pred, zero_division=0)
        print(report)
        self.report = report

    def save_history(self, binarize_on_label, model_name):
        history_df = pd.DataFrame(self.history_per_epoch)
        history_filename = f'history_{model_name}_{binarize_on_label}.csv'
        history_df.to_csv(history_filename, index=False)
        print(f"Training history saved to {history_filename}")

    def save_classification_report(self, binarize_on_label, model_name):
        report_filename = f'classification_report_{model_name}_{binarize_on_label}.txt'
        with open(report_filename, 'w') as f:
            f.write(self.report)
        print(f"Classification report saved to {report_filename}")

    def save_model(self, binarize_on_label, model_name):
        model_filename = f'model_{model_name}_{binarize_on_label}.h5'
        self.model.save(model_filename)
        print(f'Model saved as {model_filename}')

    def clean_up(self):
        del self.model
        gc.collect()


# # Usage Example
# data_path = '/path/to/data'

# # Initialize ExpertDataProcessor
# processor = ExpertDataProcessor(data_path)
# processor.load_and_preprocess_data()

# # Create a MirroredStrategy for using multiple GPUs
# strategy = tf.distribute.MirroredStrategy()

# # For each label and each model
# for label in processor.unique_labels:
#     print(f'\nProcessing label: {label}')
#     processor.binarize_labels(label)
#     X_train, X_test, y_train, y_test = processor.split_data()
#     class_weight_dict = processor.compute_class_weights(y_train)

#     # Build and train models
#     model_builder = ModelBuilderExpert(input_shape=X_train.shape[1], strategy=strategy)
#     model_build_methods = {
#             'mlp_residual': model_builder.build_mlp_residual_model,
#             'cnn': model_builder.build_cnn_model,
#             'lstm': model_builder.build_lstm_model,
#             'attention': model_builder.build_attention_model,
#         }
#     for model_name, build_method in model_build_methods.items():
#         print(f'\nTraining {model_name} model for label: {label}')
#         if model_name == 'attention':
#             model = build_method(num_heads=2)  # You can adjust num_heads as needed
#         else:
#             model = build_method()
#         trainer = ExpertModelTrainer(model=model)
#         trainer.compile_model(strategy)
#         trainer.train_model_per_epoch(
#             X_train, y_train, X_test, y_test, class_weight_dict, 
#             epochs=10, batch_size=8704
#         )
#         trainer.evaluate_model(X_test, y_test)
#         trainer.save_history(label, model_name)
#         trainer.save_classification_report(label, model_name)
#         trainer.save_model(label, model_name)
#         trainer.clean_up()

#     # Clean up data to free memory
#     del X_train, X_test, y_train, y_test
#     gc.collect()
