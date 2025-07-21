# Mixture of Experts for Intrusion Detection System

This repository implements an advanced **Mixture of Experts (MoE)** framework for intrusion detection, featuring multiple gating strategies, calibration methods, and fine-tuning capabilities. The system combines a calibrated gate model with specialized experts using flexible aggregation mechanisms.

---

## Updated Repository Structure

```
my_project/
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── setup.py                   # Package installation
├── src/                       # Core implementation
│   ├── __init__.py            
│   ├── data_preprocessing.py     # Data preprocessing utilities
│   ├── models.py              # Model architectures
│   ├── train.py               # Gate model training
│   ├── expert_models/         # Expert model implementation
│   │   ├── expert_data.py     
│   │   ├── expert_train.py    
│   ├── moe/                   # Enhanced MoE components
│   │   ├── __init__.py
│   │   ├── calibration.py     # Gate calibration strategies
│   │   ├── gating_strategies.py # Hard/Soft/Top-K gating
│   │   ├── predictors.py      # Unified prediction interface
│   │   ├── losses.py          # Custom loss functions (Focal Loss)
│   │   ├── evaluation.py      # Performance evaluation
│   │   ├── finetuning/        # Fine-tuning subsystems
│   │   │   ├── __init__.py
│   │   │   ├── layer_finetuning.py
│   │   │   └── aggregation_finetuning.py
│   │   └── trainers.py        # Training workflows
└── .gitignore
```

---

## Key Features

1. **Multiple Gating Strategies**
   - Hard/Soft/Top-K expert selection
   - Adjustable probability thresholds
   - Fallback mechanisms for edge cases

2. **Advanced Calibration**
   - Isotonic regression calibration
   - Platt scaling implementation
   - Custom calibration workflows

3. **Enhanced Fine-Tuning**
   - Layer-specific fine-tuning
   - Trainable aggregation weights
   - Focal loss implementation

4. **Comprehensive Evaluation**
   - Strategy comparison framework
   - Per-class metrics analysis
   - Threshold optimization tools

---

## Setup and Installation

```bash
git clone https://github.com/matglima/MoE_4_CyberSec.git
cd MoE_4_CyberSec
pip install -r requirements.txt
```

---

## Usage Guide

### 1. MoE Prediction with Different Strategies

```python
from src.moe import GateCalibrator, MoEPredictor

# Initialize components
calibrator = GateCalibrator(gate_model, method='isotonic').calibrate(X_cal, y_cal)
predictor = MoEPredictor(calibrator, expert_models, classes)

# Example predictions
hard_preds = predictor.predict(X_test, strategy='hard')
soft_preds = predictor.predict(X_test, strategy='soft', threshold=0.15)
topk_preds = predictor.predict(X_test, strategy='top_k', k=3)
```

### 2. Advanced Fine-Tuning

```python
from src.moe import MoEFineTuner

# Initialize fine-tuner
fine_tuner = MoEFineTuner(gate_model, expert_models, num_classes=len(classes))

# Fine-tune last two layers
fine_tuner.fine_tune_gate_last_layers(
    X_train, y_train,
    layers_to_finetune=['dense_2', 'dense_3'],
    learning_rate=1e-6
)

# Fine-tune aggregation weights
fine_tuner.fine_tune_aggregation(
    X_train, y_train,
    epochs=20,
    batch_size=256
)
```

### 3. Comprehensive Evaluation

```python
from src.moe import MoEEvaluator

# Initialize evaluator
evaluator = MoEEvaluator(y_true, classes)

# Compare multiple strategies
results = {
    'Hard Gating': hard_preds,
    'Soft Gating (0.15)': soft_preds,
    'Top-3 Experts': topk_preds
}

print(evaluator.compare_strategies(results))
```

### 4. Custom Loss Functions

```python
from src.moe.losses import FocalLoss

# Build model with focal loss
model = build_gate_model()
model.compile(
    optimizer='adam',
    loss=FocalLoss(alpha=0.25, gamma=2.0),
    metrics=['accuracy']
)
```

---

## Advanced Features

### Dynamic Threshold Adjustment
```python
from src.moe.finetuning import DynamicThresholdOptimizer

optimizer = DynamicThresholdOptimizer(predictor, X_val, y_val)
best_threshold = optimizer.find_optimal_threshold()
```

### Calibration Comparison
```python
from src.moe.calibration import CalibrationComparator

comparator = CalibrationComparator(gate_model, X_cal, y_cal)
comparator.compare_methods(['isotonic', 'sigmoid'])
```

---

## License
MIT License - See [LICENSE](LICENSE) for details.