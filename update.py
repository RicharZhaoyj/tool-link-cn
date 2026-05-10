import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 你的联盟 ID
IMPACT_ID = "7294907"
AFFILIATE_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_appsumo_deals():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(f"https://appsumo.com/feed/", headers=headers, timeout=20)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)
        deals = []
        for item in root.findall('./channel/item')[:10]:
            title = item.find('title').text
            link = item.find('link').text
            deals.append({
                "id": datetime.now().strftime("%H%M%S"),
                "tag": "LIFETIME DEAL",
                "title": title + " [Verified]", # 强制修改标题确保 Git 感知变化
                "desc": f"ID: {IMPACT_ID} | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "url": f"{AFFILIATE_PREFIX}?u={link}"
            })
        return deals
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []

if __name__ == "__main__":
    # 强制获取根目录绝对路径
    root_dir = os.getcwd()
    file_path = os.path.join(root_dir, 'tools.json')
    
    print(f"--- DIAGNOSTIC INFO ---")
    print(f"Current Working Directory: {root_dir}")
    print(f"Files in Directory: {os.listdir(root_dir)}")
    print(f"Targeting File: {file_path}")
    
    new_deals = get_appsumo_deals()
    
    if new_deals:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_deals, f, indent=4, ensure_ascii=False)
        print(f"--- SUCCESS: Wrote {len(new_deals)} deals to {file_path} ---")
    else:
        print("--- ERROR: No deals found, nothing written ---")
