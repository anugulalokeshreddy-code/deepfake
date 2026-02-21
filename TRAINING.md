# Model Training Guide

## Overview

This guide covers training and fine-tuning the Vision Transformer model for deepfake detection.

## Datasets

### Recommended Datasets

1. **Celeb-DF**
   - 590 deepfake videos from 5,639 videos and 590 real videos
   - Frame-level annotations
   - Download: https://www.cs.albany.edu/~lsw/celeb-deepfake.html

2. **FaceForensics++**
   - 1000 videos with 4 types of manipulations
   - High quality benchmark
   - Download: https://github.com/ondyari/FaceForensics

3. **DFDC (DeepFake Detection Challenge)**
   - 100K videos
   - Diverse manipulations
   - Download: https://www.kaggle.com/competitions/deepfake-detection-challenge

### Dataset Structure

```
datasets/
├── train/
│   ├── real/
│   │   ├── image_001.jpg
│   │   └── image_002.jpg
│   └── deepfake/
│       ├── image_003.jpg
│       └── image_004.jpg
├── val/
│   ├── real/
│   └── deepfake/
└── test/
    ├── real/
    └── deepfake/
```

## Training Script

Create `train_model.py`:

```python
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from transformers import ViTFeatureExtractor, ViTForImageClassification
from PIL import Image
import os
from tqdm import tqdm
import json

class DeepfakeDataset(Dataset):
    """Custom dataset for deepfake detection"""
    
    def __init__(self, image_dir, feature_extractor):
        self.image_dir = image_dir
        self.feature_extractor = feature_extractor
        self.images = []
        self.labels = []
        
        # Load real images (label=0)
        real_dir = os.path.join(image_dir, 'real')
        for img in os.listdir(real_dir):
            self.images.append(os.path.join(real_dir, img))
            self.labels.append(0)
        
        # Load deepfake images (label=1)
        fake_dir = os.path.join(image_dir, 'deepfake')
        for img in os.listdir(fake_dir):
            self.images.append(os.path.join(fake_dir, img))
            self.labels.append(1)
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
            inputs = self.feature_extractor(image, return_tensors='pt')
            
            return {
                'pixel_values': inputs['pixel_values'].squeeze(0),
                'labels': torch.tensor(label, dtype=torch.long)
            }
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Return dummy tensor on error
            return {
                'pixel_values': torch.zeros((3, 224, 224)),
                'labels': torch.tensor(0, dtype=torch.long)
            }

def train_epoch(model, dataloader, optimizer, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    
    for batch in tqdm(dataloader, desc='Training'):
        pixel_values = batch['pixel_values'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        
        outputs = model(pixel_values, labels=labels)
        loss = outputs.loss
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)

def validate(model, dataloader, device):
    """Validate model"""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc='Validating'):
            pixel_values = batch['pixel_values'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(pixel_values, labels=labels)
            loss = outputs.loss
            logits = outputs.logits
            
            total_loss += loss.item()
            
            predictions = torch.argmax(logits, dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
    
    accuracy = correct / total
    avg_loss = total_loss / len(dataloader)
    
    return avg_loss, accuracy

def train_model(train_dir, val_dir, num_epochs=10):
    """Main training function"""
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load feature extractor and model
    feature_extractor = ViTFeatureExtractor.from_pretrained(
        'google/vit-base-patch16-224-in21k'
    )
    
    model = ViTForImageClassification.from_pretrained(
        'google/vit-base-patch16-224-in21k',
        num_labels=2,
        ignore_mismatched_sizes=True
    )
    model.to(device)
    
    # Datasets
    train_dataset = DeepfakeDataset(train_dir, feature_extractor)
    val_dataset = DeepfakeDataset(val_dir, feature_extractor)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=32,
        shuffle=True,
        num_workers=4
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=32,
        shuffle=False,
        num_workers=4
    )
    
    # Optimizer
    optimizer = Adam(model.parameters(), lr=1e-4)
    
    # Training loop
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_accuracy': []
    }
    
    best_accuracy = 0
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch+1}/{num_epochs}")
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, device)
        history['train_loss'].append(train_loss)
        
        # Validate
        val_loss, val_accuracy = validate(model, val_loader, device)
        history['val_loss'].append(val_loss)
        history['val_accuracy'].append(val_accuracy)
        
        print(f"Train Loss: {train_loss:.4f}")
        print(f"Val Loss: {val_loss:.4f}")
        print(f"Val Accuracy: {val_accuracy:.4f}")
        
        # Save best model
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save(model, 'models/vit_deepfake_detector_best.pth')
            print(f"Best model saved with accuracy: {val_accuracy:.4f}")
    
    # Save final model
    torch.save(model, 'models/vit_deepfake_detector.pth')
    
    # Save history
    with open('training_history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    print("\nTraining complete!")
    return model, history

if __name__ == '__main__':
    train_dir = 'datasets/train'
    val_dir = 'datasets/val'
    
    model, history = train_model(train_dir, val_dir)
```

## Running Training

```bash
# Install additional dependencies
pip install tqdm tensorboard

# Start training
python train_model.py

# Monitor with tensorboard
tensorboard --logdir=./logs
```

## Transfer Learning Strategy

For better results with limited data:

1. **Fine-tune top layers only**
```python
# Freeze base model
for param in model.vit.parameters():
    param.requires_grad = False

# Only train classifier
for param in model.classifier.parameters():
    param.requires_grad = True
```

2. **Progressive unfreezing**
```python
# Unfreeze progressively
for i, layer in enumerate(model.vit.encoder.layer):
    if i >= len(model.vit.encoder.layer) - 4:  # Last 4 layers
        for param in layer.parameters():
            param.requires_grad = True
```

## Data Augmentation

```python
from torchvision import transforms

train_transforms = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.GaussianBlur(kernel_size=3),
    transforms.RandomResizedCrop((224, 224), scale=(0.8, 1.0))
])
```

## Hyperparameter Tuning

### Recommended Settings

| Parameter | Value |
|-----------|-------|
| Batch Size | 32 |
| Learning Rate | 1e-4 |
| Warmup Steps | 500 |
| Epochs | 10-20 |
| Optimizer | Adam |
| Scheduler | OneCycleLR |

### Using Learning Rate Scheduler

```python
from torch.optim.lr_scheduler import OneCycleLR

scheduler = OneCycleLR(
    optimizer,
    max_lr=1e-3,
    steps_per_epoch=len(train_loader),
    epochs=num_epochs
)

# In training loop
for batch in train_loader:
    # Training code
    ...
    scheduler.step()
```

## Evaluation Metrics

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)

def evaluate_model(model, dataloader, device):
    """Comprehensive evaluation"""
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for batch in dataloader:
            pixel_values = batch['pixel_values'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(pixel_values)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            
            predictions = torch.argmax(logits, dim=1)
            
            all_preds.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs[:, 1].cpu().numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds)
    recall = recall_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)
    roc_auc = roc_auc_score(all_labels, all_probs)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc
    }
```

## Model Quantization

```python
import torch.quantization as quantization

def quantize_model(model, device='cpu'):
    """Quantize model to int8"""
    
    model.to(device)
    model.eval()
    
    # Prepare for quantization
    model.qconfig = quantization.get_default_qconfig('qnnpack')
    quantization.prepare(model, inplace=True)
    
    # Calibrate with data
    # ... pass calibration data ...
    
    # Convert to quantized
    quantization.convert(model, inplace=True)
    
    return model
```

## Export to ONNX

```python
def export_onnx(model, dummy_input, output_path='models/deepfake_detector.onnx'):
    """Export model to ONNX format"""
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        input_names=['pixel_values'],
        output_names=['logits'],
        dynamic_axes={
            'pixel_values': {0: 'batch_size'},
            'logits': {0: 'batch_size'}
        },
        opset_version=14
    )
    
    print(f"Model exported to {output_path}")
```

---

For questions, refer to the main README.md
