import json
import os
import requests
from datetime import datetime

# 从 GitHub Secrets 获取秘钥
ACCOUNT_SID = os.environ.get("IMPACT_SID")
AUTH_TOKEN = os.environ.get("IMPACT_TOKEN")
BRAND_ID = "4468"  # AppSumo 的固定 ID

def get_data_from_impact():
    items_list = []
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 心跳包：显示同步状态
    items_list.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Sync Time: {now_str}",
        "desc": "Link.cn API 核心已连接。原生追踪链路就绪。",
        "url": "https://link.cn"
    })

    if not ACCOUNT_SID or not AUTH_TOKEN:
        print("Error: Missing IMPACT_SID or IMPACT_TOKEN in environment.")
        return items_list

    try:
        # 调用 Impact Mediapartner Ads 接口
        # 使用 Basic Auth 进行认证
        api_url = f"https://api.impact.com/Mediapartners/{ACCOUNT_SID}/Ads"
        params = {
            'BrandId': BRAND_ID,
            'Type': 'TEXT_LINK',
            'PageSize': '30'
        }
        
        response = requests.get(
            api_url, 
            auth=(ACCOUNT_SID, AUTH_TOKEN), 
            params=params,
            headers={'Accept': 'application/json'}
        )

        if response.status_code == 200:
            ads_data = response.json().get('Ads', [])
            print(f"API Success: Found {len(ads_data)} deals.")

            for ad in ads_data:
                tracking_url = ad.get('TrackingLink')
                name = ad.get('Name', 'AI Software')
                
                # 过滤掉一些无效或者没有描述的项目
                if tracking_url and name:
                    items_list.append({
                        "id": str(ad.get('Id')),
                        "tag": "LIFETIME DEAL",
                        "title": name.replace("AppSumo", "").strip(),
                        "desc": "Verified lifetime deal via Impact API. Limited time professional license.",
                        "url": tracking_url
                    })
        else:
            print(f"API Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Runtime Exception: {e}")

    # 如果 API 暂时没数据返回，提供固定测试位（带你的 ID）
    if len(items_list) == 1:
        items_list.append({
            "id": "API-PENDING",
            "tag": "WAITING",
            "title": "API Connecting...",
            "desc": "Impact API 已识别，正在等待 Brand 授权同步数据。通常需要几小时。",
            "url": f"https://appsumo.8io8.net/c/7294907/297384/4468"
        })

    return items_list

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    
    result = get_data_from_impact()
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully wrote {len(result)} items.")
