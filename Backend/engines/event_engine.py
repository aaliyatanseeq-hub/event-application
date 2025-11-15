"""
UNIQUE TOP N Event Discovery Engine
No duplicates - Only unique top events
"""

import requests
import os
import re
from datetime import datetime
from typing import List, Dict, Set
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ResearchEvent:
    event_name: str
    exact_date: str
    exact_venue: str
    location: str
    category: str
    confidence_score: float
    source_url: str
    posted_by: str
    hype_score: float

class SmartEventEngine:
    def __init__(self):
        self.serp_api_key = os.getenv('SERP_API_KEY')
        print(f"🔧 Event Engine: {'✅ SerpAPI Ready' if self.serp_api_key else '❌ No Key'}")

    def discover_events(self, location: str, start_date: str, end_date: str, categories: List[str], max_results: int) -> List[ResearchEvent]:
        """UNIQUE TOP N: Return exactly N unique hyped events"""
        try:
            print(f"🔥 Finding TOP {max_results} UNIQUE hyped events in {location}")
            
            if not self.serp_api_key:
                print("❌ SerpAPI key missing")
                return []

            # Get unique events from multiple queries
            unique_events = self._fetch_unique_events(location, categories, max_results * 5)
            
            # Score events by hype
            scored_events = self._score_events_by_hype(unique_events)
            
            # Return top N exactly
            top_events = scored_events[:max_results]
            
            print(f"✅ TOP {len(top_events)} UNIQUE HYPED EVENTS (requested: {max_results})")
            for i, event in enumerate(top_events[:5], 1):
                print(f"   {i}. {event.event_name} (Hype: {event.hype_score:.2f})")
            
            return top_events

        except Exception as e:
            print(f"❌ Event discovery failed: {e}")
            return []

    def _fetch_unique_events(self, location: str, categories: List[str], target_count: int) -> List[ResearchEvent]:
        """Fetch unique events with aggressive deduplication"""
        all_events = []
        seen_events: Set[str] = set()
        
        popular_queries = [
            f"popular events {location}",
            f"trending events {location}", 
            f"best events {location}",
            f"top events {location}",
            f"must-see events {location}",
            f"major events {location}",
            f"featured events {location}",
            f"upcoming events {location}",
            f"this weekend {location}",
            f"events {location} 2024"
        ]
        
        for category in categories:
            popular_queries.extend([
                f"popular {category} events {location}",
                f"best {category} {location}",
                f"top {category} events {location}"
            ])
        
        for query in popular_queries:
            if len(all_events) >= target_count:
                break
                
            events = self._fetch_serpapi_events(query, target_count - len(all_events))
            
            # Add only unique events
            for event in events:
                event_key = self._create_event_key(event)
                if event_key not in seen_events:
                    seen_events.add(event_key)
                    all_events.append(event)
        
        print(f"📊 Unique events collected: {len(all_events)}")
        return all_events

    def _create_event_key(self, event: ResearchEvent) -> str:
        """Create unique key for event deduplication"""
        # Normalize event name for comparison
        normalized_name = re.sub(r'[^\w\s]', '', event.event_name.lower())
        normalized_name = re.sub(r'\s+', ' ', normalized_name).strip()
        
        # Use name + date for uniqueness
        date_part = event.exact_date.split()[0] if event.exact_date else "nodate"
        
        return f"{normalized_name}_{date_part}"

    def _fetch_serpapi_events(self, query: str, limit: int) -> List[ResearchEvent]:
        """Fetch events from SerpAPI"""
        try:
            params = {
                "q": query,
                "engine": "google_events",
                "api_key": self.serp_api_key,
                "hl": "en",
                "gl": "us"
            }
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                events = []
                
                if 'events_results' in data and data['events_results']:
                    for event_data in data['events_results'][:limit * 2]:  # Get more to filter
                        event = self._parse_event_data(event_data)
                        if event and self._is_valid_event(event):
                            events.append(event)
                    
                    print(f"   ✅ Found {len(events)} valid events for '{query}'")
                
                return events
            else:
                print(f"   ❌ SerpAPI HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ SerpAPI fetch failed: {e}")
            return []

    def _is_valid_event(self, event: ResearchEvent) -> bool:
        """Validate event before including"""
        # Check for minimum requirements
        if not event.event_name or len(event.event_name.strip()) < 3:
            return False
        
        # Check if event name is too generic
        generic_names = ['event', 'events', 'unknown', 'unknown event']
        if event.event_name.lower() in generic_names:
            return False
            
        return True

    def _parse_event_data(self, event_data: Dict) -> ResearchEvent:
        """Parse event data"""
        try:
            title = self._safe_extract(event_data.get('title'))
            date = self._safe_extract(event_data.get('date', 'Date not specified'))
            address = self._safe_extract(event_data.get('address', ''))
            link = self._safe_extract(event_data.get('link', ''))
            
            if not title or title == 'Unknown Event':
                return None
            
            clean_name = self._clean_event_name(title)
            
            event = ResearchEvent(
                event_name=clean_name,
                exact_date=date,
                exact_venue=self._extract_venue(address),
                location=self._extract_location(address),
                category=self._classify_event_type(clean_name),
                confidence_score=0.8,
                source_url=link,
                posted_by="Popular Events",
                hype_score=0.5
            )
            
            return event
            
        except Exception as e:
            print(f"⚠️ Event parse error: {e}")
            return None

    def _score_events_by_hype(self, events: List[ResearchEvent]) -> List[ResearchEvent]:
        """Score events based on hype"""
        scored_events = []
        
        for event in events:
            hype_score = self._calculate_hype_score(event)
            event.hype_score = hype_score
            scored_events.append(event)
        
        # Sort by hype score (descending)
        scored_events.sort(key=lambda x: x.hype_score, reverse=True)
        return scored_events

    def _calculate_hype_score(self, event: ResearchEvent) -> float:
        """Calculate hype score"""
        score = 0.0
        
        # Event name indicators
        name_lower = event.event_name.lower()
        hype_keywords = [
            'festival', 'concert', 'championship', 'tournament', 'expo',
            'summit', 'conference', 'awards', 'gala', 'premiere'
        ]
        
        for keyword in hype_keywords:
            if keyword in name_lower:
                score += 0.1
        
        # Venue prestige
        venue_lower = event.exact_venue.lower()
        prestigious_venues = ['stadium', 'arena', 'center', 'garden', 'hall']
        for venue in prestigious_venues:
            if venue in venue_lower:
                score += 0.15
        
        # Category weight
        category_weights = {
            'music': 0.3, 'festival': 0.4, 'sports': 0.35,
            'conference': 0.2, 'arts': 0.25, 'food': 0.15
        }
        score += category_weights.get(event.category, 0.1)
        
        return min(1.0, score)

    def _clean_event_name(self, title: str) -> str:
        """Clean event name"""
        if not title:
            return "Event"
        
        patterns_to_remove = [
            r'\s+at\s+.+$', r'\s+in\s+.+$', r'\s*-\s*.+$',
            r'\s*\|.*$', r'\s*@\s*.+$'
        ]
        
        clean_name = title
        for pattern in patterns_to_remove:
            clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
        
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        return clean_name if clean_name else title

    def _safe_extract(self, field):
        if isinstance(field, list):
            return field[0] if field else ""
        return str(field) if field else ""

    def _extract_venue(self, address: str) -> str:
        if not address:
            return "Various Venues"
        venue = address.split(',')[0].strip()
        return venue if len(venue) > 3 else "Various Venues"

    def _extract_location(self, address: str) -> str:
        if not address:
            return "Location not specified"
        parts = address.split(',')
        return parts[-1].strip() if len(parts) > 1 else address

    def _classify_event_type(self, text: str) -> str:
        if not text:
            return 'other'
        text_lower = text.lower()
        categories = {
            'music': ['concert', 'music', 'dj', 'band', 'live music'],
            'sports': ['sports', 'game', 'match', 'tournament'],
            'arts': ['art', 'theater', 'exhibition', 'gallery'],
            'food': ['food', 'drink', 'culinary', 'wine'],
            'festival': ['festival', 'cultural'],
            'conference': ['conference', 'summit', 'workshop'],
        }
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return 'other'