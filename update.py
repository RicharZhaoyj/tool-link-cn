import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 你的 AppSumo 联盟 ID
IMPACT_ID = "7294907"
# 确保你的前缀格式正确，这里根据你提供的 ID 做了加固
AFFILIATE_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_appsumo_deals():
    try:
        # 增加伪装，防止被屏蔽
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 如果官方 RSS 抽风，可以使用这个备用抓取点
        response = requests.get("https://appsumo.com/feed/", headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # 检查是否真的拿到了内容
        if "<item>" not in response.text:
            print("RSS content is empty or blocked.")
            return []

        root = ET.fromstring(response.text)
        deals = []
        for item in root.findall('./channel/item')[:8]: # 稍微多抓几个
            title = item.find('title').text
            link = item.find('link').text
            deals.append({
                "id": datetime.now().strftime("%m%d%H%M"),
                "tag": "LIFETIME DEAL",
                "title": title,
                "desc": "Limited time offer. One-time payment via AppSumo. ID:7294907",
                "url": f"{AFFILIATE_PREFIX}?u={link}",
                "is_ads": True
            })
        return deals
    except Exception as e:
        print(f"Error fetching deals: {e}")
        return []

if __name__ == "__main__":
    new_deals = get_appsumo_deals()
    file_path = os.path.join(os.getcwd(), 'tools.json') # 强制使用绝对路径
    
    # 哪怕没抓到新数据，我们也确保 tools.json 至少存在
    tools = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tools = json.load(f)
            except:
                tools = []

    if not new_deals:
        print("Using historical data only.")
    else:
        # 合并新旧数据，并进行深度去重
        existing_titles = [t.get('title') for t in tools]
        added_count = 0
        for d in reversed(new_deals):
            if d['title'] not in existing_titles:
                tools.insert(0, d)
                added_count += 1
        print(f"Added {added_count} new unique deals.")

    # 强制写入：即使没有新数据，也重新保存一次以确保持续触发 Vercel
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tools[:30], f, indent=4, ensure_ascii=False)
    
    print(f"Successfully processed tools.json. Total count: {len(tools)}")
