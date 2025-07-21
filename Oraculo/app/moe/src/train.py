import gc
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    fbeta_score,
    precision_score,
    recall_score,
)

from src.models import ModelBuilderGate
from src.utils import multi_f2_score
from src.data_preprocessing import DataProcessor
import tensorflow.keras.backend as K

class ModelTrainer:
    """Handles model compilation, training, evaluation, and saving."""
    def __init__(self, model, num_classes):
        self.model = model
        self.num_classes = num_classes

    def compile_model(self, strategy, learning_rate=1e-3, clipvalue=1.0):
        with strategy.scope():
            optimizer = Adam(learning_rate=learning_rate, clipvalue=clipvalue, use_ema=True, weight_decay=1e-5)
            self.model.compile(
                optimizer=optimizer,
                loss='sparse_categorical_crossentropy',
                metrics=[multi_f2_score],
            )

    def train_model_per_epoch(self, X_train, y_train, X_val, y_val, class_weight_dict, epochs=10, batch_size=8704):
        history_per_epoch = {'epoch': [], 'loss': [], 'val_loss': [], 'multi_f2_score': [], 'val_multi_f2_score': []}
        
        # Initialize variables for custom early stopping and learning rate scheduling
        best_val_loss_es = np.inf
        wait_es = 0
        best_weights = None
        
        best_val_loss_lr = np.inf
        wait_lr = 0
        current_lr = self.model.optimizer.learning_rate.numpy().item()
        patience_es = 10
        patience_lr = 5
        min_delta_es = 0.001
        min_delta_lr = 0.001
        factor = 0.5
        min_lr = 1e-6
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch+1}/{epochs}")
            if epoch == 0:
                class_weight_epoch = class_weight_dict
            else:
                y_train_pred_probs = self.model.predict(X_train, batch_size=batch_size)
                if self.num_classes == 2:
                    y_train_pred = (y_train_pred_probs >= 0.5).astype(np.uint8).flatten()
                else:
                    y_train_pred = np.argmax(y_train_pred_probs, axis=-1)
                f2_scores_train = fbeta_score(y_train, y_train_pred, beta=2, average=None)
                
###################### Class Weights calculation from "Class-Balanced Loss Based on Effective Number of Samples" (CVPR 2019) ############################
                epsilon = 1e-3
                class_weight_epoch = {}
                beta = 0.99  # Smoothing factor (from paper, typically in [0.9, 0.999])
                for cls_idx in range(self.num_classes):
                    f2_cls = f2_scores_train[cls_idx]
                    
                    # Convert F2 score to "effective error rate" (lower F2 → harder class)
                    error_rate = 1.0 - f2_cls  # F2=1 → perfect, F2=0 → all wrong
                    
                    # Map error rate to pseudo "effective sample size" 
                    # (classes with higher error are treated as "rare")
                    pseudo_n_cls = 1.0 / (error_rate + epsilon)  # Inverse of error
                    
                    # Apply CVPR 2019 formula to smooth weights
                    effective_num = (1.0 - beta ** pseudo_n_cls) / (1.0 - beta)
                    class_weight_epoch[cls_idx] = 1.0 / (effective_num + epsilon)
                
                # Normalize to mean=1.0
                total_weight = sum(class_weight_epoch.values())
                class_weight_epoch = {k: v / total_weight * self.num_classes for k, v in class_weight_epoch.items()}
                print(f"Updated class weights: {class_weight_epoch}")
            
            history = self.model.fit(
                X_train,
                y_train,
                validation_data=(X_val, y_val),
                epochs=1,
                batch_size=batch_size,
                verbose=1,
                class_weight=class_weight_epoch,
                callbacks=[],  # Removed Keras callbacks
            )
            
            # Update history
            history_per_epoch['epoch'].append(epoch + 1)
            history_per_epoch['loss'].append(history.history['loss'][0])
            history_per_epoch['val_loss'].append(history.history['val_loss'][0])
            history_per_epoch['multi_f2_score'].append(history.history['multi_f2_score'][0])
            history_per_epoch['val_multi_f2_score'].append(history.history['val_multi_f2_score'][0])
            
            val_loss = history.history['val_loss'][0]
            
            # Check early stopping conditions
            if (best_val_loss_es - val_loss) > min_delta_es:
                best_val_loss_es = val_loss
                wait_es = 0
                best_weights = self.model.get_weights()
                print(f"New best validation loss: {val_loss:.4f}")
            else:
                wait_es += 1
                print(f"No improvement in validation loss for {wait_es} epochs (Early Stopping). Best: {best_val_loss_es:.4f}, Current: {val_loss:.4f}")
            
            if wait_es >= patience_es:
                print(f"\nEarly stopping triggered after {epoch+1} epochs. Restoring best weights.")
                if best_weights is not None:
                    self.model.set_weights(best_weights)
                break
            
            # Check learning rate reduction conditions
            if (best_val_loss_lr - val_loss) > min_delta_lr:
                best_val_loss_lr = val_loss
                wait_lr = 0
                print(f"New best validation loss for LR: {val_loss:.4f}")
            else:
                wait_lr += 1
                print(f"No improvement in validation loss for {wait_lr} epochs (LR Reduction). Best LR: {best_val_loss_lr:.4f}, Current: {val_loss:.4f}")
            
            if wait_lr >= patience_lr:
                new_lr = current_lr * factor
                new_lr = max(new_lr, min_lr)
                if new_lr < current_lr:
                    current_lr = new_lr
                    # Corrected line: Use assign method to update learning rate
                    self.model.optimizer.learning_rate.assign(current_lr)
                    print(f"\nReducing learning rate to {current_lr}")
                    best_val_loss_lr = np.inf  # Reset to track new best after reduction
                    wait_lr = 0
                else:
                    print("\nLearning rate already at minimum. Skipping reduction.")

        self.history_per_epoch = history_per_epoch


    def evaluate_model(self, X_test, y_test, batch_size=24576):
        y_pred_probs = self.model.predict(X_test, batch_size=batch_size)
        y_pred = np.argmax(y_pred_probs, axis=-1)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0, average='macro')
        recall = recall_score(y_test, y_pred, zero_division=0, average='macro')
        f2 = fbeta_score(y_test, y_pred, beta=2, zero_division=0, average='macro')
        print(f'Accuracy:  {accuracy * 100:.2f}%')
        print(f'Precision: {precision * 100:.2f}%')
        print(f'Recall:    {recall * 100:.2f}%')
        print(f'F2 Score:  {f2 * 100:.2f}%\n')
        print('Classification Report:')
        report = classification_report(y_test, y_pred, zero_division=0)
        print(report)
        self.report = report

    def save_history(self, model_name):
        history_df = pd.DataFrame(self.history_per_epoch)
        history_filename = f'history_{model_name}.csv'
        history_df.to_csv(history_filename, index=False)
        print(f"Training history saved to {history_filename}")

    def save_classification_report(self, model_name):
        report_filename = f'classification_report_{model_name}.txt'
        with open(report_filename, 'w') as f:
            f.write(self.report)
        print(f"Classification report saved to {report_filename}")

    def save_model(self, model_name):
        model_filename = f'model_{model_name}.h5'
        self.model.save(model_filename)
        print(f'Model saved as {model_filename}')

    def clean_up(self):
        del self.model
        gc.collect()

# # Usage Example
# data_path = '/path/to/data'

# # Initialize DataProcessor
# processor = DataProcessor(data_path)
# processor.load_and_preprocess_data()
# processor.encode_labels()
# X_train, X_test, y_train, y_test = processor.split_data()
# class_weight_dict = processor.compute_class_weights(y_train)

# # Create a MirroredStrategy for using multiple GPUs
# strategy = tf.distribute.MirroredStrategy()

# # Build and train models
# model_builder = ModelBuilderGate(
#     input_shape=X_train.shape[1],
#     num_classes=processor.num_classes,
#     strategy=strategy
# )

# model_build_methods = {
#     'mlp_residual': model_builder.build_mlp_residual_model,
#     'cnn': model_builder.build_cnn_model,
#     'lstm': model_builder.build_lstm_model,
#     'attention': model_builder.build_attention_model,
# }

# for model_name, build_method in model_build_methods.items():
#     print(f'\nTraining {model_name} model')
#     if model_name == 'attention':
#         model = build_method(num_heads=4)  # Adjust num_heads as needed
#     else:
#         model = build_method()
#     trainer = ModelTrainer(model=model)
#     trainer.compile_model(strategy, learning_rate=1e-3)
#     trainer.train_model_per_epoch(
#         X_train, y_train, X_test, y_test, class_weight_dict, 
#         epochs=100, batch_size=24576
#         )
#     trainer.evaluate_model(X_test, y_test)
#     trainer.save_history(model_name)
#     trainer.save_classification_report(model_name)
#     trainer.save_model(model_name)
#     trainer.clean_up()

# # Clean up data to free memory
# del X_train, X_test, y_train, y_test
# gc.collect()
