# OpenMail API — Confirmed Behaviours (2026-06-16)

## Inbox ID
Leo's inbox: `{{OPENMAIL_INBOX_ID}}`
Address: `{{AGENT_EMAIL}}`

## Mark Thread as Read
- **Correct:** `PATCH /v1/threads/{thread_id}` with body `{"is_read": true}` → returns `{"ok": true}`
- **Wrong (400):** `{"isRead": true}` — camelCase is rejected
- **Wrong (404):** `PUT /v1/threads/{thread_id}` — PUT is not a valid verb for this endpoint
- **Wrong (404):** `PUT /v1/inboxes/{inbox_id}/threads/{thread_id}` — nested route doesn't exist

## Filtering Inbound Replies
- `GET /v1/inboxes/{id}/threads?is_read=false` returns unread threads
- A thread can be unread because Leo SENT (not received). Always check `direction` on the latest message.
- Sort messages by `createdAt` and check `messages[-1]["direction"] == "inbound"` before processing.
- Reading thread messages via API does NOT auto-mark as read — must PATCH explicitly.

## Thread Already Read
- If Leo's API call to fetch thread messages was made earlier in the session, the thread may already be `isRead: True` even though it was never intentionally marked.
- The production inbox monitor should track processed thread IDs in a separate store (or check Engagement records) to avoid missing threads that were read but never logged.

## Reply Body Cleanup
- `bodyText` contains the full email including quoted original. Strip lines starting with `>` to get clean reply.
- Stop at the first `>` line — everything after is the quoted original.
- The `On [date] ... wrote:` line appears AFTER the `>` block in some clients — trim trailing whitespace after stripping.
