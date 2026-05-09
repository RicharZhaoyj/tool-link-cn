import json
import datetime
import requests

def fetch_real_ai_tools():
    """
    模拟从 GitHub 或 AI 资讯源获取真实数据。
    这里展示 3 个你目前可以手动维护或通过 API 接入的真实项目案例。
    """
    # 实际开发中，这里可以接入 GitHub API 搜索 'topic:mcp' 或 'topic:ai-agent'
    real_projects = [
        {
            "id": "20260509-01",
            "tag": "MCP-SERVER",
            "title": "Postgres MCP Server",
            "desc": "A Model Context Protocol server that gives AI Agents read/write access to PostgreSQL databases.",
            "link": "https://github.com/modelcontextprotocol/servers"
        },
        {
            "id": "20260509-02",
            "tag": "AGENT-FRAME",
            "title": "PydanticAI",
            "desc": "Agentic AI framework by Pydantic, designed for production-grade AI agents with strict validation.",
            "link": "https://github.com/pydantic/pydantic-ai"
        },
        {
            "id": "20260509-03",
            "tag": "INFRA",
            "title": "Link Protocol Core",
            "desc": "The behavior-driven trust network infrastructure for cross-agent interaction and identity.",
            "link": "https://link.cn" # 你的核心协议
        }
    ]
    return real_projects

def update():
    try:
        # 1. 获取真实/半真实的项目数据
        new_tools = fetch_real_ai_tools()
        
        # 2. 写入 data.json
        # 我们这里直接覆盖或合并，确保页面上有实质性的链接
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(new_tools, f, ensure_ascii=False, indent=4)
        print("Successfully updated data.json with real project links.")
            
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    update()
