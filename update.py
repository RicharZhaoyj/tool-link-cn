import json
import os
import requests # 确保你的 GitHub Action 环境安装了 requests

def fetch_real_ai_tools():
    """
    这里是脚本的'眼睛'。
    目前我们可以模拟从一个 AI 资讯源抓取，
    或者你可以接入一个简单的搜索 API。
    """
    # 示例：从一个公共的 AI 工具聚合 JSON（或你自己的爬虫逻辑）获取
    # 为了演示，我构造一个根据时间动态生成的‘准真实’数据
    import datetime
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 实际开发中，这里可以替换为：requests.get("某个AI工具列表API").json()
    return {
        "id": datetime.datetime.now().strftime("%M%S"),
        "tag": "NEW-FIND",
        "title": f"AI Agent Helper {today}",
        "desc": "Automatically discovered via Link Protocol analysis.",
        "url": "https://link.cn/discovery"
    }

def main():
    file_path = 'tools.json'
    
    # 1. 获取真实数据
    new_data = fetch_real_ai_tools()
    print(f"发现新工具: {new_data['title']}")

    # 2. 读取旧数据
    tools = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tools = json.load(f)
            except: tools = []

    # 3. 避免重复并插入
    if not any(t['title'] == new_data['title'] for t in tools):
        tools.insert(0, new_data)
        # 保持只展示最近的 15 个，防止页面太沉重
        tools = tools[:15]

    # 4. 写入
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
