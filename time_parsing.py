from datetime import datetime

FORMATS = [
    '%Y-%m-%d-%H:%M:%S',
]

def parse_time(time_str: str) -> datetime:
    for format in FORMATS:
        try:
            return datetime.strptime(time_str, format)
        except ValueError:
            pass
    raise ValueError("Invalid time format")

__all__ = ['parse_time']