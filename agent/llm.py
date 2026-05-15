from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # fast + free
            messages=[
                {"role": "system", "content": "You are an expert SRE engineer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )

        return response.choices[0].message.content

    except Exception as e:
        print("⚠️ Groq failed, fallback:", e)

        return """
Root Cause: Unknown
Severity: Medium
Suggested Fix:
- Restart service
- Check logs manually
"""