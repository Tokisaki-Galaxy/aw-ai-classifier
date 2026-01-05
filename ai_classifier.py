import requests
import json
from config import LLM_API_KEY, LLM_URL, MODEL_NAME

def batch_ask_ai_for_categories(activities, existing_categories):
    """
    批量请求 AI 对多个应用进行分类
    activities: dict {app_name: title}
    """
    # 将分类列表转为层级字符串，例如 "Work > Programming"
    cats_str = ", ".join([" > ".join(c) if isinstance(c, list) else str(c) for c in existing_categories])

    prompt = f"""
    Analyze these desktop activities (App name and Window Title):
    {json.dumps(activities, ensure_ascii=False, indent=2)}

    Task: For each App, choose the most fitting category from this list: [{cats_str}] and suggest a color.
    
    Rules:
    1. ALWAYS prefer an existing category from the list above if it fits.
    2. If you choose an existing category, return its FULL PATH exactly as shown (e.g., "Media > Games").
    3. If none of the existing categories fit perfectly, suggest a new short and descriptive category name.
    4. You can suggest hierarchical categories using " > " as a separator (e.g., "Work > Tools").
    5. Suggest a hex color code (e.g., "#FF5733") for the category. If it's an existing category, you can still suggest a color or use a standard one.
    6. DO NOT use generic names like "Unknown Software", "Other", or "Uncategorized".
    7. Suggested category names should be clean and human-readable. DO NOT include file extensions like ".exe" in the category name.
    8. If you are absolutely unsure and cannot suggest a meaningful category, DO NOT include that App in the output.

    Return ONLY a JSON object where keys are the App names and values are objects containing "category" and "color".
    Example: {{"App1": {{"category": "Media > Games", "color": "#FF5733"}}, "App2": {{"category": "Work > Programming", "color": "#33FF57"}}}}
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
        if r.status_code != 200:
            print(f"API Error (Status {r.status_code}): {r.text}")
            return None
            
        res = r.json()
        if 'choices' not in res:
            print(f"Unexpected API Response: {res}")
            return None
            
        content_str = res['choices'][0]['message']['content']
        # 尝试解析 JSON，如果 AI 返回了包含 markdown 代码块的内容，进行清理
        if "```json" in content_str:
            content_str = content_str.split("```json")[1].split("```")[0].strip()
        elif "```" in content_str:
            content_str = content_str.split("```")[1].split("```")[0].strip()
            
        content = json.loads(content_str)
        return content  # 返回 {app: category} 字典
    except Exception as e:
        print(f"AI Batch Query Error: {e}")
        return None
