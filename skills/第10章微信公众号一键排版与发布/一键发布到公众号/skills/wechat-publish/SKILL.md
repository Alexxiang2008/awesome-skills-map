#---
name: wechat-publish
description: "将 Markdown 文章发布到微信公众号草稿箱，支持多种精美主题风格。当用户需要：(1) 发布文章到公众号，(2) 发布到微信，(3) 发布小绿书/图文消息，(4) 同步到公众号草稿箱，(5) 把笔记发到公众号，(6) /publish-wechat 命令。"
---

# 微信公众号发布技能

## 概述

此技能用于将 Markdown 文章发布到微信公众号草稿箱，支持：
- **4 种精美主题风格**：简约专业、优雅文艺、活力橙、暗黑极客
- **2 种发布类型**：普通文章、小绿书

## 触发方式

- "发布到公众号"
- "发布到微信"
- "发小绿书"
- "把 xxx.md 发到公众号"
- "/publish-wechat 文件路径"

## 首次使用引导（重要！）

**每次执行前，必须先检查是否已初始化。**

### 检查初始化状态

```javascript
const { isInitialized, validateConfig, getConfigPath } = require('./config.js');

if (!isInitialized()) {
  // 进入首次使用引导流程
}
```

### 首次使用引导流程

如果用户是首次使用（`isInitialized()` 返回 `false`），按以下步骤引导：

---

**步骤 0: 欢迎提示**

向用户显示：

```
欢迎使用「微信公众号发布」技能！

首次使用需要完成以下配置：
1. 安装依赖
2. 配置微信发布 API Key（必需）
3. 配置图床 API Key（可选，用于上传文章中的本地图片）
4. 配置封面图生成 API Key（可选，用于 AI 自动生成封面）

配置将保存在: ~/.wechat-publish/config.json
```

---

**步骤 1: 安装依赖**

```bash
cd skills/wechat-publish && npm install
```

---

**步骤 2: 配置微信发布 API Key（必需）**

询问用户：

```
请输入你的微信发布 API Key。

获取方式：
1. 访问 https://wx.limyai.com
2. 注册/登录账号
3. 绑定你的微信公众号
4. 在「API 设置」中获取 API Key

请输入 API Key:
```

用户输入后，保存配置：

```javascript
const { updateConfig } = require('./config.js');
updateConfig({
  wechat: {
    apiKey: '用户输入的 API Key'
  }
});
```

---

**步骤 3: 配置图床（可选）**

询问用户：

```
是否配置图床？（用于上传文章中的本地图片）

1. 配置 ImgBB（推荐，免费）
2. 跳过（文章中不使用本地图片，或图片已是网络 URL）

请选择:
```

如果用户选择 1：

```
请输入 ImgBB API Key。

获取方式：
1. 访问 https://api.imgbb.com/
2. 注册账号
3. 获取免费 API Key

请输入 API Key:
```

保存配置：

```javascript
updateConfig({
  imgbed: {
    provider: 'imgbb',
    imgbb: {
      apiKey: '用户输入的 API Key'
    }
  }
});
```

---

**步骤 4: 配置封面图生成（可选）**

询问用户：

```
是否配置 AI 封面图生成？（自动根据文章标题生成封面图）

1. 配置 Gemini API（需要支持图片生成的 API）
2. 跳过（手动上传封面图）

请选择:
```

如果用户选择 1：

```
请输入 Gemini API Key。

获取方式：
1. 访问 https://yunwu.ai 或其他支持 Gemini 图片生成的服务商
2. 注册账号并充值
3. 获取 API Key

请输入 API Key:
```

保存配置：

```javascript
updateConfig({
  cover: {
    enabled: true,
    provider: 'gemini',
    gemini: {
      apiKey: '用户输入的 API Key'
    }
  }
});
```

---

**步骤 5: 完成初始化**

```javascript
const { markInitialized } = require('./config.js');
markInitialized();
```

向用户显示：

```
配置完成！

你的配置已保存到: ~/.wechat-publish/config.json

现在你可以：
- 说「发布到公众号」+ 文件路径
- 或使用 /publish-wechat xxx.md

如需修改配置，可以直接编辑配置文件，或删除配置文件重新初始化。
```

---

## 主题风格

| 序号 | 主题 | 说明 | 适合内容 |
|------|------|------|----------|
| 1 | **简约专业** | 蓝色主色调，清晰专业 | 技术文章、深度分析 |
| 2 | **优雅文艺** | 墨绿主色调，文艺气息 | 散文、随笔、生活类 |
| 3 | **活力橙** | 橙色主色调，活力醒目 | 营销、公告、活动类 |
| 4 | **暗黑极客** | 深色背景，科技感 | 程序员向、技术极客 |
| 5 | **原始格式** | 不做样式处理 | 已有格式的内容 |

## API 配置

**重要：API Key 从配置文件读取，不再硬编码。**

```javascript
const { getWechatConfig, getImgbedConfig, getCoverConfig } = require('./config.js');

// 获取微信 API 配置
const wechatConfig = getWechatConfig();
// wechatConfig.apiKey - API Key
// wechatConfig.apiBase - API 基础 URL

// 获取图床配置
const imgbedConfig = getImgbedConfig();
// imgbedConfig.configured - 是否已配置
// imgbedConfig.apiKey - ImgBB API Key

// 获取封面图配置
const coverConfig = getCoverConfig();
// coverConfig.configured - 是否已配置
// coverConfig.enabled - 是否启用
// coverConfig.apiKey - Gemini API Key
```

配置文件位置: `~/.wechat-publish/config.json`

## 执行流程

### 步骤 0: 检查初始化（每次必须执行）

```javascript
const { isInitialized } = require('./config.js');

if (!isInitialized()) {
  // 执行「首次使用引导流程」（见上文）
  // 引导完成后再继续
}
```

### 步骤 1: 读取文章文件

用户提供 Markdown 文件路径，读取文件内容。

### 步骤 2: 获取公众号列表

```javascript
const { getWechatConfig } = require('./config.js');
const wechatConfig = getWechatConfig();
```

```bash
curl -X POST "https://wx.limyai.com/api/openapi/wechat-accounts" \
  -H "X-API-Key: ${wechatConfig.apiKey}" \
  -H "Content-Type: application/json"
```

如果只有一个公众号，直接使用；多个则询问用户选择。

### 步骤 3: 询问用户选择风格（重要！）

**必须询问用户选择主题风格：**

```
请选择文章主题风格：
1. 简约专业 - 适合技术文章、深度分析
2. 优雅文艺 - 适合散文、随笔、生活类
3. 活力橙   - 适合营销、公告、活动类
4. 暗黑极客 - 适合程序员向、技术极客
5. 原始格式 - 不做额外样式处理

请选择发布类型：
1. 普通文章（默认）
2. 小绿书
```

### 步骤 4: 生成封面图（自动，如已配置）

**先检查是否已配置封面图生成：**

```javascript
const { getCoverConfig } = require('./config.js');
const coverConfig = getCoverConfig();

if (coverConfig.configured && coverConfig.enabled) {
  // 生成封面图
} else {
  // 跳过封面图生成，询问用户是否手动提供封面图 URL
}
```

使用 Gemini 3 Pro 根据文章标题自动生成封面图，上传到图床。

**封面图生成模块**: `skills/wechat-publish/cover-generator.js`
**提示词模板**: `skills/wechat-publish/cover-prompt.md`（可迭代优化）

```javascript
const { generateAndSaveCover, extractTitleFromMarkdown } = require('./cover-generator.js');
const { uploadToQiniu } = require('./image-uploader.js');

// 1. 提取标题
const title = extractTitleFromMarkdown(markdown);

// 2. 生成封面图
const coverResult = await generateAndSaveCover(title);

// 3. 上传到七牛云
const uploadResult = await uploadToQiniu(coverResult.filePath, `covers/${Date.now()}.png`);
const coverImageUrl = uploadResult.url;
```

**封面图规格**: 2.35:1 横版比例，适合公众号头图

### 步骤 5: 处理本地图片（自动，如已配置）

**先检查是否已配置图床：**

```javascript
const { getImgbedConfig } = require('./config.js');
const imgbedConfig = getImgbedConfig();

if (imgbedConfig.configured) {
  // 处理本地图片
} else {
  // 跳过图片上传，提醒用户文章中的本地图片将无法显示
}
```

如果文章中包含本地图片（相对路径或绝对路径），自动上传到图床并替换为 URL。

**图片上传模块**: `skills/wechat-publish/image-uploader.js`

```javascript
const { processMarkdownImages } = require('./image-uploader.js');
const path = require('path');

// 处理本地图片，上传到七牛云
const basePath = path.dirname(filePath);
const { markdown: processedMarkdown, uploadedImages } = await processMarkdownImages(markdown, basePath);

// uploadedImages 包含上传结果列表
// processedMarkdown 中的本地图片路径已替换为七牛云 URL
```

**支持的图片格式**: `![alt](./images/xxx.png)`, `![](../path/to/image.jpg)`

**注意**: 已经是 http/https URL 的图片不会被处理。

### 步骤 6: 格式转换

根据用户选择的主题，使用 `converter.js` 脚本将 Markdown 转换为带内联样式的 HTML。

**转换脚本位置**: `skills/wechat-publish/converter.js`

```javascript
const { convertMarkdown, extractMetadata } = require('./converter.js');

// 提取元信息（标题、摘要）
const metadata = extractMetadata(processedMarkdown);

// 转换为 HTML（使用选择的主题）
const html = convertMarkdown(processedMarkdown, themeName);
// themeName: 'professional' | 'elegant' | 'vibrant' | 'dark'
```

**如果用户选择"原始格式"**，跳过转换，直接使用原始 Markdown 内容，设置 `contentFormat: "markdown"`。

### 步骤 7: 发布文章

```javascript
const { getWechatConfig } = require('./config.js');
const wechatConfig = getWechatConfig();
```

```bash
curl -X POST "https://wx.limyai.com/api/openapi/wechat-publish" \
  -H "X-API-Key: ${wechatConfig.apiKey}" \
  -H "Content-Type: application/json" \
  -d '{
    "wechatAppid": "公众号AppID",
    "title": "文章标题（最多64字符）",
    "content": "转换后的HTML内容或原始Markdown",
    "summary": "摘要（最多120字符）",
    "coverImage": "封面图URL",
    "contentFormat": "html 或 markdown",
    "articleType": "news 或 newspic"
  }'
```

### 步骤 8: 返回结果

**成功：**
```
发布成功！

公众号: [名称]
文章标题: [标题]
主题风格: [选择的主题]
发布类型: 普通文章/小绿书
状态: 已添加到草稿箱

请前往公众号后台查看并发布。
```

## 主题样式详情

### 简约专业 (professional)
- 主色调: #1a73e8（蓝色）
- 标题: 蓝色下划线装饰
- 代码块: 暗色背景 + 语法高亮
- 整体: 专业、清晰、易读

### 优雅文艺 (elegant)
- 主色调: #2d5a27（墨绿）
- 标题: 居中、带间距
- 段落: 首行缩进2字符
- 整体: 文艺、优雅、舒适

### 活力橙 (vibrant)
- 主色调: #ff6b35（橙色）
- 标题: 背景色块装饰
- 代码块: 左边框高亮
- 整体: 活力、醒目、吸睛

### 暗黑极客 (dark)
- 主色调: #61dafb（青色）
- 背景: 深色 #1a1a2e
- 代码块: GitHub 暗色主题
- 整体: 科技、极客、酷炫

## 文件结构

```
skills/wechat-publish/
├── SKILL.md            # 技能说明文件
├── config.js           # 配置管理模块（新增）
├── converter.js        # Markdown 转 HTML 转换器
├── image-uploader.js   # 图床图片上传模块
├── cover-generator.js  # AI 封面图生成模块
├── cover-prompt.md     # 封面图提示词模板（可迭代）
├── temp/               # 临时文件目录（已加入 .gitignore）
└── package.json        # 依赖配置

用户配置文件位置:
~/.wechat-publish/config.json
```

## 注意事项

1. **标题限制**: 最多64字符
2. **摘要限制**: 最多120字符
3. **图片**: 系统自动从内容中提取第一张图作为封面
4. **链接**: 自动转换为文末脚注形式
5. **代码块**: 自动语法高亮
6. **发布位置**: 草稿箱，需手动发布
7. **配置文件**: 存储在 `~/.wechat-publish/config.json`，可手动编辑
8. **重新初始化**: 删除配置文件后，下次使用会重新进入引导流程
