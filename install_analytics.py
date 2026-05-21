#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install Baidu Tongji + Microsoft Clarity tracking into index.html
User needs to register and get real IDs, then replace placeholders.
"""
import re

INDEX_PATH = r'C:\Users\zhaoy\.qclaw\workspace-agent-5d8ec867\tool-link-cn\index.html'

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Baidu Tongji tracking code template
baidu_code = (
    '<!-- Baidu Tongji -->\n'
    '    <script>\n'
    '    var _hmt = _hmt || [];\n'
    '    (function() {\n'
    '        var hm = document.createElement("script");\n'
    '        hm.src = "https://hm.baidu.com/hm.js?BAIDU_TONGJI_ID";\n'
    '        var s = document.getElementsByTagName("script")[0];\n'
    '        s.parentNode.insertBefore(hm, s);\n'
    '    })();\n'
    '    </script>\n'
)

# Microsoft Clarity tracking code
clarity_code = (
    '<!-- Microsoft Clarity -->\n'
    '    <script type="text/javascript">\n'
    '    (function(c,l,a,r,i,t,y){\n'
    '        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};\n'
    '        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/CLARITY_PROJECT_ID";\n'
    '        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);\n'
    '    })(window, document, "clarity", "script", "CLARITY_PROJECT_ID");\n'
    '    </script>\n'
)

modified = False

# Only inject if not already present
if 'hm.baidu.com' not in html and 'BAIDU_TONGJI_ID' not in html:
    html = html.replace('</head>', baidu_code + '</head>')
    modified = True
    print("  + Baidu Tongji placeholder injected")

if 'clarity.ms' not in html and 'CLARITY_PROJECT_ID' not in html:
    html = html.replace('</head>', clarity_code + '</head>')
    modified = True
    print("  + Microsoft Clarity placeholder injected")

if not modified:
    print("Analytics already present, skipping injection")
else:
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Done. File size: {:,} chars".format(len(html)))
    print("")
    print("NEXT STEPS:")
    print("1. Register Baidu Tongji: https://tongji.baidu.com/")
    print("   Get your hm.js ID and replace BAIDU_TONGJI_ID in index.html")
    print("2. Register Microsoft Clarity: https://clarity.microsoft.com/")
    print("   Get your project ID and replace CLARITY_PROJECT_ID in index.html")
