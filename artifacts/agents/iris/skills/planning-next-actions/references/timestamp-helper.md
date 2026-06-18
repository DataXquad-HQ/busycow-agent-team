# Timestamp Helper — Taiwan Time (UTC+8)

Lark date fields require millisecond timestamps.

## Python
```python
from datetime import datetime, timezone, timedelta
tz = timezone(timedelta(hours=8))
today = datetime.now(tz).date()

def to_ms(year, month, day):
    return int(datetime(year, month, day, 0, 0, 0, tzinfo=tz).timestamp() * 1000)

TODAY_START = int(datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=tz).timestamp() * 1000)
TODAY_END   = int(datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=tz).timestamp() * 1000)
WEEK_END    = TODAY_START + (7 * 24 * 60 * 60 * 1000)
```
