#!/usr/bin/env python3
"""
Simple test script to verify the MusicAI app can start without critical errors
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import flask
        import requests
        import json
        import base64
        import ast
        import time
        import pprint
        import bs4
        import statistics
        import random
        import os
        from dotenv import load_dotenv
        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_env_file():
    """Test if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("⚠ .env file not found - app will use system environment variables")
        return True
    
    from dotenv import load_dotenv
    load_dotenv()
    required_vars = [
        'SPOTIFY_CLIENT_ID',
        'SPOTIFY_CLIENT_SECRET',
        'SPOTIFY_CALLBACK_URL',
        'GENIUS_API_KEY',  # Changed from OAuth to direct API key
        'WATSON_API_KEY',
        'WATSON_SERVICE_URL'
    ]
    
    optional_vars = [
        'IMGFLIP_USERNAME',
        'IMGFLIP_PASSWORD'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"⚠ Missing required environment variables: {', '.join(missing)}")
        print("  App may not function properly without these")
        return False
    else:
        print("✓ All required environment variables found")
    
    # Check optional variables
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print(f"ℹ Missing optional variables: {', '.join(missing_optional)}")
        print("  These enable additional features like meme generation")
    else:
        print("✓ All optional variables found")
    
    return True

def test_app_creation():
    """Test if the Flask app can be created without errors"""
    try:
        # Temporarily redirect stdout to suppress warnings
        import io
        import contextlib
        
        with contextlib.redirect_stdout(io.StringIO()):
            # Import the app module
            sys.path.insert(0, '.')
            from musicAI import application
            
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return False

def test_meme_functionality():
    """Test if meme generation is properly configured"""
    try:
        from musicAI import imgflip_username, imgflip_password
        
        if imgflip_username and imgflip_password:
            print("✓ Meme generation credentials found")
            return True
        else:
            print("ℹ Meme generation credentials not found (optional feature)")
            return True  # Not a failure, just informational
    except Exception as e:
        print(f"ℹ Meme functionality test skipped: {e}")
        return True  # Not a failure

def main():
    """Run all tests"""
    print("Testing MusicAI app...\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment Variables", test_env_file),
        ("App Creation", test_app_creation),
        ("Meme Functionality", test_meme_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The app should work correctly.")
        return 0
    else:
        print("⚠ Some tests failed. The app may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
