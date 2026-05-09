import json

def update():
    # 真实的 AI 项目数据
    real_projects = [
        {
            "id": "20260509-01",
            "tag": "MCP-SERVER",
            "title": "Postgres MCP Server",
            "desc": "让 AI Agent 能够读写 PostgreSQL 数据库的官方标准服务器。",
            "link": "https://github.com/modelcontextprotocol/servers"
        },
        {
            "id": "20260509-02",
            "tag": "FRAMEWORK",
            "title": "PydanticAI",
            "desc": "由 Pydantic 团队开发的生产级 Agent 框架，支持严格的类型验证。",
            "link": "https://github.com/pydantic/pydantic-ai"
        },
        {
            "id": "20260509-03",
            "tag": "PROTOCOL",
            "title": "Link Protocol Core",
            "desc": "Link.cn 核心协议：为 AI Agent 打造的行为驱动信任网络底层基础设施。",
            "link": "https://link.cn" 
        }
    ]

    # 直接在当前工作目录写入
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(real_projects, f, ensure_ascii=False, indent=4)
        print("Success: data.json has been created in the current directory.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    update()
