import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

print("🔐 Testing LOCAL Credentials...")

# Use the SAME code that works in Colab
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_SECRET') 
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

print(f"API Key: {API_KEY}")
print(f"Access Token: {ACCESS_TOKEN}")

try:
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    
    # Test posting
    response = client.create_tweet(text="🧪 Test from LOCAL environment")
    print("✅ LOCAL POSTING WORKS!")
    print("Tweet ID:", response.data['id'])
    
except Exception as e:
    print(f"❌ LOCAL ERROR: {e}")