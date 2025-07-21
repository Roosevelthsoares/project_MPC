import re
import os
import shutil

def parse_macro_f1_score(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if "macro avg" in line:
                parts = line.split()
                try:
                    f1_score = float(parts[4])
                    return f1_score
                except (IndexError, ValueError):
                    return None
    return None

def select_best_expert_models(directory_path):
    file_pattern = re.compile(r'classification_report_([a-zA-Z0-9]+)_([a-zA-Z0-9\s\-]+)\.txt')
    model_performance = {}

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".txt"):
            match = file_pattern.match(file_name)
            if match:
                model = match.group(1)
                label = match.group(2)
                file_path = os.path.join(directory_path, file_name)
                f1_score = parse_macro_f1_score(file_path)
                if f1_score is not None:
                    if label not in model_performance or model_performance[label][1] < f1_score:
                        model_performance[label] = (model, f1_score)

    best_models = []
    for label, (best_model, best_f1_score) in model_performance.items():
        print(f"Label: {label}, Best Model: {best_model}, Macro F1 Score: {best_f1_score}")
        best_models.append(f"model_{best_model}_{label}.h5")
    return model_performance, best_models

def copy_best_models(model_filenames, source_dir, dest_dir="best_models"):
    """
    Copies best model files to a separate directory.

    Args:
        model_filenames (list): List of model filenames to copy.
        source_dir (str): Directory where the model files are located.
        dest_dir (str): Directory where the best models will be copied. Defaults to 'best_models'.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for filename in model_filenames:
        src = os.path.join(source_dir, filename)
        dest = os.path.join(dest_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, dest)
            print(f"Copied {filename} to {dest_dir}")
        else:
            print(f"Warning: {filename} not found in {source_dir}")





