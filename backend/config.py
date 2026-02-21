import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' or 'mongodb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///users.db')
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/deepfake_detector')
    MONGODB_DB = os.getenv('MONGODB_DB', 'deepfake_detector')
    
    # Upload folder with absolute path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'backend', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/vit_deepfake_detector.pth')
    
    # Model settings
    DEVICE = 'cuda' if os.getenv('USE_GPU', 'False').lower() == 'true' else 'cpu'
    MODEL_NAME = 'google/vit-base-patch16-224-in21k'
    INPUT_SIZE = 224
    BATCH_SIZE = 32
    LEARNING_RATE = 1e-4
    NUM_EPOCHS = 10
    
    @staticmethod
    def init_app(app):
        """Initialize application"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        print(f"Upload folder: {Config.UPLOAD_FOLDER}")
        print(f"Upload folder exists: {os.path.exists(Config.UPLOAD_FOLDER)}")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
