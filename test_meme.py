#!/usr/bin/env python3
"""
Test script for meme generation functionality
"""

import os
from dotenv import load_dotenv
import requests

def test_meme_generation():
    """Test meme generation with imgflip API"""
    
    # Load environment variables
    load_dotenv()
    
    username = os.getenv('IMGFLIP_USERNAME')
    password = os.getenv('IMGFLIP_PASSWORD')
    
    if not username or not password:
        print("❌ IMGFLIP_USERNAME and IMGFLIP_PASSWORD not found in .env file")
        print("   Please add them to enable meme generation")
        return False
    
    print(f"✅ Found imgflip credentials for user: {username}")
    
    try:
        # Test meme generation
        url = 'https://api.imgflip.com/caption_image'
        data = {
            'username': username,
            'password': password,
            'template_id': '181913649',  # Drake Hotline Bling
            'text0': 'Test meme',
            'text1': 'from MusicAI'
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print("✅ Meme generation successful!")
            print(f"   Meme URL: {result['data']['url']}")
            return True
        else:
            print(f"❌ Meme generation failed: {result.get('error_message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing meme generation: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Testing Meme Generation...\n")
    
    if test_meme_generation():
        print("\n🎉 Meme generation is working correctly!")
        print("   You can now use memes throughout the MusicAI app")
    else:
        print("\n⚠️  Meme generation needs to be configured")
        print("   Check your .env file and imgflip credentials")
