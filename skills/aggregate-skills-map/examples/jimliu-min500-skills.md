# 🎯 JimLiu（宝玉）技能地图（⭐ ≥ 500 + 仅 Skills 关键词）

> **筛选条件**：star ≥ 500 · 仅 `skill|nuwa|darwin` 关键词 · 排除 fork
>
> 实测命令：`./aggregate.sh JimLiu --skill-only`
>
> **结果**：230 公开仓库 → 4 个 ≥500 ⭐ → **3 个真正的高质量 Skills**

## 👤 用户画像

**Jim Liu 宝玉** · 2011-03-03 加入 GitHub（**GitHub 14 年老兵**）· 4,661 followers · 230 公开仓库

- **核心定位**：中文 AI 提效博主 · 内容创作自动化（公众号工作流）+ 设计本地化 + 视频剪辑
- **代表作**：`baoyu-skills`（**23,845 ⭐** —— Claude Skills 领域全球前列）
- **生态命名**：`baoyu-*` 系列（宝玉拼音）—— 一个完整的"宝玉 AI 工具链"

---

## 🏆 旗舰（20K+ ⭐）

| ⭐ | 仓库 | 简介 |
|----|------|------|
| **23,845** | [**baoyu-skills**](https://github.com/JimLiu/baoyu-skills) | 宝玉的 skills 合集（**20+ skills**）—— 公众号文章工作流：cover-image → article-illustrator → post-to-wechat；支持 Claude Code / Codex / skills.sh；可通过 `npx skills add jimliu/baoyu-skills` 安装；支持 ClawHub / OpenClaw 分发 |

## 🧠 元能力 Skills（设计本地化）

| ⭐ | 仓库 | 简介 |
|----|------|------|
| **2,704** | [**baoyu-design**](https://github.com/JimLiu/baoyu-design) | **Claude Design 本地版**作为 Agent Skill —— 在 Cursor / Claude Code 等 Agent 中生成精美的 UI mockups、原型、slides、wireframes，自包含 HTML 输出，**无需 claude.ai/design**（推荐用 Opus 4.8） |

## 📚 教程/电子书

| ⭐ | 仓库 | 简介 |
|----|------|------|
| **594** | [**Illustrated-Agent-Skills**](https://github.com/JimLiu/Illustrated-Agent-Skills) | **《图解Skill——AI 提效实战指南》**官方 Repo（宝玉出的 Skill 实战书） |

---

## 📊 对照（star≥500 全部 4 个，含非 skills 关键词）

| ⭐ | 仓库 | 简介 | 是否 skills |
|----|------|------|----------|
| 23,845 | baoyu-skills | （空 desc） | ✅ |
| 2,704 | baoyu-design | Claude Design 本地版 | ✅ |
| 594 | Illustrated-Agent-Skills | 《图解Skill》 | ✅ |
| 512 | [**claude-agent-kit**](https://github.com/JimLiu/claude-agent-kit) | 基于 `@anthropic-ai/claude-agent-sdk` 的工具包：Session 管理、消息解析、WebSocket 编排（**不是 Skill，是 SDK**） | ❌ |

## 🔍 放宽到 ≥100 多 1 个：baocut

| ⭐ | 仓库 | 简介 |
|----|------|------|
| 225 | [**baocut**](https://github.com/JimLiu/baocut) | **BaoCut macOS 视频剪辑 Agent Skill** —— 通过自然语言驱动 BaoCut：转录、字幕添加/翻译、说话人识别、清理 talking-head 视频、导出；与 Claude Code / Codex / skills.sh 兼容；需要 macOS + 安装 BaoCut app |

---

## 🔑 关键洞察（与 alchaincyf 对比）

| 维度 | alchaincyf（花叔） | JimLiu（宝玉） |
|------|-------------------|---------------|
| **核心作品** | nuwa-skill (28K) | **baoyu-skills (24K)** —— 全球 Top 3 Skills |
| **生态命名** | nuwa-*（女娲） | baoyu-*（宝玉） |
| **核心方向** | **人物思维蒸馏**（nuwa 体系） | **内容创作工作流**（公众号自动化） |
| **元能力** | darwin-skill（自我进化） | baoyu-design（设计本地化） |
| **出版物** | 11 本橙皮书电子书 | 《图解Skill》书籍 |
| **互补性** | 蒸馏"人" | 蒸馏"事"（文章/视频/设计） |

**两者高度互补**：花叔做"AI 懂人"，宝玉做"AI 干活"。如果合并使用：
- 用 nuwa-skill 蒸馏你的写作风格
- 用 baoyu-post-to-wechat 一键发布到公众号
- 用 baoyu-cover-image 生成封面图
- 用 baoyu-design 做 UI mockup
- 用 baocut 剪视频

## 💡 给你的实战建议

宝玉的工具链对你**当前已有的 awesome-skills-map 仓库**有直接借鉴价值：
1. **`npx skills add` 安装方式** —— 比直接 clone SKILL.md 更友好
2. **`baoyu-post-to-wechat`** —— 对标你已收录的「第 10 章微信公众号一键排版」
3. **`baoyu-cover-image`** —— 配合「小红书图文生成器」封面工作流
4. **`Illustrated-Agent-Skills`** —— 可以作为 awesome-skills-map 仓库的入门读物推荐

## 🔗 相关文件

- 完整版（含所有 ≥500 ⭐ 4 个）：`jimliu.md`
- 实测脚本：`../aggregate.sh`