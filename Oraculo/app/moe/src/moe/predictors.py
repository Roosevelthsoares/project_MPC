import numpy as np
from tqdm import tqdm
import tensorflow as tf
from typing import List, Dict, Tuple
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

    def _batch_soft_predict(self, X: np.ndarray, gate_probs: np.ndarray, threshold: float) -> List[Tuple[str, float]]:
        """
        Perform batch predictions using the soft strategy.
        Returns a list of (predicted_label, confidence) tuples.
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
                    aggregated_scores[i][cls_name] = pred[0]  # raw score
        
        # Normalize scores and pick class with highest score + confidence
        predictions = []
        for idx, scores in enumerate(aggregated_scores):
            # total_weight = sum(scores.values())
            # if total_weight > 0:
            #     scores = {cls: val / total_weight for cls, val in scores.items()}
            scores = self._normalize_scores(scores)
            if scores:
                best_class = max(scores, key=scores.get)
                confidence = scores[best_class]
                predictions.append((best_class, confidence))
            else:
                fallback_class = self.classes[np.argmax(gate_probs[idx])]
                predictions.append((fallback_class, 0.0))
        return predictions


    def _hard_predict(self, x: np.ndarray, expert_name: str, threshold: float = 0.5) -> Tuple[str, float]:
        """
        Predict with a single (hard-gated) expert.
        Returns (predicted_label, confidence).
        Assumes the expert outputs a probability for `expert_name` (sigmoid).
        """
        p = float(self.expert_models[expert_name].predict(x.reshape(1, -1), verbose=0)[0][0])
        if p >= threshold:
            # Positive class: confidence is the expert's probability
            return [expert_name, p]
        else:
            # Negative class ("Unknown"): confidence is 1 - p (model's confidence it's NOT the expert)
            return ['Unknown', 1.0 - p]
    
    def _batch_top_k_predict(self, X: np.ndarray, gate_probs: np.ndarray, k: int) -> List[Tuple[str, float]]:
        """
        Perform batch predictions using the top-k strategy.
        Returns a list of (predicted_label, confidence), where confidence
        is the normalized score among the experts queried for that sample.
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
                    aggregated_scores[i][cls_name] = float(pred[0])  # raw score from this expert
        
        # Pick best class and include confidence
        predictions: List[Tuple[str, float]] = []
        for scores in aggregated_scores:
            # scores = self._normalize_scores(scores)
            if scores:
                total = sum(scores.values())
                norm = {c: (v / total) for c, v in scores.items()} if total > 0 else scores
                best = max(norm, key=norm.get)
                predictions.append((best, float(norm[best])))
            else:
                predictions.append(('Unknown', 0.0))
        return predictions

    def _normalize_scores(self, scores: dict) -> dict:
        total = sum(scores.values())
        if total > 0:
            return {cls: val / total for cls, val in scores.items()}
        return scores
