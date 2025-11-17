# KEEP YOUR EXACT ORIGINAL CODE - IT'S WORKING
"""
SIMPLE OAUTH 2.0 TOKEN GETTER
Run this to get your OAuth 2.0 User Access Token
"""

import os
import requests
import base64
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

def get_oauth_token():
    # Your credentials from Developer Portal
    CLIENT_ID = os.getenv('TWITTER_CLIENT_ID') or "YOUR_CLIENT_ID_HERE"
    CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET') or "YOUR_CLIENT_SECRET_HERE"
    
    print("🔐 Twitter OAuth 2.0 Token Generator")
    print("=" * 50)
    
    # Step 1: Generate Authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': 'https://localhost',  # Use any redirect URI
        'scope': 'tweet.read tweet.write users.read',
        'state': 'state123',
        'code_challenge': 'challenge',
        'code_challenge_method': 'plain'
    }
    
    auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(auth_params)}"
    
    print("📋 Step 1: Open this URL in your browser:")
    print(auth_url)
    print("\n🔑 Step 2: Authorize the app and copy the WHOLE redirect URL")
    print("   It will look like: https://localhost/?code=XXXXXXXX&state=state123")
    print("\n📝 Step 3: Paste the redirect URL here:")
    
    redirect_url = input("Paste the redirect URL: ").strip()
    
    # Extract code from redirect URL
    if 'code=' in redirect_url:
        code = redirect_url.split('code=')[1].split('&')[0]
        print(f"✅ Extracted authorization code: {code}")
        
        # Step 4: Exchange code for token
        print("🔄 Exchanging code for access token...")
        
        # Encode client credentials
        credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        
        token_data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'redirect_uri': 'https://localhost',
            'code_verifier': 'challenge'
        }
        
        response = requests.post(
            'https://api.twitter.com/2/oauth2/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {credentials}'
            },
            data=token_data
        )
        
        if response.status_code == 200:
            tokens = response.json()
            print("🎉 SUCCESS! Tokens received:")
            print(f"\n🔑 ACCESS TOKEN: {tokens['access_token']}")
            if 'refresh_token' in tokens:
                print(f"🔄 REFRESH TOKEN: {tokens['refresh_token']}")
            
            print(f"\n📝 Add this to your .env file:")
            print(f"TWITTER_OAUTH2_ACCESS_TOKEN={tokens['access_token']}")
            if 'refresh_token' in tokens:
                print(f"TWITTER_OAUTH2_REFRESH_TOKEN={tokens['refresh_token']}")
                
            return tokens
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    else:
        print("❌ No authorization code found in the URL")
        return None

if __name__ == "__main__":
    tokens = get_oauth_token()
    if tokens:
        print("\n✅ Setup complete! Update your .env file and restart the server.")
    else:
        print("\n❌ Failed to get tokens. Please try again.")