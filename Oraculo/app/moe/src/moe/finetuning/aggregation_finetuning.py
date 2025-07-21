import tensorflow as tf

class AggregationFineTuner:
    def __init__(self, gate_model, expert_models, num_classes):
        self.gate_model = gate_model
        self.expert_models = expert_models
        self.num_classes = num_classes
        self._build_aggregation_model()

    def _build_aggregation_model(self):
        # Create inputs matching gate model's input shape
        input_layer = tf.keras.Input(shape=self.gate_model.input_shape[1:])
        
        # Get gate probabilities
        gate_probs = self.gate_model(input_layer)
        
        # Get expert outputs (placeholder implementation)
        expert_outputs = [
            (i, expert(input_layer)) 
            for i, expert in enumerate(self.expert_models.values())
        ]
        
        # Add aggregation layer
        self.aggregation_layer = AggregationLayer(self.num_classes)
        final_output = self.aggregation_layer(expert_outputs)
        
        # Create trainable model
        self.model = tf.keras.Model(
            inputs=input_layer,
            outputs=final_output
        )
        
        # Freeze base models
        self.gate_model.trainable = False
        for expert in self.expert_models.values():
            expert.trainable = False

    def compile(self, optimizer, loss):
        self.model.compile(optimizer=optimizer, loss=loss)

    def fit(self, X_train, y_train, **kwargs):
        return self.model.fit(X_train, y_train, **kwargs)