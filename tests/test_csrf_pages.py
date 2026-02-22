"""
Automated test to verify csrf_token is available on pages
"""
import sys
sys.path.insert(0, 'd:\\python')

import os
os.chdir('d:\\python')

from app_simple import app
from flask import session

# Test URLs that should have csrf_token
test_urls = [
    ('/login', None, 'Login page'),
    ('/register', None, 'Register page'),
]

print("\n" + "="*60)
print("CSRF TOKEN AVAILABILITY TEST")
print("="*60)

with app.test_client() as client:
    app.config['WTF_CSRF_ENABLED'] = True
    
    for url, method, description in test_urls:
        print(f"\nTesting {description}...")
        response = client.get(url, follow_redirects=True)
        
        if response.status_code == 200:
            # Check if csrf_token is in response
            if 'csrf_token' in response.get_data(as_text=True):
                print(f"  ✓ Page rendered with csrf_token")
                print(f"  ✓ Status: {response.status_code}")
            else:
                print(f"  ✗ csrf_token NOT found in response")
                print(f"  Status: {response.status_code}")
        else:
            print(f"  ✗ Page returned status: {response.status_code}")

# Test authenticated pages
print("\n" + "-"*60)
print("Testing authenticated pages (requires login)...")
print("-"*60)

from flask_login import login_user
from app_simple import User

with app.test_client() as client:
    # Create test session
    with client:
        # Login with test user
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'Admin@123'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            print(f"\nLogin successful")
            
            # Test pengaturan page
            print("\nTesting Pengaturan page...")
            response = client.get('/pengaturan')
            
            if response.status_code == 200:
                if 'csrf_token' in response.get_data(as_text=True):
                    print(f"  ✓ Pengaturan page rendered with csrf_token")
                else:
                    print(f"  ✗ Pengaturan csrf_token NOT found")
            else:
                print(f"  ✗ Pengaturan page status: {response.status_code}")
            
            # Test produk page
            print("\nTesting Produk page...")
            response = client.get('/produk')
            
            if response.status_code == 200:
                print(f"  ✓ Produk page rendered successfully")
            else:
                print(f"  ✗ Produk page status: {response.status_code}")
        else:
            print(f"Login failed with status: {response.status_code}")

print("\n" + "="*60)
print("TEST COMPLETED")
print("="*60 + "\n")
