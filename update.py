import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 你的 AppSumo 联盟 ID
IMPACT_ID = "7294907"
# 确保你的前缀格式正确，这里根据你提供的 ID 做了加固
AFFILIATE_PREFIX = f"https://appsumo.8io8.net/c/{IMPACT_ID}/123456/7890"

def get_appsumo_deals():
    try:
        # 增加伪装，防止被屏蔽
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 如果官方 RSS 抽风，可以使用这个备用抓取点
        response = requests.get("https://appsumo.com/feed/", headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # 检查是否真的拿到了内容
        if "<item>" not in response.text:
            print("RSS content is empty or blocked.")
            return []

        root = ET.fromstring(response.text)
        deals = []
        for item in root.findall('./channel/item')[:8]: # 稍微多抓几个
            title = item.find('title').text
            link = item.find('link').text
            deals.append({
                "id": datetime.now().strftime("%m%d%H%M"),
                "tag": "LIFETIME DEAL",
                "title": title,
                "desc": "Limited time offer. One-time payment via AppSumo. ID:7294907",
                "url": f"{AFFILIATE_PREFIX}?u={link}",
                "is_ads": True
            })
        return deals
    except Exception as e:
        print(f"Error fetching deals: {e}")
        return []

if __name__ == "__main__":
    new_deals = get_appsumo_deals()
    file_path = 'tools.json'
    
    # 1. 强制读取（如果失败则重置为空列表）
    tools = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tools = json.load(f)
            except:
                tools = []

    # 2. 强制插入新数据（哪怕重复也先插进去，用于测试）
    if new_deals:
        # 我们把新抓到的直接放在最前面
        # 为了测试，我们甚至可以给标题加个时间戳，确保它是“全新的”
        for d in new_deals:
            d['title'] = f"{d['title']} (Updated: {datetime.now().strftime('%H:%M')})"
            tools.insert(0, d)
        
        # 只保留前 20 条
        tools = tools[:20]

        # 3. 物理删除旧文件再写入（强制触发文件变动）
        if os.path.exists(file_path):
            os.remove(file_path)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tools, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully forced update of {file_path}")
    else:
        print("No data fetched from AppSumo, skipping write.")
