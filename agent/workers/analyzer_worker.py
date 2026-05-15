import redis
import json
import os
from agent.llm import call_llm


r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

while True:
    _, data = r.brpop("raw_logs_queue")

    event = json.loads(data)

    logs = event["logs"]

    prompt = f"""
    Analyze production logs:

    {logs}

    Return JSON:
    {{
      "root_cause": "",
      "severity": "",
      "affected_service": ""
    }}
    """

    result = call_llm(prompt)

    print("=== ANALYZER ===")
    print(result)

    r.lpush("analysis_queue", result)