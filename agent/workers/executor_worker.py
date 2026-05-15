import redis
import json

from integrations.slack import send_slack_alert
from integrations.github import create_issue

import os

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

while True:
    _, data = r.brpop("action_queue")

    payload = json.loads(data)

    incident = payload["incident"]
    plan = payload["plan"]

    print("=== EXECUTOR ===")
    print(plan)

    send_slack_alert(incident)

    create_issue(incident)

    print("✅ Incident handled")