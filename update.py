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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        # 加上随机参数防止被缓存
        response = requests.get(f"https://appsumo.com/feed/?v={datetime.now().timestamp()}", headers=headers, timeout=20)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)
        deals = []
        for item in root.findall('./channel/item')[:10]:
            title = item.find('title').text
            link = item.find('link').text
            deals.append({
                "id": datetime.now().strftime("%H%M%S"),
                "tag": "LIFETIME DEAL",
                # 在标题里强行加入时间戳，确保 Git 100% 能发现文件变动了
                "title": f"{title} [{datetime.now().strftime('%H:%M')}]",
                "desc": f"ID: {IMPACT_ID} | Exclusive AppSumo Deal",
                "url": f"{AFFILIATE_PREFIX}?u={link}"
            })
        return deals
    except Exception as e:
        print(f"Error fetching: {e}")
        return []

if __name__ == "__main__":
    # 【关键修改】获取脚本所在的绝对路径，并定位到根目录下的 tools.json
    # 假设 update.py 在根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'tools.json')
    
    print(f"Target file path: {file_path}")
    
    new_deals = get_appsumo_deals()
    
    if new_deals:
        # 无论如何，直接覆盖写入
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_deals, f, indent=4, ensure_ascii=False)
        print(f"Successfully wrote {len(new_deals)} deals to {file_path}")
    else:
        print("No data fetched. Check network or RSS feed.")
