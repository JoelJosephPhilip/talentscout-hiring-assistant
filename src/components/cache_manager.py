import functools
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import threading


class ResponseCache:
    """
    Thread-safe cache for LLM responses.
    Helps reduce API calls for similar queries.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize response cache.
        
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time-to-live in seconds (default: 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def _hash_key(self, prompt: str, context: Dict = None) -> str:
        """
        Generate cache key from prompt and context.
        
        Args:
            prompt: The input prompt
            context: Optional context dictionary
        
        Returns:
            MD5 hash string
        """
        key_str = f"{prompt}::{str(context or {})}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, context: Dict = None) -> Optional[str]:
        """
        Get cached response if available and not expired.
        
        Args:
            prompt: The input prompt
            context: Optional context dictionary
        
        Returns:
            Cached response or None
        """
        key = self._hash_key(prompt, context)
        
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if datetime.now() - entry["timestamp"] > self.ttl:
                    del self.cache[key]
                    self.misses += 1
                    return None
                
                self.hits += 1
                return entry["response"]
            
            self.misses += 1
            return None
    
    def set(self, prompt: str, response: str, context: Dict = None):
        """
        Cache a response.
        
        Args:
            prompt: The input prompt
            response: The response to cache
            context: Optional context dictionary
        """
        key = self._hash_key(prompt, context)
        
        with self._lock:
            # Remove oldest if at capacity
            if len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[key] = {
                "response": response,
                "timestamp": datetime.now()
            }
    
    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with hit rate, size, etc.
        """
        with self._lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(hit_rate, 2)
            }
    
    def cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            expired_keys = []
            now = datetime.now()
            
            for key, entry in self.cache.items():
                if now - entry["timestamp"] > self.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]


class PrecomputedResponses:
    """
    Precomputed common responses to avoid LLM calls.
    """
    
    ERROR_MESSAGES = {
        "invalid_email": "That doesn't look like a valid email address. Please use a format like 'name@example.com'.",
        "invalid_phone": "Please provide a valid phone number (e.g., +1-555-123-4567).",
        "invalid_experience": "Please enter a number between 0 and 50 for years of experience.",
        "invalid_name": "Names should only contain letters, spaces, and hyphens. Could you please re-enter?",
        "invalid_input": "I didn't quite understand that. Could you please try again?",
        "empty_input": "Please provide a response to continue.",
        "tech_stack_empty": "Please list at least one technology you're proficient in."
    }
    
    CONFIRMATIONS = {
        "info_collected": "Thank you! I've recorded your information.",
        "tech_confirmed": "Great! Let's proceed to the technical assessment.",
        "answer_received": "Thanks for your answer!",
        "session_complete": "Screening complete! Thank you for your time."
    }
    
    ENCOURAGEMENTS = {
        "junior": [
            "You're doing great! Take your time.",
            "Good effort! Let's continue.",
            "Nice work so far!",
            "Keep going, you're on the right track!"
        ],
        "mid": [
            "Good answer!",
            "Thanks for that detailed response.",
            "Great, let's move to the next question.",
            "Appreciate the explanation."
        ],
        "senior": [
            "Excellent explanation.",
            "Thank you for the detailed response.",
            "That was comprehensive.",
            "Well articulated."
        ]
    }
    
    @staticmethod
    def get_error_message(error_type: str) -> str:
        """Get precomputed error message"""
        return PrecomputedResponses.ERROR_MESSAGES.get(error_type, "Please try again.")
    
    @staticmethod
    def get_confirmation(confirmation_type: str) -> str:
        """Get precomputed confirmation message"""
        return PrecomputedResponses.CONFIRMATIONS.get(confirmation_type, "Got it!")
    
    @staticmethod
    def get_encouragement(level: str = "mid") -> str:
        """Get appropriate encouragement phrase"""
        import random
        phrases = PrecomputedResponses.ENCOURAGEMENTS.get(level, PrecomputedResponses.ENCOURAGEMENTS["mid"])
        return random.choice(phrases)


# Global cache instance
_global_cache = ResponseCache()


def cached_llm_call(func):
    """
    Decorator for caching LLM calls.
    
    Usage:
        @cached_llm_call
        def generate_response(prompt, context=None):
            ...
    """
    @functools.wraps(func)
    def wrapper(prompt, context=None, *args, **kwargs):
        # Check cache first
        cached = _global_cache.get(prompt, context)
        if cached is not None:
            return cached
        
        # Make actual call
        result = func(prompt, context, *args, **kwargs)
        
        # Cache result
        _global_cache.set(prompt, result, context)
        
        return result
    
    return wrapper


def get_global_cache() -> ResponseCache:
    """Get the global cache instance"""
    return _global_cache
