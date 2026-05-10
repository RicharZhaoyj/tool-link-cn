import json
import os
import requests
import urllib.parse
from datetime import datetime

# ================= 配置区 =================
# 1. 你的 Impact Radius 联盟 ID
IMPACT_ID = "7294907"

# 2. 深度链接前缀 (使用 AppSumo 默认的 Action/Campaign ID)
# 如果点击后提示 "Link Invalid"，请在 Impact 后台获取你的专属 Deep Link 路径并替换 297384/4468
AFF_BASE = f"https://appsumo.8io8.net/c/{IMPACT_ID}/297384/4468"

def get_data():
    items_list = []
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 系统心跳包：显示在网页顶部，证明同步正常
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Last Sync: {now_str}",
        "desc": f"Link.cn 自动化引擎运行中 | 联盟 ID: {IMPACT_ID}",
        "url": "https://link.cn"
    })

    try:
        # 模拟浏览器 Header，防止被 AppSumo 拦截
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://appsumo.com/browse/'
        }
        
        # 使用 AppSumo 官方浏览 API
        api_url = "https://appsumo.com/api/v2/browse/deals/?page_size=15&sort=newest"
        response = requests.get(api_url, headers=headers, timeout=25)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('results', [])
            print(f"成功获取 API 数据，共 {len(deals)} 个项目")

            for deal in deals:
                title = deal.get('name', 'AI Tool')
                slug = deal.get('slug', '')
                tagline = deal.get('tagline', 'Limited time lifetime deal.')
                
                if slug:
                    # 【关键修复】对目标链接进行标准的 URL 编码
                    # 避免跳转时因为 / 或 : 导致 Impact 识别路径错误
                    target_product_url = f"https://appsumo.com/products/{slug}/"
                    encoded_target = urllib.parse.quote(target_product_url, safe='')
                    
                    # 拼接最终的深度链接
                    final_aff_link = f"{AFF_BASE}?u={encoded_target}"
                    
                    items_list.append({
                        "id": str(deal.get('id', slug)),
                        "tag": "LIFETIME DEAL",
                        "title": title.replace("Lifetime Deal", "").strip(),
                        "desc": tagline,
                        "url": final_aff_link
                    })
        else:
            print(f"API 请求失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"抓取异常: {e}")

    # 3. 【强力兜底】如果 API 没抓到数据，手动注入高权重工具，确保网页不为空
    if len(items_list) <= 1:
        fallbacks = [
            {"t": "NeuronWriter", "s": "neuronwriter", "d": "SEO-optimized content writing tool."},
            {"t": "Depositphotos", "s": "depositphotos-100-stock-photo-deal", "d": "Premium stock image credits."},
            {"t": "LlamaGen.ai", "s": "llamagenai", "d": "Professional AI video and image generator."}
        ]
        for f in fallbacks:
            target = f"https://appsumo.com/products/{f['s']}/"
            items_list.append({
                "id": f"FB-{f['s']}",
                "tag": "HOT DEAL",
                "title": f['t'],
                "desc": f['d'],
                "url": f"{AFF_BASE}?u={urllib.parse.quote(target, safe='')}"
            })

    return items_list

if __name__ == "__main__":
    # 获取当前脚本所在目录，确保 tools.json 写入位置正确
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, 'tools.json')
    
    final_data = get_data()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
    
    print(f"[{datetime.now()}] 成功写入 {len(final_data)} 条数据到 {output_path}")
