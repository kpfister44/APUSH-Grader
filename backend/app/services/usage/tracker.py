"""
Usage tracking service for basic safeguards and daily limits
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from app.services.logging.structured_logger import get_logger


@dataclass
class DailyUsage:
    """Track daily usage for an IP address"""
    date: str
    essay_count: int = 0
    total_word_count: int = 0
    essay_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    first_request_time: Optional[float] = None
    last_request_time: Optional[float] = None
    
    def add_essay(self, essay_type: str, word_count: int):
        """Add an essay to the daily usage"""
        current_time = time.time()
        
        if self.first_request_time is None:
            self.first_request_time = current_time
        self.last_request_time = current_time
        
        self.essay_count += 1
        self.total_word_count += word_count
        self.essay_types[essay_type] += 1


class UsageTracker:
    """Simple in-memory usage tracker for hobby project scope"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        # Dictionary to store usage by IP and date
        # Format: {ip_address: {date_string: DailyUsage}}
        self._usage_data: Dict[str, Dict[str, DailyUsage]] = defaultdict(dict)
        
        # Configuration
        self.daily_essay_limit = 100  # Very generous for teachers
        self.daily_word_limit = 50000  # Prevent extremely long essays
        self.cost_alert_threshold = 50  # Alert if someone hits 50 essays in a day
        
    def can_process_essay(self, client_ip: str, word_count: int) -> Tuple[bool, Optional[str]]:
        """
        Check if an essay can be processed based on daily limits
        
        Returns:
            (can_process, reason_if_not)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        daily_usage = self._get_daily_usage(client_ip, today)
        
        # Check daily essay limit
        if daily_usage.essay_count >= self.daily_essay_limit:
            reason = f"Daily essay limit reached ({self.daily_essay_limit} essays per day)"
            self.logger.warning(
                "Daily essay limit exceeded",
                client_ip=client_ip,
                current_count=daily_usage.essay_count,
                limit=self.daily_essay_limit
            )
            return False, reason
            
        # Check daily word count limit (prevent extremely long essays)
        if daily_usage.total_word_count + word_count > self.daily_word_limit:
            reason = f"Daily word limit reached ({self.daily_word_limit} words per day)"
            self.logger.warning(
                "Daily word limit exceeded",
                client_ip=client_ip,
                current_words=daily_usage.total_word_count,
                new_words=word_count,
                limit=self.daily_word_limit
            )
            return False, reason
            
        # Check for cost alert threshold
        if daily_usage.essay_count >= self.cost_alert_threshold:
            self.logger.warning(
                "High usage detected - cost alert",
                client_ip=client_ip,
                essay_count=daily_usage.essay_count,
                threshold=self.cost_alert_threshold,
                total_words=daily_usage.total_word_count
            )
            
        return True, None
    
    def record_essay_processed(self, client_ip: str, essay_type: str, word_count: int):
        """Record that an essay was successfully processed"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_usage = self._get_daily_usage(client_ip, today)
        
        daily_usage.add_essay(essay_type, word_count)
        
        # Log the usage for monitoring
        self.logger.info(
            "Essay processed - usage updated",
            client_ip=client_ip,
            essay_type=essay_type,
            word_count=word_count,
            daily_essay_count=daily_usage.essay_count,
            daily_word_count=daily_usage.total_word_count,
            event_type="usage_tracked"
        )
        
        # Log daily summary if this is a significant milestone
        if daily_usage.essay_count in [10, 25, 50, 75, 90]:
            self._log_daily_summary(client_ip, daily_usage)
    
    def get_daily_stats(self, client_ip: str, date: Optional[str] = None) -> Optional[DailyUsage]:
        """Get daily usage stats for an IP"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self._usage_data.get(client_ip, {}).get(date)
    
    def get_usage_summary(self) -> Dict[str, any]:
        """Get overall usage summary for monitoring"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        total_essays_today = 0
        total_words_today = 0
        active_ips_today = 0
        essay_type_counts = defaultdict(int)
        
        for ip, dates in self._usage_data.items():
            if today in dates:
                usage = dates[today]
                if usage.essay_count > 0:
                    active_ips_today += 1
                    total_essays_today += usage.essay_count
                    total_words_today += usage.total_word_count
                    
                    for essay_type, count in usage.essay_types.items():
                        essay_type_counts[essay_type] += count
        
        return {
            "date": today,
            "total_essays": total_essays_today,
            "total_words": total_words_today,
            "active_ips": active_ips_today,
            "essay_types": dict(essay_type_counts),
            "avg_words_per_essay": round(total_words_today / total_essays_today, 1) if total_essays_today > 0 else 0
        }
    
    def cleanup_old_data(self, days_to_keep: int = 7):
        """Clean up old usage data to prevent memory growth"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime("%Y-%m-%d")
        
        cleaned_count = 0
        for ip in list(self._usage_data.keys()):
            dates_to_remove = [date for date in self._usage_data[ip].keys() if date < cutoff_date]
            for date in dates_to_remove:
                del self._usage_data[ip][date]
                cleaned_count += 1
            
            # Remove IP entries with no remaining data
            if not self._usage_data[ip]:
                del self._usage_data[ip]
        
        if cleaned_count > 0:
            self.logger.info(
                "Usage data cleanup completed",
                entries_removed=cleaned_count,
                cutoff_date=cutoff_date,
                event_type="data_cleanup"
            )
    
    def _get_daily_usage(self, client_ip: str, date: str) -> DailyUsage:
        """Get or create daily usage record for IP and date"""
        if date not in self._usage_data[client_ip]:
            self._usage_data[client_ip][date] = DailyUsage(date=date)
        return self._usage_data[client_ip][date]
    
    def _log_daily_summary(self, client_ip: str, usage: DailyUsage):
        """Log daily summary at milestones"""
        self.logger.info(
            "Daily usage milestone reached",
            client_ip=client_ip,
            essay_count=usage.essay_count,
            total_words=usage.total_word_count,
            essay_types=dict(usage.essay_types),
            session_duration_hours=round((usage.last_request_time - usage.first_request_time) / 3600, 1) if usage.first_request_time else 0,
            event_type="usage_milestone"
        )


# Global usage tracker instance
_usage_tracker: Optional[UsageTracker] = None


def get_usage_tracker() -> UsageTracker:
    """Get the global usage tracker instance"""
    global _usage_tracker
    if _usage_tracker is None:
        _usage_tracker = UsageTracker()
    return _usage_tracker