import json
from aw_detector import get_uncategorized_activities
from ai_classifier import batch_ask_ai_for_categories
from config_manager import update_aw_settings

def main():
    print("正在检测未分类活动...")
    classes, unlabeled = get_uncategorized_activities(limit_hours=24)

    if not unlabeled:
        print("没有发现未分类活动。")
        return

    # 获取现有所有分类名称供 AI 参考
    existing_cats = [cls['name'] for cls in classes]

    print(f"发现 {len(unlabeled)} 个新应用，准备请求 AI 批量分类...")

    # 一次性请求所有分类
    results = batch_ask_ai_for_categories(unlabeled, existing_cats)

    if not results:
        print("无法获取 AI 分类建议。")
        return

    for app, info in results.items():
        # AI 现在返回 {"category": "...", "color": "..."}
        if isinstance(info, dict):
            suggested_cat = info.get('category')
            suggested_color = info.get('color')
        else:
            # 兼容旧格式或异常情况
            suggested_cat = info
            suggested_color = None

        print(f"AI 建议: {app} -> {suggested_cat} (颜色: {suggested_color})")
        if update_aw_settings(suggested_cat, app, color=suggested_color):
            print(f"已成功将 {app} 归类到 {suggested_cat}")
        else:
            print(f"{app} 规则更新跳过（可能已存在）。")

if __name__ == "__main__":
    main()
