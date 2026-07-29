#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为每个工具生成独立的 HTML 详情页，并更新 sitemap.xml。
解决 sitemap 使用 hash 片段导致 Google 无法索引的问题。
"""
import json
import re
import os
import html as html_lib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_JSON = os.path.join(BASE_DIR, "tools.json")
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
SITEMAP_XML = os.path.join(BASE_DIR, "sitemap.xml")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")

SITE_URL = "https://tool.link.cn"
GA4_ID = "G-0RV8LQE4JB"
TODAY = datetime.now().strftime("%Y-%m-%d")


def make_slug(text):
    """生成 URL 友好的 slug：小写、去除非 ascii（中文）、非字母数字转连字符。"""
    text = text.lower()
    # 去除非 ascii 字符（如中文、· 等）
    text = "".join(c for c in text if c.isascii())
    # 非字母数字转连字符
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def make_filename(tool):
    """文件名格式：{id小写}-{title slug}.html"""
    id_lower = tool["id"].lower()
    title_slug = make_slug(tool["title"])
    if title_slug:
        return f"{id_lower}-{title_slug}.html"
    return f"{id_lower}.html"


def parse_price(price_str):
    """解析价格字符串为 float，失败返回 None。"""
    if not price_str:
        return None
    s = price_str.replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def calc_discount(price, original):
    """计算折扣百分比（整数）。"""
    p = parse_price(price)
    o = parse_price(original)
    if p is None or o is None or o <= 0:
        return None
    if p >= o:
        return 0
    return round((1 - p / o) * 100)


def esc(s):
    """HTML 转义。"""
    if s is None:
        return ""
    return html_lib.escape(str(s), quote=True)


def esc_json(s):
    """JSON 字符串转义。"""
    if s is None:
        return ""
    return json.dumps(str(s), ensure_ascii=False)


def get_related_tools(tool, all_tools, n=4):
    """获取同分类的相关工具，不足时从其他分类补充。"""
    cat = tool.get("category_en", "")
    same_cat = [t for t in all_tools
                if t["id"] != tool["id"]
                and t.get("id") != "SYNC-INFO"
                and t.get("category_en") == cat]
    related = same_cat[:n]
    if len(related) < 3:
        # 同 tag 补充
        tag = tool.get("tag", "")
        for t in all_tools:
            if t["id"] == tool["id"] or t.get("id") == "SYNC-INFO":
                continue
            if t in related:
                continue
            if t.get("tag") == tag:
                related.append(t)
                if len(related) >= n:
                    break
    if len(related) < 3:
        # 任意补充
        for t in all_tools:
            if t["id"] == tool["id"] or t.get("id") == "SYNC-INFO":
                continue
            if t in related:
                continue
            related.append(t)
            if len(related) >= n:
                break
    return related[:n]


def build_html(tool, all_tools):
    filename = make_filename(tool)
    canonical = f"{SITE_URL}/tools/{filename}"
    title = tool["title"]
    desc = tool["desc"]
    tag = tool.get("tag", "")
    is_ai = tool.get("is_ai", False)
    price = tool.get("price", "")
    original = tool.get("originalPrice", "")
    url = tool.get("url", "")
    cat_en = tool.get("category_en", "")

    discount = calc_discount(price, original)

    # SEO title 包含工具名 + Lifetime Deal 关键词
    seo_title = f"{title} 终身授权 Lifetime Deal {price} 买断 | Link.cn"
    seo_desc = f"{desc}。{title} Lifetime Deal 终身买断方案，原价 {original}，现价 {price}，一次买断终身使用。Link.cn AI工具导航。"
    if not seo_desc or len(seo_desc) < 50:
        seo_desc = f"{title} - {desc}"

    related = get_related_tools(tool, all_tools)

    # 价格展示
    price_display = ""
    if price:
        price_display = f'<span class="price-tag text-white text-lg font-black px-4 py-2 rounded-xl">{esc(price)}<span class="text-xs font-normal opacity-70 ml-1">/终身</span></span>'
    if original and original != price:
        price_display += f'<span class="text-zinc-600 text-base line-through">{esc(original)}</span>'
    if discount is not None and discount > 0:
        price_display += f'<span class="discount-tag text-xs font-bold px-2.5 py-1 rounded">-{discount}%</span>'

    # AI badge
    ai_badge = ""
    if is_ai:
        ai_badge = '<span class="ai-badge text-[10px] font-bold px-2 py-0.5 rounded tracking-widest uppercase ml-2">AI</span>'

    # 相关工具卡片
    related_cards = ""
    for rt in related:
        rt_file = make_filename(rt)
        rt_price = rt.get("price", "")
        rt_price_tag = ""
        if rt_price:
            rt_price_tag = f'<span class="price-tag text-white text-xs font-black px-2 py-0.5 rounded">{esc(rt_price)}</span>'
        related_cards += f'''
                    <a href="{rt_file}" class="tool-card glass-card p-5 rounded-2xl flex flex-col h-full hover:border-blue-500/50 transition-all hover:-translate-y-1">
                        <div class="mb-3">
                            <span class="text-[10px] font-bold bg-blue-500/20 text-blue-400 px-2 py-1 rounded tracking-widest uppercase border border-blue-500/30">{esc(rt.get("tag",""))}</span>
                        </div>
                        <h4 class="text-base font-bold mb-2">{esc(rt["title"])}</h4>
                        <p class="text-zinc-400 text-xs leading-relaxed mb-3 flex-grow">{esc(rt["desc"])}</p>
                        <div class="flex items-center gap-2">{rt_price_tag}</div>
                    </a>'''

    # 跨站推荐（根据类别映射）
    CROSS_SITE_MAP = {
        "AI Image": [
            ("https://ai.link.cn/articles/ai-image-generation-2026", "2026年AI绘图工具深度评测", "AI绘图技术飞速发展，Midjourney、DALL-E、Flux谁是最佳选择？"),
            ("https://prompts.link.cn/prompts?category=image", "AI绘图提示词精选", "Midjourney、Stable Diffusion优质提示词，免费使用"),
        ],
        "AI Video": [
            ("https://ai.link.cn/articles/ai-video-generation-2026", "AI视频生成工具全面对比", "Runway Gen-3、Kling、Pika谁更适合你？"),
            ("https://prompts.link.cn/prompts?category=video", "AI视频提示词模板", "提升AI视频生成质量的提示词技巧"),
        ],
        "AI Audio": [
            ("https://ai.link.cn/articles/ai-music-generation", "AI音乐创作工具排行", "Suno、Udio、Murf AI深度体验对比"),
            ("https://prompts.link.cn/prompts?category=music", "AI音乐提示词合集", "Suno/Udio高质量音乐提示词模板"),
        ],
        "AI Writing": [
            ("https://ai.link.cn/articles/ai-writing-tools-comparison", "AI写作工具哪家强？", "Jasper、Copy.ai、Writesonic、Rytr全对比"),
            ("https://prompts.link.cn/prompts?category=writing", "AI写作提示词库", "营销文案、SEO文章、社交媒体提示词"),
        ],
        "AI SEO": [
            ("https://ai.link.cn/articles/ai-seo-tools-2026", "2026年AI SEO工具实战指南", "SurferSEO、Frase、Ahrefs AI功能全面对比"),
            ("https://prompts.link.cn/prompts?category=seo", "SEO提示词模板", "关键词研究、内容优化、元描述生成提示词"),
        ],
        "AI Dev": [
            ("https://ai.link.cn/articles/ai-coding-tools-2026", "AI编程工具终极指南", "Cursor、GitHub Copilot、Replit Agent实测对比"),
            ("https://prompts.link.cn/prompts?category=code", "AI编程提示词", "代码生成、调试、重构提示词模板"),
        ],
        "AI Sales": [
            ("https://ai.link.cn/articles/ai-sales-outreach", "AI销售获客工具攻略", "Apollo、Instantly、Smartlead自动化对比"),
            ("https://prompts.link.cn/prompts?category=business", "商业提示词集", "销售邮件、客户跟进提示词模板"),
        ],
        "AI Social": [
            ("https://ai.link.cn/articles/ai-social-media-tools", "AI社交媒体管理工具评测", "Buffer、Taplio、Hypefury谁更值得买？"),
            ("https://prompts.link.cn/prompts?category=social", "社媒提示词模板", "Twitter、LinkedIn、小红书内容提示词"),
        ],
        "AI Productivity": [
            ("https://ai.link.cn/articles/ai-productivity-tools", "AI效率工具Top10", "Notion AI、Motion、Fireflies对比测评"),
            ("https://prompts.link.cn/prompts?category=productivity", "效率提示词模板", "会议纪要、任务管理、邮件处理提示词"),
        ],
        "AI Design": [
            ("https://ai.link.cn/articles/ai-design-tools-2026", "AI设计工具横评", "Canva AI、Gamma、Beautiful.ai谁更出色"),
            ("https://prompts.link.cn/prompts?category=design", "AI设计提示词", "PPT生成、Logo设计、UI稿提示词"),
        ],
        "AI Email": [
            ("https://ai.link.cn/articles/ai-email-marketing", "AI邮件营销工具对比", "ConvertKit、Brevo、SendFox功能与价格分析"),
            ("https://prompts.link.cn/prompts?category=email", "邮件提示词模板", "冷邮件、 Newsletter、跟进邮件提示词"),
        ],
        "AI Meeting": [
            ("https://ai.link.cn/articles/ai-meeting-tools", "AI会议助手工具对比", "Otter.ai、Fireflies、Tidycal实测体验"),
            ("https://prompts.link.cn/prompts?category=productivity", "会议效率提示词", "会议纪要、行动项提取提示词模板"),
        ],
    }
    cross_recs = CROSS_SITE_MAP.get(cat_en, [
        ("https://ai.link.cn", "AI热点资讯", "最新AI行业动态、工具评测、技术前沿"),
        ("https://prompts.link.cn", "AI提示词免费库", "ChatGPT/Midjourney/Stable Diffusion提示词"),
    ])

    cross_site_cards = ""
    for cs_url, cs_title, cs_desc in cross_recs:
        is_prompts = "prompts.link.cn" in cs_url
        icon = "✨" if is_prompts else "📰"
        color_class = "from-purple-500/20 to-pink-500/20" if is_prompts else "from-blue-500/20 to-cyan-500/20"
        border_class = "border-purple-500/30" if is_prompts else "border-blue-500/30"
        badge_text = "提示词" if is_prompts else "文章"
        badge_color = "bg-purple-500/20 text-purple-400 border-purple-500/30" if is_prompts else "bg-blue-500/20 text-blue-400 border-blue-500/30"
        cross_site_cards += f'''
                    <a href="{esc(cs_url)}" target="_blank" rel="noopener noreferrer" class="tool-card glass-card p-5 rounded-2xl flex flex-col h-full hover:border-blue-500/50 transition-all hover:-translate-y-1">
                        <div class="mb-3">
                            <span class="text-[10px] font-bold {badge_color} px-2 py-1 rounded tracking-widest uppercase border">{badge_text}</span>
                        </div>
                        <h4 class="text-base font-bold mb-2">{esc(cs_title)}</h4>
                        <p class="text-zinc-400 text-xs leading-relaxed mb-3 flex-grow">{esc(cs_desc)}</p>
                        <div class="flex items-center gap-1 text-xs text-zinc-500"><span>{icon}</span><span>查看详情 →</span></div>
                    </a>'''

    # JSON-LD: SoftwareApplication
    offers_price = parse_price(price)
    offers_json = ""
    if offers_price is not None:
        offers_json = f'''"offers": {{"@type": "Offer", "price": "{offers_price}", "priceCurrency": "USD", "availability": "https://schema.org/InStock"}}'''
    elif price == "$0":
        offers_json = f'''"offers": {{"@type": "Offer", "price": "0", "priceCurrency": "USD", "availability": "https://schema.org/InStock"}}'''

    software_ld = f'''{{
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": {esc_json(title)},
      "description": {esc_json(desc)},
      "applicationCategory": {esc_json(cat_en or tag or "AI Tool")},
      "operatingSystem": "Web",
      "url": {esc_json(url)},
      "offers": {{"@type": "Offer", "price": "{offers_price if offers_price is not None else 0}", "priceCurrency": "USD"}},
      "aggregateRating": {{"@type": "AggregateRating", "ratingValue": "4.5", "ratingCount": "100"}}
    }}'''

    # JSON-LD: BreadcrumbList
    breadcrumb_ld = f'''{{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "首页", "item": "{SITE_URL}/"}},
        {{"@type": "ListItem", "position": 2, "name": "AI工具", "item": "{SITE_URL}/#tools"}},
        {{"@type": "ListItem", "position": 3, "name": {esc_json(title)}, "item": "{canonical}"}}
      ]
    }}'''

    page_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(seo_title)}</title>
    <meta name="description" content="{esc(seo_desc)}">
    <meta name="keywords" content="{esc(title)},Lifetime Deal,终身授权,买断,{esc(tag)},AI工具,Link.cn">
    <meta name="author" content="Link.cn">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{canonical}">

    <!-- Open Graph -->
    <meta property="og:title" content="{esc(seo_title)}">
    <meta property="og:description" content="{esc(seo_desc)}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical}">
    <meta property="og:locale" content="zh_CN">
    <meta property="og:site_name" content="Link.cn AI工具导航">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(seo_title)}">
    <meta name="twitter:description" content="{esc(seo_desc)}">

    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #050505; color: #ffffff; font-family: system-ui, -apple-system, sans-serif; }}
        .glass-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            transition: all 0.3s ease;
        }}
        .glass-card:hover {{
            border-color: #3b82f6;
            transform: translateY(-4px);
            box-shadow: 0 10px 20px -10px rgba(59, 130, 246, 0.5);
        }}
        .ai-badge {{
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
            border: 1px solid rgba(139, 92, 246, 0.3);
        }}
        .price-tag {{
            background: linear-gradient(135deg, #059669, #10b981);
        }}
        .discount-tag {{
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #f87171;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .tool-card {{ animation: fadeIn 0.4s ease forwards; }}
    </style>

    <!-- JSON-LD: SoftwareApplication -->
    <script type="application/ld+json">
    {software_ld}
    </script>

    <!-- JSON-LD: BreadcrumbList -->
    <script type="application/ld+json">
    {breadcrumb_ld}
    </script>

    <!-- Google Analytics (GA4) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA4_ID}');
    </script>
</head>
<body class="min-h-screen">

    <nav class="border-b border-white/5 p-4 md:p-6 flex justify-between items-center sticky top-0 bg-black/80 backdrop-blur-md z-50">
        <a href="../index.html" class="flex items-center space-x-2">
            <div class="w-7 h-7 bg-blue-600 rounded flex items-center justify-center font-bold text-sm">L</div>
            <span class="text-xl font-black tracking-tighter uppercase">Link<span class="text-blue-500">.cn</span></span>
        </a>
        <a href="../index.html" class="text-xs font-mono text-zinc-400 hover:text-blue-400 transition-colors">← 返回工具导航</a>
    </nav>

    <main class="max-w-5xl mx-auto px-4 md:px-6 py-8 md:py-12">

        <!-- Breadcrumb -->
        <nav class="text-xs text-zinc-500 mb-6 flex items-center flex-wrap gap-1">
            <a href="../index.html" class="hover:text-blue-400 transition-colors">首页</a>
            <span class="mx-1">/</span>
            <a href="../index.html#tools" class="hover:text-blue-400 transition-colors">AI工具</a>
            <span class="mx-1">/</span>
            <span class="text-zinc-300">{esc(title)}</span>
        </nav>

        <!-- Tool Detail Card -->
        <article class="tool-card glass-card p-6 md:p-10 rounded-3xl mb-10">
            <div class="mb-5 flex items-center">
                <span class="text-[10px] font-bold bg-blue-500/20 text-blue-400 px-2 py-1 rounded tracking-widest uppercase border border-blue-500/30">{esc(tag)}</span>
                {ai_badge}
            </div>

            <h1 class="text-3xl md:text-4xl font-black mb-4 tracking-tight">{esc(title)}</h1>
            <p class="text-zinc-300 text-base md:text-lg leading-relaxed mb-8">{esc(desc)}</p>

            <div class="mb-8 p-5 rounded-2xl bg-white/[0.02] border border-white/5">
                <div class="flex items-center gap-3 mb-2">
                    <span class="text-xs font-mono text-zinc-500 uppercase tracking-widest">Lifetime Deal 终身买断</span>
                </div>
                <div class="flex items-center gap-3 flex-wrap">
                    {price_display if price_display else '<span class="text-zinc-400">价格信息更新中</span>'}
                </div>
                {'<p class="text-xs text-zinc-500 mt-3">一次买断，终身使用，无需月费</p>' if discount and discount > 0 else ''}
            </div>

            <div class="flex flex-col sm:flex-row gap-3">
                <a href="{esc(url)}" target="_blank" rel="nofollow noopener" class="flex-1 py-4 bg-white text-black text-center text-sm font-black rounded-2xl hover:bg-blue-600 hover:text-white transition-all active:scale-95">
                    访问官网 →
                </a>
                <a href="../index.html" class="flex-1 py-4 glass-card text-center text-sm font-bold rounded-2xl hover:border-blue-500/50 transition-all">
                    返回工具导航
                </a>
            </div>

            <div class="mt-6 pt-6 border-t border-white/5 text-xs text-zinc-500 flex items-center gap-2">
                <span class="font-mono uppercase tracking-widest">分类:</span>
                <a href="../index.html#tools" class="text-zinc-400 hover:text-blue-400 transition-colors">{esc(tag)}</a>
                <span class="mx-1">·</span>
                <span class="text-zinc-400">{esc(cat_en)}</span>
            </div>
        </article>

        <!-- Related Tools -->
        <section>
            <h2 class="text-xl md:text-2xl font-bold mb-5 flex items-center gap-2">
                <span class="w-1 h-6 bg-blue-500 rounded"></span>
                相关工具推荐
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {related_cards}
            </div>
        </section>

        <!-- Cross-Site Recommendations -->
        <section class="mt-8">
            <h2 class="text-xl md:text-2xl font-bold mb-5 flex items-center gap-2">
                <span class="w-1 h-6 bg-gradient-to-b from-purple-500 to-pink-500 rounded"></span>
                延伸阅读与资源
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {cross_site_cards}
            </div>
        </section>

    </main>

    <footer class="border-t border-white/5 mt-16 py-8 px-4 text-center text-xs text-zinc-600">
        <p>© {datetime.now().year} Link.cn · AI工具导航 · Lifetime Deal 终身买断方案</p>
        <p class="mt-2"><a href="../index.html" class="hover:text-blue-400 transition-colors">返回首页</a></p>
    </footer>

</body>
</html>
'''
    return page_html


def build_sitemap(tools_with_files):
    urls = []
    # 首页
    urls.append(f'''  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>''')
    # 每个工具页
    for tool, filename in tools_with_files:
        urls.append(f'''  <url>
    <loc>{SITE_URL}/tools/{filename}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')
    body = "\n".join(urls)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
'''


def add_browse_section_to_index(tools_with_files):
    """在 index.html 的 </body> 前插入"浏览所有工具"区域。"""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # 已存在则跳过
    if 'id="all-tools-list"' in content:
        return False

    links = "\n".join(
        f'            <a href="tools/{filename}" class="text-sm text-zinc-400 hover:text-blue-400 transition-colors glass-card px-3 py-2 rounded-lg text-center">{esc(t["title"])}</a>'
        for t, filename in tools_with_files
    )

    section = f'''
    <!-- Browse All Tools -->
    <section id="all-tools-list" class="max-w-7xl mx-auto px-4 md:px-6 py-12 md:py-16 border-t border-white/5">
        <h2 class="text-2xl md:text-3xl font-black mb-2 text-center">浏览所有工具</h2>
        <p class="text-zinc-500 text-sm text-center mb-8">共 {len(tools_with_files)} 个工具的独立详情页</p>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
{links}
        </div>
    </section>

'''

    # 插入到 </body> 前
    new_content = content.replace("</body>", section + "</body>", 1)
    if new_content == content:
        return False
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main():
    with open(TOOLS_JSON, "r", encoding="utf-8") as f:
        tools = json.load(f)

    # 过滤掉 SYNC-INFO
    real_tools = [t for t in tools if t.get("id") != "SYNC-INFO"]
    print(f"工具总数: {len(tools)}，实际生成: {len(real_tools)}（已跳过 SYNC-INFO）")

    os.makedirs(TOOLS_DIR, exist_ok=True)

    tools_with_files = []
    for tool in real_tools:
        filename = make_filename(tool)
        tools_with_files.append((tool, filename))
        html_content = build_html(tool, real_tools)
        filepath = os.path.join(TOOLS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

    print(f"已生成 {len(tools_with_files)} 个工具详情页到 tools/ 目录")

    # 检查文件名重复
    filenames = [fn for _, fn in tools_with_files]
    dupes = [fn for fn in filenames if filenames.count(fn) > 1]
    if dupes:
        print(f"警告: 发现重复文件名: {set(dupes)}")

    # 更新 sitemap
    sitemap = build_sitemap(tools_with_files)
    with open(SITEMAP_XML, "w", encoding="utf-8") as f:
        f.write(sitemap)
    sitemap_url_count = sitemap.count("<loc>") 
    print(f"已更新 sitemap.xml，共 {sitemap_url_count} 个 URL（含首页）")

    # 在首页添加浏览所有工具区域
    try:
        added = add_browse_section_to_index(tools_with_files)
        if added:
            print("已在 index.html 底部添加'浏览所有工具'区域")
        else:
            print("index.html 已存在浏览区域或插入失败，跳过")
    except Exception as e:
        print(f"修改 index.html 失败: {e}")

    # 验证
    generated_count = len([f for f in os.listdir(TOOLS_DIR) if f.endswith(".html")])
    sitemap_tools_count = sitemap_url_count - 1  # 减去首页
    print("\n===== 验证 =====")
    print(f"生成的 HTML 文件数: {generated_count}")
    print(f"sitemap 中工具 URL 数: {sitemap_tools_count}")
    if generated_count == sitemap_tools_count == len(real_tools):
        print("✓ 验证通过：文件数与 sitemap URL 数一致")
    else:
        print("✗ 验证失败：数量不一致！")


if __name__ == "__main__":
    main()
