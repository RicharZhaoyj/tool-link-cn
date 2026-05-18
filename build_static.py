# build_static.py
# 生成搜索引擎友好的静态 index.html
# 同时生成 sitemap.xml 和 robots.txt

import json
import os
import re
import sys
from datetime import datetime

# Windows 终端 UTF-8 支持
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_FILE = os.path.join(SCRIPT_DIR, 'tools.json')
HTML_FILE = os.path.join(SCRIPT_DIR, 'index.html')
SITEMAP_FILE = os.path.join(SCRIPT_DIR, 'sitemap.xml')
ROBOTS_FILE = os.path.join(SCRIPT_DIR, 'robots.txt')
BASE_URL = 'https://tool.link.cn'


def load_tools():
    if not os.path.exists(TOOLS_FILE):
        print('[ERROR] tools.json not found:', TOOLS_FILE)
        return []
    with open(TOOLS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [t for t in data if t.get('id') not in ('SYNC-INFO', 'STATUS', 'API-PENDING')]


def get_discount(price, orig):
    try:
        p = float(re.sub(r'[^\d.]', '', str(price or '')))
        o = float(re.sub(r'[^\d.]', '', str(orig or '')))
        if o > 0:
            return round((1 - p / o) * 100)
    except Exception:
        pass
    return None


def build_tool_card(tool, index=0):
    discount = get_discount(tool.get('price'), tool.get('originalPrice'))
    ai_label = ''
    if tool.get('is_ai'):
        ai_label = (
            '<span class="ai-badge text-[10px] font-bold px-2 py-0.5 rounded '
            'tracking-widest uppercase ml-2">AI</span>'
        )
    tag = tool.get('tag', 'DEAL')
    title_html = tool.get('title', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    desc_html = tool.get('desc', '限时 Lifetime Deal').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    url_html = tool.get('url', '').replace('&', '&amp;')

    # price HTML
    price_html = ''
    if tool.get('price'):
        price_html = (
            '<div class="flex items-center gap-2 mb-3">'
            f'<span class="price-tag text-white text-sm font-black px-3 py-1 rounded-lg">'
            f'{tool["price"]}<span class="text-[10px] font-normal opacity-70">/终身</span></span>'
        )
        if tool.get('originalPrice') and tool['originalPrice'] != tool.get('price'):
            price_html += (
                f'<span class="text-zinc-600 text-xs line-through">{tool["originalPrice"]}</span>'
            )
        if discount and discount > 0:
            price_html += (
                f'<span class="discount-tag text-[10px] font-bold px-2 py-0.5 rounded">-{discount}%</span>'
            )
        price_html += '</div>'

    delay = index * 50
    return f'''                    <div class="tool-card glass-card p-6 md:p-8 rounded-3xl flex flex-col h-full" style="animation-delay: {delay}ms">
                        <div class="flex-grow">
                            <div class="mb-4 flex items-center">
                                <span class="text-[10px] font-bold bg-blue-500/20 text-blue-400 px-2 py-1 rounded tracking-widest uppercase border border-blue-500/30">{tag}</span>
                                {ai_label}
                            </div>
                            <h3 class="text-xl md:text-2xl font-bold mb-2">{title_html}</h3>
                            <p class="text-zinc-400 text-sm leading-relaxed mb-4">{desc_html}</p>
                            {price_html}
                        </div>
                        <a href="{url_html}" target="_blank" rel="nofollow" class="block w-full py-3.5 bg-white text-black text-center text-sm font-black rounded-2xl hover:bg-blue-600 hover:text-white transition-all active:scale-95">立即查看 →</a>
                    </div>'''


def build_item_list_schema(tools):
    items = []
    for i, tool in enumerate(tools):
        offer = {}
        if tool.get('price'):
            offer = {
                '@type': 'Offer',
                'price': tool['price'].replace('$', '').strip(),
                'priceCurrency': 'USD',
            }
        items.append({
            '@type': 'ListItem',
            'position': i + 1,
            'item': {
                '@type': 'SoftwareApplication',
                'name': tool['title'],
                'description': tool.get('desc', ''),
                'applicationCategory': tool.get('tag', ''),
                'operatingSystem': 'Web',
                'url': tool['url'],
                'offers': offer,
            },
        })
    return json.dumps({
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'AI工具Lifetime Deal买断方案',
        'description': '全球顶尖AI工具一次买断终身使用方案汇总',
        'numberOfItems': len(tools),
        'itemListElement': items,
    }, ensure_ascii=False, indent=2)


# ---- 各个构建步骤 ----
def build_tool_grid(html, tools):
    """替换 tool-grid 内的占位符为静态工具卡片"""
    tools_html = '\n'.join(build_tool_card(t, i) for i, t in enumerate(tools))
    marker = '<!-- STATIC_TOOLS -->'
    return html.replace(marker, tools_html)


def build_stats(html, tools):
    """预填统计数据"""
    total = len(tools)
    ai_count = sum(1 for t in tools if t.get('is_ai'))
    deal_count = sum(1 for t in tools if t.get('price'))

    html = html.replace(
        'id="stats-bar" class="grid grid-cols-3 gap-4 mb-8 hidden"',
        'id="stats-bar" class="grid grid-cols-3 gap-4 mb-8"',
    )
    html = html.replace('id="stat-total">0<', f'id="stat-total">{total}<')
    html = html.replace('id="stat-ai">0<', f'id="stat-ai">{ai_count}<')
    html = html.replace('id="stat-deal">0<', f'id="stat-deal">{deal_count}<')
    html = html.replace(
        'id="tool-count" class="text-xs font-mono text-zinc-500 hidden md:inline">',
        f'id="tool-count" class="text-xs font-mono text-zinc-500 hidden md:inline">{total} 个工具',
    )
    return html


def build_tags(html, tools):
    """预填分类标签"""
    tags = sorted(set(t.get('tag', '') for t in tools if t.get('tag')))
    buttons = '\n'.join(
        f'                <button class="filter-btn px-4 py-2 rounded-full text-xs font-medium" '
        f'data-filter="{tag}">{tag}</button>'
        for tag in tags
    )
    return html.replace('<!-- STATIC_TAGS -->', buttons)


def build_schema(html, tools):
    """插入 ItemList 结构化数据"""
    schema_script = (
        '\n    <script type="application/ld+json">\n'
        f'{build_item_list_schema(tools)}'
        '\n    </script>\n</head>'
    )
    return html.replace('</head>', schema_script)


def build_meta_description(html, tools):
    """更新 meta description 包含工具名"""
    top = [t['title'] for t in tools[:8]]
    desc = f'发现{len(tools)}个AI工具Lifetime Deal：{", ".join(top)}...一次买断终身使用。'
    return re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{desc}">',
        html,
    )


def build_all():
    tools = load_tools()
    if not tools:
        print('[ERROR] No tools data, abort.')
        return

    tools.sort(key=lambda t: (not t.get('is_ai'), t.get('id', '')))

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    html = build_tool_grid(html, tools)
    html = build_stats(html, tools)
    html = build_tags(html, tools)
    html = build_schema(html, tools)
    html = build_meta_description(html, tools)

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    ai_count = sum(1 for t in tools if t.get('is_ai'))
    deal_count = sum(1 for t in tools if t.get('price'))
    print(f'[OK] index.html updated ({len(tools)} tools pre-rendered)')
    print(f'     AI: {ai_count} | Deal: {deal_count}')


def build_sitemap(tools):
    entries = [(BASE_URL + '/', 'daily', '1.0')]
    for tool in tools:
        entries.append((f'{BASE_URL}/r/{tool["id"]}', 'weekly', '0.6'))
    urls = '\n'.join(
        f'  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>'
        f'\n    <priority>{prio}</priority>\n  </url>'
        for loc, freq, prio in entries
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{urls}\n</urlset>'
    )
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(xml)
    print(f'[OK] sitemap.xml ({len(entries)} URLs)')


def build_robots():
    content = f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n'
    with open(ROBOTS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] robots.txt')


if __name__ == '__main__':
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'=== Link.cn SEO Build ===')
    print(f'Time: {now}')
    print()

    tools = load_tools()
    if not tools:
        print('[ERROR] Abort.')
        sys.exit(1)

    build_all()
    build_sitemap(tools)
    build_robots()

    print()
    print('All done. Push to GitHub → Vercel auto-deploys.')