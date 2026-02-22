"""Create test user for testing"""
import sys
import os
sys.path.insert(0, 'd:\\python')
os.chdir('d:\\python')

from app_simple import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            nama='Administrator',
            password=generate_password_hash('Admin@123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created (username: admin, password: Admin@123)")
    else:
        print("✓ Admin user already exists")
    
    # Check if cashier user exists
    kasir = User.query.filter_by(username='kasir').first()
    if not kasir:
        kasir = User(
            username='kasir',
            nama='Kasir 1',
            password=generate_password_hash('Kasir@123'),
            role='kasir'
        )
        db.session.add(kasir)
        db.session.commit()
        print("✓ Kasir user created (username: kasir, password: Kasir@123)")
    else:
        print("✓ Kasir user already exists")
