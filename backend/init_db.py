# Database initialization script

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User

def init_db():
    """Initialize database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Create sample user (optional)
        existing_user = User.query.filter_by(username='demo').first()
        if not existing_user:
            demo_user = User(
                username='demo',
                email='demo@example.com'
            )
            demo_user.set_password('Demo@12345')
            db.session.add(demo_user)
            db.session.commit()
            print("✓ Demo user created: username=demo, password=Demo@12345")
        
        print("\n✓ Database initialization complete!")
        print(f"✓ Database file: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    init_db()
