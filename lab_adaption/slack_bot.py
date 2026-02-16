import os
import requests

token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
user_id = "U08PHN5K0P3"  # my user ID

if not token:
    raise SystemExit("Missing SLACK_BOT_TOKEN environment variable.")

def slack_post(url: str, payload: dict):
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=10,
    )
    data = resp.json()
    if not data.get("ok", False):
        raise RuntimeError(f"Slack API error: {data}")
    return data

# open (or get) the DM channel
data = slack_post(
    "https://slack.com/api/conversations.open",
    {"users": user_id},
)
dm_channel = data["channel"]["id"]

# send message
data = slack_post(
    "https://slack.com/api/chat.postMessage",
    {"channel": dm_channel, "text": "Hello from Python!"},
)

print(data)
