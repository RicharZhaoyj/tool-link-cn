import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 配置
IMPACT_ID = "7294907"
AFF_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_data():
    items_list = []
    # 无论如何先加一个时间戳项，确保文件内容永远在变，防止 Git 认为无需提交
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "desc": "Automated sync active for ID: 7294907",
        "url": "https://link.cn"
    })

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # 加上随机数绕过缓存
        url = f"https://appsumo.com/feed/?v={datetime.now().timestamp()}"
        r = requests.get(url, headers=headers, timeout=30)
        r.encoding = 'utf-8'
        
        if r.status_code == 200:
            root = ET.fromstring(r.text)
            for item in root.findall('./channel/item')[:15]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                if title_elem is not None and link_elem is not None:
                    items_list.append({
                        "id": datetime.now().strftime("%H%M%S"),
                        "tag": "LIFETIME DEAL",
                        "title": title_elem.text,
                        "desc": "Limited time offer via AppSumo.",
                        "url": f"{AFF_PREFIX}?u={link_elem.text}",
                        "is_ads": True
                    })
        else:
            print(f"AppSumo RSS returned status code: {r.status_code}")
    except Exception as e:
        print(f"Error during execution: {e}")
    
    return items_list

if __name__ == "__main__":
    # 强制定位路径
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    
    result = get_data()
    
    # 哪怕只抓到了系统时间项，也要写入，保证 tools.json 存在
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved {len(result)} items to {target_file}")
