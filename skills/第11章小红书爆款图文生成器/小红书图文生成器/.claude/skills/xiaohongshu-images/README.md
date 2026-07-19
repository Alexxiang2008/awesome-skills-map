# 小红书图文生成器

一键将文章转换为小红书风格的精美图文，自动分页，文字不截断。

## 功能特点

- 📝 支持 Markdown、HTML、纯文本输入
- 🎨 精美卡片式排版（奶油色卡片 + 深色背景）
- 📐 自动生成 3:4 比例图片（1200×1600px 高清）
- ✂️ 智能分页，确保文字不被截断
- 🖼️ 可选：AI 生成《纽约客》风格封面图
- 🎯 首次使用引导，小白友好

## 快速开始

### 1. 安装 Skill

**方式一：使用 Skills CLI（推荐）**

```bash
npx skills add your-username/xiaohongshu-images -g
```

**方式二：手动安装**

1. 下载本仓库
2. 复制到 Claude Code 技能目录：
   ```bash
   cp -r xiaohongshu-images ~/.claude/skills/
   ```

### 2. 安装依赖

```bash
# 安装 Playwright（截图工具）
pip3 install playwright

# 安装 Chromium 浏览器（约 130MB）
python3 -m playwright install chromium

# 安装 requests（封面图 API 调用需要）
pip3 install requests
```

**常见安装问题：**

- 权限不足？加 `--user`：`pip3 install --user playwright`
- Chromium 下载慢？设置国内镜像：
  ```bash
  export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
  python3 -m playwright install chromium
  ```
- Mac 提示 `xcrun: error`？运行 `xcode-select --install`

### 3. 开始使用

在 Claude Code 中输入：

```
/xiaohongshu-images /path/to/your/article.md
```

首次使用会有引导设置，按提示操作即可。设置完成后还可以用内置示例文章体验效果。

## 使用方法

支持三种输入方式：

```bash
# 1. 文件路径
/xiaohongshu-images /Users/xxx/article.md

# 2. 网页链接
/xiaohongshu-images https://example.com/article

# 3. 直接粘贴内容
/xiaohongshu-images
（然后粘贴文章内容）
```

## 输出示例

```
小红书输出/
└── 2024-01-01-我的文章标题/
    ├── xhs-preview.html    # 浏览器预览
    └── _attachments/
        ├── cover-xhs.png   # 封面图（可选）
        ├── xhs-01.png      # 第 1 页
        ├── xhs-02.png      # 第 2 页
        └── ...
```

## 配置文件

首次使用后，配置保存在项目目录：

```
.xiaohongshu-images/config.yaml
```

可手动编辑修改：

```yaml
# 输出设置
output:
  mode: project          # project（当前项目）或 custom（自定义）
  subfolder: "小红书输出"  # 输出子目录名

# 封面图设置
cover:
  enabled: true          # 是否启用 AI 封面图
  api: volcano           # volcano（推荐）/ yunwu / openai / none
  style: default         # default / tech / warm / minimal / ink-wash

# 样式设置
style:
  template: default      # default / mom-reading-club
```

## 封面图功能

### 支持的 API

| API | 环境变量 | 获取地址 | 说明 |
|-----|---------|---------|------|
| **火山方舟（推荐）** | `ARK_API_KEY` | https://console.volcengine.com/ark | 国内访问最稳定，豆包 seedream 模型 |
| 云雾 API | `YUNWU_API_KEY` | https://yunwu.ai | Gemini 代理 |
| OpenAI DALL-E | `OPENAI_API_KEY` | https://platform.openai.com | 需要科学上网 |

### 配置步骤（以火山方舟为例）

```bash
# 1. 设置环境变量
export ARK_API_KEY="你的API Key"

# 2. 编辑配置文件，启用封面图
# .xiaohongshu-images/config.yaml
cover:
  enabled: true
  api: volcano
  style: default  # 可选: tech / warm / minimal / ink-wash
```

**火山方舟 API Key 获取：**
1. 访问 https://console.volcengine.com/ark 注册火山引擎账号
2. 开通方舟大模型服务
3. 创建 API Key
4. 设置环境变量：`export ARK_API_KEY="你的API Key"`

### 封面风格

| 风格 | 说明 | 适用场景 |
|------|------|---------|
| `default` | 《纽约客》风格插画 | 通用文章 |
| `tech` | 科技蓝色调 | AI、编程、技术类 |
| `warm` | 暖色调 | 个人故事、情感类 |
| `minimal` | 极简风格 | 简洁、禅意内容 |
| `ink-wash` | 书法水墨风 | 文化、读书类 |

## 依赖说明

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| Python 3.8+ | 运行脚本 | 系统自带或 `brew install python3` |
| Playwright | 浏览器截图 | `pip3 install playwright` |
| Chromium | 无头浏览器 | `python3 -m playwright install chromium` |
| requests | API 调用 | `pip3 install requests` |

## 常见问题

### Q: 截图失败怎么办？

重新安装 Playwright：
```bash
pip3 install playwright
python3 -m playwright install chromium
```

### Q: Mac 提示 "xcrun: error"？

安装 Xcode 命令行工具：
```bash
xcode-select --install
```

### Q: 字体显示为方块/豆腐块？

需要等待 Google Fonts 加载。如果网络不好：
1. 使用代理
2. 或手动安装 Noto Serif SC 字体到系统

### Q: 封面图生成失败？

1. 检查环境变量是否设置：`echo $ARK_API_KEY`
2. 检查网络连接
3. 可以选择跳过封面图，之后手动添加

### Q: 如何重新运行设置？

```bash
rm -rf .xiaohongshu-images/
```
然后重新调用 `/xiaohongshu-images`

### Q: 图片太多怎么办？

小红书单篇最多 18 张图。建议：
- 精简文章内容
- 拆分为多篇发布

## 目录结构

```
xiaohongshu-images/
├── SKILL.md              # 技能定义（Claude 读取）
├── README.md             # 本文件
├── prompts/
│   ├── default.md        # 默认样式模板
│   └── mom-reading-club.md  # 书法水墨风格
└── scripts/
    ├── screenshot.py     # 截图脚本
    └── cover_generator.py  # 封面图生成脚本
```

## 许可证

MIT License
