import json
import os
import requests
from datetime import datetime

# 配置你的联盟 ID
IMPACT_ID = "7294907"
# 标准 Impact Radius 深度链接前缀
# 格式通常为: https://appsumo.8io8.net/c/[YourID]/[ActionID]/[CampaignID]
# 这里的 123456 和 7890 是示例占位符，如果你的平台提供了更具体的 URL 请替换，否则使用下方通用跳转
BASE_AFF_URL = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_data():
    items_list = []
    now_str = datetime.now().strftime('%H:%M:%S')
    
    # 心跳包
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Last Sync: {now_str}",
        "desc": "Link.cn 引擎状态：已连接。链接重定向：已激活。",
        "url": "https://link.cn"
    })

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        # 使用 AppSumo 官方 Browse API，这最稳定
        url = "https://appsumo.com/api/v2/browse/deals/?page_size=15&sort=newest"
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            deals = response.json().get('results', [])
            for deal in deals:
                title = deal.get('name', '')
                slug = deal.get('slug', '')
                # 【核心修复】使用 ?u= 拼接时，确保后缀是干净的 slug 地址
                # 标准跳转格式: BASE_URL?u=https://appsumo.com/products/[slug]/
                target_link = f"{BASE_AFF_URL}?u=https://appsumo.com/products/{slug}/"
                
                items_list.append({
                    "id": str(deal.get('id')),
                    "tag": "LIFETIME DEAL",
                    "title": title.replace("Lifetime Deal", "").strip(),
                    "desc": deal.get('tagline', 'Grab this exclusive deal on AppSumo today.'),
                    "url": target_link
                })
        
    except Exception as e:
        print(f"API Error: {e}")

    # 兜底固定链接测试
    if len(items_list) <= 1:
        test_slugs = ["neuronwriter", "depositphotos-100-stock-photo-deal"]
        for slug in test_slugs:
            items_list.append({
                "id": f"FIXED-{slug}",
                "tag": "HOT DEAL",
                "title": slug.capitalize(),
                "desc": "High-value deal verified by Link.cn protocol.",
                "url": f"{BASE_AFF_URL}?u=https://appsumo.com/products/{slug}/"
            })

    return items_list

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(get_data(), f, indent=4, ensure_ascii=False)
