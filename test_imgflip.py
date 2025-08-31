#!/usr/bin/env python3
"""
Test script to verify imgflip credentials work
"""

import os
import requests
from dotenv import load_dotenv

def test_imgflip_login():
    """Test imgflip login with credentials from .env"""
    
    # Load environment variables
    load_dotenv()
    
    username = os.getenv('IMGFLIP_USERNAME')
    password = os.getenv('IMGFLIP_PASSWORD')
    
    print(f"Testing imgflip credentials:")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'None'}")
    print()
    
    if not username or not password:
        print("❌ IMGFLIP_USERNAME or IMGFLIP_PASSWORD not found in .env file")
        return False
    
    try:
        # Test with a simple meme template (Drake meme)
        url = 'https://api.imgflip.com/caption_image'
        data = {
            'username': username,
            'password': password,
            'template_id': '181913649',  # Drake meme template
            'text0': 'Test',
            'text1': 'Success'
        }
        
        print("🔄 Testing meme generation...")
        response = requests.post(url, data=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ SUCCESS! Credentials are working!")
            print(f"Generated meme URL: {result['data']['url']}")
            return True
        else:
            error_msg = result.get('error_message', 'Unknown error')
            print(f"❌ FAILED: {error_msg}")
            
            if 'Invalid username/password' in error_msg:
                print("\n🔧 SOLUTION:")
                print("1. Go to https://imgflip.com")
                print("2. Create a NEW account (not log in with email)")
                print("3. Use the username you created (not your email)")
                print("4. Use the password you set during registration")
                print("5. Update your .env file with the new credentials")
            
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_imgflip_login()
