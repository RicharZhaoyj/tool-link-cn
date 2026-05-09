import json
import os

def update():
    # 你的 Impact/AppSumo 专属追踪 ID
    MY_AFFILIATE_ID = "7284907"
    
    # 1. 核心资产：Link Protocol & 招聘位
    # 利用 link.cn 自 2003 年起积累的 23 年资产信誉作为背书
    head_cards = [
        {
            "id": "LINK-CORE",
            "tag": "OFFICIAL",
            "title": "Link Protocol",
            "desc": "基于行为驱动的 AI Agent 信任网络。利用 20 余年资产沉淀，为 AI 时代建立信用身份。",
            "link": "https://link.cn"
        },
        {
            "id": "JOIN-US",
            "tag": "WANTED",
            "title": "Seeking Tech Partner",
            "desc": "寻找 AI 基础设施方向的核心合伙人（Ali P8+ / Byte 3-1）。共建基于 link.cn 的信任协议。",
            "link": "https://link.cn" # 可替换为你的联系方式
        }
    ]
    
    # 2. 商业变现：AppSumo 精选 AI 工具 (Lifetime Deals)
    # 重点推荐“一次性付费，终身使用”的项目，转化率最高
    appsumo_deals = [
        {
            "id": "AS-2026-001",
            "tag": "LIFETIME DEAL",
            "title": "NeuronWriter",
            "desc": "顶级的 AI 内容与 SEO 优化工具，AppSumo 长期销量冠军。一次性付费，永久告别月费。",
            "link": f"https://appsumo.com/products/neuronwriter/?rid={MY_AFFILIATE_ID}"
        },
        {
            "id": "AS-2026-002",
            "tag": "AGENT / AUTO",
            "title": "Taskade",
            "desc": "集成 AI Agent 的第二大脑，支持自动化工作流拆解。AI 时代的高效团队协同神器。",
            "link": f"https://appsumo.com/products/taskade/?rid={MY_AFFILIATE_ID}"
        },
        {
            "id": "AS-2026-003",
            "tag": "VIDEO AI",
            "title": "Synthesys",
            "desc": "AI 虚拟人视频生成平台，支持 140+ 语言。输入文字即可生成专业级口播内容。",
            "link": f"https://appsumo.com/products/synthesys/?rid={MY_AFFILIATE_ID}"
        }
    ]

    final_data = head_cards + appsumo_deals

    try:
        # 确保在根目录生成 data.json
        file_path = 'data.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"成功更新商业数据，追踪 ID: {MY_AFFILIATE_ID}")
    except Exception as e:
        print(f"写入失败: {e}")
        exit(1)

if __name__ == "__main__":
    update()
