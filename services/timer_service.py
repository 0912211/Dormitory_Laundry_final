from datetime import datetime
from services.clock import now_local

def remaining_seconds(end_time: datetime, current_time: datetime | None = None) -> int:
    current_time = current_time or now_local()
    return max(0, int((end_time - current_time).total_seconds()))

def format_remaining(seconds: int) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"
