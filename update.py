import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 配置信息
IMPACT_ID = "7294907"
AFF_LINK = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def fetch_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        # 加上时间戳参数彻底避开缓存
        r = requests.get(f"https://appsumo.com/feed/?v={datetime.now().timestamp()}", headers=headers, timeout=20)
        r.encoding = 'utf-8'
        root = ET.fromstring(r.text)
        
        deals = []
        # 强制在第一条加入系统时间，用于肉眼对账
        deals.append({
            "id": "STATUS",
            "tag": "SYSTEM",
            "title": f"Last Sync: {datetime.now().strftime('%H:%M:%S')}",
            "desc": "If this time changes, automation is WORKING.",
            "url": "https://link.cn"
        })

        for item in root.findall('./channel/item')[:15]:
            title = item.find('title').text
            link = item.find('link').text
            deals.append({
                "id": datetime.now().strftime("%d%H%M"),
                "tag": "LIFETIME DEAL",
                "title": title,
                "desc": "Exclusive AI Tool Deal via AppSumo.",
                "url": f"{AFF_LINK}?u={link}"
            })
        return deals
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []

if __name__ == "__main__":
    # 强制定位到脚本所在目录的 tools.json
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools.json')
    data = fetch_data()
    
    if data:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"DONE: Wrote {len(data)} items to {path}")
