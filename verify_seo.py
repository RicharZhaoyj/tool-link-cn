import re
with open(r'C:\Users\zhaoy\.qclaw\workspace-agent-5d8ec867\tool-link-cn\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print('noscript found:', 'SEO_NOSCRIPT_START' in html)
print('Fliki in html:', 'Fliki' in html)

# Check meta description
m = re.search(r'name="description" content="([^"]+)"', html)
if m:
    print('meta description:', m.group(1)[:100])
else:
    print('meta description: NOT FOUND')

# Check file size
print('file size:', len(html), 'chars')
print('Fliki price tag present:', '$28' in html)
