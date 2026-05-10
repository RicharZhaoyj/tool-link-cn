import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 你的 AppSumo 联盟 ID
IMPACT_ID = "7294907"
AFFILIATE_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_appsumo_deals():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get("https://appsumo.com/feed/", headers=headers, timeout=20)
        # 强制指定编码，防止中文或特殊字符报错
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)
        
        deals = []
        for item in root.findall('./channel/item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            deals.append({
                "id": datetime.now().strftime("%H%M%S"),
                "tag": "LIFETIME DEAL",
                "title": title,
                "desc": "Limited time offer. One-time payment via AppSumo.",
                "url": f"{AFFILIATE_PREFIX}?u={link}",
                "is_ads": True
            })
        return deals
    except Exception as e:
        print(f"Error fetching deals: {e}")
        return []

if __name__ == "__main__":
    new_deals = get_appsumo_deals()
    if not new_deals:
        print("No new deals found, exiting.")
    else:
        file_path = 'tools.json'
        tools = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try: tools = json.load(f)
                except: tools = []
        
        # 合并新旧数据
        titles = [t['title'] for t in tools]
        for d in reversed(new_deals):
            if d['title'] not in titles:
                tools.insert(0, d)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tools[:25], f, indent=4, ensure_ascii=False)
        print("Successfully updated tools.json")
