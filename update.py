import json
import os
import requests
import re
from datetime import datetime

# 配置你的联盟 ID
IMPACT_ID = "7294907"
AFF_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_data():
    items_list = []
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. 核心心跳包：证明脚本在跑，且 ID 正确
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Last Sync: {now_str}",
        "desc": f"Link.cn 引擎运行中 | Partner ID: {IMPACT_ID}",
        "url": "https://link.cn"
    })

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/xml,application/xml,application/rss+xml'
        }
        # 加上随机参数绕过可能的服务器缓存
        url = f"https://appsumo.com/feed/?v={datetime.now().timestamp()}"
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        content = response.text

        # 2. 使用正则表达式强行提取 <item> 块，无视命名空间
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        print(f"检测到项目数量: {len(items)}")

        for item_content in items[:15]:
            try:
                # 提取标题 (处理 CDATA 和普通文本)
                title_match = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item_content)
                # 提取链接
                link_match = re.search(r'<link>(.*?)</link>', item_content)
                
                if title_match and link_match:
                    title = title_match.group(1).replace("Lifetime Deal", "").strip()
                    link = link_match.group(1).strip()
                    
                    items_list.append({
                        "id": str(abs(hash(title)))[:8],
                        "tag": "LIFETIME DEAL",
                        "title": title,
                        "desc": "Limited time offer via AppSumo. Get exclusive lifetime access to this tool.",
                        "url": f"{AFF_PREFIX}?u={link}"
                    })
            except Exception as inner_e:
                print(f"单条目解析跳过: {inner_e}")
                continue
                
    except Exception as e:
        print(f"网络或全局解析异常: {e}")
    
    # 3. 兜底测试：如果还是只有 1 条，强行加一个测试位，防止 Git 认为没变化
    if len(items_list) == 1:
        items_list.append({
            "id": "TEST-CARD",
            "tag": "DEBUG",
            "title": "Wait for Next Sync",
            "desc": "AppSumo RSS 响应为空。系统会在下次同步时再次尝试。",
            "url": "https://link.cn"
        })
    
    return items_list

if __name__ == "__main__":
    # 确保写入路径正确
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    
    result = get_data()
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"处理完成: 共写入 {len(result)} 条数据到 {target_file}")
