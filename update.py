import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ================= 配置区 =================
# 在 AppSumo 后台找到你的联盟短链模板，通常格式如下：
# https://appsumo.8io8.net/c/你的ID/xxxx/xxxx
MY_IMPACT_URL_PREFIX = "https://appsumo.8io8.net/c/你的ID/123456/7890" 
# ==========================================

def get_latest_appsumo_deals():
    """
    通过 AppSumo 的 RSS Feed 抓取最新 Deal
    """
    try:
        # AppSumo 的官方 RSS 地址
        rss_url = "https://appsumo.com/feed/"
        response = requests.get(rss_url, timeout=15)
        root = ET.fromstring(response.content)
        
        deals = []
        # 解析 RSS 中的 item
        for item in root.findall('./channel/item')[:3]: # 每次取前 3 个最新的
            title = item.find('title').text
            original_link = item.find('link').text
            # 提取产品 Slug 并构造你的返佣链接
            # 逻辑：将原始链接拼接到你的 Impact 前缀后面
            affiliate_link = f"{MY_IMPACT_URL_PREFIX}?u={original_link}"
            
            deals.append({
                "id": datetime.now().strftime("%y%m%d"),
                "tag": "LIFETIME DEAL",
                "title": title,
                "desc": "AppSumo 限时终身授权，无需月费。",
                "url": affiliate_link,
                "is_ads": True
            })
        return deals
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def main():
    file_path = 'tools.json'
    
    # 1. 抓取真实返佣数据
    new_deals = get_latest_appsumo_deals()
    
    # 2. 读取现有数据
    tools = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tools = json.load(f)
            except: tools = []

    # 3. 合并数据（去重并在最前方插入新 Deal）
    existing_titles = [t['title'] for t in tools]
    for deal in reversed(new_deals): # 反向插入保证顺序
        if deal['title'] not in existing_titles:
            tools.insert(0, deal)
    
    # 保持工具列表不要过长
    tools = tools[:30]

    # 4. 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=4, ensure_ascii=False)
    print(f"更新成功：新增了 {len(new_deals)} 个返佣工具。")

if __name__ == "__main__":
    main()
    main()
