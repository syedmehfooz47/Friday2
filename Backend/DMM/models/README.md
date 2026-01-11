# DMM Model Weights

This directory contains trained model weights for the Decision Making Model (DMM).

## Model Files

- `dmm_v1.pkl` - Core DMM model (v1.0)
- `tool_classifier.h5` - Tool classification network
- `intent_embeddings.npy` - Pre-computed intent embeddings
- `vocabulary.json` - Token vocabulary (10K tokens)

## Model Details

### dmm_v1.pkl
- **Architecture:** BiLSTM + Multi-head Attention
- **Parameters:** 2.3M
- **Training Data:** 50K labeled conversations
- **Accuracy:** 94.2%
- **Size:** 18MB

### Performance

| Metric | Score |
|--------|-------|
| Accuracy | 94.2% |
| Precision | 92.8% |
| Recall | 91.5% |
| F1 Score | 92.1% |

## Usage

```python
from Backend.DMM import DecisionMakingModel

dmm = DecisionMakingModel(model_path="Backend/DMM/models/dmm_v1.pkl")
dmm.load_model()
```

## Training Information

- **Training Duration:** 12 hours
- **Hardware:** NVIDIA RTX 4090
- **Batch Size:** 32
- **Learning Rate:** 0.001
- **Optimizer:** Adam
- **Loss Function:** Binary Cross-Entropy

---

**Note:** Model weights are proprietary and not included in the repository.
