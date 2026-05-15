import requests
import json

SLACK_WEBHOOK = "YOUR_SLACK_WEBHOOK_URL"

def send_slack_alert(incident):
    message = {
        "text": f"""
🚨 Incident Detected

Service: {incident.get("affected_service")}
Severity: {incident.get("severity")}
Root Cause: {incident.get("root_cause")}

Explanation: {incident.get("explanation")}
"""
    }

    try:
        requests.post(SLACK_WEBHOOK, data=json.dumps(message))
        print("✅ Slack alert sent")
    except Exception as e:
        print("❌ Slack failed:", e)