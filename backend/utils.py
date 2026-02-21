# Utility functions for the application

import os
import hashlib
from datetime import datetime, timedelta
from functools import wraps
import time

def secure_filename(filename):
    """Secure a filename to prevent directory traversal"""
    import os
    filename = os.path.basename(filename)
    filename = "".join(c for c in filename if c.isalnum() or c in '._-')
    return filename

def get_file_size_mb(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0

def delete_old_uploads(upload_folder, days=7):
    """Delete uploads older than specified days"""
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    
    for filename in os.listdir(upload_folder):
        filepath = os.path.join(upload_folder, filename)
        if os.path.isfile(filepath):
            if os.path.getctime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    print(f"Deleted old file: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

def format_size(size_bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def time_ago(dt):
    """Convert datetime to 'time ago' format"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        return f"{diff.days // 365} years ago"
    elif diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "just now"

def validate_image_file(filepath):
    """Validate if file is a proper image"""
    try:
        from PIL import Image
        image = Image.open(filepath)
        image.verify()
        return True
    except Exception as e:
        print(f"Image validation error: {e}")
        return False

def get_image_info(filepath):
    """Get image information"""
    try:
        from PIL import Image
        image = Image.open(filepath)
        return {
            'format': image.format,
            'size': image.size,
            'mode': image.mode,
            'width': image.width,
            'height': image.height
        }
    except Exception as e:
        print(f"Error getting image info: {e}")
        return None

def create_backup(database_path, backup_dir='backups'):
    """Create database backup"""
    if not os.path.exists(database_path):
        return False
    
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
    
    try:
        import shutil
        shutil.copy2(database_path, backup_path)
        print(f"Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False
