# KEEP YOUR EXACT ORIGINAL CODE - IT'S WORKING
"""
OAUTH 2.0 TWITTER CLIENT - SIMPLIFIED
Uses OAuth 2.0 User Context with your existing credentials
"""

import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

class OAuthTwitterClient:
    def __init__(self):
        # Use OAuth 2.0 Access Token (we'll get this from the script)
        self.access_token = os.getenv('TWITTER_OAUTH2_ACCESS_TOKEN')
        self.base_url = "https://api.twitter.com/2"
        
    def is_configured(self) -> bool:
        """Check if OAuth 2.0 access token is available"""
        return self.access_token is not None
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get OAuth 2.0 User Context headers"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def post_tweet(self, text: str, reply_to_tweet_id: Optional[str] = None) -> Dict:
        """Post a tweet or reply"""
        try:
            if not self.is_configured():
                return {'success': False, 'error': 'OAuth 2.0 access token not configured'}
            
            url = f"{self.base_url}/tweets"
            payload = {'text': text}
            
            if reply_to_tweet_id:
                payload['reply'] = {'in_reply_to_tweet_id': reply_to_tweet_id}
            
            print(f"🐦 Posting tweet: {text[:50]}...")
            response = requests.post(
                url,
                headers=self._get_auth_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Tweet posted successfully: {result['data']['id']}")
                return {
                    'success': True,
                    'tweet_id': result['data']['id'],
                    'text': text
                }
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Tweet failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {error_msg}"
                }
                
        except Exception as e:
            print(f"❌ Tweet error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_info(self) -> Dict:
        """Get current user info to verify authentication"""
        try:
            if not self.is_configured():
                return {'success': False, 'error': 'OAuth 2.0 not configured'}
            
            url = f"{self.base_url}/users/me"
            response = requests.get(
                url,
                headers=self._get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'user': result['data']
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'response': response.text
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def quote_tweet(self, tweet_id: str, text: str) -> Dict:
        """Post a quote tweet (retweet with comment)"""
        try:
            if not self.is_configured():
                return {'success': False, 'error': 'OAuth 2.0 access token not configured'}
            
            url = f"{self.base_url}/tweets"
            payload = {
                'text': text,
                'quote_tweet_id': tweet_id
            }
            
            print(f"🔁 Posting quote tweet: {text[:50]}...")
            response = requests.post(
                url,
                headers=self._get_auth_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Quote tweet posted successfully: {result['data']['id']}")
                return {
                    'success': True,
                    'tweet_id': result['data']['id'],
                    'text': text,
                    'quoted_tweet_id': tweet_id
                }
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Quote tweet failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {error_msg}"
                }
                
        except Exception as e:
            print(f"❌ Quote tweet error: {e}")
            return {'success': False, 'error': str(e)}
    
    def refresh_access_token(self) -> bool:
        """Refresh the OAuth 2.0 access token"""
        # This method would need to be implemented based on your OAuth 2.0 setup
        # For now, return False as tokens don't typically expire
        return False