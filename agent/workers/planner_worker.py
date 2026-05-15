import redis
import json
from agent.llm import call_llm

import os


r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

while True:
    _, data = r.brpop("analysis_queue")

    incident = json.loads(data)

    prompt = f"""
    Incident:

    {json.dumps(incident)}

    Create remediation plan.
    """

    result = call_llm(prompt)

    action = {
        "incident": incident,
        "plan": result
    }

    print("=== PLANNER ===")
    print(action)

    r.lpush("action_queue", json.dumps(action))