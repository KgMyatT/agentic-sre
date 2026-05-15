from llm import call_llm

def plan():
    data = open("analysis.txt").read()

    prompt = f"""
    Based on this analysis:
    {data}

    Suggest safe remediation steps.
    """

    result = call_llm(prompt)

    with open("plan.txt", "w") as f:
        f.write(result)

    print("=== REMEDIATION PLAN ===")
    print(result)

if __name__ == "__main__":
    plan()
prompt = f"""
You are an SRE.

Based on this incident:
{analysis}

Provide:

1. Immediate Fix
2. Short-term Fix
3. Long-term Prevention

Be practical and safe.
"""    