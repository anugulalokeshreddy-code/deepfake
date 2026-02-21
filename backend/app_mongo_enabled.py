import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user
from flask_cors import CORS
from config import config

# Initialize extensions (will be configured in create_app)
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Determine database type
    db_type = app.config.get('DB_TYPE', 'sqlite').lower()
    
    # Initialize appropriate database
    if db_type == 'mongodb':
        # MongoDB initialization
        from mongoengine import connect, ConnectionError
        try:
            connect(
                db=app.config.get('MONGODB_DB', 'deepfake_detector'),
                host=app.config.get('MONGODB_URI', 'mongodb://localhost:27017/deepfake_detector'),
                connect=False
            )
            print(f"✓ Connected to MongoDB: {app.config.get('MONGODB_URI')}")
        except ConnectionError as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise
        
        # Register MongoDB login manager
        from mongo_models import MongoUser
        
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return MongoUser.objects(id=user_id).first()
            except:
                return None
        
        # Register blueprints for MongoDB
        from auth_mongo import auth_mongo_bp
        from api_routes_mongo import detection_mongo_bp, init_detector
        
        app.register_blueprint(auth_mongo_bp)
        app.register_blueprint(detection_mongo_bp)
        
        # Initialize detector
        init_detector(app)
        
    else:
        # SQLite initialization
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy()
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
        
        # Register SQLite login manager
        from models import User
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Register blueprints for SQLite
        from auth import auth_bp
        from api_routes import detection_bp, init_detector
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(detection_bp)
        
        # Initialize detector
        init_detector(app)
    
    # Initialize LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Route handlers
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html', user=current_user)
    
    @app.route('/login')
    def login():
        """Login page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        """Registration page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('register.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        return render_template('dashboard.html', user=current_user)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'database': db_type,
            'message': f'Deepfake Detector API running on {db_type}'
        }), 200
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request"""
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle unauthorized access"""
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden access"""
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found"""
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server error"""
        return jsonify({'error': 'Server error', 'message': 'An unexpected error occurred'}), 500
    
    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
