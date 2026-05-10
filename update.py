import json
import os
import requests
from datetime import datetime

# 配置你的联盟 ID
IMPACT_ID = "7294907"
AFF_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_data():
    items_list = []
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. 核心心跳包
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Last Sync: {now_str}",
        "desc": f"Link.cn 引擎正在通过 API 模式运行 | ID: {IMPACT_ID}",
        "url": "https://link.cn"
    })

    try:
        # 2. 模拟真实浏览器 Header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://appsumo.com/browse/'
        }
        
        # 这是一个更隐蔽的 JSON 数据源地址
        url = f"https://appsumo.com/api/v2/browse/deals/?page_size=20&sort=newest"
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # 根据 AppSumo API 结构提取（通常在 results 下）
            deals = data.get('results', [])
            print(f"API 抓取成功，检测到交易数量: {len(deals)}")

            for deal in deals[:15]:
                title = deal.get('name', '')
                slug = deal.get('slug', '')
                # 拼接完整链接
                deal_url = f"https://appsumo.com/products/{slug}/"
                
                if title and slug:
                    items_list.append({
                        "id": str(deal.get('id', datetime.now().timestamp())),
                        "tag": "LIFETIME DEAL",
                        "title": title.replace("Lifetime Deal", "").strip(),
                        "desc": deal.get('tagline', 'Grab this exclusive AI tool deal on AppSumo today.'),
                        "url": f"{AFF_PREFIX}?u={deal_url}"
                    })
        else:
            print(f"API 请求失败，状态码: {response.status_code}")

    except Exception as e:
        # 如果 API 挂了，尝试备用的简单网页正则解析
        print(f"API 模式失败，尝试网页 fallback: {e}")
    
    # 3. 如果 API 和 RSS 都没抓到，注入 3 条真实的高转化工具（手动兜底）
    # 确保页面永远不会是空的，且能为你产生点击
    if len(items_list) == 1:
        fallback_deals = [
            {"title": "NeuronWriter", "slug": "neuronwriter", "desc": "Optimize your website content for SEO with ease."},
            {"title": "Depositphotos", "slug": "depositphotos-100-stock-photo-deal", "desc": "Premium stock photos for your creative projects."},
            {"title": "LlamaGen.ai", "slug": "llamagenai", "desc": "Generate high-quality AI images and videos."}
        ]
        for fd in fallback_deals:
            items_list.append({
                "id": f"FALLBACK-{fd['slug']}",
                "tag": "HOT DEAL",
                "title": fd['title'],
                "desc": fd['desc'],
                "url": f"{AFF_PREFIX}?u=https://appsumo.com/products/{fd['slug']}/"
            })

    return items_list

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    result = get_data()
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"最终写入: {len(result)} 条数据。")
