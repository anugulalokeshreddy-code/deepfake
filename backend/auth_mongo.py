from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from mongo_models import MongoUser
import re

auth_mongo_bp = Blueprint('auth_mongo', __name__, url_prefix='/api/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, ""

@auth_mongo_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if not email or not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        valid, message = validate_password(password)
        if not valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        if MongoUser.objects(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if MongoUser.objects(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = MongoUser(username=username, email=email)
        user.set_password(password)
        user.save()
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user.id,
            'username': user.username
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_mongo_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Username/Email and password required'}), 400
        
        # Find user by username or email
        user = MongoUser.objects(
            __raw__={'$or': [{'username': username_or_email}, {'email': username_or_email}]}
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        
        login_user(user, remember=data.get('remember', False))
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_mongo_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_mongo_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'user_id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'created_at': current_user.created_at.isoformat()
    }), 200

@auth_mongo_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not current_user.check_password(old_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
        
        valid, message = validate_password(new_password)
        if not valid:
            return jsonify({'error': message}), 400
        
        current_user.set_password(new_password)
        current_user.save()
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to change password: {str(e)}'}), 500
