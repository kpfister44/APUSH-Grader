"""
Simple usage limiting for hobby project serving 2-12 teachers
"""

import time
from datetime import datetime
from typing import Dict, Tuple
from collections import defaultdict


class SimpleUsageTracker:
    """Basic daily usage counter for hobby project"""

    def __init__(self):
        # Simple in-memory counter: {date: count}
        self._daily_counts: Dict[str, int] = defaultdict(int)
        self._last_cleanup = datetime.now().date()

        # Cache metrics tracking (for prompt caching cost monitoring)
        self._cache_metrics = {
            "total_input_tokens": 0,
            "total_cache_creation_tokens": 0,
            "total_cache_read_tokens": 0,
            "total_output_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # Conservative limits for hobby project
        self.daily_limit = 50  # 50 essays per day total (not per IP)
        self.max_words = 10000  # Reject extremely long essays
    
    def can_process_essay(self, client_ip: str, word_count: int) -> Tuple[bool, str]:
        """Check if essay can be processed"""
        self._cleanup_old_data()
        
        today = datetime.now().strftime("%Y-%m-%d")
        current_count = self._daily_counts[today]
        
        # Check word count limit
        if word_count > self.max_words:
            return False, f"Essay too long ({word_count} words). Maximum {self.max_words} words allowed."
        
        # Check daily limit
        if current_count >= self.daily_limit:
            return False, f"Daily limit of {self.daily_limit} essays reached. Please try again tomorrow."
        
        return True, ""
    
    def record_essay_processed(self, client_ip: str, essay_type: str, word_count: int):
        """Record that an essay was processed"""
        today = datetime.now().strftime("%Y-%m-%d")
        self._daily_counts[today] += 1

    def record_cache_metrics(self, metrics: Dict[str, int]):
        """
        Record prompt caching metrics for cost monitoring.

        Prompt caching saves costs by reusing document images across grading requests.
        Cache hits indicate successful reuse, reducing API costs by ~90%.

        Args:
            metrics: Dict with keys: input_tokens, cache_creation_tokens,
                     cache_read_tokens, output_tokens
        """
        self._cache_metrics["total_input_tokens"] += metrics.get("input_tokens", 0)
        self._cache_metrics["total_cache_creation_tokens"] += metrics.get("cache_creation_tokens", 0)
        self._cache_metrics["total_cache_read_tokens"] += metrics.get("cache_read_tokens", 0)
        self._cache_metrics["total_output_tokens"] += metrics.get("output_tokens", 0)

        # Track cache hits/misses
        if metrics.get("cache_read_tokens", 0) > 0:
            self._cache_metrics["cache_hits"] += 1
        elif metrics.get("cache_creation_tokens", 0) > 0:
            self._cache_metrics["cache_misses"] += 1

    def get_usage_summary(self) -> Dict[str, any]:
        """Get simple usage summary with cache metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        used = self._daily_counts[today]

        # Calculate cache efficiency
        total_cache_requests = self._cache_metrics["cache_hits"] + self._cache_metrics["cache_misses"]
        cache_hit_rate = (
            (self._cache_metrics["cache_hits"] / total_cache_requests * 100)
            if total_cache_requests > 0
            else 0
        )

        return {
            "essays_processed_today": used,
            "daily_limit": self.daily_limit,
            "remaining": max(0, self.daily_limit - used),
            "cache_metrics": {
                "total_input_tokens": self._cache_metrics["total_input_tokens"],
                "total_cache_creation_tokens": self._cache_metrics["total_cache_creation_tokens"],
                "total_cache_read_tokens": self._cache_metrics["total_cache_read_tokens"],
                "total_output_tokens": self._cache_metrics["total_output_tokens"],
                "cache_hits": self._cache_metrics["cache_hits"],
                "cache_misses": self._cache_metrics["cache_misses"],
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
            }
        }
    
    def _cleanup_old_data(self):
        """Remove data older than 2 days"""
        current_date = datetime.now().date()
        
        # Only cleanup once per day
        if current_date <= self._last_cleanup:
            return
        
        cutoff_date = current_date.strftime("%Y-%m-%d")
        
        # Keep only today's data
        keys_to_remove = [
            date_str for date_str in self._daily_counts.keys() 
            if date_str < cutoff_date
        ]
        
        for key in keys_to_remove:
            del self._daily_counts[key]
        
        self._last_cleanup = current_date


# Global instance
_usage_tracker = SimpleUsageTracker()

def get_simple_usage_tracker() -> SimpleUsageTracker:
    """Get the global usage tracker instance"""
    return _usage_tracker