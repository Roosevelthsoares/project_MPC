from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Optimizer

class LayerFineTuner:
    def __init__(self, model: Model, trainable_layers: list):
        self.model = model
        self.trainable_layers = trainable_layers
        self._freeze_non_trainable()

    def _freeze_non_trainable(self):
        for layer in self.model.layers:
            layer.trainable = layer.name in self.trainable_layers

    def compile_for_finetuning(self, 
                             optimizer: Optimizer, 
                             loss: str, 
                             learning_rate: float = 1e-5):
        """Recompile model with frozen layers"""
        optimizer = optimizer(learning_rate=learning_rate)
        self.model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=['accuracy']
        )

    def fine_tune(self, X_train, y_train, 
                epochs: int = 10, 
                batch_size: int = 32,
                validation_data: tuple = None,
                callbacks: list = None):
        return self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            callbacks=callbacks
        )