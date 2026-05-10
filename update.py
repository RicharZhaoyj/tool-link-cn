import json
import os
import requests
from datetime import datetime

# 配置你的 AppSumo 联盟信息
APPSUMO_PARTNER_ID = "你的注册ID" # 填入你在 AppSumo 获取的 ID
AFFILIATE_BASE_URL = f"https://appsumo.8io8.net/c/{APPSUMO_PARTNER_ID}/123456/7890" # 请根据你后台的实际链接格式调整

def fetch_appsumo_deals():
    """
    抓取 AppSumo 最新的 Deals。
    这里可以使用他们的 RSS Feed 或特定的 API 接口。
    """
    # 模拟抓取逻辑，实际可以使用 requests 访问 AppSumo 的公开 Feed
    # 例如：https://appsumo.com/feed/
    
    # 假设这是抓取回来的最新 Deal
    deal_title = "AI Content Writer Pro"
    deal_slug = "ai-content-writer-pro" # 抓取到的产品唯一标识
    
    # 自动生成你的返佣链接
    # 注意：具体的拼接规则请参照你的联盟后台生成的链接样式
    affiliate_link = f"https://appsumo.8io8.net/c/{APPSUMO_PARTNER_ID}/your_deal_path/{deal_slug}"
    
    return {
        "id": datetime.now().strftime("%y%m%d%H"),
        "tag": "LIFETIME DEAL",
        "title": deal_title,
        "desc": "Limited time software deal from AppSumo. One-time payment.",
        "url": affiliate_link, # 注入返佣链接
        "is_affiliate": True
    }

def main():
    file_path = 'tools.json'
    
    # 获取新的返佣工具
    new_deal = fetch_appsumo_deals()
    
    # 读取历史数据
    tools = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tools = json.load(f)
            except: tools = []

    # 优先推荐：如果不存在就插入到最前面
    if not any(t['title'] == new_deal['title'] for t in tools):
        tools.insert(0, new_deal)
        tools = tools[:20] # 保持 20 个最新工具

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
