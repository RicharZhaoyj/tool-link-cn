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
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 始终保留第一条作为“心跳包”，证明脚本在跑
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Last Sync: {now_str}",
        "desc": f"ID:{IMPACT_ID} | 自动抓取引擎运行正常",
        "url": "https://link.cn"
    })

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # 使用更稳定的 RSS 地址
        url = "https://appsumo.com/feed/"
        r = requests.get(url, headers=headers, timeout=30)
        r.encoding = 'utf-8'
        
        # 尝试暴力解析：直接寻找 <item> 标签内容
        content = r.text
        # 简单粗暴的分割法，绕过复杂的 XML 命名空间问题
        parts = content.split('<item>')[1:16] # 抓取前 15 个
        
        for p in parts:
            try:
                title = p.split('<title>')[1].split('</title>')[0].replace('<![CDATA[', '').replace(']]>', '').strip()
                link = p.split('<link>')[1].split('</link>')[0].strip()
                
                if title and link:
                    items_list.append({
                        "id": str(hash(title)),
                        "tag": "LIFETIME DEAL",
                        "title": title,
                        "desc": "Limited time offer: Professional AI tool lifetime access.",
                        "url": f"{AFF_PREFIX}?u={link}"
                    })
            except:
                continue
                
    except Exception as e:
        print(f"抓取异常: {e}")
    
    return items_list

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    result = get_data()
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"写入完成，共 {len(result)} 条。")
