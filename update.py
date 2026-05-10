import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ================= 佣金配置 =================
IMPACT_ID = "7294907"
# AppSumo 的标准 Impact 深度链接前缀
AFFILIATE_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"
# ============================================

def get_appsumo_deals():
    """
    通过 AppSumo 官方 RSS 抓取最新 Lifetime Deals
    """
    try:
        # 增加 headers 模拟浏览器访问，防止被拦截
        headers = {'User-Agent': 'Mozilla/5.0'}
        rss_url = "https://appsumo.com/feed/"
        response = requests.get(rss_url, headers=headers, timeout=15)
        root = ET.fromstring(response.content)
        
        deals = []
        # 获取前 5 个最新产品
        for item in root.findall('./channel/item')[:5]:
            title = item.find('title').text
            original_link = item.find('link').text
            
            # 【核心逻辑】生成你的联盟链接
            # 采用深度链接拼接方式：前缀 + u=原始地址
            aff_link = f"{AFFILIATE_PREFIX}?u={original_link}"
            
            deals.append({
                "id": datetime.now().strftime("%y%m%d%H%M"),
                "tag": "LIFETIME DEAL",
                "title": title,
                "desc": "AppSumo 限时特惠：一次性付费，终身使用。AI 生产力神器。",
                "url": aff_link,
                "is_ads": True
            })
        return deals
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def main():
    file_path = 'tools.json'
    
    # 1. 抓取带返佣的新数据
    new_deals = get_appsumo_deals()
    
    # 2. 读取 tools.json (历史数据)
    tools = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tools = json.load(f)
            except: tools = []

    # 3. 优先级合并：新 Deal 置顶，去重
    existing_titles = [t['title'] for t in tools]
    for deal in reversed(new_deals):
        if deal['title'] not in existing_titles:
            tools.insert(0, deal)
    
    # 4. 保持数据新鲜（保留 20 条）
    tools = tools[:20]

    # 5. 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=4, ensure_ascii=False)
    
    print(f"已同步 {len(new_deals)} 个 AppSumo 工具到 tools.json，佣金 ID: {IMPACT_ID}")

if __name__ == "__main__":
    main()
