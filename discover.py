"""
Link.cn 工具发现引擎
从多个数据源自动发现新的 AI 工具候选，输出 candidates.json
适用范围: AI SaaS 工具、Lifetime Deal、新兴工具
"""

import json
import os
import re
import requests
import time
from datetime import datetime

# ========== 配置 ==========
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'candidates.json')
EXISTING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools.json')
MAX_CANDIDATES = 30

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
}


def load_existing_tools():
    """加载已有工具列表，用于去重"""
    try:
        with open(EXISTING_FILE, 'r', encoding='utf-8') as f:
            tools = json.load(f)
        titles = {t.get('title', '').lower() for t in tools}
        urls = {t.get('url', '').lower().rstrip('/') for t in tools}
        return titles, urls
    except Exception:
        return set(), set()


# ========== 数据源 1: Product Hunt ==========
def fetch_product_hunt():
    """抓取 Product Hunt 首页 AI 专区"""
    candidates = []
    try:
        # Product Hunt RSS feed for AI category
        r = requests.get('https://www.producthunt.com/feed?category=ai', headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"PH returned {r.status_code}")
            return candidates

        # 提取产品卡片数据
        html = r.text

        # 查找 JSON-LD 结构化数据
        jsonld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        for match in jsonld_matches:
            try:
                data = json.loads(match)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'SoftwareApplication':
                            name = item.get('name', '')
                            desc = item.get('description', '')[:200]
                            url = item.get('url', '')
                            if name and url:
                                candidates.append({
                                    'title': name,
                                    'desc': desc,
                                    'url': url,
                                    'source': 'producthunt',
                                    'is_ai': True,
                                    'discovered_at': datetime.now().strftime('%Y-%m-%d'),
                                })
            except json.JSONDecodeError:
                continue

        # 备选：从 meta 标签提取
        if len(candidates) < 5:
            name_matches = re.findall(r'<a[^>]+class="[^"]*\bstyles_itemName\b[^"]*"[^>]*>\s*(.*?)\s*</a>', html)
            desc_matches = re.findall(r'<p[^>]+class="[^"]*\bstyles_tagline\b[^"]*"[^>]*>\s*(.*?)\s*</p>', html)
            for i, name in enumerate(name_matches[:20]):
                name = re.sub(r'<[^>]+>', '', name).strip()
                if name:
                    desc = re.sub(r'<[^>]+>', '', desc_matches[i]).strip() if i < len(desc_matches) else ''
                    candidates.append({
                        'title': name,
                        'desc': desc[:200],
                        'url': f'https://www.producthunt.com/search?q={name.replace(" ", "+")}',
                        'source': 'producthunt-html',
                        'is_ai': True,
                        'discovered_at': datetime.now().strftime('%Y-%m-%d'),
                    })

    except Exception as e:
        print(f"PH error: {e}")

    return candidates


# ========== 数据源 2: Tool目录 / 热榜 ==========
def fetch_futurepedia():
    """抓取 Futurepedia AI 工具目录"""
    candidates = []
    try:
        r = requests.get('https://www.futurepedia.io/', headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"Futurepedia returned {r.status_code}")
            return candidates

        html = r.text
        # 提取工具名称和链接
        card_matches = re.findall(r'<a[^>]*href="(/tool/([^"]+))"[^>]*>([^<]+)</a>', html)
        seen = set()
        for path, slug, name in card_matches[:30]:
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                candidates.append({
                    'title': name,
                    'desc': f'来自 Futurepedia AI 工具目录',
                    'url': f'https://www.futurepedia.io{path}',
                    'source': 'futurepedia',
                    'is_ai': True,
                    'discovered_at': datetime.now().strftime('%Y-%m-%d'),
                })

    except Exception as e:
        print(f"Futurepedia error: {e}")

    return candidates


# ========== 数据源 3: 手工推荐列表 ==========
def get_curated_discoveries():
    """定期推荐新发现的 AI 工具（手动维护，作为补充）"""
    # 当前推荐列表
    return [
        {
            'title': 'Cursor',
            'desc': 'AI-first 代码编辑器，代码库级上下文理解，Tab 补全精度极高',
            'url': 'https://cursor.sh/',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI开发',
            'price': '$20',
            'originalPrice': '$40',
            'note': '已有，建议深度评测'
        },
        {
            'title': 'v0.dev',
            'desc': 'Vercel 出品，自然语言描述直接生成 React UI 组件，shadcn/ui 集成',
            'url': 'https://v0.dev/',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI开发',
            'price': '$20',
            'originalPrice': '$40',
            'note': '已有，建议评测'
        },
        {
            'title': 'Bolt.new',
            'desc': '浏览器内全栈开发平台，AI 驱动的即时应用生成和部署',
            'url': 'https://bolt.new/',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI开发',
            'price': 'Free',
            'originalPrice': '',
            'note': '已有，建议评测'
        },
        {
            'title': 'Replit Agent',
            'desc': 'Replit 的 AI 编程代理，想法到部署一站式，支持自然语言开发',
            'url': 'https://replit.com/ai',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI开发',
            'price': '$25',
            'originalPrice': '',
            'note': '已有，建议评测'
        },
        {
            'title': 'Claude Desktop',
            'desc': 'Anthropic 桌面客户端，支持文件/MCP 工具调用，开发效率神器',
            'url': 'https://claude.ai/download',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI工具',
            'price': 'Free',
            'originalPrice': '',
            'note': '新兴工具，建议收录'
        },
        {
            'title': 'Perplexity Pro',
            'desc': 'AI 搜索引擎，实时联网，学术/调研/购物场景全覆盖',
            'url': 'https://www.perplexity.ai/',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI工具',
            'price': '$20',
            'originalPrice': '',
            'note': '已有，建议评测'
        },
        {
            'title': 'Devin',
            'desc': 'Cognition 出品的 AI 软件工程师，自主完成编码任务',
            'url': 'https://www.cognition.ai/',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI开发',
            'price': '$500',
            'originalPrice': '',
            'note': '热门，高价，观察市场反馈'
        },
        {
            'title': 'Lovable',
            'desc': 'AI 驱动的前端应用生成器，GPT-4 驱动，支持全栈部署',
            'url': 'https://lovable.dev/',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI开发',
            'price': '$20',
            'originalPrice': '$40',
            'note': '新兴工具，已收录可选评测'
        },
        {
            'title': 'OpenClaw Gateway',
            'desc': '自托管 AI Agent 网关，支持多渠道消息路由、浏览器自动化',
            'url': 'https://openclaw.ai/',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI工具',
            'price': 'Free',
            'originalPrice': '',
            'note': '开源工具，适合开发者'
        },
        {
            'title': 'Codeium Windsurf',
            'desc': 'Codeium 出品的 AI IDE，免费替代 GitHub Copilot，支持 VS Code 插件',
            'url': 'https://codeium.com/windsurf',
            'source': 'curated',
            'is_ai': True,
            'tag': 'AI开发',
            'price': 'Free',
            'originalPrice': '$15',
            'note': '免费替代品，建议收录'
        },
    ]


# ========== 主流程 ==========
def main():
    existing_titles, existing_urls = load_existing_tools()
    all_candidates = []
    seen = set()

    print("=== Link.cn 工具发现引擎 ===\n")

    # 1. 手工精选（优先，保证质量）
    curated = get_curated_discoveries()
    print(f"[精选] {len(curated)} 个推荐工具")

    # 2. Product Hunt
    ph = fetch_product_hunt()
    print(f"[Product Hunt] {len(ph)} 个工具")

    # 3. Futurepedia
    fp = fetch_futurepedia()
    print(f"[Futurepedia] {len(fp)} 个工具")

    # 合并 + 去重
    all_items = curated + ph + fp
    for item in all_items:
        key = item['title'].lower().strip()
        url_key = item.get('url', '').lower().rstrip('/')

        # 跳过已收录的
        if key in existing_titles or url_key in existing_urls:
            continue
        # 跳过重复
        if key in seen:
            continue
        # 跳过非 AI 工具（除非来自 curated）
        if item['source'] != 'curated' and not item.get('is_ai'):
            continue

        seen.add(key)
        all_candidates.append(item)

    # 限制数量
    all_candidates = all_candidates[:MAX_CANDIDATES]

    # 统计
    new_count = sum(1 for c in all_candidates if c['title'].lower() not in existing_titles)
    print(f"\n总候选: {len(all_candidates)} (新工具: {new_count})")

    # 写入
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(all_candidates),
            'new_discoveries': new_count,
            'candidates': all_candidates,
        }, f, ensure_ascii=False, indent=2)

    print(f"输出: {OUTPUT_FILE}")

    return all_candidates


if __name__ == '__main__':
    main()