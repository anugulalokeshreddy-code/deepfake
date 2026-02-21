from functools import wraps
from flask import request, jsonify, session
from flask_login import current_user, login_required as flask_login_required

def login_required(f):
    """Custom login required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_file_upload(allowed_extensions={'jpg', 'jpeg', 'png', 'bmp', 'gif'}):
    """Decorator to validate file uploads"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({'error': 'No file part in request'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Check file extension
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return jsonify({'error': f'Only {allowed_extensions} files are allowed'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_exceptions(f):
    """Decorator to handle exceptions and return JSON responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    return decorated_function
