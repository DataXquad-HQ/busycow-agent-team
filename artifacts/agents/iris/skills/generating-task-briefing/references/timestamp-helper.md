# Timestamp Helper — Taiwan Time (UTC+8)

## Python
```python
from datetime import datetime, timezone, timedelta
tz = timezone(timedelta(hours=8))
today = datetime.now(tz).date()

TODAY_START = int(datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=tz).timestamp() * 1000)
TODAY_END   = int(datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=tz).timestamp() * 1000)
WEEK_END    = TODAY_START + (7 * 24 * 60 * 60 * 1000)

# ms → date string
def ms_to_date(ms):
    return datetime.fromtimestamp(ms / 1000, tz=tz).strftime('%m/%d')
```

## pytz fallback (if pytz not available)
```python
from datetime import datetime, timezone, timedelta
tz = timezone(timedelta(hours=8))
now_tw = datetime.now(tz)
day = now_tw.strftime('%A')  # Monday / Tuesday / ...
```
