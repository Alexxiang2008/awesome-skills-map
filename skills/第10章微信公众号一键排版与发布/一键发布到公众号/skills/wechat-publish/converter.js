/**
 * 微信公众号 Markdown 转 HTML 转换器
 * 使用 marked + juice + highlight.js 的专业方案
 */

const { marked } = require('marked');
const juice = require('juice');
const hljs = require('highlight.js');

// 主题定义
const themes = {
  professional: {
    name: '简约专业',
    description: '适合技术文章、深度分析',
    primaryColor: '#1a73e8',
    css: `
      .wechat-content {
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 16px;
        line-height: 1.8;
        color: #333;
      }
      .wechat-content h1 {
        font-size: 24px;
        font-weight: bold;
        color: #1a73e8;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #1a73e8;
      }
      .wechat-content h2 {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        margin: 25px 0 15px 0;
        padding-left: 12px;
        border-left: 4px solid #1a73e8;
      }
      .wechat-content h3 {
        font-size: 18px;
        font-weight: bold;
        color: #555;
        margin: 20px 0 12px 0;
      }
      .wechat-content h4 {
        font-size: 16px;
        font-weight: bold;
        color: #666;
        margin: 18px 0 10px 0;
      }
      .wechat-content p {
        margin: 16px 0;
        line-height: 1.8;
        color: #3f3f3f;
        text-align: justify;
      }
      .wechat-content strong {
        font-weight: bold;
        color: #1a73e8;
      }
      .wechat-content em {
        font-style: italic;
        color: #666;
      }
      .wechat-content code {
        background-color: #f5f7f9;
        color: #c7254e;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 14px;
      }
      .wechat-content pre {
        background-color: #282c34;
        color: #abb2bf;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 14px;
        line-height: 1.6;
        margin: 16px 0;
      }
      .wechat-content pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
        font-size: inherit;
      }
      .wechat-content blockquote {
        margin: 16px 0;
        padding: 12px 20px;
        background-color: #f8f9fa;
        border-left: 4px solid #1a73e8;
        color: #666;
      }
      .wechat-content blockquote p {
        margin: 0;
      }
      .wechat-content ul, .wechat-content ol {
        margin: 16px 0;
        padding-left: 24px;
      }
      .wechat-content li {
        margin: 8px 0;
        line-height: 1.8;
        color: #3f3f3f;
      }
      .wechat-content a {
        color: #1a73e8;
        text-decoration: none;
      }
      .wechat-content img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 16px auto;
        display: block;
      }
      .wechat-content hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 30px 0;
      }
      .wechat-content table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 14px;
      }
      .wechat-content th {
        background-color: #1a73e8;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
      }
      .wechat-content td {
        padding: 10px 12px;
        border-bottom: 1px solid #e0e0e0;
      }
      .wechat-content tr:nth-child(even) {
        background-color: #f8f9fa;
      }
      .wechat-content .footnotes {
        font-size: 14px;
        color: #888;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
      }
      .wechat-content .footnotes p {
        margin: 4px 0;
        word-break: break-all;
      }
    `
  },
  elegant: {
    name: '优雅文艺',
    description: '适合散文、随笔、生活类文章',
    primaryColor: '#2d5a27',
    css: `
      .wechat-content {
        padding: 24px;
        font-family: "Georgia", "Songti SC", serif;
        font-size: 17px;
        line-height: 2;
        color: #2c3e50;
      }
      .wechat-content h1 {
        font-size: 26px;
        font-weight: normal;
        color: #2d5a27;
        margin: 36px 0 24px 0;
        text-align: center;
        letter-spacing: 2px;
      }
      .wechat-content h2 {
        font-size: 21px;
        font-weight: normal;
        color: #2d5a27;
        margin: 30px 0 18px 0;
        text-align: center;
        letter-spacing: 1px;
      }
      .wechat-content h3 {
        font-size: 18px;
        font-weight: bold;
        color: #34495e;
        margin: 24px 0 14px 0;
      }
      .wechat-content h4 {
        font-size: 16px;
        font-weight: normal;
        color: #5d6d7e;
        margin: 20px 0 12px 0;
      }
      .wechat-content p {
        margin: 20px 0;
        line-height: 2;
        color: #34495e;
        text-indent: 2em;
        text-align: justify;
      }
      .wechat-content strong {
        font-weight: bold;
        color: #2d5a27;
      }
      .wechat-content em {
        font-style: italic;
        color: #7f8c8d;
      }
      .wechat-content code {
        background-color: #ecf0f1;
        color: #2d5a27;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, monospace;
        font-size: 15px;
      }
      .wechat-content pre {
        background-color: #2c3e50;
        color: #ecf0f1;
        padding: 18px;
        border-radius: 6px;
        overflow-x: auto;
        font-family: "SFMono-Regular", Consolas, monospace;
        font-size: 14px;
        line-height: 1.7;
        margin: 20px 0;
      }
      .wechat-content pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
      }
      .wechat-content blockquote {
        margin: 24px 0;
        padding: 16px 24px;
        background-color: #f9f9f7;
        border-left: 3px solid #2d5a27;
        color: #5d6d7e;
      }
      .wechat-content blockquote p {
        margin: 0;
        text-indent: 0;
      }
      .wechat-content ul, .wechat-content ol {
        margin: 18px 0;
        padding-left: 28px;
      }
      .wechat-content li {
        margin: 10px 0;
        line-height: 1.9;
        color: #34495e;
      }
      .wechat-content a {
        color: #2d5a27;
        text-decoration: none;
        border-bottom: 1px dashed #2d5a27;
      }
      .wechat-content img {
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        margin: 24px auto;
        display: block;
      }
      .wechat-content hr {
        border: none;
        margin: 36px 0;
        text-align: center;
      }
      .wechat-content hr::after {
        content: "✦";
        color: #2d5a27;
      }
      .wechat-content table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 15px;
      }
      .wechat-content th {
        background-color: #2d5a27;
        color: white;
        padding: 14px;
        text-align: left;
      }
      .wechat-content td {
        padding: 12px 14px;
        border-bottom: 1px solid #e0e0e0;
      }
      .wechat-content tr:nth-child(even) {
        background-color: #f9f9f7;
      }
      .wechat-content .footnotes {
        font-size: 14px;
        color: #888;
        margin-top: 30px;
      }
    `
  },
  vibrant: {
    name: '活力橙',
    description: '适合营销、公告、活动类文章',
    primaryColor: '#ff6b35',
    css: `
      .wechat-content {
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.8;
        color: #333;
      }
      .wechat-content h1 {
        font-size: 26px;
        font-weight: bold;
        color: #ff6b35;
        margin: 28px 0 18px 0;
        text-align: center;
        padding: 10px 0;
      }
      .wechat-content h2 {
        font-size: 20px;
        font-weight: bold;
        color: #ff6b35;
        margin: 24px 0 14px 0;
        padding: 8px 16px;
        background-color: #fff5f0;
        border-radius: 6px;
      }
      .wechat-content h3 {
        font-size: 18px;
        font-weight: bold;
        color: #e55a2b;
        margin: 20px 0 12px 0;
      }
      .wechat-content h4 {
        font-size: 16px;
        font-weight: bold;
        color: #ff6b35;
        margin: 18px 0 10px 0;
      }
      .wechat-content p {
        margin: 16px 0;
        line-height: 1.85;
        color: #444;
      }
      .wechat-content strong {
        font-weight: bold;
        color: #ff6b35;
      }
      .wechat-content em {
        font-style: italic;
        color: #888;
      }
      .wechat-content code {
        background-color: #fff5f0;
        color: #ff6b35;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 14px;
      }
      .wechat-content pre {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        font-family: monospace;
        font-size: 14px;
        line-height: 1.6;
        margin: 16px 0;
        border-left: 4px solid #ff6b35;
      }
      .wechat-content pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
      }
      .wechat-content blockquote {
        margin: 18px 0;
        padding: 14px 20px;
        background-color: #fff5f0;
        border-left: 4px solid #ff6b35;
        color: #666;
        border-radius: 0 8px 8px 0;
      }
      .wechat-content blockquote p {
        margin: 0;
      }
      .wechat-content ul, .wechat-content ol {
        margin: 16px 0;
        padding-left: 24px;
      }
      .wechat-content li {
        margin: 8px 0;
        line-height: 1.8;
        color: #444;
      }
      .wechat-content a {
        color: #ff6b35;
        text-decoration: none;
        font-weight: bold;
      }
      .wechat-content img {
        max-width: 100%;
        height: auto;
        border-radius: 12px;
        margin: 20px auto;
        display: block;
      }
      .wechat-content hr {
        border: none;
        border-top: 2px dashed #ff6b35;
        margin: 28px 0;
      }
      .wechat-content table {
        width: 100%;
        border-collapse: collapse;
        margin: 18px 0;
        font-size: 14px;
      }
      .wechat-content th {
        background-color: #ff6b35;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
      }
      .wechat-content td {
        padding: 10px 12px;
        border-bottom: 1px solid #ffe0d0;
      }
      .wechat-content tr:nth-child(even) {
        background-color: #fff5f0;
      }
      .wechat-content .footnotes {
        font-size: 14px;
        color: #888;
        margin-top: 30px;
      }
    `
  },
  dark: {
    name: '暗黑极客',
    description: '适合程序员向、技术极客类内容',
    primaryColor: '#61dafb',
    css: `
      .wechat-content {
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.8;
        color: #e0e0e0;
        background-color: #1a1a2e;
      }
      .wechat-content h1 {
        font-size: 24px;
        font-weight: bold;
        color: #61dafb;
        margin: 28px 0 18px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #61dafb;
      }
      .wechat-content h2 {
        font-size: 20px;
        font-weight: bold;
        color: #bb86fc;
        margin: 24px 0 14px 0;
        padding-left: 14px;
        border-left: 4px solid #bb86fc;
      }
      .wechat-content h3 {
        font-size: 18px;
        font-weight: bold;
        color: #03dac6;
        margin: 20px 0 12px 0;
      }
      .wechat-content h4 {
        font-size: 16px;
        font-weight: bold;
        color: #bb86fc;
        margin: 18px 0 10px 0;
      }
      .wechat-content p {
        margin: 16px 0;
        line-height: 1.85;
        color: #b0b0b0;
      }
      .wechat-content strong {
        font-weight: bold;
        color: #61dafb;
      }
      .wechat-content em {
        font-style: italic;
        color: #888;
      }
      .wechat-content code {
        background-color: #2d2d44;
        color: #f8c555;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: "Fira Code", "SFMono-Regular", Consolas, monospace;
        font-size: 14px;
      }
      .wechat-content pre {
        background-color: #0d1117;
        color: #c9d1d9;
        padding: 18px;
        border-radius: 8px;
        overflow-x: auto;
        font-family: "Fira Code", "SFMono-Regular", Consolas, monospace;
        font-size: 14px;
        line-height: 1.6;
        margin: 18px 0;
        border: 1px solid #30363d;
      }
      .wechat-content pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
      }
      .wechat-content blockquote {
        margin: 18px 0;
        padding: 14px 20px;
        background-color: #2d2d44;
        border-left: 4px solid #61dafb;
        color: #a0a0a0;
      }
      .wechat-content blockquote p {
        margin: 0;
      }
      .wechat-content ul, .wechat-content ol {
        margin: 16px 0;
        padding-left: 24px;
      }
      .wechat-content li {
        margin: 8px 0;
        line-height: 1.8;
        color: #b0b0b0;
      }
      .wechat-content a {
        color: #61dafb;
        text-decoration: none;
        border-bottom: 1px solid #61dafb;
      }
      .wechat-content img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 20px auto;
        display: block;
        border: 1px solid #30363d;
      }
      .wechat-content hr {
        border: none;
        border-top: 1px solid #30363d;
        margin: 28px 0;
      }
      .wechat-content table {
        width: 100%;
        border-collapse: collapse;
        margin: 18px 0;
        font-size: 14px;
      }
      .wechat-content th {
        background-color: #2d2d44;
        color: #61dafb;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        border-bottom: 2px solid #61dafb;
      }
      .wechat-content td {
        padding: 10px 12px;
        border-bottom: 1px solid #30363d;
        color: #b0b0b0;
      }
      .wechat-content tr:nth-child(even) {
        background-color: #16162a;
      }
      .wechat-content .footnotes {
        font-size: 14px;
        color: #666;
        margin-top: 30px;
      }
    `
  }
};

/**
 * 配置 marked 渲染器
 * @param {Object} theme - 主题配置
 * @param {boolean} useSectionList - 是否使用 section 替代 ul/ol（解决微信列表空行问题）
 */
function createRenderer(theme, useSectionList = true) {
  const renderer = new marked.Renderer();

  // 存储链接用于生成脚注
  const links = [];
  let linkIndex = 0;

  // 有序列表计数器栈（支持嵌套列表）
  const olCounterStack = [];

  // 自定义链接渲染 - 转换为脚注形式
  renderer.link = function(href, title, text) {
    // 处理新版 marked 的参数格式
    if (typeof href === 'object') {
      text = href.text;
      title = href.title;
      href = href.href;
    }
    linkIndex++;
    links.push({ index: linkIndex, text, url: href });
    return `<span class="link-text">${text}</span><sup class="link-sup">[${linkIndex}]</sup>`;
  };

  if (useSectionList) {
    // 方案：使用 section 替代 ul/ol，彻底解决微信空行问题

    // 自定义列表渲染
    renderer.list = function(body, ordered, start) {
      // 处理新版 marked 的参数格式
      if (typeof body === 'object') {
        ordered = body.ordered;
        start = body.start;
        // items 已经是渲染后的 HTML 字符串数组
        if (body.items) {
          body = body.items.map((item, index) => {
            const num = (start || 1) + index;
            // item.tokens 包含已解析的 token，需要用 marked.parser 渲染
            let itemHtml = '';
            if (item.tokens) {
              itemHtml = marked.parser(item.tokens);
            } else {
              itemHtml = item.text || item.raw || '';
            }
            return renderListItem(itemHtml, ordered, num, theme);
          }).join('');
        } else {
          body = body.raw || '';
        }
      }

      // 不使用 ul/ol 包裹，直接返回列表项
      return body;
    };

    // 列表项渲染辅助函数
    function renderListItem(text, ordered, num, theme) {
      // 移除可能包裹在 <p> 中的内容
      text = text.replace(/^<p[^>]*>([\s\S]*)<\/p>$/i, '$1').trim();

      // 获取主题样式
      const liStyle = theme.css.match(/\.wechat-content li \{([^}]+)\}/);
      const liStyleStr = liStyle ? liStyle[1].trim().replace(/\s+/g, ' ') : 'margin: 8px 0; line-height: 1.8; color: #3f3f3f;';

      // 根据列表类型选择前缀
      let prefix;
      if (ordered) {
        prefix = `<span style="color: ${theme.primaryColor}; font-weight: bold; margin-right: 8px;">${num}.</span>`;
      } else {
        prefix = `<span style="color: ${theme.primaryColor}; margin-right: 8px;">•</span>`;
      }

      // 使用 section 包裹，完全避免 li 标签
      return `<section style="${liStyleStr} display: block; padding-left: 8px;">${prefix}${text}</section>`;
    }

    // 自定义列表项渲染（作为备用）
    renderer.listitem = function(text, task, checked, ordered, num) {
      // 处理新版 marked 的参数格式
      if (typeof text === 'object') {
        const item = text;
        if (item.tokens) {
          text = marked.parser(item.tokens);
        } else {
          text = item.text || item.raw || '';
        }
        task = item.task;
        checked = item.checked;
      }
      return renderListItem(text, ordered, num || 1, theme);
    };
  } else {
    // 备选方案：仍使用 ul/ol/li，但在 li 内添加 section 包裹
    renderer.listitem = function(text, task, checked) {
      if (typeof text === 'object') {
        text = text.text || text.raw || '';
      }
      // 在 li 内部添加 section 包裹，防止微信自动添加标签导致空行
      return `<li><section>${text}</section></li>`;
    };
  }

  // 获取收集的链接
  renderer.getLinks = function() {
    return links;
  };

  return renderer;
}

/**
 * 将 Markdown 转换为微信公众号 HTML
 * @param {string} markdown - Markdown 内容
 * @param {string} themeName - 主题名称
 * @param {Object} options - 选项
 * @param {boolean} options.useSectionList - 是否使用 section 替代 ul/ol（默认 true）
 */
function convertMarkdown(markdown, themeName = 'professional', options = {}) {
  const { useSectionList = true } = options;
  const theme = themes[themeName] || themes.professional;
  const renderer = createRenderer(theme, useSectionList);

  // 配置 marked
  marked.setOptions({
    renderer: renderer,
    highlight: function(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(code, { language: lang }).value;
        } catch (e) {}
      }
      return hljs.highlightAuto(code).value;
    },
    gfm: true,
    breaks: false,
    pedantic: false,
    smartLists: true,
    smartypants: false
  });

  // 移除 YAML frontmatter
  let content = markdown.replace(/^---[\s\S]*?---\n*/m, '');

  // 转换 Markdown 为 HTML
  let html = marked.parse(content);

  // 清理列表标记注释
  html = html.replace(/<!--LIST_START-->/g, '').replace(/<!--LIST_END-->/g, '');

  // 移除多余的空行和换行符（微信会将其渲染为空行）
  html = html.replace(/>\s*\n\s*</g, '><');

  // 添加脚注
  const links = renderer.getLinks();
  if (links.length > 0) {
    html += '<div class="footnotes"><p><strong>参考链接：</strong></p>';
    for (const link of links) {
      html += `<p>[${link.index}] ${link.text}: ${link.url}</p>`;
    }
    html += '</div>';
  }

  // 包装内容 - 使用 section 而非 div（更好的微信兼容性）
  html = `<section class="wechat-content">${html}</section>`;

  // 添加样式
  const fullHtml = `<style>${theme.css}</style>${html}`;

  // 使用 juice 将 CSS 内联
  const inlinedHtml = juice(fullHtml, {
    removeStyleTags: true,
    preserveImportant: true
  });

  return inlinedHtml;
}

/**
 * 从 Markdown 提取元信息
 */
function extractMetadata(markdown) {
  const metadata = {
    title: '',
    summary: '',
    author: ''
  };

  // 尝试从 YAML frontmatter 提取
  const frontmatterMatch = markdown.match(/^---\n([\s\S]*?)\n---/);
  if (frontmatterMatch) {
    const frontmatter = frontmatterMatch[1];

    const titleMatch = frontmatter.match(/title:\s*["']?([^"'\n]+)["']?/);
    if (titleMatch) metadata.title = titleMatch[1].trim();

    const descMatch = frontmatter.match(/(?:description|summary):\s*["']?([^"'\n]+)["']?/);
    if (descMatch) metadata.summary = descMatch[1].trim();

    const authorMatch = frontmatter.match(/author:\s*["']?([^"'\n]+)["']?/);
    if (authorMatch) metadata.author = authorMatch[1].trim();
  }

  // 如果没有从 frontmatter 获取到标题，从第一个 # 标题获取
  if (!metadata.title) {
    const h1Match = markdown.match(/^# (.+)$/m);
    if (h1Match) metadata.title = h1Match[1].trim();
  }

  // 如果没有摘要，从正文提取前120字
  if (!metadata.summary) {
    const cleanText = markdown
      .replace(/^---[\s\S]*?---\n*/m, '')
      .replace(/^#+\s+.+$/gm, '')
      .replace(/!\[.*?\]\(.*?\)/g, '')
      .replace(/\[.*?\]\(.*?\)/g, '')
      .replace(/[*_`#]/g, '')
      .replace(/\n+/g, ' ')
      .trim();
    metadata.summary = cleanText.substring(0, 117) + '...';
  }

  return metadata;
}

/**
 * 获取可用主题列表
 */
function getAvailableThemes() {
  return Object.keys(themes).map(key => ({
    key,
    name: themes[key].name,
    description: themes[key].description
  }));
}

module.exports = {
  convertMarkdown,
  extractMetadata,
  getAvailableThemes,
  themes
};
