import requests
import json
import re
from datetime import datetime, timedelta
from config import AW_API_BASE, SETTINGS_PATH

def get_window_bucket_id():
    try:
        resp = requests.get(f"{AW_API_BASE}/buckets/")
        buckets = resp.json()
        for bucket_id, info in buckets.items():
            if info.get("type") == "currentwindow":
                return bucket_id
        return None
    except:
        return None

def get_uncategorized_activities(limit_hours=2):
    bucket_id = get_window_bucket_id()
    if not bucket_id:
        return {}

    # 1. 加载现有分类规则
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        settings = json.load(f)
    
    classes = []
    for cls in settings.get("classes", []):
        if cls.get("rule", {}).get("type") == "regex":
            classes.append({
                "name": cls["name"],
                "regex": cls["rule"]["regex"],
                "ignore_case": cls["rule"].get("ignore_case", False)
            })
    print(f"Loaded {len(classes)} classification rules.")
    print(f"{classes}")

    # 2. 设置时间范围 (UTC)
    time_end = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    time_start = (datetime.utcnow() - timedelta(hours=limit_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 3. 只获取原始事件，不让服务器分类（服务器分类不准）
    query = f"RETURN = query_bucket('{bucket_id}');"

    try:
        resp = requests.post(f"{AW_API_BASE}/query/", json={
            "query": [query],
            "timeperiods": [f"{time_start}/{time_end}"]
        })
        
        if resp.status_code != 200:
            return {}

        all_events = resp.json()[0]
        unique_apps = {}

        # 4. 在 Python 本地进行模拟匹配
        for event in all_events:
            data = event.get("data", {})
            app = data.get("app", "")
            title = data.get("title", "")
            
            # 拼接用于匹配的文本（模拟 AW 行为：匹配 app 或 title）
            content_to_match = f"{app} {title}"
            
            is_categorized = False
            for rule in classes:
                flags = re.IGNORECASE if rule["ignore_case"] else 0
                # 只要 app 或 title 命中任何一个现有正则，就标记为“已分类”
                if re.search(rule["regex"], content_to_match, flags):
                    is_categorized = True
                    break
            
            # 如果所有规则都没命中
            if not is_categorized:
                if app and app.lower() != "unknown" and app not in unique_apps:
                    unique_apps[app] = title
        
        return unique_apps

    except Exception as e:
        print(f"检测脚本运行异常: {e}")
        return {}

if __name__ == "__main__":
    results = get_uncategorized_activities(limit_hours=24)
    print(f"--- 正在检测过去 24 小时的未分类活动 (Python 本地匹配模式) ---")
    if results:
        for app, title in results.items():
            print(f"[待分类] App: {app} | 标题: {title}")
    else:
        print("所有活动已匹配现有规则，没有发现需要 AI 处理的活动。")
