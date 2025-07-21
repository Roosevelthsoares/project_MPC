from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
import numpy as np

class MoEEvaluator:
    def __init__(self, true_labels, classes):
        self.true_labels = true_labels
        self.classes = classes

    def evaluate(self, predictions, average: str = 'weighted') -> dict:
        return {
            'f1': f1_score(self.true_labels, predictions, average=average, zero_division=0),
            'precision': precision_score(self.true_labels, predictions, average=average, zero_division=0),
            'recall': recall_score(self.true_labels, predictions, average=average, zero_division=0),
            'accuracy': accuracy_score(self.true_labels, predictions)
        }

    def evaluate_per_class(self, predictions, average: str = 'None'):
        # Calculate F1 score, precision, recall, and accuracy per class
        f1_scores = f1_score(self.true_labels, predictions, average=average, zero_division=0)
        precision_scores = precision_score(self.true_labels, predictions, average=average, zero_division=0)
        recall_scores = recall_score(self.true_labels, predictions, average=average, zero_division=0)
        
        # Calculate accuracy and support per class
        accuracy_per_class = []
        support_per_class = []
        for cls in [i for i in range(len(self.classes))]:
            cls_mask = (self.true_labels == cls)
            support = np.sum(cls_mask)  # Number of samples for this class
            support_per_class.append(support)
            
            if support == 0:  # No samples for this class in true labels
                accuracy_per_class.append(np.nan)  # Set accuracy to NaN for missing classes
            else:
                # Calculate accuracy only for the samples of the current class
                correct_predictions = np.sum(predictions[cls_mask] == self.true_labels[cls_mask])
                cls_accuracy = correct_predictions / support
                accuracy_per_class.append(cls_accuracy)
        
        # Determine the maximum class name length for formatting
        max_class_name_length = max(len(str(cls)) for cls in self.classes)
        class_column_width = max(max_class_name_length, len("Class"))  # Ensure column is wide enough for the header
        
        # Print the results in a readable format
        print("{:<{}} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
            'Class', class_column_width, 'F1 Score', 'Precision', 'Recall', 'Accuracy', 'Support'
        ))
        for i, cls in enumerate(self.classes):
            print("{:<{}} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10}".format(
                str(cls), class_column_width, f1_scores[i], precision_scores[i], recall_scores[i], 
                accuracy_per_class[i], support_per_class[i]
            ))

    def compare_strategies(self, predictions_dict: dict, average: str = 'weighted', per_class: bool = False) -> dict:
        results = {}
        for name, preds in predictions_dict.items():
            if per_class:
                print(f"Metrics for strategy: {name}")
                self.evaluate_per_class(preds, average=average)
                print("\n")  # Add a newline for separation
            else:
                metrics = self.evaluate(preds, average=average)
                results[name] = metrics
                print(f"Metrics for strategy: {name}")
                print(f"  F1 Score: {metrics['f1']:.4f}")
                print(f"  Precision: {metrics['precision']:.4f}")
                print(f"  Recall: {metrics['recall']:.4f}")
                print(f"  Accuracy: {metrics['accuracy']:.4f}")
                print("\n")  # Add a newline for separation
        return results

# Example usage:
# Assuming true_labels and predictions are numpy arrays, and classes is a list of class labels
# true_labels = np.array([0, 1, 2, 0, 1, 2])
# classes = ["class_0", "class_1", "class_2"]
# results = {
#     'strategy_1': np.array([0, 1, 2, 0, 1, 2]),
#     'strategy_2': np.array([0, 0, 2, 0, 1, 2])
# }
# evaluator = MoEEvaluator(true_labels, classes)
# print("\nStrategy Comparison:")
# comparison = evaluator.compare_strategies(results, average='macro', per_class=True)