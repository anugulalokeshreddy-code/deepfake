from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from mongo_models import MongoDetection, MongoUser
from deepfake_detector import DeepfakeDetector
from decorators import validate_file_upload, handle_exceptions
import os
import uuid
from werkzeug.utils import secure_filename

detection_mongo_bp = Blueprint('detection_mongo', __name__, url_prefix='/api/detection')

# Initialize detector globally
detector = None

def init_detector(app):
    """Initialize detector with app context"""
    global detector
    detector = DeepfakeDetector(
        model_path=app.config['MODEL_PATH'],
        device=app.config['DEVICE']
    )

@detection_mongo_bp.route('/upload', methods=['POST'])
@login_required
@validate_file_upload()
@handle_exceptions
def upload_and_detect():
    """Upload image and detect deepfake"""
    try:
        file = request.files['file']
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        filename = f"{unique_id}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(filepath)
        
        # Run detection
        prediction, confidence, processing_time = detector.detect(filepath)
        
        # Save to database
        detection = MongoDetection(
            user_id=current_user.id,
            filename=filename,
            original_filename=secure_filename(file.filename),
            prediction=prediction,
            confidence=confidence,
            processing_time=processing_time
        )
        detection.save()
        
        return jsonify({
            'detection_id': detection.id,
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'processing_time': round(processing_time, 2),
            'filename': file.filename,
            'message': f'Image classified as {prediction.upper()}'
        }), 200
    
    except Exception as e:
        # Clean up uploaded file if detection fails
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        raise

@detection_mongo_bp.route('/history', methods=['GET'])
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
        skip = (page - 1) * limit
        detections = list(MongoDetection.objects(user_id=current_user.id).order_by('-created_at').skip(skip).limit(limit))
        total = MongoDetection.objects(user_id=current_user.id).count()
        pages = (total + limit - 1) // limit
        
        detection_list = [d.to_dict() for d in detections]
        
        return jsonify({
            'detections': detection_list,
            'total': total,
            'pages': pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        raise

@detection_mongo_bp.route('/details/<detection_id>', methods=['GET'])
@login_required
@handle_exceptions
def get_detection_details(detection_id):
    """Get details of a specific detection"""
    try:
        detection = MongoDetection.objects(
            id=detection_id,
            user_id=current_user.id
        ).first()
        
        if not detection:
            return jsonify({'error': 'Detection not found'}), 404
        
        return jsonify(detection.to_dict()), 200
    
    except Exception as e:
        raise

@detection_mongo_bp.route('/delete/<detection_id>', methods=['DELETE'])
@login_required
@handle_exceptions
def delete_detection(detection_id):
    """Delete a detection record"""
    try:
        detection = MongoDetection.objects(
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
        detection.delete()
        
        return jsonify({'message': 'Detection deleted successfully'}), 200
    
    except Exception as e:
        raise

@detection_mongo_bp.route('/stats', methods=['GET'])
@login_required
@handle_exceptions
def get_stats():
    """Get detection statistics for current user"""
    try:
        total_detections = MongoDetection.objects(user_id=current_user.id).count()
        real_count = MongoDetection.objects(
            user_id=current_user.id,
            prediction='REAL'
        ).count()
        deepfake_count = MongoDetection.objects(
            user_id=current_user.id,
            prediction='DEEPFAKE'
        ).count()
        
        # Calculate average confidence
        detections = list(MongoDetection.objects(user_id=current_user.id))
        avg_confidence = sum(d.confidence for d in detections) / len(detections) if detections else 0
        
        return jsonify({
            'total_detections': total_detections,
            'real_images': real_count,
            'deepfake_images': deepfake_count,
            'average_confidence': round(float(avg_confidence), 4)
        }), 200
    
    except Exception as e:
        raise
