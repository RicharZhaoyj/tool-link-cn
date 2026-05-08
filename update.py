import json

# 模拟抓取到的新数据
new_data = {
    "id": "131",
    "tag": "AGENT",
    "title": "New AI Agent",
    "desc": "Real-time behavior tracking.",
    "url": "https://link.cn"
}

# 1. 读取现有的数据
with open('tools.json', 'r') as f:
    tools = json.load(f)

# 2. 加入新工具并保持最新在最前
tools.insert(0, new_data)

# 3. 重新写入文件，Vercel 会感知并自动发布新网页
with open('tools.json', 'w') as f:
    json.dump(tools, f, indent=4)
