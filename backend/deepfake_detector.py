import torch
import torch.nn as nn
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import cv2
import numpy as np
import os
from typing import Tuple
import time

class DeepfakeDetector:
    """ViT-based Deepfake Detector"""
    
    def __init__(self, model_path: str = None, device: str = 'cpu', model_name: str = 'google/vit-base-patch16-224-in21k'):
        """
        Initialize the deepfake detector
        
        Args:
            model_path: Path to saved model weights
            device: Device to use ('cpu' or 'cuda')
            model_name: HuggingFace model identifier
        """
        self.device = device
        self.model_name = model_name
        self.model_path = model_path
        self.image_processor = None
        self.model = None
        self.classes = ['REAL', 'DEEPFAKE']
        
        self._load_model()
    
    def _load_model(self):
        """Load ViT model and image processor"""
        try:
            # Load image processor (replaces feature extractor)
            self.image_processor = ViTImageProcessor.from_pretrained(self.model_name)
            
            # Load or initialize model
            if self.model_path and os.path.exists(self.model_path):
                # Load fine-tuned model
                self.model = torch.load(self.model_path, map_location=self.device)
            else:
                # Load pre-trained model and adapt for binary classification
                base_model = ViTForImageClassification.from_pretrained(
                    self.model_name,
                    num_labels=2,
                    ignore_mismatched_sizes=True
                )
                self.model = base_model
            
            self.model.to(self.device)
            self.model.eval()
            print(f"Model loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image as tensor
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to read image: {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image for image processor
            image = Image.fromarray(image)
            
            # Image processing
            inputs = self.image_processor(images=image, return_tensors='pt')
            
            return inputs['pixel_values'].to(self.device)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            raise
    
    def detect(self, image_path: str) -> Tuple[str, float, float]:
        """
        Detect if image contains deepfake
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (prediction, confidence, processing_time)
        """
        start_time = time.time()
        
        try:
            # Preprocess image
            inputs = self.preprocess_image(image_path)
            
            # Inference
            with torch.no_grad():
                outputs = self.model(inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
                prediction_idx = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0, prediction_idx].item()
            
            prediction = self.classes[prediction_idx]
            processing_time = time.time() - start_time
            
            return prediction, confidence, processing_time
        
        except Exception as e:
            print(f"Error during detection: {e}")
            raise
    
    def detect_batch(self, image_paths: list) -> list:
        """
        Detect deepfakes in batch
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of (prediction, confidence) tuples
        """
        results = []
        for image_path in image_paths:
            try:
                prediction, confidence, _ = self.detect(image_path)
                results.append((prediction, confidence))
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                results.append(('ERROR', 0.0))
        
        return results
    
    def save_model(self, path: str):
        """Save model weights"""
        try:
            torch.save(self.model, path)
            print(f"Model saved to {path}")
        except Exception as e:
            print(f"Error saving model: {e}")
            raise
