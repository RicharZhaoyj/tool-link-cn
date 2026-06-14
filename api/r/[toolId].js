// api/r/[toolId].js
// AI 工具 Lifetime Deal 详情落地页
// 访问 /r/CUR-001 → 展示工具Deal详情 + 关联链接 + 3秒后自动跳转

export default async function handler(req, res) {
  const { toolId } = req.query;

  if (!toolId) {
    return res.status(400).json({ error: '缺少 toolId 参数' });
  }

  try {
    // 读取 tools.json
    let tool = null;
    let targetUrl = 'https://tool.link.cn';

    try {
      const origin = req.headers['x-forwarded-proto'] + '://' + req.headers['host'];
      const toolsRes = await fetch(origin + '/tools.json');
      if (toolsRes.ok) {
        const toolsData = await toolsRes.json();
        tool = toolsData.find(t => t.id === toolId);
        if (tool) {
          targetUrl = tool.url || 'https://tool.link.cn';
        }
      }
    } catch (e) {
      console.warn('读取 tools.json 失败:', e.message);
    }

    // 尝试读取联盟链接
    try {
      const origin = req.headers['x-forwarded-proto'] + '://' + req.headers['host'];
      const affRes = await fetch(origin + '/affiliate-links.json');
      if (affRes.ok) {
        const affData = await affRes.json();
        const aff = affData[toolId];
        if (aff && aff.affiliate_url && aff.status === 'active') {
          targetUrl = aff.affiliate_url;
        }
      }
    } catch (e) {
      // 无联盟链接，使用直链
    }

    if (!tool) {
      return res.redirect(302, 'https://tool.link.cn');
    }

    const title = tool.title || 'AI 工具 Deal';
    const desc = tool.desc || 'Lifetime Deal 买断方案';
    const price = tool.price || '';
    const orig = tool.originalPrice || '';
    const tag = tool.tag || '';
    const isAi = tool.is_ai || false;
    const reviewSlug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '');

    // 计算节省比例
    let savings = '';
    try {
      const p = parseFloat(String(price).replace(/[^0-9.]/g, ''));
      const o = parseFloat(String(orig).replace(/[^0-9.]/g, ''));
      if (!isNaN(p) && !isNaN(o) && o > 0) {
        const s = Math.round((1 - p / o) * 100);
        if (s > 0) savings = `省 ${s}%`;
      }
    } catch (e) {}

    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} Lifetime Deal | LINK.CN</title>
    <meta name="description" content="${title} — ${desc}。原价${orig}，Deal价${price}${savings ? '，' + savings : ''}。发现值得一次买断的AI工具。">
    <meta name="robots" content="noindex, follow">
    <meta property="og:title" content="${title} Lifetime Deal | LINK.CN">
    <meta property="og:description" content="${desc} | 原价${orig} → Deal价${price}${savings ? ' ' + savings : ''}">
    <meta http-equiv="refresh" content="5;url=${targetUrl}">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #050505; color: #fff; font-family: system-ui, -apple-system, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 40px; max-width: 520px; width: 90%; text-align: center; }
        .tag { display: inline-block; background: rgba(59,130,246,0.15); color: #60a5fa; font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 16px; border: 1px solid rgba(59,130,246,0.3); }
        h1 { font-size: 28px; font-weight: 900; margin-bottom: 8px; }
        .desc { color: #a1a1aa; font-size: 14px; line-height: 1.6; margin-bottom: 24px; }
        .price-block { margin-bottom: 28px; }
        .deal-price { font-size: 36px; font-weight: 900; color: #34d399; }
        .orig-price { color: #71717a; text-decoration: line-through; font-size: 18px; margin-left: 12px; }
        .save-badge { display: inline-block; background: rgba(239,68,68,0.15); color: #f87171; font-size: 14px; font-weight: 700; padding: 4px 12px; border-radius: 8px; margin-left: 12px; border: 1px solid rgba(239,68,68,0.3); }
        .btn { display: block; width: 100%; padding: 16px; background: #fff; color: #000; text-align: center; font-size: 16px; font-weight: 900; border-radius: 16px; text-decoration: none; transition: all 0.2s; }
        .btn:hover { background: #3b82f6; color: #fff; }
        .redirect-hint { color: #71717a; font-size: 11px; margin-top: 12px; }
        .links { margin-top: 28px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: center; gap: 20px; }
        .links a { color: #71717a; font-size: 12px; text-decoration: none; transition: color 0.2s; }
        .links a:hover { color: #60a5fa; }
    </style>
</head>
<body>
    <div class="card">
        <div class="tag">${tag || 'Deal'}${isAi ? ' · AI' : ''}</div>
        <h1>${title}</h1>
        <p class="desc">${desc}</p>
        <div class="price-block">
            <span class="deal-price">${price}</span>
            ${orig ? `<span class="orig-price">${orig}</span>` : ''}
            ${savings ? `<span class="save-badge">${savings}</span>` : ''}
        </div>
        <a href="${targetUrl}" class="btn">前往查看 →</a>
        <p class="redirect-hint">5 秒后自动跳转...</p>
        <div class="links">
            <a href="https://tools.link.cn/review/${reviewSlug}" target="_blank">📝 工具评测</a>
            <a href="https://ai.link.cn" target="_blank">📰 AI 资讯</a>
            <a href="https://prompts.link.cn" target="_blank">💡 提示词</a>
            <a href="https://tool.link.cn">← 返回导航</a>
        </div>
    </div>
</body>
</html>`;

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    return res.status(200).send(html);

  } catch (error) {
    console.error('[Link.cn Landing Error]', error);
    return res.redirect(302, 'https://tool.link.cn');
  }
}
