import json
import os

# 1. 这里填入你新抓取到的工具
new_data = {
    "id": str(int(100 + (len(os.listdir()) * 7) % 900)), # 自动生成一个不重复的 ID
    "tag": "AGENT",
    "title": "New AI Discovery",
    "desc": "Automated discovery via Link Protocol.",
    "url": "https://link.cn"
}

file_path = 'tools.json'

# 2. 读取旧数据（核心：绝对不能丢掉旧链接）
tools = []
if os.path.exists(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                tools = json.loads(content)
    except Exception as e:
        print(f"读取旧数据出错: {e}")

# 3. 合并数据：把新的放在最前面，旧的接在后面
# 检查是否已存在（按标题去重）
if not any(t['title'] == new_data['title'] for t in tools):
    tools.insert(0, new_data)

# 4. 写入文件
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(tools, f, indent=4, ensure_ascii=False)

print(f"成功更新！当前共有 {len(tools)} 个工具链接。")
