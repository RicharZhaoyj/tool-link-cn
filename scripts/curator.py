import json
import datetime

def fetch_new_tool():
    # 这里未来可以对接 Gemini API 来获取真正的全网动态
    # 目前先模拟一个自动生成逻辑
    now = datetime.datetime.now()
    return {
        "id": now.strftime("%m%d%H"),
        "tag": "AUTO-GEN",
        "title": f"AI Agent - {now.strftime('%H:%M')}",
        "desc": "由 Link-Bot 自动发现并验证的最新 AI 工具。",
        "link": "https://link.cn"
    }

def update():
    with open('data.json', 'r', encoding='utf-8') as f:
        tools = json.load(f)
    
    # 获取新工具并放在列表首位
    new_tool = fetch_new_tool()
    tools.insert(0, new_tool)
    
    # 只保留最近的 12 个工具，维持页面整洁
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(tools[:12], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    update()
