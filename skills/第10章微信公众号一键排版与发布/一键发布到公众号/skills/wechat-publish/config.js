/**
 * 配置管理模块
 * 配置存储在用户目录 ~/.wechat-publish/config.json
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// 配置目录和文件路径
const CONFIG_DIR = path.join(os.homedir(), '.wechat-publish');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

// 默认配置（不含敏感信息）
const DEFAULT_CONFIG = {
  // 微信发布 API
  wechat: {
    apiKey: '',
    apiBase: 'https://wx.limyai.com/api/openapi'
  },
  // 图床配置
  imgbed: {
    provider: 'imgbb',  // imgbb | qiniu
    imgbb: {
      apiKey: ''
    },
    qiniu: {
      accessKey: '',
      secretKey: '',
      bucket: '',
      domain: ''
    }
  },
  // 封面图生成配置
  cover: {
    enabled: true,
    provider: 'gemini',
    gemini: {
      apiKey: '',
      baseUrl: 'https://yunwu.ai',
      endpoint: '/v1beta/models/gemini-3-pro-image-preview:generateContent'
    }
  },
  // 初始化标记
  initialized: false
};

/**
 * 确保配置目录存在
 */
function ensureConfigDir() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

/**
 * 读取配置
 * @returns {Object} 配置对象
 */
function loadConfig() {
  ensureConfigDir();

  if (!fs.existsSync(CONFIG_FILE)) {
    return { ...DEFAULT_CONFIG };
  }

  try {
    const content = fs.readFileSync(CONFIG_FILE, 'utf-8');
    const config = JSON.parse(content);
    // 合并默认配置，确保新增字段有默认值
    return deepMerge(DEFAULT_CONFIG, config);
  } catch (e) {
    console.error('读取配置文件失败:', e.message);
    return { ...DEFAULT_CONFIG };
  }
}

/**
 * 保存配置
 * @param {Object} config - 配置对象
 */
function saveConfig(config) {
  ensureConfigDir();
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
}

/**
 * 更新部分配置
 * @param {Object} updates - 要更新的配置
 */
function updateConfig(updates) {
  const config = loadConfig();
  const newConfig = deepMerge(config, updates);
  saveConfig(newConfig);
  return newConfig;
}

/**
 * 检查是否已初始化
 * @returns {boolean}
 */
function isInitialized() {
  const config = loadConfig();
  return config.initialized === true;
}

/**
 * 标记为已初始化
 */
function markInitialized() {
  updateConfig({ initialized: true });
}

/**
 * 检查必要配置是否完整
 * @returns {Object} { valid: boolean, missing: string[] }
 */
function validateConfig() {
  const config = loadConfig();
  const missing = [];

  // 检查微信 API Key（必需）
  if (!config.wechat?.apiKey) {
    missing.push('微信发布 API Key');
  }

  return {
    valid: missing.length === 0,
    missing,
    config
  };
}

/**
 * 获取微信 API 配置
 */
function getWechatConfig() {
  const config = loadConfig();
  return {
    apiKey: config.wechat?.apiKey || '',
    apiBase: config.wechat?.apiBase || DEFAULT_CONFIG.wechat.apiBase
  };
}

/**
 * 获取图床配置
 */
function getImgbedConfig() {
  const config = loadConfig();
  const provider = config.imgbed?.provider || 'imgbb';

  if (provider === 'imgbb') {
    return {
      provider: 'imgbb',
      apiKey: config.imgbed?.imgbb?.apiKey || '',
      configured: !!config.imgbed?.imgbb?.apiKey
    };
  } else if (provider === 'qiniu') {
    return {
      provider: 'qiniu',
      accessKey: config.imgbed?.qiniu?.accessKey || '',
      secretKey: config.imgbed?.qiniu?.secretKey || '',
      bucket: config.imgbed?.qiniu?.bucket || '',
      domain: config.imgbed?.qiniu?.domain || '',
      configured: !!(config.imgbed?.qiniu?.accessKey && config.imgbed?.qiniu?.secretKey)
    };
  }

  return { provider: 'none', configured: false };
}

/**
 * 获取封面图生成配置
 */
function getCoverConfig() {
  const config = loadConfig();
  return {
    enabled: config.cover?.enabled !== false,
    provider: config.cover?.provider || 'gemini',
    apiKey: config.cover?.gemini?.apiKey || '',
    baseUrl: config.cover?.gemini?.baseUrl || DEFAULT_CONFIG.cover.gemini.baseUrl,
    endpoint: config.cover?.gemini?.endpoint || DEFAULT_CONFIG.cover.gemini.endpoint,
    configured: !!config.cover?.gemini?.apiKey
  };
}

/**
 * 获取配置文件路径（用于提示用户）
 */
function getConfigPath() {
  return CONFIG_FILE;
}

/**
 * 重置配置
 */
function resetConfig() {
  saveConfig(DEFAULT_CONFIG);
}

/**
 * 深度合并对象
 */
function deepMerge(target, source) {
  const result = { ...target };
  for (const key in source) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = deepMerge(target[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

module.exports = {
  loadConfig,
  saveConfig,
  updateConfig,
  isInitialized,
  markInitialized,
  validateConfig,
  getWechatConfig,
  getImgbedConfig,
  getCoverConfig,
  getConfigPath,
  resetConfig,
  CONFIG_DIR,
  CONFIG_FILE
};
