import redis
import json
from llm import call_llm

r = redis.Redis(host="54.165.17.84", port=6379)

while True:
    _, data = r.brpop("incident_queue")

    incident = json.loads(data)

    logs = incident["logs"]

    prompt = f"""
    Analyze logs:

    {logs}
    """

    result = call_llm(prompt)

    print(result)