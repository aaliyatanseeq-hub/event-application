
import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

# Your Basic tier credentials
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

print("🔐 Testing Basic Tier Posting Access...")

try:
    # OAuth 1.1 for posting
    auth = tweepy.OAuth1UserHandler(
        API_KEY, API_SECRET,
        ACCESS_TOKEN, ACCESS_SECRET
    )
    api = tweepy.API(auth)
    
    # Test authentication
    user = api.verify_credentials()
    print(f"✅ Authenticated as: @{user.screen_name}")
    
    # Test posting a regular tweet
    test_tweet = api.update_status("🧪 Test tweet from Basic Tier API - please ignore!")
    print(f"✅ Tweet posted successfully! ID: {test_tweet.id}")
    
    # Test replying to your existing tweet
    existing_tweet_id = "1989579561244250138"  # Your tweet ID
    
    reply_tweet = api.update_status(
        status="🧪 Test REPLY from Basic Tier API - this should appear as a comment!", 
        in_reply_to_status_id=existing_tweet_id,
        auto_populate_reply_metadata=True
    )
    print(f"✅ Reply posted successfully! ID: {reply_tweet.id}")
    print(f"🔗 Reply URL: https://twitter.com/{user.screen_name}/status/{reply_tweet.id}")
    
    print("🎉 BASIC TIER POSTING & COMMENTING WORKS!")
    
except Exception as e:
    print(f"❌ Error: {e}")
