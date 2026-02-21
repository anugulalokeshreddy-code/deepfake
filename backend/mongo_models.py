from mongoengine import Document, StringField, EmailField, BooleanField, FloatField, DateTimeField, ReferenceField, CASCADE
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class MongoUser(Document):
    """MongoDB User model"""
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }
    
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    username = StringField(max_length=80, unique=True, required=True)
    email = EmailField(unique=True, required=True)
    password_hash = StringField(max_length=255, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = BooleanField(default=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Get user ID for Flask-Login"""
        return self.id
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def __repr__(self):
        return f'<MongoUser {self.username}>'

class MongoDetection(Document):
    """MongoDB Detection model"""
    meta = {
        'collection': 'detections',
        'indexes': [('user_id', 'created_at'), 'user_id']
    }
    
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = StringField(required=True, index=True)  # Reference to User ID
    filename = StringField(max_length=255, required=True)
    original_filename = StringField(max_length=255, required=True)
    prediction = StringField(max_length=20, required=True)  # 'REAL' or 'DEEPFAKE'
    confidence = FloatField(required=True)
    processing_time = FloatField()  # in seconds
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<MongoDetection {self.id}: {self.prediction}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'filename': self.original_filename,
            'prediction': self.prediction,
            'confidence': round(self.confidence, 2),
            'processing_time': round(self.processing_time, 2) if self.processing_time else None,
            'created_at': self.created_at.isoformat()
        }
