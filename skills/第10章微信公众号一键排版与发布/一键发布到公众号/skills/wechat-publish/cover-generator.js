/**
 * 封面图生成模块
 * 使用 Gemini 3 Pro Image Preview 生成公众号封面图
 */

const fs = require('fs');
const path = require('path');
const { getCoverConfig } = require('./config.js');

/**
 * 加载提示词模板
 */
function loadPromptTemplate() {
  const templatePath = path.join(__dirname, 'cover-prompt.md');
  try {
    const content = fs.readFileSync(templatePath, 'utf-8');
    // 提取"当前版本"部分的提示词
    const match = content.match(/## 当前版本\n\n([\s\S]*?)(?=\n---|\n## |$)/);
    if (match) {
      return match[1].trim();
    }
    return content;
  } catch (e) {
    // 默认提示词
    return `请你仔细阅读以下文章标题，生成一张爆款公众号封面图。

要求：
1. 比例 2.35:1（横版封面）
2. 视觉冲击力强，吸引点击
3. 标题文字清晰醒目，放在画面中央或显眼位置
4. 配色鲜明，符合文章主题
5. 背景简洁不杂乱，突出标题

文章标题：{{title}}`;
  }
}

/**
 * 生成封面图
 * @param {string} title - 文章标题
 * @returns {Promise<{success: boolean, imageData: Buffer, mimeType: string}>}
 */
async function generateCoverImage(title) {
  // 获取配置
  const coverConfig = getCoverConfig();
  if (!coverConfig.configured || !coverConfig.apiKey) {
    throw new Error('封面图生成未配置。请先运行初始化流程配置 Gemini API Key。');
  }

  // 加载并填充提示词
  const promptTemplate = loadPromptTemplate();
  const prompt = promptTemplate.replace('{{title}}', title);

  console.log('正在生成封面图...');
  console.log('标题:', title);

  const url = `${coverConfig.baseUrl}${coverConfig.endpoint}`;

  const requestBody = {
    contents: [{
      parts: [{
        text: prompt
      }]
    }],
    generationConfig: {
      responseModalities: ["image", "text"],
      responseMimeType: "image/png"
    }
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${coverConfig.apiKey}`
    },
    body: JSON.stringify(requestBody)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API 请求失败: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  // 解析响应，提取图片数据
  if (data.candidates && data.candidates[0] && data.candidates[0].content) {
    const parts = data.candidates[0].content.parts;
    for (const part of parts) {
      if (part.inlineData) {
        const imageData = Buffer.from(part.inlineData.data, 'base64');
        const mimeType = part.inlineData.mimeType || 'image/png';
        return {
          success: true,
          imageData,
          mimeType
        };
      }
    }
  }

  throw new Error('API 响应中未找到图片数据');
}

/**
 * 生成封面图并保存到临时文件
 * @param {string} title - 文章标题
 * @param {string} [outputPath] - 输出路径（可选）
 * @returns {Promise<{success: boolean, filePath: string}>}
 */
async function generateAndSaveCover(title, outputPath) {
  const result = await generateCoverImage(title);

  // 确定输出路径
  const ext = result.mimeType === 'image/jpeg' ? '.jpg' : '.png';
  const fileName = `cover_${Date.now()}${ext}`;
  const filePath = outputPath || path.join(__dirname, 'temp', fileName);

  // 确保目录存在
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  // 保存文件
  fs.writeFileSync(filePath, result.imageData);
  console.log('封面图已保存:', filePath);

  return {
    success: true,
    filePath,
    mimeType: result.mimeType
  };
}

/**
 * 从 Markdown 提取标题
 * @param {string} markdown - Markdown 内容
 * @returns {string}
 */
function extractTitleFromMarkdown(markdown) {
  // 尝试从 YAML frontmatter 提取
  const frontmatterMatch = markdown.match(/^---\n([\s\S]*?)\n---/);
  if (frontmatterMatch) {
    const titleMatch = frontmatterMatch[1].match(/title:\s*["']?([^"'\n]+)["']?/);
    if (titleMatch) return titleMatch[1].trim();
  }

  // 从第一个 # 标题提取
  const h1Match = markdown.match(/^# (.+)$/m);
  if (h1Match) return h1Match[1].trim();

  // 返回默认标题
  return '精彩文章';
}

module.exports = {
  generateCoverImage,
  generateAndSaveCover,
  extractTitleFromMarkdown,
  loadPromptTemplate
};
