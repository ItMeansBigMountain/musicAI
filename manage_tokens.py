#!/usr/bin/env python3
"""
Token Management Script for MusicAI
Helps users view and manage their stored authentication tokens
"""

import os
import json
import time
from datetime import datetime

TOKEN_FILE = 'user_tokens.json'

def view_tokens():
    """Display all stored tokens"""
    if not os.path.exists(TOKEN_FILE):
        print("❌ No tokens found. Run the app first to authenticate.")
        return
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
        
        print(f"🔑 Found {len(tokens)} user(s) with stored tokens:\n")
        
        for user_id, token_data in tokens.items():
            print(f"👤 User: {user_id}")
            print(f"   Spotify Token: {'✅ Valid' if token_data.get('spotify_token') else '❌ Missing'}")
            print(f"   Refresh Token: {'✅ Available' if token_data.get('spotify_refresh_token') else '❌ Missing'}")
            
            expires_at = token_data.get('spotify_expires_at')
            if expires_at:
                expiry_time = datetime.fromtimestamp(expires_at)
                now = datetime.now()
                if expiry_time > now:
                    time_left = expiry_time - now
                    print(f"   Expires: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')} (in {time_left})")
                else:
                    print(f"   Expires: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')} (EXPIRED)")
            else:
                print("   Expires: Unknown")
            
            print(f"   Genius Token: {'✅ Available' if token_data.get('genius_token') else '❌ Missing'}")
            print(f"   Last Updated: {datetime.fromtimestamp(token_data.get('last_updated', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
    except Exception as e:
        print(f"❌ Error reading tokens: {e}")

def clear_tokens():
    """Clear all stored tokens"""
    if not os.path.exists(TOKEN_FILE):
        print("❌ No tokens found to clear.")
        return
    
    try:
        os.remove(TOKEN_FILE)
        print("✅ All stored tokens have been cleared.")
        print("   You will need to re-authenticate with Spotify next time you use the app.")
    except Exception as e:
        print(f"❌ Error clearing tokens: {e}")

def clear_user_tokens(user_id):
    """Clear tokens for a specific user"""
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ No tokens found for user {user_id}.")
        return
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
        
        if user_id in tokens:
            del tokens[user_id]
            
            with open(TOKEN_FILE, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"✅ Tokens cleared for user {user_id}.")
        else:
            print(f"❌ No tokens found for user {user_id}.")
            
    except Exception as e:
        print(f"❌ Error clearing user tokens: {e}")

def main():
    """Main menu"""
    while True:
        print("\n🔐 MusicAI Token Manager")
        print("1. View all tokens")
        print("2. Clear all tokens")
        print("3. Clear specific user tokens")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            view_tokens()
        elif choice == '2':
            confirm = input("⚠️  This will clear ALL stored tokens. Are you sure? (y/N): ").strip().lower()
            if confirm == 'y':
                clear_tokens()
            else:
                print("Operation cancelled.")
        elif choice == '3':
            user_id = input("Enter user ID to clear tokens for: ").strip()
            if user_id:
                clear_user_tokens(user_id)
            else:
                print("❌ Invalid user ID.")
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
