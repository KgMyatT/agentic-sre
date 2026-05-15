import json
import os

#from integrations.slack import send_slack_alert
#from integrations.github import create_issue
# Relative import - add this at the top
#import sys
#from pathlib import Path
#sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.slack import send_slack_alert
from integrations.github import create_issue


def load_incidents():
    if not os.path.exists("analysis.json"):
        print("❌ analysis.json not found")
        return []
    return json.load(open("analysis.json"))


def decide_action(incident):
    root = incident.get("root_cause", "").lower()

    if "nullpointer" in root:
        return "restart_app"

    if "database" in root:
        return "restart_db"

    return "manual_check"


def execute_action(action):
    print(f"⚡ Action Plan: {action}")

    if action == "manual_check":
        print("⚠️ Requires human intervention")


def run():
    incidents = load_incidents()

    print("=== INCIDENT PIPELINE ===")

    for inc in incidents:
        send_slack_alert(inc)
        create_issue(inc)

        action = decide_action(inc)
        execute_action(action)


if __name__ == "__main__":
    run()