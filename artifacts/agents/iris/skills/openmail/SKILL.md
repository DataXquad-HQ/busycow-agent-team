---
name: openmail
description: >
  Query Leo's OpenMail inbox via REST API — read thread list, check inbound
  replies, read message bodies, mark threads as read. Iris uses this for
  pipeline status checks and outreach health monitoring. Does NOT send email
  (sending is Leo's domain via nurturing-leads skill).
triggers:
  - "check outreach replies"
  - "any email replies"
  - "openmail"
  - "Leo's inbox"
  - "outreach status"
  - "any email replies"
  - "nurturing email replies"
version: "1.0"
author: [Org]/Iris
---

# OpenMail — Read Access Skill (Iris)

## Scope

Iris uses this skill **read-only** — check reply counts, retrieve inbound messages, verify delivery status. Do **not** send emails via this skill; that belongs to Leo via `nurturing-leads`.

---

## Credentials & IDs

| Item | Value |
|---|---|
| API base URL | `https://api.openmail.sh/v1` |
| Leo's token | load from Leo's env (see Auth below) |
| Leo's inbox ID | `0527f34e-65ad-4a02-adbc-e7872a9a921e` |
| Leo's address | `leo-dx@openmail.sh` |

**Auth — load Leo's token at runtime:**

```python
import requests, json

def load_openmail_token():
    with open("{{HOME_DIR}}/.hermes/profiles/leo/.env") as f:
        for line in f:
            line = line.strip()
            if "OPENMAIL_API_KEY" in line and "=" in line:
                return line.split("=", 1)[1].strip()
    return None

OM_TOKEN = load_openmail_token()
OM_HEADERS = {"Authorization": f"Bearer {OM_TOKEN}"}
INBOX_ID = "0527f34e-65ad-4a02-adbc-e7872a9a921e"
BASE = "https://api.openmail.sh/v1"
```

---

## Core Endpoints

### List unread threads
```python
resp = requests.get(
    f"{BASE}/inboxes/{INBOX_ID}/threads?is_read=false",
    headers=OM_HEADERS
)
threads = resp.json().get("data", [])
```

### List ALL threads (with pagination)
```python
resp = requests.get(
    f"{BASE}/inboxes/{INBOX_ID}/threads?limit=50",
    headers=OM_HEADERS
)
data = resp.json()
threads = data.get("data", [])
# next_cursor = data.get("meta", {}).get("next_cursor")
```

### Get messages in a thread
```python
resp = requests.get(
    f"{BASE}/threads/{thread_id}/messages",
    headers=OM_HEADERS
)
messages = resp.json().get("data", [])
```

### Mark thread as read
```python
resp = requests.patch(
    f"{BASE}/threads/{thread_id}",
    headers=OM_HEADERS,
    json={"is_read": True}          # snake_case — camelCase is rejected
)
# Returns {"ok": true}
```

---

## Detecting Inbound Replies

A thread shows as unread when Leo **sent** it, not just when the contact replies. Always check `direction` on the latest message:

```python
def get_inbound_replies(threads):
    """Return threads where the most recent message is inbound (contact replied)."""
    inbound = []
    for thread in threads:
        resp = requests.get(
            f"{BASE}/threads/{thread['id']}/messages",
            headers=OM_HEADERS
        )
        messages = resp.json().get("data", [])
        if not messages:
            continue
        # Sort by createdAt, take latest
        messages.sort(key=lambda m: m.get("createdAt", ""))
        latest = messages[-1]
        if latest.get("direction") == "inbound":
            inbound.append({
                "thread_id": thread["id"],
                "sender_email": latest.get("from", {}).get("email"),
                "subject": thread.get("subject"),
                "body_preview": strip_quoted_reply(latest.get("bodyText", ""))
            })
    return inbound

def strip_quoted_reply(body: str) -> str:
    """Strip quoted original email (lines starting with >)."""
    lines = []
    for line in body.splitlines():
        if line.startswith(">"):
            break
        lines.append(line)
    return "\n".join(lines).strip()
```

---

## Common Patterns for Iris

### Outreach health check — count sent vs replied
```python
# Sent count: query CRM OutreachMessages with status=SENT
# Reply count: count Engagement records with type=EMAIL created by contacts
# (Don't parse OpenMail directly for this — CRM is the source of truth after Leo processes replies)
```

### Check if a specific contact replied
```python
# Preferred: query CRM Engagement for person
# Fallback: search threads by subject containing contact name or company
resp = requests.get(
    f"{BASE}/inboxes/{INBOX_ID}/threads?search=CompanyName",
    headers=OM_HEADERS
)
```

---

## Pitfalls

- **camelCase rejected** — `{"isRead": true}` returns 400. Use `{"is_read": true}`.
- **PUT on threads is 404** — only `PATCH /v1/threads/{id}` works for updates.
- **Unread ≠ inbound reply** — always check `direction` on latest message. Unread threads include threads Leo sent (direction: outbound).
- **Reading via API does NOT auto-mark as read** — must `PATCH` explicitly.
- **CRM is the source of truth** — after Leo's inbox monitor cron runs, reply data is in CRM Engagement records. Prefer querying CRM over parsing raw inbox for Iris-level checks.
- **Thread already processed** — if Leo's cron already ran, a replied thread may be `isRead: true`. Track by CRM Engagement records, not inbox read status.
- **Token is Leo's** — loaded from Leo's `.env`. Iris has read access via this credential, but should not mutate Leo's inbox state unless auditing reply processing.
