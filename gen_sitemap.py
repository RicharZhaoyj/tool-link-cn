import os, glob
from datetime import datetime

base = 'https://tool.link.cn'
now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')

urls = []
urls.append(('/', '1.0', 'daily'))

cats = ['audio','coding','collab','design','image','marketing','productivity','research','sales','social','video','writing']
for c in cats:
    urls.append(('/category/' + c + '.html', '0.8', 'weekly'))

guides = sorted([os.path.basename(f)[:-5] for f in glob.glob('guides/*.html')])
for g in guides:
    urls.append(('/guides/' + g + '.html', '0.7', 'monthly'))

tools = sorted(glob.glob('tools/*.html'))
for t in tools:
    fname = os.path.basename(t)
    urls.append(('/tools/' + fname, '0.8', 'weekly'))

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
for path, prio, freq in urls:
    lines.append('  <url>')
    lines.append('    <loc>' + base + path + '</loc>')
    lines.append('    <lastmod>' + now + '</lastmod>')
    lines.append('    <changefreq>' + freq + '</changefreq>')
    lines.append('    <priority>' + prio + '</priority>')
    lines.append('  </url>')
lines.append('</urlset>')

with open('sitemap.xml','w',encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print('Generated sitemap with ' + str(len(urls)) + ' URLs')
