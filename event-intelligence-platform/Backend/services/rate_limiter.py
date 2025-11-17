"""
ADVANCED RATE LIMITER - FINAL
Preserves quotas across all system phases
"""

from datetime import datetime, timedelta
import threading

class TwitterRateLimiter:
    def __init__(self):
        self.rate_limits = {}
        self.lock = threading.Lock()
        self.setup_advanced_limits()

    def setup_advanced_limits(self):
        """Setup comprehensive rate limits"""
        # Basic tier limits
        self.rate_limits['search_recent'] = {
            'limit': 60,
            'remaining': 60,
            'reset_time': None,
            'window_minutes': 15
        }
        self.rate_limits['post_tweet'] = {
            'limit': 100,
            'remaining': 100, 
            'reset_time': None,
            'window_minutes': 1440  # 24 hours
        }
        self.rate_limits['retweet'] = {
            'limit': 5,
            'remaining': 5,
            'reset_time': None,
            'window_minutes': 15
        }

    def check_rate_limit(self, endpoint: str) -> bool:
        """Check if request is allowed"""
        with self.lock:
            if endpoint not in self.rate_limits:
                return True

            limit_info = self.rate_limits[endpoint]
            now = datetime.now()

            # Initialize reset time if not set
            if not limit_info['reset_time']:
                limit_info['reset_time'] = now + timedelta(minutes=limit_info['window_minutes'])

            # Reset if time window passed
            if now > limit_info['reset_time']:
                limit_info['remaining'] = limit_info['limit']
                limit_info['reset_time'] = now + timedelta(minutes=limit_info['window_minutes'])

            if limit_info['remaining'] > 0:
                limit_info['remaining'] -= 1
                return True
            else:
                print(f"🚫 {endpoint} limit: {limit_info['remaining']}/{limit_info['limit']}")
                return False

    def get_limits_status(self):
        """Get comprehensive status"""
        status = {}
        for endpoint, limit_info in self.rate_limits.items():
            reset_in = 0
            if limit_info['reset_time']:
                reset_in = max(0, (limit_info['reset_time'] - datetime.now()).total_seconds() / 60)
            
            status[endpoint] = {
                'remaining': limit_info['remaining'],
                'limit': limit_info['limit'],
                'reset_in_minutes': int(reset_in),
                'window': f"{limit_info['window_minutes']}min"
            }
        return status