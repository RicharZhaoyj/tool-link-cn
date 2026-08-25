# build_static.py
# 生成搜索引擎友好的静态 index.html
# 同时生成 sitemap.xml 和 robots.txt

import json
import html as html_lib
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
AFFILIATE_FILE = os.path.join(SCRIPT_DIR, 'affiliate-links.json')
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


def load_affiliate_links():
    """读取已审核的联盟配置；缺失或异常时保持官网直链兜底。"""
    try:
        with open(AFFILIATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as exc:
        print(f'    [WARN] affiliate-links.json unavailable: {exc}')
        return {}


def get_cta(tool, affiliate_links):
    """只将 status=active 且有 URL 的条目视为可变现联盟 CTA。"""
    tool_id = str(tool.get('id', ''))
    affiliate = affiliate_links.get(tool_id, {})
    if affiliate.get('status') == 'active' and affiliate.get('affiliate_url'):
        return affiliate['affiliate_url'], 'affiliate_click', '查看优惠 →', 'active'
    return tool.get('url', ''), 'tool_click', '访问官网 →', 'direct'


def get_discount(price, orig):
    try:
        p = float(re.sub(r'[^\d.]', '', str(price or '')))
        o = float(re.sub(r'[^\d.]', '', str(orig or '')))
        if o > 0:
            return round((1 - p / o) * 100)
    except Exception:
        pass
    return None


def build_tool_card(tool, affiliate_links, index=0):
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
    tool_id_html = html_lib.escape(str(tool.get('id', '')), quote=True)
    cta_url, growth_event, cta_label, affiliate_status = get_cta(tool, affiliate_links)
    cta_url_html = html_lib.escape(cta_url, quote=True)

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
                        <a href="{cta_url_html}" target="_blank" rel="nofollow noopener" data-growth-event="{growth_event}" data-monetization="{affiliate_status}" data-tool-id="{tool_id_html}" data-tool-name="{title_html}" data-placement="home_card" class="block w-full py-3.5 bg-white text-black text-center text-sm font-black rounded-2xl hover:bg-blue-600 hover:text-white transition-all active:scale-95">{cta_label}</a>
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
def build_tool_grid(html, tools, affiliate_links):
    """替换 tool-grid 内的占位符或已渲染内容为最新静态工具卡片"""
    import re
    tools_html = '\n'.join(build_tool_card(t, affiliate_links, i) for i, t in enumerate(tools))

    # 先尝试替换已有标记之间的内容（幂等：支持多次运行）
    pattern = r'<!-- STATIC_TOOLS_START -->.*?<!-- STATIC_TOOLS_END -->'
    if re.search(pattern, html, re.DOTALL):
        return re.sub(pattern, f'<!-- STATIC_TOOLS_START -->\n{tools_html}\n            <!-- STATIC_TOOLS_END -->', html, flags=re.DOTALL)

    # 兼容旧版：替换占位符（首次运行）
    marker = '<!-- STATIC_TOOLS -->'
    if marker in html:
        return html.replace(marker, f'<!-- STATIC_TOOLS_START -->\n{tools_html}\n            <!-- STATIC_TOOLS_END -->')

    # 兼容早期已经预渲染的首页：按 data-tool-id 更新 CTA，确保联盟配置真正生效。
    updated = 0
    for tool in tools:
        cta_url, growth_event, cta_label, affiliate_status = get_cta(tool, affiliate_links)
        url_html = html_lib.escape(str(cta_url), quote=True)
        title_html = html_lib.escape(str(tool.get('title', '')), quote=True)
        tool_id_html = html_lib.escape(str(tool.get('id', '')), quote=True)
        anchor_pattern = (
            rf'<a\b[^>]*data-tool-id="{re.escape(tool_id_html)}"'
            rf'[^>]*data-placement="home_card"[^>]*>.*?</a>'
        )

        def update_anchor(match):
            anchor = match.group(0)
            anchor = re.sub(r'href="[^"]*"', f'href="{url_html}"', anchor, count=1)
            anchor = re.sub(r'data-growth-event="[^"]*"', f'data-growth-event="{growth_event}"', anchor, count=1)
            if 'data-monetization=' in anchor:
                anchor = re.sub(r'data-monetization="[^"]*"', f'data-monetization="{affiliate_status}"', anchor, count=1)
            else:
                anchor = anchor.replace(f'data-growth-event="{growth_event}"', f'data-growth-event="{growth_event}" data-monetization="{affiliate_status}"', 1)
            anchor = re.sub(r'>\s*[^<]*</a>', f'>{cta_label}</a>', anchor, count=1)
            return anchor

        html, count = re.subn(anchor_pattern, update_anchor, html, count=1, flags=re.DOTALL)
        if count:
            updated += 1
    print(f'    [OK] tool-grid: updated pre-rendered CTA tracking ({updated}/{len(tools)})')
    return html


def build_stats(html, tools):
    """预填统计数据"""
    import re
    total = len(tools)
    ai_count = sum(1 for t in tools if t.get('is_ai'))
    deal_count = sum(1 for t in tools if t.get('price'))

    html = html.replace(
        'id="stats-bar" class="grid grid-cols-3 gap-4 mb-8 hidden"',
        'id="stats-bar" class="grid grid-cols-3 gap-4 mb-8"',
    )
    html = re.sub(r'(id="stat-total">)\d*(<)', rf'\g<1>{total}\g<2>', html)
    html = re.sub(r'(id="stat-ai">)\d*(<)', rf'\g<1>{ai_count}\g<2>', html)
    html = re.sub(r'(id="stat-deal">)\d*(<)', rf'\g<1>{deal_count}\g<2>', html)
    html = re.sub(
        r'(id="tool-count" class="text-xs font-mono text-zinc-500 hidden md:inline">)[^<]*(<)',
        rf'\g<1>{total} 个工具\g<2>',
        html
    )
    return html


def build_tags(html, tools):
    """预填分类标签"""
    import re
    tags = sorted(set(t.get('tag', '') for t in tools if t.get('tag')))
    buttons = '\n'.join(
        f'                <button class="filter-btn px-4 py-2 rounded-full text-xs font-medium" '
        f'data-filter="{tag}">{tag}</button>'
        for tag in tags
    )
    # 幂等：先尝试替换已有标记之间的内容
    pattern = r'<!-- STATIC_TAGS_START -->.*?<!-- STATIC_TAGS_END -->'
    if re.search(pattern, html, re.DOTALL):
        return re.sub(pattern, f'<!-- STATIC_TAGS_START -->\n{buttons}\n                <!-- STATIC_TAGS_END -->', html, flags=re.DOTALL)
    # 兼容旧版占位符
    return html.replace('<!-- STATIC_TAGS -->', f'<!-- STATIC_TAGS_START -->\n{buttons}\n                <!-- STATIC_TAGS_END -->')


def build_schema(html, tools):
    """幂等写入唯一一份 ItemList 结构化数据，并清理旧版重复块。"""
    import re
    start_marker = '<!-- ITEM_LIST_SCHEMA_START -->'
    end_marker = '<!-- ITEM_LIST_SCHEMA_END -->'
    schema_script = (
        f'{start_marker}\n'
        '    <script type="application/ld+json">\n'
        f'{build_item_list_schema(tools)}'
        f'\n    </script>\n{end_marker}'
    )

    marker_pattern = re.compile(
        rf'{re.escape(start_marker)}.*?{re.escape(end_marker)}',
        re.DOTALL,
    )
    if marker_pattern.search(html):
        return marker_pattern.sub(schema_script, html, count=1)

    legacy_pattern = re.compile(
        r'\s*<script type="application/ld\+json">\s*'
        r'(?=\{.*?"@type"\s*:\s*"ItemList").*?</script>',
        re.DOTALL,
    )
    html, removed = legacy_pattern.subn('', html)
    if removed:
        print(f'    [OK] schema: removed {removed} legacy ItemList blocks')
    return html.replace('</head>', f'\n    {schema_script}\n</head>', 1)


def build_meta_description(html, tools):
    """更新 meta description 包含工具名"""
    top = [t['title'] for t in tools[:8]]
    desc = f'发现{len(tools)}个AI工具Lifetime Deal：{", ".join(top)}...一次买断终身使用。'
    return re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{desc}">',
        html,
    )


def build_update_time(html):
    """从 tools.json 读取 SYNC-INFO，预填 update-time"""
    try:
        import json, os, re
        tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools.json')
        data = json.load(open(tools_path, 'r', encoding='utf-8'))
        si = next((t for t in data if t.get('id') == 'SYNC-INFO'), None)
        if si:
            sync_time = si.get('title', '').replace('Sync Time: ', '')
            # 用 regex 匹配任意已存在的日期文本（包括"加载中..."和具体日期）
            html = re.sub(
                r'(id="update-time"[^>]*>最后更新：)[^<]*(</p>)',
                rf'\g<1>{sync_time}\g<2>',
                html
            )
            print(f'    [OK] update-time pre-filled: {sync_time}')
    except Exception as e:
        print(f'    [WARN] build_update_time failed: {e}')
    return html


def build_growth_tracking(html):
    """给首页外链 CTA 增加 GA4 事件监听，并区分联盟与普通官网访问。"""
    import re
    marker = '<!-- LINK_GROWTH_TRACKING -->'
    script = f'''\n    {marker}
    <script>
      document.addEventListener('click', function (event) {{
        const link = event.target.closest('a[data-growth-event]');
        if (!link || typeof window.gtag !== 'function') return;
        window.gtag('event', link.dataset.growthEvent, {{
          event_category: link.dataset.monetization === 'active' ? 'monetization' : 'outbound',
          tool_id: link.dataset.toolId || '',
          tool_name: link.dataset.toolName || '',
          has_affiliate: link.dataset.monetization === 'active',
          placement: link.dataset.placement || 'home_card',
          destination: link.href
        }});
      }});
    </script>'''
    if marker in html:
        pattern = re.compile(rf'{re.escape(marker)}.*?</script>', re.DOTALL)
        return pattern.sub(script.strip(), html, count=1)
    return html.replace('</head>', script + '\n</head>', 1)


def build_all():
    tools = load_tools()
    if not tools:
        print('[ERROR] No tools data, abort.')
        return

    tools.sort(key=lambda t: (not t.get('is_ai'), t.get('id', '')))
    affiliate_links = load_affiliate_links()

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    html = build_tool_grid(html, tools, affiliate_links)
    html = build_stats(html, tools)
    html = build_tags(html, tools)
    html = build_schema(html, tools)
    html = build_meta_description(html, tools)
    html = build_update_time(html)
    html = build_growth_tracking(html)

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
