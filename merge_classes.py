import json
import os

path = r'C:\Users\tokisaki\AppData\Local\activitywatch\activitywatch\aw-server\settings.json'

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

classes = data.get('classes', [])
# 按叶子节点名称合并，解决 "Games" 出现多次的问题
leaf_merged = {}

print(f"Original classes count: {len(classes)}")

for cls in classes:
    if not cls.get('name'): continue
    # 取分类路径的最后一个词作为 Key (例如 "Media > Games" 的 Key 是 "Games")
    leaf = cls['name'][-1]
    
    if leaf not in leaf_merged:
        leaf_merged[leaf] = cls
    else:
        # 合并到已存在的同名分类中
        existing = leaf_merged[leaf]
        print(f"Merging '{cls['name']}' into '{existing['name']}'")
        
        r1 = existing.get('rule', {}).get('regex', '')
        r2 = cls.get('rule', {}).get('regex', '')
        
        # 合并正则并去重
        p1 = [p.strip() for p in r1.split('|') if p.strip()]
        p2 = [p.strip() for p in r2.split('|') if p.strip()]
        combined = []
        seen = set()
        for p in p1 + p2:
            if p.lower() not in seen:
                combined.append(p)
                seen.add(p.lower())
        
        existing['rule']['regex'] = '|'.join(combined)
        existing['rule']['type'] = 'regex'
        existing['rule']['ignore_case'] = True

# 重新分配 ID
new_classes = list(leaf_merged.values())
for i, cls in enumerate(new_classes):
    cls['id'] = i

data['classes'] = new_classes

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=True)

print(f"Final classes count: {len(new_classes)}")
print("Successfully merged all classes by leaf name.")
