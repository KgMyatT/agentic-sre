import redis
import json

r = redis.Redis(host="54.165.17.84", port=6379)

logs = open("logs.txt").read()

event = {
    "service": "user-api",
    "logs": logs
}

r.lpush("incident_queue", json.dumps(event))

print("✅ Incident pushed to Redis")