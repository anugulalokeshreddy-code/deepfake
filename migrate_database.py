"""
SQLite to MongoDB Migration Script
Migrates user accounts and detection history from SQLite to MongoDB
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

def migrate_to_mongodb():
    """Migrate data from SQLite to MongoDB"""
    
    print("=" * 60)
    print("SQLite to MongoDB Migration Tool")
    print("=" * 60)
    
    # Configure Flask app for SQLite
    os.environ['DB_TYPE'] = 'sqlite'
    os.environ['FLASK_APP'] = 'backend/app.py'
    
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from config import config
    
    # Create Flask app for reading from SQLite
    app = Flask(__name__)
    app.config.from_object(config['development'])
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///backend/users.db')
    
    db = SQLAlchemy(app)
    
    # Import SQLAlchemy models
    from models import User, Detection
    
    print("\n1. Reading from SQLite database...")
    
    with app.app_context():
        try:
            # Count records
            user_count = User.query.count()
            detection_count = Detection.query.count()
            
            print(f"   ✓ Found {user_count} users")
            print(f"   ✓ Found {detection_count} detections")
            
            if user_count == 0:
                print("\n   ✓ No data to migrate")
                return
            
            # Get all data
            users = User.query.all()
            detections = Detection.query.all()
            
        except Exception as e:
            print(f"   ✗ Error reading SQLite: {e}")
            return
    
    # Configure MongoDB
    print("\n2. Connecting to MongoDB...")
    
    os.environ['DB_TYPE'] = 'mongodb'
    
    from mongoengine import connect, ConnectionError
    from mongo_models import MongoUser, MongoDetection
    
    try:
        connect(
            db=os.getenv('MONGODB_DB', 'deepfake_detector'),
            host=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/deepfake_detector'),
            connect=False
        )
        print(f"   ✓ Connected to MongoDB: {os.getenv('MONGODB_URI')}")
    except ConnectionError as e:
        print(f"   ✗ MongoDB connection failed: {e}")
        print("\n   Please ensure MongoDB is running:")
        print("   Windows: mongod or MongoDB service")
        print("   Linux/Mac: sudo systemctl start mongod")
        return
    
    # Migrate users
    print("\n3. Migrating users...")
    
    migrated_users = 0
    for user in users:
        try:
            existing = MongoUser.objects(username=user.username).first()
            if existing:
                print(f"   ⊗ User '{user.username}' already exists - skipping")
                continue
            
            mongo_user = MongoUser(
                username=user.username,
                email=user.email,
                password_hash=user.password_hash
            )
            mongo_user.save()
            migrated_users += 1
            print(f"   ✓ Migrated user: {user.username}")
            
        except Exception as e:
            print(f"   ✗ Error migrating user '{user.username}': {e}")
    
    print(f"\n   Total users migrated: {migrated_users}/{user_count}")
    
    # Migrate detections
    print("\n4. Migrating detection records...")
    
    migrated_detections = 0
    failed_detections = 0
    
    for detection in detections:
        try:
            # Get corresponding MongoDB user
            mongo_user = MongoUser.objects(id=str(detection.user_id)).first()
            
            if not mongo_user:
                # Try to find by username
                sqlite_user = User.query.get(detection.user_id)
                if sqlite_user:
                    mongo_user = MongoUser.objects(username=sqlite_user.username).first()
            
            if not mongo_user:
                print(f"   ⊗ User not found for detection {detection.id} - skipping")
                failed_detections += 1
                continue
            
            # Check if detection already exists
            existing = MongoDetection.objects(id=detection.id).first()
            if existing:
                print(f"   ⊗ Detection {detection.id} already exists - skipping")
                continue
            
            mongo_detection = MongoDetection(
                user_id=mongo_user.id,
                filename=detection.filename,
                original_filename=detection.original_filename if hasattr(detection, 'original_filename') else detection.filename,
                prediction=detection.prediction,
                confidence=detection.confidence,
                processing_time=detection.processing_time,
                created_at=detection.created_at if hasattr(detection, 'created_at') else None
            )
            mongo_detection.save()
            migrated_detections += 1
            
            if migrated_detections % 10 == 0:
                print(f"   ✓ Migrated {migrated_detections} detections...")
            
        except Exception as e:
            print(f"   ✗ Error migrating detection {detection.id}: {e}")
            failed_detections += 1
    
    print(f"\n   Total detections migrated: {migrated_detections}/{detection_count}")
    print(f"   Failed migrations: {failed_detections}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Users migrated:      {migrated_users}/{user_count}")
    print(f"Detections migrated: {migrated_detections}/{detection_count}")
    print(f"Failed records:      {failed_detections}")
    
    if failed_detections == 0:
        print("\n✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update .env: Set DB_TYPE=mongodb")
        print("2. Update .env: Set FLASK_APP=backend/app_mongo_enabled.py")
        print("3. Restart your application")
    else:
        print("\n⚠ Migration completed with errors")
        print("Please review the errors above and retry")
    
    print("\nBackup your SQLite database before removing it:")
    print("   Original database: backend/users.db")
    print("=" * 60)

def reverse_migration():
    """Reverse migration: MongoDB to SQLite (creates backup)"""
    
    print("=" * 60)
    print("MongoDB to SQLite Reverse Migration (Backup)")
    print("=" * 60)
    
    print("\nNote: This will create a backup in SQLite format")
    print("Original MongoDB data is not deleted")
    
    from mongoengine import connect, ConnectionError
    from mongo_models import MongoUser, MongoDetection
    
    # Connect to MongoDB
    print("\n1. Connecting to MongoDB...")
    
    try:
        connect(
            db=os.getenv('MONGODB_DB', 'deepfake_detector'),
            host=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/deepfake_detector'),
            connect=False
        )
        print(f"   ✓ Connected to MongoDB")
    except ConnectionError as e:
        print(f"   ✗ MongoDB connection failed: {e}")
        return
    
    # Read from MongoDB
    print("\n2. Reading from MongoDB...")
    
    try:
        users = list(MongoUser.objects.all())
        detections = list(MongoDetection.objects.all())
        
        print(f"   ✓ Found {len(users)} users")
        print(f"   ✓ Found {len(detections)} detections")
        
    except Exception as e:
        print(f"   ✗ Error reading MongoDB: {e}")
        return
    
    # Create SQLite backup
    print("\n3. Creating SQLite backup...")
    
    import shutil
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from config import config
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config['development'])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backend/users_backup.db'
    
    db = SQLAlchemy(app)
    
    from models import User, Detection
    
    with app.app_context():
        db.create_all()
        
        print("   ✓ Creating backup database...")
        
        # Migrate users
        for user in users:
            try:
                existing = User.query.filter_by(username=user.username).first()
                if existing:
                    print(f"   ⊗ User '{user.username}' already in backup")
                    continue
                
                backup_user = User(
                    username=user.username,
                    email=user.email,
                    password_hash=user.password_hash
                )
                db.session.add(backup_user)
            except Exception as e:
                print(f"   ✗ Error backing up user: {e}")
        
        # Migrate detections
        for detection in detections:
            try:
                sqlite_user = User.query.filter_by(username=MongoUser.objects(id=detection.user_id).first().username).first()
                if not sqlite_user:
                    print(f"   ⊗ User not found for detection backup")
                    continue
                
                backup_detection = Detection(
                    user_id=sqlite_user.id,
                    filename=detection.filename,
                    original_filename=detection.original_filename,
                    prediction=detection.prediction,
                    confidence=detection.confidence,
                    processing_time=detection.processing_time
                )
                db.session.add(backup_detection)
            except Exception as e:
                print(f"   ✗ Error backing up detection: {e}")
        
        db.session.commit()
        print(f"   ✓ Backup created: backend/users_backup.db")
    
    print("\n✓ Reverse migration (backup) completed!")
    print("=" * 60)

if __name__ == '__main__':
    
    print("\nMigration Tool Options:")
    print("1. SQLite → MongoDB (migrate production data)")
    print("2. MongoDB → SQLite (create backup)")
    print("0. Exit")
    
    choice = input("\nSelect option (0-2): ").strip()
    
    if choice == '1':
        confirm = input("\nThis will migrate all data to MongoDB. Continue? (yes/no): ").strip().lower()
        if confirm == 'yes':
            migrate_to_mongodb()
        else:
            print("Migration cancelled")
    
    elif choice == '2':
        confirm = input("\nThis will create a SQLite backup from MongoDB. Continue? (yes/no): ").strip().lower()
        if confirm == 'yes':
            reverse_migration()
        else:
            print("Reverse migration cancelled")
    
    else:
        print("Exiting...")
