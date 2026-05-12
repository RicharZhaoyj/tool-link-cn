import json
import os
import re
import requests
from datetime import datetime

# 从 GitHub Secrets 获取秘钥
ACCOUNT_SID = os.environ.get("IMPACT_SID")
AUTH_TOKEN = os.environ.get("IMPACT_TOKEN")
BRAND_ID = "4468"  # AppSumo 的固定 ID
AFFILIATE_ID = "7294907"
AFFILIATE_LINK_TEMPLATE = f"https://appsumo.8io8.net/c/{AFFILIATE_ID}/297384/4468"

# 中文分类映射
CATEGORY_MAP = {
    "Social media": "社交媒体",
    "Calendar & scheduling": "日历排期",
    "Development tools": "开发工具",
    "Productivity": "效率工具",
    "Lead generation": "获客引流",
    "Video": "视频工具",
    "SEO": "SEO优化",
    "Audio": "音频工具",
    "Content marketing": "内容营销",
    "Project management": "项目管理",
    "Email marketing": "邮件营销",
    "Design": "设计工具",
    "Analytics": "数据分析",
    "Customer support": "客户支持",
    "E-commerce": "电商工具",
    "Writing": "写作工具",
    "AI": "AI工具",
}

# AI 工具关键词（用于自动打标签）
AI_KEYWORDS = [
    "ai", "artificial intelligence", "chatgpt", "gpt", "claude", "gemini",
    "machine learning", "ml", "automation", "smart", "intelligent",
    "neural", "deep learning", "nlp", "natural language"
]


def get_category_tag(category_en):
    """将英文分类转为中文标签"""
    if not category_en:
        return "AI工具"
    for key, val in CATEGORY_MAP.items():
        if key.lower() in category_en.lower():
            return val
    # 如果没匹配到，检查是否含 AI 关键词
    cat_lower = category_en.lower()
    for kw in AI_KEYWORDS:
        if kw in cat_lower:
            return "AI工具"
    return "精选工具"


def is_ai_tool(name, desc=""):
    """判断是否为 AI 工具"""
    text = f"{name} {desc}".lower()
    for kw in AI_KEYWORDS:
        if kw in text:
            return True
    return False


def build_affiliate_url(product_url):
    """构建联盟链接（掩码形式，后续可在前端做跳转）"""
    # 保留原始链接，在前端通过 /go/ 路由跳转
    # 当前直接用 AppSumo 联盟链接模板
    if "appsumo.com" in product_url:
        # 提取产品 slug
        slug = product_url.rstrip("/").split("/")[-1]
        if slug:
            return f"https://appsumo.8io8.net/c/{AFFILIATE_ID}/297384/4468?u={product_url}"
    return product_url


def scrape_appsumo_deals():
    """从 AppSumo 网站抓取当前 Lifetime Deals"""
    items_list = []
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        # 抓取主页面
        response = requests.get('https://appsumo.com/software/', headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"AppSumo scrape failed: {response.status_code}")
            return items_list

        html = response.text

        # 尝试从页面中提取 JSON 数据（AppSumo 使用 Next.js，数据在 __NEXT_DATA__ 中）
        next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                # 解析 Next.js 数据结构
                products = []
                props = data.get('props', {}).get('pageProps', {})

                # 尝试多种数据路径
                for key in ['products', 'deals', 'listings', 'software']:
                    if key in props:
                        products = props[key]
                        break

                # 也可能在其他层级
                if not products:
                    for key in props:
                        if isinstance(props[key], list) and len(props[key]) > 3:
                            products = props[key]
                            break

                for product in products[:30]:
                    name = product.get('name', product.get('title', ''))
                    desc = product.get('short_description', product.get('description', product.get('summary', '')))
                    slug = product.get('slug', product.get('url_slug', ''))
                    price = product.get('price', product.get('lifetime_price', ''))
                    original_price = product.get('original_price', product.get('regular_price', ''))
                    category = product.get('category', product.get('categories', [{}]))
                    if isinstance(category, list) and category:
                        category = category[0].get('name', '') if isinstance(category[0], dict) else str(category[0])
                    elif isinstance(category, dict):
                        category = category.get('name', '')

                    if not name:
                        continue

                    product_url = f"https://appsumo.com/software/{slug}/" if slug else ""

                    items_list.append({
                        "id": f"AS-{slug or hash(name) % 10000}",
                        "tag": get_category_tag(category),
                        "title": name,
                        "desc": desc[:150] if desc else f"限时 Lifetime Deal，一次买断终身使用",
                        "price": f"${price}" if price else "",
                        "originalPrice": f"${original_price}" if original_price else "",
                        "url": build_affiliate_url(product_url) if product_url else AFFILIATE_LINK_TEMPLATE,
                        "category_en": category or "",
                        "is_ai": is_ai_tool(name, desc),
                        "source": "appsumo"
                    })
            except json.JSONDecodeError:
                print("Failed to parse __NEXT_DATA__")

        # 如果 Next.js 数据提取失败，用正则从 HTML 提取
        if not items_list:
            print("Falling back to HTML regex extraction...")
            items_list = parse_html_deals(html)

    except Exception as e:
        print(f"Scrape exception: {e}")

    return items_list


def parse_html_deals(html):
    """从 HTML 内容正则提取 deals 信息（备用方案）"""
    items = []

    # 提取交易块 - 匹配模式：名称 + 价格 + 分类
    # AppSumo 的列表页结构
    deal_pattern = re.compile(
        r'(?:Deal ends in|Price increases in)?\s*(\d+\s*(?:days?|hours?))?\s*\n'
        r'(\w[\w\s&.!-]+?)\s+in\s+\[([^\]]+)\]',
        re.MULTILINE
    )

    price_pattern = re.compile(r'\$(\d+)/lifetime\$?([\d,]+)?')

    matches = deal_pattern.findall(html)
    prices = price_pattern.findall(html)

    for i, (deadline, name, category) in enumerate(matches[:30]):
        name = name.strip()
        if not name or len(name) < 2:
            continue

        price = ""
        original_price = ""
        if i < len(prices):
            price = f"${prices[i][0]}"
            original_price = f"${prices[i][1]}" if prices[i][1] else ""

        product_url = f"https://appsumo.com/software/{name.lower().replace(' ', '-').replace('.', '')}/"

        items.append({
            "id": f"AS-{hash(name) % 100000:05d}",
            "tag": get_category_tag(category),
            "title": name,
            "desc": f"限时 Lifetime Deal，一次买断终身使用" + (f"，原价 ${original_price}" if original_price else ""),
            "price": price,
            "originalPrice": original_price,
            "url": build_affiliate_url(product_url),
            "category_en": category,
            "is_ai": is_ai_tool(name),
            "source": "appsumo"
        })

    return items


def get_data_from_impact():
    """从 Impact API 获取数据（主数据源，审核通过后生效）"""
    items_list = []

    if not ACCOUNT_SID or not AUTH_TOKEN:
        print("Impact credentials not configured, skipping.")
        return items_list

    try:
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
            headers={'Accept': 'application/json'},
            timeout=30
        )

        if response.status_code == 200:
            ads_data = response.json().get('Ads', [])
            print(f"Impact API Success: Found {len(ads_data)} deals.")

            for ad in ads_data:
                tracking_url = ad.get('TrackingLink')
                name = ad.get('Name', '')

                if tracking_url and name:
                    items_list.append({
                        "id": str(ad.get('Id')),
                        "tag": "LIFETIME DEAL",
                        "title": name.replace("AppSumo", "").strip(),
                        "desc": "Verified lifetime deal via Impact API. 一次买断终身使用。",
                        "price": "",
                        "originalPrice": "",
                        "url": tracking_url,
                        "category_en": "",
                        "is_ai": is_ai_tool(name),
                        "source": "impact"
                    })
        else:
            print(f"Impact API Failed: {response.status_code}")

    except Exception as e:
        print(f"Impact API Exception: {e}")

    return items_list


def get_manual_curated_deals():
    """手动精选 AI 工具库（兜底数据 + 补充数据）"""
    return [
        {
            "id": "CUR-001",
            "tag": "AI写作",
            "title": "Writingmate",
            "desc": "一个工作台调用 200+ AI 模型，生成文字/图片/视频内容，ChatGPT/Claude/Gemini 全覆盖",
            "price": "$59",
            "originalPrice": "$199",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Development tools",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-002",
            "tag": "AI视频",
            "title": "Reelify AI",
            "desc": "检测病毒传播时刻，自动加字幕，本地导出竖屏视频，无额度限制",
            "price": "$49",
            "originalPrice": "$177",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Video",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-003",
            "tag": "AI社交",
            "title": "replient.ai",
            "desc": "AI 智能回复社交媒体评论和私信，提升互动效率 10 倍",
            "price": "$59",
            "originalPrice": "$180",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Social media",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-004",
            "tag": "AI开发",
            "title": "Notte",
            "desc": "一个平台构建浏览器自动化脚本、AI 代理和无服务器 API 端点",
            "price": "$59",
            "originalPrice": "$240",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Development tools",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-005",
            "tag": "AI效率",
            "title": "Hedy AI",
            "desc": "AI 实时对话助手，帮你自信应对商务会议、面试、谈判等专业场景",
            "price": "$179",
            "originalPrice": "$299",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Productivity",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-006",
            "tag": "SEO优化",
            "title": "TextFocus",
            "desc": "分析任意页面，对标竞品，获取 SEO 和 GEO 优化建议，提升搜索排名",
            "price": "$94",
            "originalPrice": "$645",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "SEO",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-007",
            "tag": "AI获客",
            "title": "DM Champ",
            "desc": "白标 AI 销售代理，转售给客户并保留 100% 利润",
            "price": "$59",
            "originalPrice": "$804",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Lead generation",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-008",
            "tag": "AI写作",
            "title": "Prompt Architects",
            "desc": "为 ChatGPT/Gemini/Claude 增强 Prompt，内置文字/图片/视频模板库",
            "price": "$39",
            "originalPrice": "$120",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Productivity",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-009",
            "tag": "AI音频",
            "title": "Blip AI",
            "desc": "语音转文字，按快捷键即可在任何应用中口述输入，解放双手",
            "price": "$49",
            "originalPrice": "$144",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Audio",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-010",
            "tag": "内容营销",
            "title": "MagicFit",
            "desc": "从产品图片或 URL 自动生成广告、视频和社交媒体帖子，零设计技能",
            "price": "$89",
            "originalPrice": "$120",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Content marketing",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-011",
            "tag": "获客引流",
            "title": "Sbl.so",
            "desc": "LinkedIn 自动化外联，生成线索、筛选潜在客户、预约销售通话",
            "price": "$89",
            "originalPrice": "$1,188",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Lead generation",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-012",
            "tag": "社交媒体",
            "title": "Sociamonials",
            "desc": "自动发布社媒内容、病毒式抽奖、高级数据分析，一站式社媒管理",
            "price": "$69",
            "originalPrice": "$1,788",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Social media",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-013",
            "tag": "效率工具",
            "title": "Shareables",
            "desc": "连接 Google Sheets/Airtable/Notion，零代码生成自定义网站",
            "price": "$59",
            "originalPrice": "$96",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Productivity",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-014",
            "tag": "AI视频",
            "title": "Subscribr",
            "desc": "AI 生成 YouTube 长视频脚本，内置爆款钩子和故事框架",
            "price": "$69",
            "originalPrice": "$94",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Video",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-015",
            "tag": "日历排期",
            "title": "TidyCal",
            "desc": "强大的日程安排软件，自定义会议类型，集成主流日历",
            "price": "$29",
            "originalPrice": "$144",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Calendar & scheduling",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-016",
            "tag": "效率工具",
            "title": "BreezeDoc",
            "desc": "简洁的电子签名工具，简化文档签署流程，法律效力保障",
            "price": "$19",
            "originalPrice": "$180",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Productivity",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-017",
            "tag": "项目管理",
            "title": "NextStep",
            "desc": "构建标准作业流程(SOP)和工作流，动态截止日期+实时追踪",
            "price": "$39",
            "originalPrice": "$129",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Project management",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-018",
            "tag": "效率工具",
            "title": "Journal it!",
            "desc": "日记+规划+笔记+习惯+追踪，一站式加密私人生活管理器",
            "price": "$39",
            "originalPrice": "$99",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Productivity",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-019",
            "tag": "邮件营销",
            "title": "SendFox",
            "desc": "经济实惠的邮件营销工具，自动化邮件增长，无需昂贵月费",
            "price": "$49",
            "originalPrice": "$480",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Email marketing",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-020",
            "tag": "AI获客",
            "title": "ScaliQ",
            "desc": "AI 代理端到端运行和扩展 LinkedIn 外联，安全自动化获客",
            "price": "$99",
            "originalPrice": "$552",
            "url": "https://appsumo.8io8.net/c/7294907/297384/4468",
            "category_en": "Lead generation",
            "is_ai": True,
            "source": "curated"
        },
    ]


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    all_items = []

    # 1. 系统状态信息
    all_items.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Sync Time: {now_str}",
        "desc": "Link.cn 数据同步完成",
        "url": "https://tool.link.cn",
        "price": "",
        "originalPrice": "",
        "category_en": "",
        "is_ai": False,
        "source": "system"
    })

    # 2. 尝试 Impact API（主数据源，审核通过后自动启用）
    impact_items = get_data_from_impact()
    if impact_items:
        print(f"Impact API returned {len(impact_items)} items")
        all_items.extend(impact_items)

    # 3. 抓取 AppSumo 页面（备用数据源，始终运行）
    scraped_items = scrape_appsumo_deals()
    if scraped_items:
        print(f"AppSumo scrape returned {len(scraped_items)} items")
        # 去重（与 Impact 数据比对）
        impact_ids = {item['id'] for item in impact_items}
        impact_titles = {item['title'].lower() for item in impact_items}
        for item in scraped_items:
            if item['id'] not in impact_ids and item['title'].lower() not in impact_titles:
                all_items.append(item)

    # 4. 手动精选数据（兜底 + 补充）
    if len(all_items) < 5:
        print("Using curated fallback data")
        all_items.extend(get_manual_curated_deals())

    # 5. 如果有抓取数据但不够丰富，补充精选数据
    elif len(all_items) < 15:
        curated = get_manual_curated_deals()
        existing_titles = {item['title'].lower() for item in all_items}
        for item in curated:
            if item['title'].lower() not in existing_titles:
                all_items.append(item)
                existing_titles.add(item['title'].lower())

    # 统计
    ai_count = sum(1 for item in all_items if item.get('is_ai'))
    total_count = len(all_items) - 1  # 减去 SYNC-INFO

    print(f"Total: {total_count} tools ({ai_count} AI tools)")

    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=4, ensure_ascii=False)

    print(f"Successfully wrote {len(all_items)} items to {target_file}")
