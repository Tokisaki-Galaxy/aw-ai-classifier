import json
from aw_detector import get_uncategorized_activities
from ai_classifier import ask_ai_for_category
from config_manager import update_aw_settings
from config import SETTINGS_PATH

def main():
    print("正在检测未分类活动...")
    unlabeled = get_uncategorized_activities(limit_hours=2)

    if not unlabeled:
        print("没有发现未分类活动。")
        return

    # 获取现有所有分类名称供 AI 参考
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        settings = json.load(f)
    existing_cats = [cls['name'] for cls in settings['classes']]

    print(f"发现 {len(unlabeled)} 个新应用，准备请求 AI 分类...")

    for app, title in unlabeled.items():
        print(f"分类中: {app} ({title})")
        suggested_cat = ask_ai_for_category(app, title, existing_cats)

        if suggested_cat:
            print(f"AI 建议分类: {suggested_cat}")
            if update_aw_settings(suggested_cat, app):
                print(f"已成功将 {app} 归类到 {suggested_cat}")
            else:
                print(f"{app} 已经存在于规则中，跳过。")
        else:
            print(f"无法获取 {app} 的 AI 分类。")

if __name__ == "__main__":
    main()
