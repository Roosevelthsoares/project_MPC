from tensorflow.keras.callbacks import EarlyStopping

class MoETrainer:
    def __init__(self, gate_model, expert_models, num_classes):
        self.gate_model = gate_model
        self.expert_models = expert_models
        self.num_classes = num_classes
        self.finetuner = MoEFineTuner(gate_model, expert_models, num_classes)

    def full_finetuning_pipeline(self, X_train, y_train, X_val, y_val):
        """
        Complete fine-tuning workflow:
        1. Fine-tune gate last layers
        2. Fine-tune aggregation weights
        """
        # Phase 1: Gate model fine-tuning
        print("Phase 1: Fine-tuning gate model last layers")
        hist1 = self.finetuner.fine_tune_gate_last_layers(
            X_train, y_train,
            epochs=10,
            learning_rate=1e-5
        )
        
        # Phase 2: Aggregation fine-tuning
        print("\nPhase 2: Fine-tuning aggregation weights")
        hist2 = self.finetuner.fine_tune_aggregation(
            X_train, y_train,
            epochs=20,
            batch_size=128,
            validation_data=(X_val, y_val),
            callbacks=[EarlyStopping(patience=3)]
        )
        
        return hist1, hist2