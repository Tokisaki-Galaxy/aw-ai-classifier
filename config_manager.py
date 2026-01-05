import json
import re
import os
from config import SETTINGS_PATH

def update_aw_settings(category_name, app_name):
    if not os.path.exists(SETTINGS_PATH):
        print(f"错误：找不到配置文件 {SETTINGS_PATH}")
        return False

    # 处理 AI 返回的层级字符串，例如 "Work > Tools"
    if isinstance(category_name, str):
        if " > " in category_name:
            category_list = [c.strip() for c in category_name.split(" > ")]
        else:
            category_list = [category_name.strip()]
    elif isinstance(category_name, list):
        category_list = category_name
    else:
        category_list = [str(category_name)]

    # 使用最后一个元素作为匹配标识
    leaf_category = category_list[-1]

    # 使用 utf-8-sig 读取
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8-sig') as f:
            settings = json.load(f)
    except Exception:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)

    # --- 全局强制大小写不敏感 ---
    for cls in settings.get('classes', []):
        if cls.get('rule', {}).get('type') == 'regex':
            cls['rule']['ignore_case'] = True

    # 清理 app_name，剥离最后一个点及其后缀
    if '.' in app_name:
        clean_app_name = app_name.rsplit('.', 1)[0]
    else:
        clean_app_name = app_name
    app_pattern = re.escape(clean_app_name)

    # 1. 查找目标分类
    target_class = None
    
    # 优先进行全路径匹配
    for cls in settings['classes']:
        if cls['name'] == category_list:
            target_class = cls
            break
            
    # 如果全路径没匹配到，尝试叶子节点匹配
    if not target_class:
        for cls in settings['classes']:
            if isinstance(cls['name'], list) and len(cls['name']) > 0:
                if cls['name'][-1] == leaf_category:
                    target_class = cls
                    break

    if target_class:
        # 2. 如果找到了现有分类，更新正则
        current_regex = target_class['rule'].get('regex', '')
        existing_patterns = current_regex.split('|') if current_regex else []
        if app_pattern.lower() not in [p.lower() for p in existing_patterns]:
            if current_regex:
                clean_regex = current_regex.strip('|')
                target_class['rule']['regex'] = f"{clean_regex}|{app_pattern}"
            else:
                target_class['rule']['regex'] = app_pattern
        
        # 确保规则类型正确
        target_class['rule']['type'] = 'regex'
        target_class['rule']['ignore_case'] = True
    else:
        # 3. 如果是新分类，创建它
        existing_ids = [c['id'] for c in settings.get('classes', [])]
        new_id = max(existing_ids) + 1 if existing_ids else 0
        
        new_class = {
            "id": new_id,
            "name": category_list, 
            "rule": {
                "type": "regex", 
                "regex": app_pattern, 
                "ignore_case": True 
            },
            "data": {"color": "#999999"}
        }
        settings['classes'].append(new_class)

    # 保存修改：在 Windows 上必须使用 ensure_ascii=True，否则 aw-server 会报 UnicodeDecodeError
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=True)
        return True
    except Exception as e:
        print(f"写入配置文件失败: {e}")
        return False
