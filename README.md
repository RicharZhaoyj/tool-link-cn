# Link.cn AI 工具导航

🤖 全球顶尖 AI 工具 Lifetime Deal 导航站 | [tool.link.cn](https://tool.link.cn)

## 特性

- 🔄 24小时自动更新（每12小时同步）
- 🤖 AI 工具优先展示与标注
- 🔍 中文搜索 + 分类筛选
- 💰 价格标签 + 折扣百分比
- 🌐 完整 SEO（meta/OG/structured data/sitemap）
- 📱 响应式设计，移动端友好

## 技术栈

- **数据源**: Impact API + AppSumo 页面抓取 + 手动精选（三级容灾）
- **Backend**: Python (Requests)
- **Automation**: GitHub Actions (Python 3.11)
- **Frontend**: HTML5 + TailwindCSS + Vanilla JS
- **Deployment**: Vercel

## 数据流

```
Impact API (主) → AppSumo 页面抓取 (备) → 手动精选 (兜底)
       ↓                    ↓                     ↓
            合并去重 + 中文标签 + 价格数据
                        ↓
                   tools.json
                        ↓
              Vercel 自动部署
```

## 联盟追踪

- AppSumo 联盟 ID: `7294907`
- Impact Brand ID: `4468`
- 所有出站链接自动注入联盟参数

## 本地开发

```bash
# 1. 运行数据脚本
python update.py

# 2. 本地预览（需安装 vercel-cli）
npx vercel dev
```

## 推广渠道

- 小红书 / 知乎 / 抖音 / 头条 / 即刻 / 推特

## License

MIT
