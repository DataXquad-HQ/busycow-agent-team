# OpenMail API Patterns

Base URL: `https://api.openmail.sh`
Auth: `Authorization: Bearer <token>`
Leo's mailbox: `{{AGENT_EMAIL}}`
Token: stored in env as `OPENMAIL_TOKEN`

---

## Key Endpoints

### Send Email
```bash
curl -X POST https://api.openmail.sh/v1/messages \
  -H "Authorization: Bearer $OPENMAIL_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "from": "{{AGENT_EMAIL}}",
    "to": "prospect@company.com",
    "subject": "Subject line",
    "html": "<p>Body</p>",
    "threadId": "thread_xxx"  # omit for new thread, include to reply
  }'
```
⚠️ `Idempotency-Key` header is REQUIRED on every send. Use a UUID. OpenMail rejects duplicate keys for 24h.

### List Unread Threads
```bash
curl "https://api.openmail.sh/v1/inboxes/{inbox_id}/threads?is_read=false" \
  -H "Authorization: Bearer $OPENMAIL_TOKEN"
```

### Get Thread Messages (full history)
```bash
curl "https://api.openmail.sh/v1/threads/{thread_id}/messages" \
  -H "Authorization: Bearer $OPENMAIL_TOKEN"
```

### Mark Thread Read
```bash
curl -X PUT "https://api.openmail.sh/v1/threads/{thread_id}" \
  -H "Authorization: Bearer $OPENMAIL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_read": true}'
```

### List Inboxes
```bash
curl "https://api.openmail.sh/v1/inboxes" \
  -H "Authorization: Bearer $OPENMAIL_TOKEN"
```

---

## Threading Model

- Emails auto-grouped into threads by subject + message headers
- To reply in an existing thread: include `threadId` in send payload
- Thread history: use `GET /v1/threads/{id}/messages` — returns messages in order

## Rate Limits

- 10 sends/min per inbox
- 200 sends/day per inbox
- 100 inbox creations/day (account level)

## Inbound Detection (Prospect → Lead conversion)

A reply from a Prospect to `{{AGENT_EMAIL}}` signals intent.
Options for detection:
1. **Webhook** — real-time, HMAC-SHA256 signed, recommended for production
2. **Polling** — `GET /v1/inboxes/{id}/threads?is_read=false` on a schedule
