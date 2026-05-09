import json
import os

def update():
    # 模拟从返利聚合源（如 AppSumo 或 Futurepedia）获取的数据
    # 在实际组局中，你会将这些链接替换为你申请到的 Affiliate URL
    market_data = [
        {
            "id": "PRO-2026-001",
            "tag": "HOT / DEALS",
            "title": "InVideo AI",
            "desc": "最强大的 AI 视频生成工具，支持文本直接转专业视频。通过 Link.cn 访问可获取早鸟折扣。",
            "link": "https://invideo.io/i/link_cn_special" # 示例返利链接
        },
        {
            "id": "PRO-2026-002",
            "tag": "AGENT / TOOL",
            "title": "AdCreative.ai",
            "desc": "为电商打造的 AI 广告素材生成器。高转化率背书，Link Protocol 合作伙伴。",
            "link": "https://free-trial.adcreative.ai/link-cn" # 示例返利链接
        },
        {
            "id": "PRO-2026-003",
            "tag": "DEV / MCP",
            "title": "Cursor AI",
            "desc": "当前最火的 AI 编程环境。集成全自动 Agent 模式，开发者必备。",
            "link": "https://cursor.com" 
        }
    ]

    # 保持 Link Protocol 核心资产置顶，确立“组局者”身份
    core_protocol = {
        "id": "CORE-001",
        "tag": "OFFICIAL",
        "title": "Link Protocol Ecosystem",
        "desc": "加入行为驱动信任网络，为你的 AI Agent 建立数字身份与信誉体系。",
        "link": "https://link.cn"
    }
    
    final_list = [core_protocol] + market_data

    try:
        # 确保在仓库根目录生成
        file_path = 'data.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        print(f"Commercial data sync successful: {os.path.abspath(file_path)}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    update()
