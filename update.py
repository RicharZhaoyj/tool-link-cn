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
        # 强制请求最新 RSS
        response = requests.get(f"https://appsumo.com/feed/?t={datetime.now().timestamp()}", headers=headers, timeout=20)
        response.encoding = 'utf-8'
        
        if "<item>" not in response.text:
            return []

        root = ET.fromstring(response.text)
        deals = []
        for item in root.findall('./channel/item')[:10]:
            title = item.find('title').text
            link = item.find('link').text
            # 拼接 ID
            aff_link = f"{AFFILIATE_PREFIX}?u={link}"
            
            deals.append({
                "id": datetime.now().strftime("%H%M%S"),
                "tag": "LIFETIME DEAL",
                "title": title,
                "desc": f"Limited time offer via AppSumo. ID: {IMPACT_ID}",
                "url": aff_link,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        return deals
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []

if __name__ == "__main__":
    # 获取脚本所在的绝对路径，确保在 GitHub Actions 环境里不跑偏
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, 'tools.json')
    
    print(f"Target path: {file_path}")

    new_deals = get_appsumo_deals()
    
    if new_deals:
        # 暴力逻辑：不再对比，直接生成包含最新数据的列表
        # 写入前打印第一个标题，方便在 Actions 日志里对账
        print(f"First Deal Found: {new_deals[0]['title']}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_deals, f, indent=4, ensure_ascii=False)
        
        print("WRITE SUCCESS: tools.json has been overwritten.")
    else:
        print("CRITICAL: No deals fetched. Check AppSumo RSS status.")
