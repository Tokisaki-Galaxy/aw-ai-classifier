import json
import re
import os
from config import SETTINGS_PATH

def update_aw_settings(category_name, app_name):
    if not os.path.exists(SETTINGS_PATH):
        print(f"错误：找不到配置文件 {SETTINGS_PATH}")
        return False

    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    # --- 全局强制大小写不敏感 ---
    # 遍历所有分类，只要是 regex 类型的规则，全部设为 ignore_case: True
    for cls in settings.get('classes', []):
        if cls.get('rule', {}).get('type') == 'regex':
            cls['rule']['ignore_case'] = True
    # ------------------------------------

    updated = True # 因为我们做了全局强制转换，这里默认为 True，确保修改被保存
    app_pattern = re.escape(app_name)

    # 1. 查找目标分类
    target_class = None
    for cls in settings['classes']:
        if category_name in cls['name']:
            target_class = cls
            break

    if target_class:
        # 2. 如果找到了现有分类，更新正则
        current_regex = target_class['rule'].get('regex', '')
        # 精准比对，避免重复添加
        existing_patterns = current_regex.split('|') if current_regex else []
        if app_pattern.lower() not in [p.lower() for p in existing_patterns]:
            if current_regex:
                target_class['rule']['regex'] = f"{current_regex}|{app_pattern}"
            else:
                target_class['rule']['regex'] = app_pattern
    else:
        # 3. 如果是新分类，创建它
        existing_ids = [c['id'] for c in settings.get('classes', [])]
        new_id = max(existing_ids) + 1 if existing_ids else 0
        
        new_class = {
            "id": new_id,
            "name": [category_name],
            "rule": {
                "type": "regex", 
                "regex": app_pattern, 
                "ignore_case": True # 新创建的也设为 True
            },
            "data": {"color": "#999999"}
        }
        settings['classes'].append(new_class)

    # 保存修改
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"写入配置文件失败: {e}")
        return False
