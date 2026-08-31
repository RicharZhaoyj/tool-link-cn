"""
Build <noscript> static SEO fallback for index.html
Called by: python build_noscript.py
"""
import json, re, sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_PATH = os.path.join(BASE_DIR, 'tools.json')
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')

with open(TOOLS_PATH, 'r', encoding='utf-8') as f:
    tools = json.load(f)

items = [t for t in tools if t.get('id', '').startswith('CUR')]
ai_count = sum(1 for t in items if t.get('is_ai'))

def get_discount(p, op):
    try:
        pv = float(re.sub(r'[^0-9.]', '', p)) if p else 0
        ov = float(re.sub(r'[^0-9.]', '', op)) if op else 0
        if pv > 0 and ov > 0 and ov > pv:
            return round((1 - pv / ov) * 100)
    except:
        pass
    return None

cards = []
for item in items[:57]:  # max 57 to keep HTML reasonable
    tag = item.get('tag', '')
    name = item.get('title', '')
    desc = item.get('desc', '')
    price = item.get('price', '')
    original = item.get('originalPrice', '')
    price_suffix = item.get('priceSuffix', '/终身')
    url = item.get('url', '#')
    is_ai = item.get('is_ai', False)
    discount = get_discount(price, original)
    
    ai_badge = '<span class="ai-badge" style="margin-left:8px;">AI</span>' if is_ai else ''
    
    price_html = ''
    if price:
        parts = [f'<span class="price-tag">{price}<span style="font-size:10px;font-weight:400;opacity:0.7">{price_suffix}</span></span>']
        if original:
            parts.append(f'<span style="color:#71717a;font-size:12px;text-decoration:line-through;margin-left:4px;">{original}</span>')
        if discount:
            parts.append(f'<span class="discount-tag" style="margin-left:4px;">-{discount}%</span>')
        price_html = f'<div style="margin-bottom:12px;">{" ".join(parts)}</div>'
    
    card = f'''<div class="tool-card glass-card" style="padding:24px;margin:12px;display:inline-block;width:300px;vertical-align:top;border-radius:24px;">
<div style="margin-bottom:16px;">
<span style="background:rgba(59,130,246,0.2);border:1px solid rgba(59,130,246,0.3);color:#60a5fa;font-size:10px;font-weight:700;padding:4px 8px;border-radius:4px;">{tag}</span>{ai_badge}
</div>
<h3 style="font-size:20px;font-weight:700;margin-bottom:8px;">{name}</h3>
<p style="color:#a1a1aa;font-size:14px;line-height:1.6;margin-bottom:12px;">{desc}</p>
{price_html}
<a href="{url}" target="_blank" rel="nofollow" style="display:block;width:100%;padding:14px;background:#fff;color:#000;text-align:center;font-size:14px;font-weight:900;border-radius:16px;">立即查看 →</a>
</div>'''
    cards.append(card)

# Build noscript block
noscript_html = f'''<!-- SEO_NOSCRIPT_START -->
<noscript>
<div style="max-width:1400px;margin:0 auto;padding:32px 16px;font-family:system-ui,-apple-system,sans-serif;background:#050505;color:#fff;">
<h2 style="font-size:28px;font-weight:900;margin-bottom:8px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{len(items)} 个 AI 工具 Lifetime Deal</h2>
<p style="color:#a1a1aa;font-size:14px;margin-bottom:24px;">覆盖 AI 写作、绘图、视频、音频、开发、SEO、营销等15个分类 · 其中{ai_count}个AI工具 · 一次买断终身使用</p>
<div style="display:flex;flex-wrap:wrap;justify-content:center;">
{"".join(cards)}
</div>
<footer style="text-align:center;padding:32px 0;color:#71717a;font-size:12px;">© 2026 Link.cn · AI 工具导航 · tool.link.cn</footer>
</div>
</noscript>
<!-- SEO_NOSCRIPT_END -->'''

# Read index.html
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Remove old noscript block if exists
html = re.sub(r'<!-- SEO_NOSCRIPT_START -->.*?<!-- SEO_NOSCRIPT_END -->', '', html, flags=re.DOTALL)

# Inject before </body>
if '<!-- SEO_NOSCRIPT' not in html:
    html = html.replace('</body>', f'{noscript_html}\n</body>')

# Update meta description count
html = html.replace('发现55个AI工具Lifetime Deal', f'发现{len(items)}个AI工具Lifetime Deal')

# Write back
with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Injected noscript block: {len(items)} tools ({ai_count} AI)")
print(f"File size: {len(html):,} chars")
