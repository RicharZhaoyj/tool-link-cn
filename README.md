# Link.cn AI Tool Curator

自动化抓取 AppSumo 优质 AI 工具 Lifetime Deals 并展示在 link.cn 导航页。

## 技术栈
- **Backend:** Python (Requests + XML Parser)
- **Automation:** GitHub Actions (Node 24)
- **Frontend:** HTML5 + TailwindCSS + Vanilla JS
- **Deployment:** Vercel

## 自动更新逻辑
- 每 12 小时通过 `update.py` 抓取 RSS 源。
- 自动注入联盟 ID `7294907`。
- 推送至 `tools.json` 触发 Vercel 自动增量更新。
