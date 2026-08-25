// api/r/[toolId].js
// 联盟链接跳转 API
// 访问格式: /r/CUR-001 → 重定向到目标URL（联盟链接或直链）
// 同时记录点击数据到控制台日志（可扩展为写入数据库/发送到Analytics）

const AFFILIATE_FILE = 'affiliate-links.json';
const TOOLS_FILE = 'tools.json';

export default async function handler(req, res) {
  const { toolId } = req.query;

  if (!toolId) {
    return res.status(400).json({ error: '缺少 toolId 参数' });
  }

  try {
    // 顶层 GET 导航通常没有 Origin 头，不能只依赖 req.headers.origin。
    const protocol = req.headers['x-forwarded-proto'] || 'https';
    const host = req.headers.host || 'tool.link.cn';
    const baseUrl = req.headers.origin || `${protocol}://${host}`;

    // 1. 获取工具直链（兜底）
    let directUrl = 'https://tool.link.cn';
    let toolName = '';

    try {
      const toolsRes = await fetch(`${baseUrl}/${TOOLS_FILE}`);
      if (toolsRes.ok) {
        const toolsData = await toolsRes.json();
        const tool = toolsData.find(t => t.id === toolId);
        if (tool) {
          directUrl = tool.url || 'https://tool.link.cn';
          toolName = tool.title || '';
        }
      }
    } catch (e) {
      console.warn('读取 tools.json 失败:', e.message);
    }

    // 2. 查找联盟链接
    let targetUrl = directUrl;
    let isAffiliate = false;
    let commission = '';
    let program = '';

    try {
      const affRes = await fetch(`${baseUrl}/${AFFILIATE_FILE}`);
      if (affRes.ok) {
        const affData = await affRes.json();
        const aff = affData[toolId];
        if (aff && aff.affiliate_url && aff.status === 'active') {
          targetUrl = aff.affiliate_url;
          isAffiliate = true;
          commission = aff.commission || '';
          program = aff.program || '';
        }
      }
    } catch (e) {
      console.warn('读取 affiliate-links.json 失败:', e.message);
    }

    // 3. 记录点击（可扩展：发送到微信通知 / Slack / 数据库）
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      toolId,
      toolName,
      isAffiliate,
      commission,
      program,
      targetUrl: targetUrl.substring(0, 100),
      userAgent: req.headers['user-agent'] || '',
      referer: req.headers['referer'] || req.headers['referrer'] || '',
    };

    // 开发环境打印日志，生产环境可发送到日志服务
    console.log('[Link.cn Click]', JSON.stringify(logEntry));

    // 4. 执行 302 重定向
    // 使用 302 临时重定向（可追踪），301 适合 SEO 但难追踪
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('X-Tool-Id', toolId);
    res.setHeader('X-Is-Affiliate', isAffiliate ? '1' : '0');
    if (commission) res.setHeader('X-Commission', commission);

    return res.redirect(302, targetUrl);

  } catch (error) {
    console.error('[Link.cn Redirect Error]', error);
    // 出错时回到首页
    return res.redirect(302, 'https://tool.link.cn');
  }
}
