---
name: openmail
description: >
  Send and receive email via Leo's OpenMail account — draft and send outreach,
  check inbox for inbound replies, manage thread state. Load this skill before
  any email send or inbox read operation.
triggers:
  - "send email"
  - "check inbox"
  - "any replies"
  - "openmail"
  - "outreach email"
  - "有沒有人回信"
  - "寄信"
  - "nurturing email"
  - "inbox monitor"
version: "1.0"
author: {{COMPANY_NAME}}/Leo
---

# OpenMail — Full Access Skill (Leo)

## Credentials & IDs

| Item | Value |
|---|---|
| API base URL | `https://api.openmail.sh/v1` |
| Leo's inbox ID | `{{OPENMAIL_INBOX_ID}}` |
| Leo's address | `{{AGENT_EMAIL}}` |
| Token env key | `OPENMAIL_API_KEY` |

**Load token at runtime — never hardcode:**

```python
import requests, json, uuid

def load_om_token():
    with open("~/.hermes/profiles/leo/.env") as f:
        for line in f:
            line = line.strip()
            if "OPENMAIL_API_KEY" in line and "=" in line:
                return line.split("=", 1)[1].strip()
    return None

OM_TOKEN = load_om_token()
OM_HEADERS = {"Authorization": f"Bearer {OM_TOKEN}", "Content-Type": "application/json"}
INBOX_ID = "{{OPENMAIL_INBOX_ID}}"
BASE = "https://api.openmail.sh/v1"
```

---

## Sending Email

### New outreach thread
```python
idempotency_key = str(uuid.uuid4())  # REQUIRED — omitting causes duplicate sends

resp = requests.post(
    f"{BASE}/messages",
    headers={**OM_HEADERS, "Idempotency-Key": idempotency_key},
    json={
        "from": "{{AGENT_EMAIL}}",
        "to": "prospect@company.com",
        "subject": "Subject line",
        "html": "<p>Email body in HTML</p>",
        # omit threadId for new thread
    }
)
result = resp.json()
# result contains: id, threadId, messageId
```

### Reply to existing thread
```python
resp = requests.post(
    f"{BASE}/messages",
    headers={**OM_HEADERS, "Idempotency-Key": str(uuid.uuid4())},
    json={
        "from": "{{AGENT_EMAIL}}",
        "to": "prospect@company.com",
        "subject": "Re: Subject line",
        "html": "<p>Reply body</p>",
        "threadId": "thread_xxx"       # include to reply in same thread
    }
)
```

**Rate limits:** 10 sends/min, 200 sends/day per inbox.

---

## Reading Inbox

### List unread threads
```python
resp = requests.get(
    f"{BASE}/inboxes/{INBOX_ID}/threads?is_read=false",
    headers=OM_HEADERS
)
threads = resp.json().get("data", [])
```

### List all threads (with limit)
```python
resp = requests.get(
    f"{BASE}/inboxes/{INBOX_ID}/threads?limit=50",
    headers=OM_HEADERS
)
threads = resp.json().get("data", [])
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
    json={"is_read": True}       # snake_case — camelCase rejected
)
# Returns {"ok": true}
```

---

## Detecting Inbound Replies

Unread ≠ inbound reply. An unread thread could be one Leo sent. Always check `direction` on the latest message:

```python
def get_inbound_replies(threads):
    inbound = []
    for thread in threads:
        resp = requests.get(f"{BASE}/threads/{thread['id']}/messages", headers=OM_HEADERS)
        messages = resp.json().get("data", [])
        if not messages:
            continue
        messages.sort(key=lambda m: m.get("createdAt", ""))
        latest = messages[-1]
        if latest.get("direction") == "inbound":
            inbound.append({
                "thread_id": thread["id"],
                "sender_email": latest.get("from", {}).get("email"),
                "subject": thread.get("subject"),
                "body": strip_quoted_reply(latest.get("bodyText", ""))
            })
    return inbound

def strip_quoted_reply(body: str) -> str:
    """Strip original quoted email — lines starting with >."""
    lines = []
    for line in body.splitlines():
        if line.startswith(">"):
            break
        lines.append(line)
    return "\n".join(lines).strip()
```

---

## After Send — CRM Write Pattern

After every successful send, always:
1. Update `OutreachMessage.status` → `SENT`, set `sentAt`
2. Update `Person.lastContactDate` → ISO now
3. Create `Engagement` record (type=EMAIL, status=COMPLETED) linked to Person + Company
4. Write Hindsight memory to `{{ORG_PREFIX}}-pipeline`

---

## Fallback Behavior

- **If `https://api.openmail.sh` is unreachable**: do not silently skip; surface the error: "OpenMail is unavailable — [send/inbox check] could not complete. Retrying next scheduled run (or retry manually)." For sends: leave OutreachMessage status as SCHEDULED so the next cron run can retry. Do not mark as SENT.
- **If a send returns a non-2xx status**: do NOT mark the OutreachMessage as SENT; log the HTTP status and response body to Backend Report; do not retry immediately (may be a duplicate or rate limit); leave for human review.
- **If `Idempotency-Key` is rejected (duplicate key within 24h)**: a prior send attempt may have succeeded — check CRM for an existing Engagement or OutreachMessage with `status: SENT` for this recipient before retrying with a new key. If found: the send succeeded; update CRM status accordingly.
- **If the inbox poll returns 0 unread threads but replies are expected**: `is_read=false` may have returned false negatives (threads read by prior API call). Fall back to listing all threads with `limit=50` and filtering by `direction: inbound` + absence of existing CRM Engagement.
- **If OPENMAIL_API_KEY is missing from `.env`**: surface immediately: "OPENMAIL_API_KEY not found — email operations are blocked. Check `.env` configuration."
- **If rate limit is hit** (10 sends/min, 200 sends/day): pause sends; log count to Backend Report; resume next run or next day. Do not drop the queue — pending SCHEDULED messages will be retried.

## Pitfalls

- **`Idempotency-Key` is required** on every send — OpenMail rejects duplicate keys for 24h. Use `str(uuid.uuid4())` each time.
- **`PATCH`, not `PUT`** for mark-as-read — `PUT /threads/{id}` returns 404. Use `PATCH /threads/{id}`.
- **camelCase rejected** — `{"isRead": true}` returns 400. Use `{"is_read": true}`.
- **Unread ≠ inbound** — always check `direction` on latest message. Unread threads include ones Leo sent.
- **Reading via API does NOT auto-mark as read** — must `PATCH` explicitly.
- **Thread already processed** — the inbox monitor cron runs daily. Track processed replies via CRM Engagement records, not inbox read state, to avoid double-logging.
- **HTML body required** — `html` field, not `text`. Plain text sends may fail or render poorly.
- **Body cleanup** — `bodyText` of inbound messages includes full quoted history. Strip lines starting with `>` to get just the reply content.
