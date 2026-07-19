/**
 * ImgBB 图片上传模块
 * 用于将本地图片上传到 ImgBB，返回 URL
 */

const path = require('path');
const fs = require('fs');
const { getImgbedConfig } = require('./config.js');

// ImgBB API 端点
const IMGBB_ENDPOINT = 'https://api.imgbb.com/1/upload';

/**
 * 上传单个文件到 ImgBB
 * @param {string} localFilePath - 本地文件路径
 * @param {string} [fileName] - 文件名（可选）
 * @returns {Promise<{success: boolean, url: string, deleteUrl: string}>}
 */
async function uploadToImgBB(localFilePath, fileName) {
  // 获取配置
  const imgbedConfig = getImgbedConfig();
  if (!imgbedConfig.configured || !imgbedConfig.apiKey) {
    throw new Error('图床未配置。请先运行初始化流程配置 ImgBB API Key。');
  }

  // 检查文件是否存在
  if (!fs.existsSync(localFilePath)) {
    throw new Error(`文件不存在: ${localFilePath}`);
  }

  // 读取文件并转为 base64
  const imageData = fs.readFileSync(localFilePath);
  const base64Image = imageData.toString('base64');

  // 构建请求
  const formData = new URLSearchParams();
  formData.append('key', imgbedConfig.apiKey);
  formData.append('image', base64Image);
  if (fileName) {
    formData.append('name', fileName);
  }

  const response = await fetch(IMGBB_ENDPOINT, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`上传失败: ${response.status} - ${errorText}`);
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(`上传失败: ${JSON.stringify(result)}`);
  }

  return {
    success: true,
    url: result.data.url,
    displayUrl: result.data.display_url,
    deleteUrl: result.data.delete_url,
    thumb: result.data.thumb ? result.data.thumb.url : null
  };
}

/**
 * 上传文件的统一接口（兼容旧代码）
 */
async function uploadToQiniu(localFilePath, fileName) {
  return uploadToImgBB(localFilePath, fileName);
}

/**
 * 处理 Markdown 中的本地图片，上传到 ImgBB 并替换 URL
 * @param {string} markdown - Markdown 内容
 * @param {string} basePath - Markdown 文件所在目录（用于解析相对路径）
 * @returns {Promise<{markdown: string, uploadedImages: Array}>}
 */
async function processMarkdownImages(markdown, basePath) {
  const uploadedImages = [];

  // 匹配 Markdown 图片语法: ![alt](path)
  // 排除已经是 http/https 的 URL
  const imageRegex = /!\[([^\]]*)\]\((?!https?:\/\/)([^)]+)\)/g;

  // 收集所有需要处理的图片
  const matches = [];
  let match;
  while ((match = imageRegex.exec(markdown)) !== null) {
    matches.push({
      fullMatch: match[0],
      alt: match[1],
      imagePath: match[2]
    });
  }

  if (matches.length === 0) {
    return { markdown, uploadedImages: [] };
  }

  console.log(`发现 ${matches.length} 张本地图片，开始上传...`);

  // 逐个处理图片
  let processedMarkdown = markdown;
  for (const img of matches) {
    try {
      // 解析图片路径
      let absolutePath = img.imagePath;
      if (!path.isAbsolute(img.imagePath)) {
        absolutePath = path.resolve(basePath, img.imagePath);
      }

      console.log(`上传: ${img.imagePath}`);
      const result = await uploadToImgBB(absolutePath);

      // 替换 Markdown 中的路径
      const newImageTag = `![${img.alt}](${result.url})`;
      processedMarkdown = processedMarkdown.replace(img.fullMatch, newImageTag);

      uploadedImages.push({
        original: img.imagePath,
        uploaded: result.url,
        deleteUrl: result.deleteUrl
      });

      console.log(`  -> ${result.url}`);
    } catch (err) {
      console.error(`上传失败: ${img.imagePath} - ${err.message}`);
      // 失败时保留原路径
    }
  }

  return { markdown: processedMarkdown, uploadedImages };
}

/**
 * 检查配置是否有效
 */
function isConfigured() {
  const config = getImgbedConfig();
  return config.configured;
}

/**
 * 获取当前配置信息
 */
function getConfig() {
  const config = getImgbedConfig();
  return {
    provider: config.provider,
    configured: config.configured
  };
}

module.exports = {
  uploadToImgBB,
  uploadToQiniu,  // 兼容旧代码
  processMarkdownImages,
  isConfigured,
  getConfig
};
