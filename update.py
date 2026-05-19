import json
import os
import re
import requests
from datetime import datetime

# ============================================================
# Link.cn 数据更新脚本 v2.0
# 变更: 移除 Impact API / AppSumo 联盟依赖
# 数据源: 手动精选(主) + StackSocial/Dealify 抓取(辅) + 其他LTD平台
# 链接策略: 官网直链 (后续接入联盟后可批量替换)
# ============================================================

# 中文分类映射 (扩展版)
CATEGORY_MAP = {
    "Social media": "社交媒体",
    "Calendar & scheduling": "日历排期",
    "Development tools": "AI开发",
    "Productivity": "效率工具",
    "Lead generation": "获客引流",
    "Video": "AI视频",
    "SEO": "SEO优化",
    "Audio": "AI音频",
    "Content marketing": "内容营销",
    "Project management": "项目管理",
    "Email marketing": "邮件营销",
    "Design": "设计工具",
    "Analytics": "数据分析",
    "Customer support": "客户支持",
    "E-commerce": "电商工具",
    "Writing": "AI写作",
    "AI": "AI工具",
    "Marketing": "营销工具",
    "Sales": "销售工具",
    "HR": "人事管理",
    "Finance": "财务工具",
    "Education": "教育学习",
    "Image": "AI绘图",
    "Voice": "语音工具",
    "Automation": "自动化",
}

# AI 工具关键词（用于自动打标签）
AI_KEYWORDS = [
    "ai", "artificial intelligence", "chatgpt", "gpt", "claude", "gemini",
    "machine learning", "ml", "automation", "smart", "intelligent",
    "neural", "deep learning", "nlp", "natural language", "copilot",
    "assistant", "generative", "llm", "openai", "anthropic", "midjourney",
    "dall-e", "stable diffusion", "whisper", "tts", "text-to-speech",
    "text-to-image", "image generation", "voice clone"
]


def get_category_tag(category_en):
    """将英文分类转为中文标签"""
    if not category_en:
        return "AI工具"
    for key, val in CATEGORY_MAP.items():
        if key.lower() in category_en.lower():
            return val
    cat_lower = category_en.lower()
    for kw in AI_KEYWORDS:
        if kw in cat_lower:
            return "AI工具"
    return "精选工具"


def is_ai_tool(name, desc=""):
    """判断是否为 AI 工具"""
    text = f"{name} {desc}".lower()
    for kw in AI_KEYWORDS:
        if kw in text:
            return True
    return False


def get_discount_percent(price_str, original_str):
    """计算折扣百分比"""
    try:
        p = float(re.sub(r'[^\d.]', '', price_str or ''))
        o = float(re.sub(r'[^\d.]', '', original_str or ''))
        if o > 0:
            return round((1 - p / o) * 100)
    except:
        pass
    return None


# ============================================================
# 数据源 1: 手动精选工具库 (主数据源 - 50+ 工具)
# 所有链接均为官网直链，不含联盟参数
# ============================================================

def get_manual_curated_deals():
    """手动精选 AI/SaaS 工具库 — 主数据源"""
    return [
        # ===== AI 写作类 =====
        {
            "id": "CUR-001",
            "tag": "AI写作",
            "title": "Jasper",
            "desc": "企业级 AI 内容创作平台，支持博客、广告、邮件、社媒等多场景，内置品牌语调管理",
            "price": "$49",
            "originalPrice": "$99",
            "url": "https://www.jasper.ai/",
            "category_en": "Writing",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-002",
            "tag": "AI写作",
            "title": "Copy.ai",
            "desc": "AI 文案生成器，一键生成营销文案、博客文章、社媒内容，支持多语言",
            "price": "$36",
            "originalPrice": "$96",
            "url": "https://www.copy.ai/",
            "category_en": "Writing",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-003",
            "tag": "AI写作",
            "title": "Writesonic",
            "desc": "全能 AI 写作助手，支持 SEO 文章、产品描述、广告文案、故事创作等 80+ 模板",
            "price": "$39",
            "originalPrice": "$119",
            "url": "https://writesonic.com/",
            "category_en": "Writing",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-004",
            "tag": "AI写作",
            "title": "Rytr",
            "desc": "轻量级 AI 写作工具，40+ 用例模板，适合个人创作者和小团队",
            "price": "$29",
            "originalPrice": "$90",
            "url": "https://rytr.me/",
            "category_en": "Writing",
            "is_ai": True,
            "source": "curated"
        },

        # ===== AI 绘图类 =====
        {
            "id": "CUR-010",
            "tag": "AI绘图",
            "title": "Midjourney",
            "desc": "顶级 AI 图像生成器，艺术风格多样，细节表现力强，设计师和艺术家首选",
            "price": "$10",
            "originalPrice": "$30",
            "url": "https://www.midjourney.com/",
            "category_en": "Image",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-011",
            "tag": "AI绘图",
            "title": "DALL·E 3 (ChatGPT Plus)",
            "desc": "OpenAI 出品，文字理解能力最强，可直接在 ChatGPT 中生成和编辑图片",
            "price": "$20",
            "originalPrice": "$20",
            "url": "https://openai.com/dall-e-3/",
            "category_en": "Image",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-012",
            "tag": "AI绘图",
            "title": "Leonardo.ai",
            "desc": "免费 AI 图像生成与画布编辑，支持角色一致性、模型训练，游戏/漫画创作者利器",
            "price": "$0",
            "originalPrice": "$19",
            "url": "https://leonardo.ai/",
            "category_en": "Image",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-013",
            "tag": "AI绘图",
            "title": "Ideogram",
            "desc": "AI 图像生成新秀，文字渲染能力突出，Logo 和海报设计神器",
            "price": "$0",
            "originalPrice": "$15",
            "url": "https://ideogram.ai/",
            "category_en": "Image",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-014",
            "tag": "AI绘图",
            "title": "Flux (Black Forest Labs)",
            "desc": "开源图像生成模型，画质媲美 Midjourney，支持本地部署和 API 调用",
            "price": "$0",
            "originalPrice": "$20",
            "url": "https://blackforestlabs.ai/",
            "category_en": "Image",
            "is_ai": True,
            "source": "curated"
        },

        # ===== AI 视频类 =====
        {
            "id": "CUR-020",
            "tag": "AI视频",
            "title": "Runway Gen-3",
            "desc": "好莱坞级 AI 视频生成，文生视频/图生视频，Motion Brush 精准控制运动轨迹",
            "price": "$12",
            "originalPrice": "$76",
            "url": "https://runwayml.com/",
            "category_en": "Video",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-021",
            "tag": "AI视频",
            "title": "Pika Labs",
            "desc": "AI 视频生成与编辑，支持 Lip Sync 口型同步、视频扩展、风格转换",
            "price": "$0",
            "originalPrice": "$20",
            "url": "https://pika.art/",
            "category_en": "Video",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-022",
            "tag": "AI视频",
            "title": "Kling AI (快手)",
            "desc": "国产 AI 视频生成黑马，2分钟超长视频生成，物理模拟逼真，免费可用",
            "price": "$0",
            "originalPrice": "$15",
            "url": "https://klingai.com/",
            "category_en": "Video",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-023",
            "tag": "AI视频",
            "title": "HeyGen",
            "desc": "AI 数字人视频生成，口型同步精准，100+ 语音可选，支持照片说话功能",
            "price": "$24",
            "originalPrice": "$120",
            "url": "https://www.heygen.com/",
            "category_en": "Video",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-024",
            "tag": "AI视频",
            "title": "Opus Clip",
            "desc": "AI 一键将长视频剪辑成短视频 Viral Clips，自动添加字幕和表情符号",
            "price": "$19",
            "originalPrice": "$79",
            "url": "https://www.opus.pro/",
            "category_en": "Video",
            "is_ai": True,
            "source": "curated"
        },

        # ===== AI 音频/语音类 =====
        {
            "id": "CUR-030",
            "tag": "AI音频",
            "title": "ElevenLabs",
            "desc": "业界最强 AI 语音合成，29种语言，情感控制精细，声音克隆效果惊人",
            "price": "$5",
            "originalPrice": "$22",
            "url": "https://elevenlabs.io/",
            "category_en": "Audio",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-031",
            "tag": "AI音频",
            "title": "Murf.ai",
            "desc": "专业 AI 配音工具，120+ 语音，内置视频编辑器，适合教程/营销视频制作",
            "price": "$19",
            "originalPrice": "$78",
            "url": "https://murf.ai/",
            "category_en": "Audio",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-032",
            "tag": "AI音频",
            "title": "Suno AI",
            "desc": "AI 音乐生成，输入文字即可生成完整歌曲，支持多种音乐风格和乐器编排",
            "price": "$0",
            "originalPrice": "$10",
            "url": "https://suno.com/",
            "category_en": "Audio",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-033",
            "tag": "AI音频",
            "title": "Udio",
            "desc": "AI 音乐创作平台，高质量音乐生成，支持歌词到歌曲的完整流程",
            "price": "$0",
            "originalPrice": "$10",
            "url": "https://www.udio.com/",
            "category_en": "Audio",
            "is_ai": True,
            "source": "curated"
        },

        # ===== AI 效率/办公类 =====
        {
            "id": "CUR-040",
            "tag": "效率工具",
            "title": "Notion AI",
            "desc": "Notion 内置 AI 助手，写作、总结、翻译、数据库查询一体化，知识管理首选",
            "price": "$8",
            "originalPrice": "$16",
            "url": "https://www.notion.so/product/ai",
            "category_en": "Productivity",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-041",
            "tag": "效率工具",
            "title": "Motion",
            "desc": "AI 日历助手，自动安排会议时间，智能调度日历，与 Google Calendar 深度集成",
            "price": "$19",
            "originalPrice": "$34",
            "url": "https://usemotion.com/",
            "category_en": "Productivity",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-042",
            "tag": "效率工具",
            "title": "Otter.ai",
            "desc": "AI 会议记录，实时转录+自动总结+行动项提取，支持 Zoom/Teams/Google Meet",
            "price": "$8",
            "originalPrice": "$17",
            "url": "https://otter.ai/",
            "category_en": "Productivity",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-043",
            "tag": "效率工具",
            "title": "Fireflies.ai",
            "desc": "AI 会议笔记助手，自动录制会议、转录、标记关键决策，CRM 集成",
            "price": "$18",
            "originalPrice": "$39",
            "url": "https://fireflies.ai/",
            "category_en": "Productivity",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-044",
            "tag": "效率工具",
            "title": "TidyCal",
            "desc": "强大的日程安排软件，自定义会议类型，集成主流日历，无限预约",
            "price": "$29",
            "originalPrice": "$144",
            "url": "https://tidycal.com/",
            "category_en": "Calendar & scheduling",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-045",
            "tag": "效率工具",
            "title": "BreezeDoc",
            "desc": "简洁的电子签名工具，简化文档签署流程，法律效力保障",
            "price": "$19",
            "originalPrice": "$180",
            "url": "https://breezedoc.com/",
            "category_en": "Productivity",
            "is_ai": False,
            "source": "curated"
        },

        # ===== AI 开发/编程类 =====
        {
            "id": "CUR-050",
            "tag": "AI开发",
            "title": "GitHub Copilot",
            "desc": "微软出品 AI 编程助手，代码补全、聊天、Agent 三合一，支持所有主流语言",
            "price": "$10",
            "originalPrice": "$19",
            "url": "https://github.com/features/copilot",
            "category_en": "Development tools",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-051",
            "tag": "AI开发",
            "title": "Cursor",
            "desc": "AI 原生代码编辑器，基于 VS Code，代码库级理解，Tab 补全体验丝滑",
            "price": "$20",
            "originalPrice": "$40",
            "url": "https://cursor.sh/",
            "category_en": "Development tools",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-052",
            "tag": "AI开发",
            "title": "v0 by Vercel",
            "desc": "用自然语言生成 React/Tailwind UI 组件，前端开发者效率倍增器",
            "price": "$0",
            "originalPrice": "$20",
            "url": "https://v0.dev/",
            "category_en": "Development tools",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-053",
            "tag": "AI开发",
            "title": "Replit Agent",
            "desc": "浏览器内 AI 编程 Agent，从想法到部署一站式完成，无需本地环境配置",
            "price": "$7",
            "originalPrice": "$25",
            "url": "https://replit.com/",
            "category_en": "Development tools",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-054",
            "tag": "AI开发",
            "title": "Bolt.new (StackBlitz)",
            "desc": "浏览器中用 AI 构建和部署全栈应用，Prompt 直接出可运行项目",
            "price": "$0",
            "originalPrice": "$20",
            "url": "https://bolt.new/",
            "category_en": "Development tools",
            "is_ai": True,
            "source": "curated"
        },

        # ===== SEO / 营销类 =====
        {
            "id": "CUR-060",
            "tag": "SEO优化",
            "title": "SurferSEO",
            "desc": "AI SEO 内容优化器，分析 Top 排名页面，给出具体优化建议，提升排名",
            "price": "$29",
            "originalPrice": "$129",
            "url": "https://surferseo.com/",
            "category_en": "SEO",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-061",
            "tag": "SEO优化",
            "title": "Frase.io",
            "desc": "AI 内容研究 + 写作 + SEO 优化一体化，从研究到发布全流程覆盖",
            "price": "$14.99",
            "originalPrice": "$114",
            "url": "https://frase.io/",
            "category_en": "SEO",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-062",
            "tag": "SEO优化",
            "title": "Ahrefs",
            "desc": "全网最强 SEO 工具套件，关键词研究、竞品分析、外链监控、排名追踪",
            "price": "$49",
            "originalPrice": "$199",
            "url": "https://ahrefs.com/",
            "category_en": "Analytics",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-063",
            "tag": "内容营销",
            "title": "Canva Pro",
            "desc": "在线设计神器，海量模板 + AI 图片生成 + 团队协作，非设计师也能做出专业作品",
            "price": "$6.49",
            "originalPrice": "$55",
            "url": "https://www.canva.com/pro/",
            "category_en": "Design",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-064",
            "tag": "内容营销",
            "title": "Descript",
            "desc": "像编辑文档一样编辑视频/音频，AI 语音克隆 + 自动去除填充词 + 字幕生成",
            "price": "$24",
            "originalPrice": "$60",
            "url": "https://www.descript.com/",
            "category_en": "Content marketing",
            "is_ai": True,
            "source": "curated"
        },

        # ===== 获客/销售类 =====
        {
            "id": "CUR-070",
            "tag": "获客引流",
            "title": "Apollo.io",
            "desc": "B2B 销售情报平台，2亿+联系人数据库，邮箱验证 + 外联自动化",
            "price": "$24",
            "originalPrice": "$99",
            "url": "https://www.apollo.io/",
            "category_en": "Lead generation",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-071",
            "tag": "获客引流",
            "title": "Instantly.ai",
            "desc": "冷邮件自动化 + 邮箱预热 + 收件箱保护，B2B 获客三件套",
            "price": "$37",
            "originalPrice": "$97",
            "url": "https://instantly.ai/",
            "category_en": "Lead generation",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-072",
            "tag": "获客引流",
            "title": "Smartlead.ai",
            "desc": "大规模冷邮件发送平台，无限发送账号，AI 优化送达率",
            "price": "$34",
            "originalPrice": "$94",
            "url": "https://smartlead.ai/",
            "category_en": "Email marketing",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-073",
            "tag": "获客引流",
            "title": "Clay",
            "desc": "AI 增强的 B2B 数据 enrichment 平台，50+ 数据源整合，个性化外联规模化",
            "price": "$149",
            "originalPrice": "$800",
            "url": "https://www.clay.com/",
            "category_en": "Lead generation",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-074",
            "tag": "社交媒体",
            "title": "Buffer",
            "desc": "社媒排程发布工具，统一管理多平台内容，最佳发布时间 AI 推荐",
            "price": "$6",
            "originalPrice": "$24",
            "url": "https://buffer.com/",
            "category_en": "Social media",
            "is_ai": False,
            "source": "curated"
        },

        # ===== 社交媒体/客服类 =====
        {
            "id": "CUR-080",
            "tag": "社交媒体",
            "title": "Taplio",
            "desc": "LinkedIn 增长工具，AI 内容灵感 + 排程发布 + 关系管理，个人品牌打造必备",
            "price": "$27",
            "originalPrice": "$83",
            "url": "https://taplio.com/",
            "category_en": "Social media",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-081",
            "tag": "社交媒体",
            "title": "Hypefury",
            "desc": "Twitter/X 增长工具，AI 写推文 + 自动转发 + 排程发布 + 分析统计",
            "price": "$19",
            "originalPrice": "$48",
            "url": "https://hypefury.com/",
            "category_en": "Social media",
            "is_ai": True,
            "source": "curated"
        },

        # ===== 项目管理类 =====
        {
            "id": "CUR-090",
            "tag": "项目管理",
            "title": "ClickUp",
            "desc": "全能项目管理平台，任务/文档/目标/白板/Chat 全集成，AI 助手加持",
            "price": "$7",
            "originalPrice": "$19",
            "url": "https://clickup.com/",
            "category_en": "Project management",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-091",
            "tag": "项目管理",
            "title": "Notion",
            "desc": "全能工作空间，笔记/项目/ Wiki/数据库一体，模板生态丰富，个人团队都适用",
            "price": "$0",
            "originalPrice": "$10",
            "url": "https://www.notion.so/",
            "category_en": "Project management",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-092",
            "tag": "项目管理",
            "title": "NextStep",
            "desc": "构建标准作业流程(SOP)和工作流，动态截止日期+实时追踪",
            "price": "$39",
            "originalPrice": "$129",
            "url": "https://nextstep.so/",
            "category_en": "Project management",
            "is_ai": False,
            "source": "curated"
        },

        # ===== 邮件营销类 =====
        {
            "id": "CUR-100",
            "tag": "邮件营销",
            "title": "ConvertKit",
            "desc": "创作者友好型邮件营销平台，自动化序列 + 表单 + 标签系统，订阅者变现首选",
            "price": "$9",
            "originalPrice": "$59",
            "url": "https://convertkit.com/",
            "category_en": "Email marketing",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-101",
            "tag": "邮件营销",
            "title": "SendFox",
            "desc": "经济实惠的邮件营销工具，自动化邮件增长，无需昂贵月费",
            "price": "$49",
            "originalPrice": "$480",
            "url": "https://sendfox.com/",
            "category_en": "Email marketing",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-102",
            "tag": "邮件营销",
            "title": "Brevo (原 Sendinblue)",
            "desc": "全能营销平台，邮件+短信+WhatsApp+聊天，免费版含每日300封邮件",
            "price": "$9",
            "originalPrice": "$65",
            "url": "https://www.brevo.com/",
            "category_en": "Email marketing",
            "is_ai": True,
            "source": "curated"
        },

        # ===== 设计/创意类 =====
        {
            "id": "CUR-110",
            "tag": "设计工具",
            "title": "Figma",
            "desc": "协作式 UI/UX 设计工具，原型+设计系统+开发交付，全球设计师标配",
            "price": "$0",
            "originalPrice": "$15",
            "url": "https://www.figma.com/",
            "category_en": "Design",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-111",
            "tag": "设计工具",
            "title": "Gamma",
            "desc": "AI 演示文稿/PPT 生成器，输入主题自动生成精美幻灯片，告别模板搬运",
            "price": "$0",
            "originalPrice": "$15",
            "url": "https://gamma.app/",
            "category_en": "Design",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-112",
            "tag": "设计工具",
            "title": "Beautiful.ai",
            "desc": "AI 驱动的 PPT 设计工具，智能排版自适应，专业演示零门槛",
            "price": "$12",
            "originalPrice": "$44",
            "url": "https://www.beautiful.ai/",
            "category_en": "Design",
            "is_ai": True,
            "source": "curated"
        },

        # ===== 个人效率/生活类 =====
        {
            "id": "CUR-120",
            "tag": "效率工具",
            "title": "Journal it!",
            "desc": "日记+规划+笔记+习惯+追踪，一站式加密私人生活管理器",
            "price": "$39",
            "originalPrice": "$99",
            "url": "https://journal-it.app/",
            "category_en": "Productivity",
            "is_ai": False,
            "source": "curated"
        },
        {
            "id": "CUR-121",
            "tag": "效率工具",
            "title": "Shareables",
            "desc": "连接 Google Sheets/Airtable/Notion，零代码生成自定义网站",
            "price": "$59",
            "originalPrice": "$96",
            "url": "https://shareables.co/",
            "category_en": "Productivity",
            "is_ai": False,
            "source": "curated"
        },

        # ===== AI 对话/搜索类 =====
        {
            "id": "CUR-130",
            "tag": "AI工具",
            "title": "Perplexity AI",
            "desc": "AI 搜索引擎，实时联网检索+引用来源，比传统搜索引擎更智能的回答",
            "price": "$0",
            "originalPrice": "$20",
            "url": "https://www.perplexity.ai/",
            "category_en": "AI",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-131",
            "tag": "AI工具",
            "title": "You.com",
            "desc": "隐私优先的 AI 搜索引擎，支持自定义模式切换，无追踪无广告",
            "price": "$0",
            "originalPrice": "$15",
            "url": "https://you.com/",
            "category_en": "AI",
            "is_ai": True,
            "source": "curated"
        },
        {
            "id": "CUR-132",
            "tag": "AI工具",
            "title": "NotebookLM (Google)",
            "desc": "Google 出品 AI 笔记助手，上传资料自动生成播客/学习指南/问答",
            "price": "$0",
            "originalPrice": "$0",
            "url": "https://notebooklm.google.com/",
            "category_en": "AI",
            "is_ai": True,
            "source": "curated"
        },
    ]


# ============================================================
# 数据源 2: StackSocial 抓取 (辅助)
# ============================================================

def scrape_stacksocial():
    """从 StackSocial 抓取当前 LTD"""
    items = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        }
        resp = requests.get('https://stacksocial.com/deals', headers=headers, timeout=15)
        if resp.status_code == 200:
            html = resp.text
            # 提取 deal 信息
            product_pattern = re.compile(r'<a[^>]*href="(/deals/[^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
            price_pattern = re.compile(r'\$(\d+(?:,\d+)*)')
            matches = product_pattern.findall(html)[:20]
            for url_path, content in matches[:15]:
                name_match = re.search(r'>([^<]{4,60})<', content)
                if name_match:
                    name = name_match.group(1).strip()
                    if len(name) > 3 and not any(x in name.lower() for x in ['script', 'div', 'class']):
                        items.append({
                            "id": f"SS-{hash(name) % 100000:05d}",
                            "tag": get_category_tag(""),
                            "title": name,
                            "desc": f"StackSocial 限时优惠，一次买断终身使用",
                            "price": "",
                            "originalPrice": "",
                            "url": f"https://stacksocial.com{url_path}" if url_path.startswith('/') else url_path,
                            "category_en": "",
                            "is_ai": is_ai_tool(name),
                            "source": "stacksocial"
                        })
            print(f"StackSocial scrape: {len(items)} items")
    except Exception as e:
        print(f"StackSocial scrape failed: {e}")
    return items


# ============================================================
# 数据源 3: Dealify 抓取 (辅助)
# ============================================================

def scrape_dealify():
    """从 Dealify 抓取 LTD"""
    items = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        resp = requests.get('https://dealify.com/deals', headers=headers, timeout=15)
        if resp.status_code == 200:
            html = resp.text
            # 简单提取
            title_pattern = re.compile(r'<h[23][^>]*>([^<]+(?:Deal|Lifetime|App|Tool|AI)[^<]*)</h[23]>', re.IGNORECASE)
            titles = list(set(title_pattern.findall(html)))[:15]
            for t in titles:
                clean_t = re.sub(r'<[^>]+>', '', t).strip()
                if len(clean_t) > 3:
                    items.append({
                        "id": f"DF-{hash(clean_t) % 100000:05d}",
                        "tag": get_category_tag(clean_t),
                        "title": clean_t,
                        "desc": "Dealify SaaS Lifetime Deal",
                        "price": "",
                        "originalPrice": "",
                        "url": "https://dealify.com/deals",
                        "category_en": "",
                        "is_ai": is_ai_tool(clean_t),
                        "source": "dealify"
                    })
            print(f"Dealify scrape: {len(items)} items")
    except Exception as e:
        print(f"Dealify scrape failed: {e}")
    return items


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(base_path, 'tools.json')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    all_items = []

    # 1. 系统状态信息
    all_items.append({
        "id": "SYNC-INFO",
        "tag": "SYSTEM",
        "title": f"Sync Time: {now_str}",
        "desc": "Link.cn 数据同步完成 | v2.0 多源数据",
        "url": "https://tool.link.cn",
        "price": "",
        "originalPrice": "",
        "category_en": "",
        "is_ai": False,
        "source": "system"
    })

    # 2. 手动精选数据（主数据源）
    curated = get_manual_curated_deals()
    print(f"Curated data: {len(curated)} tools")
    all_items.extend(curated)

    # 3. StackSocial 抓取（辅助数据源）
    ss_items = scrape_stacksocial()
    if ss_items:
        existing_titles = {item['title'].lower() for item in all_items}
        for item in ss_items:
            if item['title'].lower() not in existing_titles:
                all_items.append(item)
                existing_titles.add(item['title'].lower())

    # 4. Dealify 抓取（辅助数据源）
    df_items = scrape_dealify()
    if df_items:
        existing_titles = {item['title'].lower() for item in all_items}
        for item in df_items:
            if item['title'].lower() not in existing_titles:
                all_items.append(item)
                existing_titles.add(item['title'].lower())

    # 保留已有联盟链接（防止自动同步覆盖）
    try:
        if os.path.exists(target_file):
            with open(target_file, 'r', encoding='utf-8') as f:
                old_items = json.load(f)
            affiliate_items = [t for t in old_items if t.get('source') == 'affiliate']
            existing_ids = {t['id'] for t in all_items}
            for aff in affiliate_items:
                if aff['id'] not in existing_ids:
                    all_items.append(aff)
                    existing_ids.add(aff['id'])
                    print(f"Preserved affiliate: {aff['title']} ({aff['url']})")
    except Exception as e:
        print(f"Preserve affiliate failed (non-critical): {e}")

    # 统计
    ai_count = sum(1 for item in all_items if item.get('is_ai'))
    total_count = len(all_items) - 1

    print(f"Total: {total_count} tools ({ai_count} AI tools)")

    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=4, ensure_ascii=False)

    print(f"Successfully wrote {len(all_items)} items to {target_file}")
