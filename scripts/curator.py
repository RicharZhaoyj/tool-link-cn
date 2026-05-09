import json
import os

def update():
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

    # 强制在当前执行脚本的同级目录生成文件，或者直接指定根目录
    file_path = 'data.json'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(real_projects, f, ensure_ascii=False, indent=4)
    
    print(f"Success: {os.path.abspath(file_path)}")

if __name__ == "__main__":
    update()
