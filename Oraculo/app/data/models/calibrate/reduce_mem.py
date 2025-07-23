import pandas as pd
from sklearn.model_selection import train_test_split
import gc

# Load full DataFrame (optimize types or use columns=... if needed)
df = pd.read_parquet('CICIDS2018_preprocessed_test.parquet', engine='pyarrow')

# Assume the target column is named 'label' (replace if needed)
y = df['Label']
X = df.drop(columns=['Label'])

# Stratified sampling (preserves class balance)
_, X_reduced, _, y_reduced = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# Recombine X and y for saving
df_reduced = X_reduced.copy()
df_reduced['Label'] = y_reduced

# Free memory
del df, X, y, X_reduced, y_reduced
gc.collect()

# Save reduced dataset
df_reduced.to_parquet("CICIDS2018_preprocessed_test_reduced.parquet", index=False)
