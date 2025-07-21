import numpy as np
from typing import List, Tuple

class GatingStrategy:
    @staticmethod
    def hard(gate_probs: np.ndarray, classes: List[str]) -> str:
        """Hard gating - select expert with highest probability"""
        max_idx = np.argmax(gate_probs)
        return classes[max_idx]

    @staticmethod
    def soft(gate_probs: np.ndarray, classes: List[str], threshold: float) -> List[Tuple[str, float]]:
        """Soft gating with adjustable threshold"""
        return [(cls, prob) for cls, prob in zip(classes, gate_probs) if prob >= threshold]

    @staticmethod
    def top_k(gate_probs: np.ndarray, classes: List[str], k: int) -> List[Tuple[str, float]]:
        """Top-K expert selection"""
        top_k_indices = np.argsort(gate_probs)[-k:]
        return [(classes[idx], gate_probs[idx]) for idx in top_k_indices if gate_probs[idx] > 0]