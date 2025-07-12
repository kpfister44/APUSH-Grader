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
    
    def get_usage_summary(self) -> Dict[str, any]:
        """Get simple usage summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        used = self._daily_counts[today]
        
        return {
            "essays_processed_today": used,
            "daily_limit": self.daily_limit,
            "remaining": max(0, self.daily_limit - used)
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