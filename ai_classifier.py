import requests
import json
from config import LLM_API_KEY, LLM_URL, MODEL_NAME

def ask_ai_for_category(app_name, title, existing_categories):
    cats_str = ", ".join([str(c) for c in existing_categories])

    prompt = f"""
    Analyze this desktop activity:
    App: "{app_name}"
    Window Title: "{title}"

    Task: Choose the most fitting category from this list: [{cats_str}].
    If none fit perfectly, suggest a new short category name.

    Return ONLY a JSON object: {{"category": "Name"}}
    """

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        r = requests.post(LLM_URL, headers=headers, json=payload)
        res = r.json()
        content = json.loads(res['choices'][0]['message']['content'])
        return content.get("category")
    except Exception as e:
        print(f"AI Query Error: {e}")
        return None
