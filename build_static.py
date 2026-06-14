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

    # Deal type badge
    price_str = str(tool.get('price', ''))
    is_sub = '/' in price_str or '月起' in price_str or '付费' in price_str
    if price_str:
        deal_badge = (
            '<span class="text-[10px] font-bold bg-zinc-700/30 text-zinc-400 px-2 py-0.5 '
            'rounded tracking-widest uppercase ml-2 border border-zinc-600/30">订阅</span>'
            if is_sub else
            '<span class="text-[10px] font-bold bg-emerald-500/15 text-emerald-400 px-2 py-0.5 '
            'rounded tracking-widest uppercase ml-2 border border-emerald-500/30">LTD</span>'
        )
    else:
        deal_badge = ''

    # price HTML
    price_html = ''
    if tool.get('price'):
        display_price = price_str.replace('/月', '<span class="text-sm font-normal text-emerald-400/70">/月</span>')
        display_price = display_price.replace('/月起', '<span class="text-sm font-normal text-emerald-400/70">/月起</span>')
        price_html = (
            '<div class="mb-4"><div class="flex items-baseline gap-3 mb-2">'
            f'<span class="text-2xl md:text-3xl font-black text-emerald-400">{display_price}</span>'
        )
        if tool.get('originalPrice') and tool['originalPrice'] != tool.get('price'):
            price_html += (
                f'<span class="text-zinc-600 text-sm line-through">{tool["originalPrice"]}</span>'
            )
        if discount and discount > 0:
            price_html += (
                f'<span class="discount-tag text-xs font-bold px-2 py-1 rounded">省 {discount}%</span>'
            )
        price_html += '</div>'
        if discount and discount > 50:
            price_html += '<div class="text-[10px] font-mono text-amber-400/80 mb-1">热门 Deal · 节省超一半</div>'
        price_html += '</div>'
    else:
        price_html = '<div class="mb-4 text-zinc-600 text-sm font-mono">暂无报价</div>'

    # Review link
    review_slug = tool.get('title', '').lower().replace(' ', '-')
    review_slug = ''.join(c if c.isalnum() or c == '-' else '' for c in review_slug)
    review_url = f'https://tools.link.cn/review/{review_slug}'

    delay = index * 50
    return f'''                    <div class="tool-card glass-card p-6 md:p-8 rounded-3xl flex flex-col h-full" style="animation-delay: {delay}ms">
                        <div class="flex-grow">
                            <div class="mb-4 flex items-center flex-wrap gap-1">
                                <span class="text-[10px] font-bold bg-blue-500/20 text-blue-400 px-2 py-1 rounded tracking-widest uppercase border border-blue-500/30">{tag}</span>
                                {ai_label}
                                {deal_badge}
                            </div>
                            <h3 class="text-xl md:text-2xl font-bold mb-2">{title_html}</h3>
                            <p class="text-zinc-400 text-sm leading-relaxed mb-4">{desc_html}</p>
                            {price_html}
                        </div>
                        <div class="space-y-2">
                            <a href="{url_html}" target="_blank" rel="nofollow" class="block w-full py-3.5 bg-white text-black text-center text-sm font-black rounded-2xl hover:bg-blue-600 hover:text-white transition-all active:scale-95">立即查看 →</a>
                            <a href="{review_url}" target="_blank" class="block w-full py-2 text-zinc-600 text-center text-xs font-mono hover:text-blue-400 transition-colors">工具评测 ↗</a>
                        </div>
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
    """替换 tool-grid 内的工具卡片为静态预渲染版本"""
    tools_html = '\n'.join(build_tool_card(t, i) for i, t in enumerate(tools))
    marker = '<!-- STATIC_TOOLS -->'
    if marker in html:
        return html.replace(marker, tools_html)
    # Fallback: find tool-grid and replace content between opening tag and next </div>
    import re
    m = re.search(r'<div id="tool-grid"[^>]*>.*?(?=<div id="empty-state")', html, re.DOTALL)
    if m:
        return html[:m.end()] + '\n' + tools_html + '\n                    ' + html[m.end():]
    print('[WARN] build_tool_grid: could not find grid container')
    return html


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


def build_hero_title(html):
    """更新 Hero h1 内的工具数量为静态已知值"""
    import json, os
    tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools.json')
    try:
        data = json.load(open(tools_path, 'r', encoding='utf-8'))
        count = len([t for t in data if t.get('id') not in ('SYNC-INFO', 'STATUS', 'API-PENDING')])
        tagline = f'发现 {count} 个值得一次买断的优质 AI 工具'
        old = '<p class="text-zinc-400 text-base md:text-lg mb-1">发现值得一次买断的优质 AI 工具</p>'
        if old in html:
            html = html.replace(old, f'<p class="text-zinc-400 text-base md:text-lg mb-1">{tagline}</p>')
    except Exception as e:
        print(f'    [WARN] build_hero_title: {e}')
    return html


def build_meta_description(html, tools):
    """更新 meta description 包含工具名"""
    top = [t['title'] for t in tools[:8]]
    desc = f'发现{len(tools)}个AI工具Lifetime Deal：{", ".join(top)}...原价+Deal价+节省比例，一次买断终身使用。'
    return re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{desc}">',
        html,
    )


def build_update_time(html):
    """从 tools.json 读取 SYNC-INFO，预填 update-time"""
    try:
        import json, os
        tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools.json')
        data = json.load(open(tools_path, 'r', encoding='utf-8'))
        si = next((t for t in data if t.get('id') == 'SYNC-INFO'), None)
        if si:
            sync_time = si.get('title', '').replace('Sync Time: ', '')
            html = html.replace(
                'id="update-time" class="text-zinc-600 text-xs font-mono mt-1">最后更新：加载中...</p>',
                f'id="update-time" class="text-zinc-600 text-xs font-mono mt-1">最后更新：{sync_time}</p>'
            )
            print(f'    [OK] update-time pre-filled: {sync_time}')
    except Exception as e:
        print(f'    [WARN] build_update_time failed: {e}')
    return html


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
    html = build_hero_title(html)
    html = build_meta_description(html, tools)
    html = build_update_time(html)

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