---
name: xiaohongshu-images
description: 将文章转换为小红书图文 - 支持 Markdown/HTML/文本，自动生成 3:4 比例精美图片
---

# 小红书图文生成器

将你的文章一键转换为小红书风格的精美图文，自动分页，文字不截断。

## 功能特点

- 📝 支持 Markdown、HTML、纯文本输入
- 🎨 精美的卡片式排版（奶油色卡片 + 深色背景）
- 📐 自动生成 3:4 比例图片（小红书最佳尺寸）
- ✂️ 智能分页，确保文字不被截断
- 🖼️ 可选：AI 生成封面图

---

## 使用方法

```
/xiaohongshu-images <文章路径或内容>
```

**示例：**
```
/xiaohongshu-images /path/to/article.md
/xiaohongshu-images https://example.com/article
/xiaohongshu-images （然后粘贴文章内容）
```

---

## 执行流程

当用户调用此技能时，按以下步骤执行：

### Step 0: 首次使用检查 ⛔ 必须先完成

**每次调用技能时，首先检查配置文件是否存在：**

```bash
test -f "{{PROJECT_DIR}}/.xiaohongshu-images/config.yaml" && echo "configured" || echo "not configured"
```

**如果返回 "not configured"，必须先完成首次设置，不要执行任何其他操作。**

#### 首次设置流程

**0.1 欢迎语**

向用户显示：

```
👋 欢迎使用小红书图文生成器！

这是你第一次使用，我需要帮你完成一些简单的设置。

让我们开始吧！
```

**0.2 环境诊断（一次性检查所有依赖）**

执行以下命令，一次性检查所有环境依赖：

```bash
echo "=== ENV_CHECK_START ==="
echo -n "python3: "; python3 --version 2>/dev/null || echo "NOT FOUND"
echo -n "pip3: "; pip3 --version 2>/dev/null || echo "NOT FOUND"
python3 -c "import playwright; print('playwright: OK')" 2>/dev/null || echo "playwright: NOT FOUND"
python3 -c "from playwright.sync_api import sync_playwright; b=sync_playwright().start().chromium.launch(headless=True); b.close(); print('chromium: OK')" 2>/dev/null || echo "chromium: NOT FOUND"
echo "=== ENV_CHECK_END ==="
```

根据结果，显示一个清晰的环境状态表：

```
📋 环境检查结果：

  ✅ Python    3.11.5
  ✅ pip       23.2.1
  ❌ Playwright 未安装
  —  Chromium   等待 Playwright 安装

需要安装 Playwright 才能继续。
```

- 如果 Python 未检测到 → 告诉用户：
  ```
  ❌ 未检测到 Python 环境

  这个工具需要 Python 来运行。请先安装 Python：

  Mac 用户：
  1. 打开终端
  2. 运行：brew install python3

  或者访问 https://www.python.org/downloads/ 下载安装

  安装完成后，请重新运行 /xiaohongshu-images
  ```
  然后停止执行。

- 如果 Python 和 pip 正常但 Playwright 未安装 → 进入 Step 0.3
- 如果所有依赖都正常 → 跳到 Step 0.4

**0.3 检查并安装 Playwright**

如果 Playwright 未安装，向用户显示详细信息并询问：

```
🔧 正在检查截图工具...

❌ 未检测到 Playwright

Playwright 是生成图片的核心工具，需要安装。
```

使用 AskUserQuestion 工具：
```yaml
header: "安装依赖"
question: "需要安装截图工具（Playwright），这是生成图片必需的。是否现在安装？"
options:
  - label: "是，帮我安装（推荐）"
    description: "自动安装 Playwright 和浏览器"
  - label: "稍后手动安装"
    description: "显示安装命令，你自己来操作"
```

**如果用户选择"是"，执行：**
```bash
pip3 install playwright && python3 -m playwright install chromium
```

注意：使用 `python3 -m playwright` 而不是直接调用 `playwright` 命令，避免 PATH 问题。

安装完成后显示：
```
✅ Playwright 安装完成！
```

**如果用户选择"稍后手动安装"，显示详细指引：**

```
📋 安装步骤：
1. 安装 Python 包：
   pip3 install playwright

2. 安装浏览器（约 130MB）：
   python3 -m playwright install chromium

⚠️  常见问题：
• 如果提示 "permission denied"，请加 --user：
  pip3 install --user playwright

• 如果 chromium 下载太慢，可设置国内镜像：
  export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

• 如果提示 "playwright: command not found"，请用：
  python3 -m playwright install chromium

安装完成后，请重新运行 /xiaohongshu-images
```
然后停止执行。

**0.4 询问输出目录偏好**

使用 AskUserQuestion 工具：
```yaml
header: "输出目录"
question: "生成的图片保存到哪里？"
options:
  - label: "当前项目目录（推荐）"
    description: "保存到 ./小红书输出/<文章标题>/"
  - label: "自定义目录"
    description: "指定一个固定的输出目录"
```

如果选择"自定义目录"，再询问具体路径。

**0.5 询问封面图功能**

使用 AskUserQuestion 工具：
```yaml
header: "封面图"
question: "是否需要 AI 自动生成封面图？"
options:
  - label: "不需要（推荐新手）"
    description: "直接从文章标题开始，你可以之后手动添加封面"
  - label: "需要，我有 API Key"
    description: "使用 AI 生成《纽约客》风格的封面插画"
```

如果选择"需要"，继续询问 API 配置：
```yaml
header: "图像 API"
question: "你使用哪个图像生成服务？"
options:
  - label: "火山方舟（推荐）"
    description: "使用豆包 seedream 模型，国内访问最稳定，需要 ARK_API_KEY"
  - label: "云雾 API"
    description: "使用 yunwu.ai 代理 Gemini，需要 YUNWU_API_KEY"
  - label: "OpenAI DALL-E"
    description: "需要 OPENAI_API_KEY，需要科学上网"
  - label: "其他/稍后配置"
    description: "你可以之后在配置文件中添加"
```

根据选择，提示用户设置环境变量：

**如果选择"火山方舟"：**
```
请设置 ARK_API_KEY 环境变量：

1. 访问 https://console.volcengine.com/ark 注册火山引擎账号
2. 开通方舟大模型服务
3. 创建 API Key
4. 设置环境变量（在终端运行）：
   export ARK_API_KEY="你的API Key"

5. 或添加到 ~/.zshrc（永久生效）：
   echo 'export ARK_API_KEY="你的API Key"' >> ~/.zshrc
   source ~/.zshrc

设置好后，封面图功能就可以使用了！
```

**如果选择"云雾 API"：**
```
请设置 YUNWU_API_KEY 环境变量：

1. 获取 API Key：访问 https://yunwu.ai 注册并获取
2. 设置环境变量（在终端运行）：
   export YUNWU_API_KEY="你的API Key"

3. 或添加到 ~/.zshrc（永久生效）：
   echo 'export YUNWU_API_KEY="你的API Key"' >> ~/.zshrc
   source ~/.zshrc

设置好后，封面图功能就可以使用了！
```

**如果选择"OpenAI DALL-E"：**
```
请设置 OPENAI_API_KEY 环境变量：

1. 获取 API Key：访问 https://platform.openai.com/api-keys
2. 设置环境变量：
   export OPENAI_API_KEY="你的API Key"
```

**0.6 保存配置**

创建配置目录和文件：

```bash
mkdir -p "{{PROJECT_DIR}}/.xiaohongshu-images"
```

写入配置文件 `{{PROJECT_DIR}}/.xiaohongshu-images/config.yaml`：

```yaml
# 小红书图文生成器配置
# 创建时间: {{当前日期时间}}

# 输出设置
output:
  # 输出目录模式: project（当前项目）或 custom（自定义路径）
  mode: project
  # 自定义路径（仅当 mode 为 custom 时有效）
  custom_path: ""
  # 输出子目录名称
  subfolder: "小红书输出"

# 封面图设置
cover:
  # 是否启用 AI 封面图生成
  enabled: false
  # 图像生成 API: volcano / yunwu / openai / none
  api: none
  # API Key 环境变量名（不要直接写 key）
  api_key_env: ""
  # 封面风格: default / tech / warm / minimal / ink-wash
  style: default

# 样式设置
style:
  # 使用的模板: default / mom-reading-club
  template: default

# 首次设置已完成
setup_completed: true
```

**0.7 设置完成 & 快速体验**

显示：
```
🎉 设置完成！

你的配置：
• 输出目录：当前项目/小红书输出/
• 封面图：[已启用/未启用]
• 样式模板：default
```

然后使用 AskUserQuestion 工具提供快速体验选项：

```yaml
header: "快速体验"
question: "要不要用示例文章试一下效果？"
options:
  - label: "好的，试一下（推荐）"
    description: "用一段内置的短文章生成 2-3 张图片，看看效果"
  - label: "不用了，我有自己的文章"
    description: "直接开始使用"
```

**如果用户选择"好的，试一下"：**

使用以下内置示例文章，直接走完 Step 2-8 流程：

```markdown
# 为什么高手都在用清单思维

你有没有发现，越忙的人越不容易出错？

不是因为他们更聪明，而是因为他们善用**清单**。

## 清单思维的三个层次

**第一层：不遗漏**

把要做的事全部列出来，大脑就不需要时刻记着。一旦写下来，焦虑感会立刻降低 50%。

**第二层：分优先级**

不是所有事情都一样重要。每天只做最重要的三件事，其他的要么删掉，要么推迟。

**第三层：复用模板**

每周重复的工作，做成模板。下次直接套用，效率翻倍。

> 查理·芒格说过：「用清单来避免愚蠢，比努力变聪明要容易得多。」

## 今天就开始

拿出手机备忘录，写下明天最重要的三件事。就这么简单。

你会发现，清单不只是工具，它是一种**掌控感**。
```

**如果用户选择"不用了"，显示：**
```
现在你可以开始使用了！请提供你要转换的文章。
```

---

### Step 1: 读取配置

如果配置文件存在，读取配置：

```bash
cat "{{PROJECT_DIR}}/.xiaohongshu-images/config.yaml"
```

解析配置内容，获取：
- 输出目录设置
- 封面图是否启用
- 使用的样式模板

---

### Step 2: 获取输入内容

用户会提供以下之一：
- 文件路径（如 `/path/to/article.md`）
- URL（如 `https://example.com/article`）
- 直接粘贴的文章内容

**如果用户没有提供任何内容**，询问：
```
请提供你要转换的文章：

1. 📁 文件路径：直接输入文件路径，如 /Users/xxx/article.md
2. 🔗 网页链接：输入文章 URL
3. 📝 直接粘贴：把文章内容粘贴到这里

你想用哪种方式？
```

---

### Step 3: 读取样式模板

根据配置中的 `style.template` 读取对应模板：

```
{{SKILL_DIR}}/prompts/{{template}}.md
```

默认使用 `default.md`。

---

### Step 4: 创建输出目录

根据配置创建输出目录：

**如果 mode 是 project：**
```bash
mkdir -p "{{PROJECT_DIR}}/小红书输出/{{日期}}-{{文章标题}}/_attachments"
```

**如果 mode 是 custom：**
```bash
mkdir -p "{{custom_path}}/{{日期}}-{{文章标题}}/_attachments"
```

文章标题处理规则：
- 替换空格为连字符
- 移除特殊字符
- 最多保留 30 个字符

---

### Step 5: 生成封面图（可选）

**只有当配置中 `cover.enabled: true` 时才执行此步骤。**

如果未启用，跳过此步骤，在 HTML 中不包含封面图。

如果启用，根据配置的 `cover.api` 选择生成方式：

#### 方式一：使用火山方舟 API（推荐）

当 `cover.api: volcano` 时：

1. **检查环境变量**
   ```bash
   test -n "$ARK_API_KEY" && echo "configured" || echo "not configured"
   ```

   如果未配置，提示用户：
   ```
   ⚠️ 未检测到 ARK_API_KEY 环境变量

   请先设置：
   export ARK_API_KEY="你的API Key"

   获取 API Key：https://console.volcengine.com/ark
   ```

2. **调用封面生成脚本**
   ```bash
   python3 "{{SKILL_DIR}}/scripts/cover_generator.py" \
     --title "{{文章标题}}" \
     --style "{{cover.style}}" \
     --api volcano \
     --output "{{输出目录}}/_attachments/cover-xhs.png"
   ```

3. **显示进度**
   ```
   🎨 正在生成封面图...
   使用模型：doubao-seedream-5-0-260128
   风格：{{cover.style}}
   ```

4. **生成成功后显示**
   ```
   ✅ 封面图生成完成！
   位置：{{输出目录}}/_attachments/cover-xhs.png
   ```

#### 方式二：使用云雾 API

当 `cover.api: yunwu` 时：

1. **检查环境变量**
   ```bash
   test -n "$YUNWU_API_KEY" && echo "configured" || echo "not configured"
   ```

   如果未配置，提示用户：
   ```
   ⚠️ 未检测到 YUNWU_API_KEY 环境变量

   请先设置：
   export YUNWU_API_KEY="你的API Key"

   获取 API Key：https://yunwu.ai
   ```

2. **调用封面生成脚本**
   ```bash
   python3 "{{SKILL_DIR}}/scripts/cover_generator.py" \
     --title "{{文章标题}}" \
     --style "{{cover.style}}" \
     --api yunwu \
     --output "{{输出目录}}/_attachments/cover-xhs.png"
   ```

3. **显示进度**
   ```
   🎨 正在生成封面图...
   使用模型：gemini-3-pro-image-preview
   风格：{{cover.style}}
   ```

4. **生成成功后显示**
   ```
   ✅ 封面图生成完成！
   位置：{{输出目录}}/_attachments/cover-xhs.png
   ```

#### 方式三：使用 OpenAI DALL-E

当 `cover.api: openai` 时：

1. 检查 `OPENAI_API_KEY` 环境变量
2. 调用封面生成脚本（`--api openai`）
3. 保存到 `_attachments/cover-xhs.png`

#### 封面风格选项

| 风格 | 说明 | 适用场景 |
|------|------|---------|
| `default` | 《纽约客》风格插画 | 通用文章 |
| `tech` | 科技蓝色调 | AI、编程、技术类 |
| `warm` | 暖色调 | 个人故事、情感类 |
| `minimal` | 极简风格 | 简洁、禅意内容 |
| `ink-wash` | 书法水墨风 | 文化、读书类 |

#### 生成失败处理

如果生成失败，询问用户：
```yaml
header: "封面图"
question: "封面图生成失败，如何处理？"
options:
  - label: "继续，不要封面图"
    description: "直接从文章标题开始"
  - label: "重试"
    description: "再试一次生成封面图"
  - label: "手动上传"
    description: "你可以稍后手动添加封面图到 _attachments/cover-xhs.png"
```

---

### Step 6: 生成 HTML 页面

根据样式模板将文章内容转换为 HTML：

1. **解析文章内容**
   - 提取标题（h1）
   - 识别段落、列表、引用、代码块等

2. **应用样式**
   - 深色渐变背景
   - 600×800px 奶油色卡片
   - Noto Serif SC 字体（标题）
   - 自动高亮金句（使用 `<mark>` 标签）

3. **保存 HTML**
   - 保存到输出目录的 `xhs-preview.html`

4. **告知用户**
   ```
   📄 HTML 预览页面已生成
   位置：{{输出目录}}/xhs-preview.html

   正在生成截图...
   ```

---

### Step 7: 截图生成图片

使用 Playwright 截取 HTML 页面：

```bash
cd "{{SKILL_DIR}}" && python3 scripts/screenshot.py "{{HTML文件路径}}"
```

**截图规格：**
- 尺寸：1200×1600px（3:4 比例，2x 高清）
- 智能分页：确保文字不被截断
- 输出：`xhs-01.png`, `xhs-02.png`, ...

**显示进度：**
```
📸 正在截图...
  ✓ xhs-01.png
  ✓ xhs-02.png
  ✓ xhs-03.png
  ...
```

---

### Step 8: 完成报告

截图完成后，向用户报告：

```
🎉 小红书图文生成完成！

📊 生成结果：
• 图片数量：{{N}} 张
• 图片尺寸：1200×1600px（3:4 比例）
• 保存位置：{{输出目录}}

📁 文件列表：
├── xhs-preview.html    # 预览页面
├── _attachments/
│   ├── xhs-01.png      # 第 1 页
│   ├── xhs-02.png      # 第 2 页
│   └── ...

💡 下一步：
1. 打开 _attachments 文件夹查看图片
2. 直接上传到小红书发布
3. 建议添加 3-5 个相关话题标签

需要我帮你打开输出文件夹吗？
```

然后询问：
```yaml
header: "打开文件"
question: "需要我帮你打开输出文件夹吗？"
options:
  - label: "是，打开文件夹"
    description: "在 Finder 中打开输出目录"
  - label: "是，打开第一张图片"
    description: "预览生成的第一张图片"
  - label: "不用了"
    description: "我自己去找"
```

根据选择执行：
```bash
# 打开文件夹
open "{{输出目录}}"

# 或打开第一张图片
open "{{输出目录}}/_attachments/xhs-01.png"
```

---

## 配置文件说明

配置文件位置：`{{PROJECT_DIR}}/.xiaohongshu-images/config.yaml`

用户可以手动编辑此文件修改设置：

```yaml
# 输出设置
output:
  mode: project          # project 或 custom
  custom_path: ""        # 自定义路径
  subfolder: "小红书输出"  # 子目录名称

# 封面图设置
cover:
  enabled: false         # 是否启用
  api: volcano           # volcano / yunwu / openai / none
  style: default         # default / tech / warm / minimal / ink-wash

# 样式设置
style:
  template: default      # default / mom-reading-club
```

### 封面图 API 配置

| API | 环境变量 | 获取地址 | 说明 |
|-----|---------|---------|------|
| **火山方舟（推荐）** | `ARK_API_KEY` | https://console.volcengine.com/ark | 国内访问最稳定，豆包 seedream 模型 |
| 云雾 API | `YUNWU_API_KEY` | https://yunwu.ai | Gemini 代理，需要一定网络条件 |
| OpenAI DALL-E | `OPENAI_API_KEY` | https://platform.openai.com/api-keys | 需要科学上网 |

---

## 常见问题

### Q: 截图失败怎么办？

检查 Playwright 是否正确安装：
```bash
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

如果报错，重新安装：
```bash
pip3 install playwright
python3 -m playwright install chromium
```

### Q: Mac 提示 "xcrun: error" 怎么办？

安装 Xcode 命令行工具：
```bash
xcode-select --install
```

### Q: 字体显示为方块/豆腐块？

需要等待 Google Fonts 加载。如果网络不好，可以：
1. 使用代理
2. 或手动安装 Noto Serif SC 字体到系统

### Q: 生成的图片背景颜色不对？

确保使用默认样式模板，不要手动修改 HTML 中的背景色。

### Q: 如何重新运行设置？

删除配置文件后重新运行：
```bash
rm -rf .xiaohongshu-images/
```
然后重新调用 `/xiaohongshu-images`

### Q: Playwright 安装遇到问题？

**提示 "permission denied"：**
```bash
pip3 install --user playwright
```

**Chromium 下载太慢：**
```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
python3 -m playwright install chromium
```

**提示 "playwright: command not found"：**
```bash
python3 -m playwright install chromium
```

### Q: 如何更换样式模板？

编辑配置文件，修改 `style.template` 的值，可选：
- `default` - 标准样式
- `mom-reading-club` - 书法水墨风格

### Q: 如何启用封面图功能？

1. 编辑配置文件，设置 `cover.enabled: true`
2. 设置 `cover.api` 为 `volcano`（推荐）、`yunwu` 或 `openai`
3. 设置对应的环境变量：
   ```bash
   # 火山方舟（推荐）
   export ARK_API_KEY="你的API Key"

   # 或 云雾 API
   export YUNWU_API_KEY="你的API Key"

   # 或 OpenAI
   export OPENAI_API_KEY="你的API Key"
   ```

### Q: 封面图有哪些风格？

| 风格 | 说明 |
|------|------|
| `default` | 《纽约客》风格插画，通用 |
| `tech` | 科技蓝色调，适合技术文章 |
| `warm` | 暖色调，适合情感故事 |
| `minimal` | 极简风格，大量留白 |
| `ink-wash` | 书法水墨风，适合文化类 |

### Q: 图片太多怎么办？

小红书单篇笔记最多支持 18 张图片。如果生成超过 18 张，建议：
1. 精简文章内容
2. 拆分为多篇笔记发布

---

## 依赖说明

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| Python 3.8+ | 运行脚本 | 系统自带或 `brew install python3` |
| Playwright | 浏览器截图 | `pip3 install playwright` |
| Chromium | 无头浏览器 | `python3 -m playwright install chromium` |
| requests | API 调用（封面图） | `pip3 install requests` |

---

## 目录结构

```
{{SKILL_DIR}}/
├── SKILL.md              # 本文件
├── README.md             # 用户文档
├── prompts/
│   ├── default.md        # 默认样式模板
│   └── mom-reading-club.md  # 书法水墨风格模板
└── scripts/
    ├── screenshot.py     # 截图脚本
    └── cover_generator.py  # 封面图生成脚本

{{PROJECT_DIR}}/
├── .xiaohongshu-images/
│   └── config.yaml       # 用户配置
└── 小红书输出/
    └── {{日期}}-{{标题}}/
        ├── xhs-preview.html
        └── _attachments/
            ├── cover-xhs.png  # 封面图（可选）
            ├── xhs-01.png
            ├── xhs-02.png
            └── ...
```

---

## 小红书社区规范提醒

生成的内容请确保符合小红书社区规范：

⚠️ **避免以下内容：**
- 绝对化用语（最好、第一、国家级）
- 夸大效果（一分钟见效、立刻瘦10斤）
- 未经证实的医疗/投资建议
- 诋毁他人或品牌的内容

📋 **官方规范：**
- 社区规范：https://www.xiaohongshu.com/crown/community/rules
- 社区公约：https://www.xiaohongshu.com/crown/community/agreement
