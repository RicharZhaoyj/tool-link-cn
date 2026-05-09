import json
import os

def update():
    # 填入你真正想要展示的高质量 AI 项目链接
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

    # 确保 data.json 写入根目录
    try:
        # 获取当前脚本所在目录的上一级（即仓库根目录）
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, 'data.json')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(real_projects, f, ensure_ascii=False, indent=4)
        print(f"Successfully updated {file_path}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    update()
if __name__ == "__main__":
    update()
