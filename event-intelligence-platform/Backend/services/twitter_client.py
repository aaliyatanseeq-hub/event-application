"""
HIGHLY ENGINEERED TWITTER CLIENT - FINAL
Combines OAuth 1.1 (working) + v2 API + Rate Limiting + Basic Tier compatibility
"""

import os
import tweepy
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TwitterClient:
    def __init__(self):
        self.consumer_key = os.getenv('TWITTER_API_KEY')
        self.consumer_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Dual clients for maximum compatibility
        self.client_v2 = None  # v2 API for posting (PROVEN WORKING)
        self.api_v1 = None     # v1.1 API for search
        self.rate_limit_remaining = 60
        self.last_reset_time = datetime.now()
        self.total_searches_used = 0
        self.setup_clients()

    def setup_clients(self):
        """Setup both v2 and v1.1 clients"""
        try:
            # v2 Client for posting (YOUR WORKING CODE)
            self.client_v2 = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                bearer_token=self.bearer_token,
                wait_on_rate_limit=False
            )
            
            # v1.1 API for search (backup)
            if all([self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret]):
                auth = tweepy.OAuth1UserHandler(
                    self.consumer_key, self.consumer_secret,
                    self.access_token, self.access_token_secret
                )
                self.api_v1 = tweepy.API(auth)
            
            print("✅ Twitter clients: v2 (posting) + v1.1 (search)")
            
            # Test authentication
            user = self.client_v2.get_me()
            print(f"✅ Authenticated as: @{user.data.username}")
            
            return True
        except Exception as e:
            print(f"❌ Twitter setup failed: {e}")
            return False

    def _check_rate_limit(self):
        """Manual rate limit checking"""
        now = datetime.now()
        time_since_reset = (now - self.last_reset_time).total_seconds()
        
        # Reset every 15 minutes
        if time_since_reset >= 900:
            self.rate_limit_remaining = 60
            self.last_reset_time = now
            self.total_searches_used = 0
        
        if self.rate_limit_remaining <= 0:
            return False
        return True

    def search_recent_tweets_safe(self, query: str, max_results: int = 10, **kwargs):
        """Optimized search with manual rate limiting"""
        try:
            if not self._check_rate_limit():
                print("🚫 Search blocked: Rate limit reached")
                return None
            
            print(f"🔍 Searching: '{query}'")
            print(f"📊 Quota: {self.rate_limit_remaining}/60 searches left")
            
            response = self.client_v2.search_recent_tweets(
                query=query,
                max_results=min(max_results, 15),
                **kwargs
            )
            
            self.rate_limit_remaining -= 1
            self.total_searches_used += 1
            
            if response and response.data:
                print(f"✅ Found {len(response.data)} tweets")
            else:
                print("❌ No tweets found")
            
            return response
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return None

    def post_tweet(self, text: str, reply_to_tweet_id: str = None):
        """POSTING THAT WORKS - Using v2 API (YOUR WORKING CODE)"""
        try:
            print(f"🐦 Posting: {text[:50]}...")
            
            if reply_to_tweet_id:
                # Post as reply using v2 API
                response = self.client_v2.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=reply_to_tweet_id
                )
                print(f"✅ Reply posted to {reply_to_tweet_id}")
            else:
                # Post as new tweet
                response = self.client_v2.create_tweet(text=text)
                print(f"✅ Tweet posted")
            
            print(f"📝 Tweet ID: {response.data['id']}")
            return {'success': True, 'tweet_id': response.data['id']}
            
        except Exception as e:
            print(f"❌ Post failed: {e}")
            return {'success': False, 'error': str(e)}

    def retweet_tweet(self, tweet_id: str):
        """Retweet using v2 API"""
        try:
            user = self.client_v2.get_me()
            user_id = user.data.id
            
            print(f"🔄 Retweeting: {tweet_id}")
            response = self.client_v2.retweet(user_id, tweet_id)
            print(f"✅ Retweeted: {tweet_id}")
            return True
            
        except Exception as e:
            print(f"❌ Retweet failed: {e}")
            return False

    def like_tweet(self, tweet_id: str):
        """Like using v2 API"""
        try:
            user = self.client_v2.get_me()
            user_id = user.data.id
            
            print(f"❤️  Liking: {tweet_id}")
            response = self.client_v2.like(user_id, tweet_id)
            print(f"✅ Liked: {tweet_id}")
            return True
            
        except Exception as e:
            print(f"❌ Like failed: {e}")
            return False

    def is_operational(self):
        return self.client_v2 is not None

    def get_usage_stats(self):
        now = datetime.now()
        time_since_reset = (now - self.last_reset_time).total_seconds()
        reset_in = max(0, 900 - time_since_reset)
        
        return {
            "searches_remaining": self.rate_limit_remaining,
            "searches_used": self.total_searches_used,
            "searches_limit": 60,
            "reset_in_minutes": int(reset_in / 60),
            "posting_limit": "100 posts/24hr"
        }