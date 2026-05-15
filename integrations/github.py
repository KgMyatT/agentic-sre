import requests

GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
REPO = "your-username/agentic-sre"

def create_issue(incident):
    url = f"https://api.github.com/repos/{REPO}/issues"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    data = {
        "title": f"[{incident.get('severity')}] {incident.get('root_cause')}",
        "body": f"""
Service: {incident.get("affected_service")}

Root Cause:
{incident.get("root_cause")}

Explanation:
{incident.get("explanation")}
"""
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("✅ GitHub issue created")
    else:
        print("❌ GitHub issue failed:", response.text)