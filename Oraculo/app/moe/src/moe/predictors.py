import numpy as np
from tqdm import tqdm
import tensorflow as tf
from typing import List, Dict
from .gating_strategies import GatingStrategy
import numpy as np
from tqdm import tqdm
import tensorflow as tf

class MoEPredictor:
    def __init__(self, calibrator, expert_models: Dict[str, object], classes: List[str]):
        self.calibrator = calibrator
        self.expert_models = expert_models
        self.classes = classes

        # Suppress TensorFlow verbose output
        tf.get_logger().setLevel('ERROR')
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

    def predict(self, X_input: np.ndarray, strategy: str = 'soft', threshold: float = 0.1, batch_size: int = 32, **kwargs) -> List[str]:
        """
        Predict using batch processing for efficiency.
        
        Args:
            batch_size: Number of samples to process at once.
        """
        gate_probs = self.calibrator.predict_proba(X_input)
        predictions = []
        
        # Process in batches
        for i in tqdm(range(0, len(X_input), batch_size), desc="MoE Prediction", leave=True):
            batch_X = X_input[i:i+batch_size]
            batch_probs = gate_probs[i:i+batch_size]
            
            # Batch predictions for all experts
            if strategy == 'hard':
                expert_names = [
                    GatingStrategy.hard(prob, self.classes) for prob in batch_probs
                ]
                batch_preds = [
                    self._hard_predict(x, expert_name)
                    for x, expert_name in zip(batch_X, expert_names)
                ]
            elif strategy == 'soft':
                batch_preds = self._batch_soft_predict(batch_X, batch_probs, threshold)
            elif strategy == 'top_k':
                batch_preds = self._batch_top_k_predict(batch_X, batch_probs, kwargs.get('k', 2))
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
            
            predictions.extend(batch_preds)
        
        return predictions

    def _batch_soft_predict(self, X: np.ndarray, gate_probs: np.ndarray, threshold: float) -> List[str]:
        """
        Perform batch predictions using the soft strategy.
        """
        expert_inputs = {cls_name: [] for cls_name in self.classes}
        input_indices = {cls_name: [] for cls_name in self.classes}
        
        # Collect inputs for each expert
        for idx, (x, probs) in enumerate(zip(X, gate_probs)):
            experts = GatingStrategy.soft(probs, self.classes, threshold)
            for cls_name, _ in experts:
                expert_inputs[cls_name].append(x)
                input_indices[cls_name].append(idx)
        
        # Perform batch predictions for each expert
        aggregated_scores = [{} for _ in range(len(X))]
        for cls_name, inputs in expert_inputs.items():
            if inputs:
                preds = self.expert_models[cls_name].predict(np.array(inputs), verbose=0)
                for i, pred in zip(input_indices[cls_name], preds):
                    aggregated_scores[i][cls_name] = pred[0]
        
        # Normalize scores and select the class with the highest score
        predictions = []
        for idx, scores in enumerate(aggregated_scores):
            total_weight = sum(scores.values())
            if total_weight > 0:
                scores = {cls: val / total_weight for cls, val in scores.items()}
            try:
                # Use the current instance's gate_probs to pick a fallback class
                predictions.append(max(scores, key=scores.get) if scores else self.classes[np.argmax(gate_probs[idx])])
            except IndexError:
                # Handle edge cases with fallback
                print(f"Warning: Index {idx} is out of bounds for gate_probs or classes. Using default fallback.")
                predictions.append(self.classes[0])  # Default to the first class or a defined fallback
        return predictions


    def _hard_predict(self, x: np.ndarray, expert_name: str) -> str:
        expert_pred = self.expert_models[expert_name].predict(x.reshape(1, -1), verbose=0)[0][0]
        return expert_name if expert_pred >= 0.5 else 'Unknown'
    
    def _batch_top_k_predict(self, X: np.ndarray, gate_probs: np.ndarray, k: int) -> List[str]:
        """
        Perform batch predictions using the top-k strategy.
        """
        expert_inputs = {cls_name: [] for cls_name in self.classes}
        input_indices = {cls_name: [] for cls_name in self.classes}
        
        # Collect inputs for top-k experts
        for idx, (x, probs) in enumerate(zip(X, gate_probs)):
            experts = GatingStrategy.top_k(probs, self.classes, k)
            for cls_name, _ in experts:
                expert_inputs[cls_name].append(x)
                input_indices[cls_name].append(idx)
        
        # Perform batch predictions for each expert
        aggregated_scores = [{} for _ in range(len(X))]
        for cls_name, inputs in expert_inputs.items():
            if inputs:
                preds = self.expert_models[cls_name].predict(np.array(inputs), verbose=0)
                for i, pred in zip(input_indices[cls_name], preds):
                    aggregated_scores[i][cls_name] = pred[0]
        
        # Select the class with the highest score
        predictions = []
        for scores in aggregated_scores:
            predictions.append(max(scores, key=scores.get) if scores else 'Unknown')
        return predictions

