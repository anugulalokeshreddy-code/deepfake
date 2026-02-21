import unittest
import tempfile
import os
from unittest.mock import MagicMock, patch
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.deepfake_detector import DeepfakeDetector

class DeepfakeDetectorTestCase(unittest.TestCase):
    """Test deepfake detector model"""
    
    @patch('backend.deepfake_detector.ViTFeatureExtractor')
    @patch('backend.deepfake_detector.ViTForImageClassification')
    def test_detector_initialization(self, mock_model, mock_extractor):
        """Test detector initialization"""
        mock_extractor.from_pretrained = MagicMock()
        mock_model.from_pretrained = MagicMock()
        
        detector = DeepfakeDetector(device='cpu')
        
        self.assertIsNotNone(detector)
        self.assertEqual(detector.device, 'cpu')
        self.assertEqual(detector.classes, ['REAL', 'DEEPFAKE'])
    
    def test_image_validation(self):
        """Test image validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple test image
            from PIL import Image
            import numpy as np
            
            img = Image.fromarray(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
            img_path = os.path.join(tmpdir, 'test.png')
            img.save(img_path)
            
            self.assertTrue(os.path.exists(img_path))

if __name__ == '__main__':
    unittest.main()
