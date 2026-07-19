# 微信公众号发布技能

## 功能介绍

将 Markdown 文章一键发布到微信公众号草稿箱，包含：
- 4 种精美主题风格（简约专业、优雅文艺、活力橙、暗黑极客）
- AI 自动生成封面图（基于文章标题）
- 本地图片自动上传到图床
- 链接自动转换为文末脚注
- 代码块语法高亮
- CSS 内联化（完美适配微信编辑器）

## 安装方法

1. 将 `wechat-publish` 文件夹复制到 `~/.claude/skills/` 目录下
2. 进入目录执行 `npm install` 安装依赖
3. 重启 Claude Code

## 首次使用

首次使用会自动进入配置引导，需要准备：
- **微信发布 API Key**（必需）- 从 https://wx.limyai.com 获取
- **ImgBB API Key**（可选）- 从 https://api.imgbb.com 获取，用于上传文章图片
- **Gemini API Key**（可选）- 用于 AI 生成封面图

配置保存在 `~/.wechat-publish/config.json`

## 使用方法

```
/publish-wechat <文件路径>
```

或直接说：
```
发布到公众号 xxx.md
把这篇文章发到微信
```

## 使用示例

```
/publish-wechat ./my-article.md
/publish-wechat ~/Documents/技术分享.md
发布到公众号 ./weekly-report.md
把 readme.md 发到微信
```

## 文件结构

```
wechat-publish/
├── SKILL.md              # 技能说明文件
├── config.js             # 配置管理模块
├── converter.js          # Markdown 转 HTML 转换器
├── image-uploader.js     # 图床上传模块
├── cover-generator.js    # AI 封面图生成模块
├── cover-prompt.md       # 封面图提示词模板
├── package.json          # 依赖配置
└── temp/                 # 临时文件目录
```
