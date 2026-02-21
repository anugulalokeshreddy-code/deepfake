from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from models import db, Detection
from deepfake_detector import DeepfakeDetector
from decorators import validate_file_upload, handle_exceptions
import os
import uuid
from werkzeug.utils import secure_filename
import logging

# Setup logging
logger = logging.getLogger(__name__)

detection_bp = Blueprint('detection', __name__, url_prefix='/api/detection')

# Initialize detector globally
detector = None

def init_detector(app):
    """Initialize detector with app context"""
    global detector
    detector = DeepfakeDetector(
        model_path=app.config['MODEL_PATH'],
        device=app.config['DEVICE']
    )

@detection_bp.route('/upload', methods=['POST'])
@login_required
@validate_file_upload()
@handle_exceptions
def upload_and_detect():
    """Upload image and detect deepfake"""
    try:
        logger.info("=== Upload request started ===")
        logger.info(f"User: {current_user.username}")
        
        file = request.files['file']
        logger.info(f"File received: {file.filename}")
        
        # Get upload folder from config
        upload_folder = current_app.config['UPLOAD_FOLDER']
        logger.info(f"Upload folder: {upload_folder}")
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        logger.info(f"Upload folder exists: {os.path.exists(upload_folder)}")
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        filename = f"{unique_id}.{ext}"
        filepath = os.path.join(upload_folder, filename)
        logger.info(f"Saving to: {filepath}")
        
        # Save uploaded file
        file.save(filepath)
        logger.info(f"File saved successfully")
        
        # Verify file was saved
        if not os.path.exists(filepath):
            logger.error(f"File NOT saved: {filepath}")
            raise Exception(f"Failed to save file at {filepath}")
        
        logger.info(f"File verification passed, size: {os.path.getsize(filepath)} bytes")
        
        # Run detection
        logger.info("Starting deepfake detection...")
        prediction, confidence, processing_time = detector.detect(filepath)
        logger.info(f"Detection result: {prediction}, confidence: {confidence}")
        
        # Save to database
        detection = Detection(
            user_id=current_user.id,
            filename=filename,
            original_filename=secure_filename(file.filename),
            prediction=prediction,
            confidence=confidence,
            processing_time=processing_time
        )
        
        db.session.add(detection)
        db.session.commit()
        logger.info(f"Detection record saved with ID: {detection.id}")
        
        return jsonify({
            'detection_id': detection.id,
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'processing_time': round(processing_time, 2),
            'filename': file.filename,
            'message': f'Image classified as {prediction.upper()}'
        }), 200
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        # Clean up uploaded file if detection fails
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        db.session.rollback()
        raise

@detection_bp.route('/history', methods=['GET'])
@login_required
@handle_exceptions
def get_history():
    """Get detection history for current user"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Validate pagination
        if page < 1 or limit < 1 or limit > 100:
            return jsonify({'error': 'Invalid pagination parameters'}), 400
        
        # Query detections
        paginated = Detection.query.filter_by(user_id=current_user.id).order_by(
            Detection.created_at.desc()
        ).paginate(page=page, per_page=limit)
        
        detections = [d.to_dict() for d in paginated.items]
        
        return jsonify({
            'detections': detections,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        raise

@detection_bp.route('/details/<detection_id>', methods=['GET'])
@login_required
@handle_exceptions
def get_detection_details(detection_id):
    """Get details of a specific detection"""
    try:
        detection = Detection.query.filter_by(
            id=detection_id,
            user_id=current_user.id
        ).first()
        
        if not detection:
            return jsonify({'error': 'Detection not found'}), 404
        
        return jsonify(detection.to_dict()), 200
    
    except Exception as e:
        raise

@detection_bp.route('/delete/<detection_id>', methods=['DELETE'])
@login_required
@handle_exceptions
def delete_detection(detection_id):
    """Delete a detection record"""
    try:
        detection = Detection.query.filter_by(
            id=detection_id,
            user_id=current_user.id
        ).first()
        
        if not detection:
            return jsonify({'error': 'Detection not found'}), 404
        
        # Delete uploaded image file
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], detection.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete database record
        db.session.delete(detection)
        db.session.commit()
        
        return jsonify({'message': 'Detection deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        raise

@detection_bp.route('/stats', methods=['GET'])
@login_required
@handle_exceptions
def get_stats():
    """Get detection statistics for current user"""
    try:
        total_detections = Detection.query.filter_by(user_id=current_user.id).count()
        real_count = Detection.query.filter_by(
            user_id=current_user.id,
            prediction='REAL'
        ).count()
        deepfake_count = Detection.query.filter_by(
            user_id=current_user.id,
            prediction='DEEPFAKE'
        ).count()
        
        avg_confidence = db.session.query(db.func.avg(Detection.confidence)).filter_by(
            user_id=current_user.id
        ).scalar() or 0
        
        return jsonify({
            'total_detections': total_detections,
            'real_images': real_count,
            'deepfake_images': deepfake_count,
            'average_confidence': round(float(avg_confidence), 4)
        }), 200
    
    except Exception as e:
        raise
