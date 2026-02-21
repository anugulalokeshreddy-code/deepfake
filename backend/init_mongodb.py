import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from mongo_models import MongoUser, MongoDetection
import mongoengine

def init_mongodb():
    """Initialize MongoDB connection and create indexes"""
    
    # Connect to MongoDB
    try:
        mongoengine.connect(
            db=Config.MONGODB_DB,
            host=Config.MONGODB_URI,
            alias='default'
        )
        print("✓ Connected to MongoDB successfully")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print(f"  Make sure MongoDB is running at: {Config.MONGODB_URI}")
        return False
    
    # Create indexes
    try:
        MongoUser.ensure_indexes()
        MongoDetection.ensure_indexes()
        print("✓ Database indexes created")
    except Exception as e:
        print(f"✗ Index creation failed: {e}")
        return False
    
    # Create demo user
    try:
        existing_user = MongoUser.objects(username='demo').first()
        if not existing_user:
            demo_user = MongoUser(
                username='demo',
                email='demo@example.com'
            )
            demo_user.set_password('Demo@12345')
            demo_user.save()
            print("✓ Demo user created: username=demo, password=Demo@12345")
        else:
            print("✓ Demo user already exists")
    except Exception as e:
        print(f"✗ Demo user creation failed: {e}")
        return False
    
    print("\n✓ MongoDB initialization complete!")
    return True

if __name__ == '__main__':
    init_mongodb()
