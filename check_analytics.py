import re

with open(r'C:\Users\zhaoy\.qclaw\workspace-agent-5d8ec867\tool-link-cn\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('Google Analytics (gtag)', 'gtag' in html.lower() or 'googletagmanager' in html.lower()),
    ('Google Analytics (ga.js)', 'google-analytics.com' in html.lower()),
    ('Baidu Tongji (百度统计)', 'hm.baidu.com' in html.lower()),
    ('Vercel Analytics', 'vercel' in html.lower() and 'analytics' in html.lower()),
    ('Microsoft Clarity', 'clarity.microsoft.com' in html.lower()),
    ('Plausible', 'plausible.io' in html.lower()),
    ('Umami', 'umami' in html.lower()),
    ('Cloudflare Analytics', 'cloudflareinsights.com' in html.lower()),
    ('Any tracking script', '<script' in html.lower() and 'src=' in html.lower()),
]

print("=== Analytics & Tracking Check ===")
for name, found in checks:
    status = '   [FOUND]' if found else '   [NONE]'
    print(f'{name}:{status}')

# Find all script sources
scripts = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', html)
print(f'\n=== External Scripts ({len(scripts)}) ===')
for s in scripts:
    print(f'  {s}')