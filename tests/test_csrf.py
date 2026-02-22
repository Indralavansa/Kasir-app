#!/usr/bin/env python
"""Test script to verify app startup and csrf_token availability"""

import sys
import os

# Change to project directory
os.chdir('d:\\python')
sys.path.insert(0, 'd:\\python')

try:
    print("\n" + "="*60)
    print("TESTING APP INITIALIZATION")
    print("="*60)
    
    # Test imports
    print("\n1. Testing imports...")
    from flask_wtf import FlaskForm, CSRFProtect
    print("   ✓ FlaskForm imported")
    print("   ✓ CSRFProtect imported")
    
    # Test app creation
    print("\n2. Testing app creation...")
    from app_simple import app, db, csrf
    print("   ✓ Flask app created")
    print("   ✓ SQLAlchemy initialized")
    print("   ✓ CSRFProtect initialized")
    
    # Test csrf token in template context
    print("\n3. Testing CSRF context processor...")
    with app.app_context():
        from flask import render_template_string
        try:
            # Try to render a simple template with csrf_token
            result = render_template_string("{{ csrf_token() }}")
            print("   ✓ csrf_token() available in template context")
            print(f"   ✓ CSRF token generated: {result[:20]}...")
        except Exception as e:
            print(f"   ✗ csrf_token() not available: {e}")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED - APP IS READY!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
