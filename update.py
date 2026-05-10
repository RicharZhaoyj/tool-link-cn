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
    # 永远保留系统时间戳，确保 tools.json 物理内容永远在变，触发 Git 提交
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Last Sync: {now_str}",
        "desc": f"Link.cn 自动监测引擎已启动 | ID:{IMPACT_ID}",
        "url": "https://link.cn"
    })

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml'
        }
        # 加上随机参数绕过 CDN 缓存
        url = f"https://appsumo.com/feed/?nocache={datetime.now().timestamp()}"
        r = requests.get(url, headers=headers, timeout=30)
        
        if r.status_code == 200:
            # 自动处理编码
            r.encoding = 'utf-8'
            # 兼容性解析
            content = r.text.strip()
            root = ET.fromstring(content)
            
            # 尝试抓取所有 item 节点
            raw_items = root.findall('.//item')
            print(f"找到原始节点数量: {len(raw_items)}")

            for item in raw_items[:15]:
                # 兼容性获取 title 和 link (处理可能存在的命名空间)
                title = item.findtext('title')
                link = item.findtext('link')
                
                if title and link:
                    items_list.append({
                        "id": datetime.now().strftime("%H%M%S") + str(len(items_list)),
                        "tag": "LIFETIME DEAL",
                        "title": title.replace("Lifetime Deal", "").strip(),
                        "desc": "Limited time offer: Get lifetime access to this professional AI tool.",
                        "url": f"{AFF_PREFIX}?u={link}",
                        "is_ads": True
                    })
        else:
            print(f"请求失败，状态码: {r.status_code}")

    except Exception as e:
        print(f"解析过程中出现异常: {e}")
    
    # --- 兜底逻辑：如果除了系统项外没有抓到任何数据，插入一条提示 ---
    if len(items_list) <= 1:
        items_list.append({
            "id": "RETRY",
            "tag": "NOTICE",
            "title": "正在等待 AppSumo 数据同步...",
            "desc": "由于接口响应较慢，数据可能在下次更新时显示。请稍后刷新。",
            "url": "https://link.cn"
        })
    
    return items_list

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    
    result = get_data()
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"成功写入 {len(result)} 条数据到 {target_file}")
