from llm import call_llm
import os
import json

def filter_logs(raw_logs):
    lines = raw_logs.split("\n")
    return "\n".join([l for l in lines if "ERROR" in l or "WARN" in l])


def load_prompt(logs):
    with open("prompts/analyzer.txt", "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{logs}", logs)


def deduplicate(incidents):
    seen = set()
    unique = []

    for inc in incidents:
        key = (inc.get("root_cause"), inc.get("affected_service"))

        if key not in seen:
            seen.add(key)
            unique.append(inc)

    return unique


def safe_parse_json(text):
    try:
        return json.loads(text)
    except:
        # محاولة إصلاح JSON مقطوع (quick fix)
        try:
            fixed = text.strip()

            if not fixed.endswith("]"):
                fixed += "]"

            return json.loads(fixed)
        except:
            return None


def analyze():
    if not os.path.exists("logs.txt"):
        print("❌ logs.txt not found")
        return

    raw_logs = open("logs.txt", encoding="utf-8", errors="ignore").read()
    logs = filter_logs(raw_logs)

    if not logs:
        print("⚠️ No ERROR/WARN logs")
        return

    prompt = load_prompt(logs)

    result = call_llm(prompt)

    print("=== RAW AI OUTPUT ===")
    print(result)

    parsed = safe_parse_json(result)

    if parsed is None:
        print("⚠️ JSON parse failed, fallback")
        incidents = [{
            "root_cause": "unknown",
            "severity": "MEDIUM",
            "affected_service": "unknown",
            "explanation": result
        }]
    else:
        if isinstance(parsed, list):
            incidents = parsed
        else:
            incidents = [parsed]

    incidents = deduplicate(incidents)

    print("=== FINAL INCIDENTS ===")
    for i, inc in enumerate(incidents, 1):
        print(f"\nIncident {i}: {inc}")

    with open("analysis.json", "w") as f:
        json.dump(incidents, f, indent=2)


if __name__ == "__main__":
    analyze()