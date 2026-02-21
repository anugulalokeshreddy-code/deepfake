import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import db, User, Detection

class BaseTestCase(unittest.TestCase):
    """Base test case with setup and teardown"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

class AuthTestCase(BaseTestCase):
    """Test authentication endpoints"""
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('user_id', data)
        self.assertEqual(data['username'], 'testuser')
    
    def test_registration_invalid_password(self):
        """Test registration with weak password"""
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'weak',
            'confirm_password': 'weak'
        })
        
        self.assertEqual(response.status_code, 400)
    
    def test_registration_existing_user(self):
        """Test registration with existing username"""
        # Create first user
        self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        })
        
        # Try to register with same username
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        })
        
        self.assertEqual(response.status_code, 409)
    
    def test_user_login_success(self):
        """Test successful login"""
        # Register user first
        self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        })
        
        # Login
        response = self.client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'WrongPass123'
        })
        
        self.assertEqual(response.status_code, 401)

class DetectionTestCase(BaseTestCase):
    """Test detection endpoints"""
    
    def setUp(self):
        super().setUp()
        
        # Create test user
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('TestPass123')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def test_detection_history_empty(self):
        """Test detection history for new user"""
        with self.app.app_context():
            # Create session cookie
            self.client.post('/api/auth/login', json={
                'username': 'testuser',
                'password': 'TestPass123'
            })
        
        response = self.client.get('/api/detection/history')
        self.assertEqual(response.status_code, 401)  # Not authenticated via API

class UserTestCase(BaseTestCase):
    """Test user model"""
    
    def test_password_hashing(self):
        """Test password hashing"""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('TestPass123')
            
            self.assertTrue(user.check_password('TestPass123'))
            self.assertFalse(user.check_password('WrongPassword'))

if __name__ == '__main__':
    unittest.main()
