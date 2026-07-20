# 🌟 75 个 Claude Skills 候选全景图

> **来源**：`discover.py` 自动扫描 GitHub（4 个 topic × 50 候选 = 189 个原始 → 排除索引库 18 个 → 真 skill 153 个 → **入选 75 个**）
>
> **评分**：硬指标 4 维（stars 30 + forks/stars 15 + recency 25 + issue_close 10）+ 卫生指标 15 + 生态 5 = **100 分上限**
>
> **阈值**：score ≥ 50 入选（基于 v0.4 实测中位数 ≈ 56.8）

---

## 📊 扫描统计

| 项 | 数量 |
|---|---|
| 原始候选 | 189 |
| 排除索引库/课程（awesome-*, -tutorial, framework 等） | 18 |
| 真 skill 候选 | 153 |
| **≥ 50 分入选** | **75** |
| 平均分 | ~60 |
| 最高分 | 74.7（career-ops / JeecgBoot） |

---

## 🏆 Tier 1 · Top 10 详细介绍（score ≥ 70）

### 1️⃣ career-ops（74.7 · 60K ⭐ · 19.7% forks/stars）
- **作者**：santifer
- **GitHub**：https://github.com/santifer/career-ops
- **简介**：Open-source AI 求职助手，扫描招聘网站、A-F 评分、定制简历、追踪申请进度。本地运行在 AI coding CLI（Claude Code / Gemini / Codex / OpenCode）
- **标签**：ai-agent, career, claude-code, job-search, resume
- **适合**：求职者节省筛选时间
- **价值**：⭐⭐⭐⭐⭐（60K 高 stars + 高 forks 实测真用）

### 2️⃣ JeecgBoot（74.7 · 47K ⭐ · 34.2% forks/stars）⭐ 高活跃度
- **作者**：jeecgboot
- **GitHub**：https://github.com/jeecgboot/JeecgBoot
- **简介**：AI 低代码平台 v2.0，**AI Skills 一句话生成整个系统**（前后端代码 / 流程 / 表单 / 报表 / 大屏）。内置 AI 应用平台：聊天、知识库、流程编排、MCP 插件
- **标签**：springboot, claude-code, mcp, rag, low-code, skills
- **适合**：Java 项目快速生成（声称解决 90% 重复工作）
- **价值**：⭐⭐⭐⭐（forks/stars 34.2% 极高，开发者真用过）
- **⚠️ 注意**：Java 生态，体积大，跟 Claude Skill 概念不完全等同

### 3️⃣ CowAgent（74.6 · 46K ⭐ · 22.3% forks/stars）
- **作者**：zhayujie
- **GitHub**：https://github.com/zhayujie/CowAgent
- **简介**：Open-source 超级 AI 助手 + Agent Harness。**规划任务、运行 tools 和 skills、记忆自进化**。多模型多渠道，一行安装
- **标签**：claude-code, codex, openclaw, multi-agent, harness
- **适合**：想要"开箱即用"全功能 agent 框架
- **价值**：⭐⭐⭐⭐⭐（中文作者维护，含 OpenClaw 支持）

### 4️⃣ hermes-agent（73.8 · **217K ⭐** · 18.8% forks/stars）⚡ 流量王
- **作者**：NousResearch
- **GitHub**：https://github.com/NousResearch/hermes-agent
- **简介**：The agent that grows with you（与你共成长的 agent）
- **标签**：anthropic, claude-code, codex, hermes, openclaw
- **适合**：高 star 信誉背书的通用 agent
- **价值**：⭐⭐⭐⭐（star 数恐怖，但描述极简——可能过度营销）

### 5️⃣ nanoclaw（72.6 · 30K ⭐ · **42.5% forks/stars**）⭐ 实战之王
- **作者**：nanocoai
- **GitHub**：https://github.com/nanocoai/nanoclaw
- **简介**：轻量级 OpenClaw 替代，**跑在 Docker 容器里**更安全。连接 WhatsApp/Telegram/Slack/Discord/Gmail，有记忆、定时任务
- **标签**：ai-agents, claude-code, openclaw
- **适合**：想本地跑 agent 又担心安全的用户
- **价值**：⭐⭐⭐⭐⭐（**forks/stars 42.5% 极高**，说明大量开发者 clone 实际用）

### 6️⃣ nanobot（72.3 · 46K ⭐ · 17.7% forks/stars）
- **作者**：HKUDS
- **GitHub**：https://github.com/HKUDS/nanobot
- **简介**：轻量级开源 AI agent，为 tools/chats/workflows 设计
- **标签**：claude-code, codex-cli, openclaw
- **适合**：想要轻量级可嵌入的 agent
- **价值**：⭐⭐⭐⭐（HKUDS 是顶级学术实验室，质量保证）

### 7️⃣ learn-claude-code（71.3 · 71K ⭐ · 16.3% forks/stars）⚡ 教育类
- **作者**：shareAI-lab
- **GitHub**：https://github.com/shareAI-lab/learn-claude-code
- **简介**：**Bash is all you need** —— 用最少代码从 0 到 1 实现 nano claude code-like agent harness
- **标签**：educational, tutorial, teaching
- **适合**：想**理解 Claude Code 内部原理**的开发者（71K ⭐ 教育类第一）
- **价值**：⭐⭐⭐⭐（教育类硬通货）

### 8️⃣ system_prompts_leaks（71.3 · 59K ⭐ · 16.3% forks/stars）
- **作者**：asgeirtj
- **GitHub**：https://github.com/asgeirtj/system_prompts_leaks
- **简介**：提取的 system prompts 集合：Anthropic（Claude Fable 5、Opus 4.8、Claude Code、Design）、OpenAI、xAI、Google Gemini 等
- **适合**：研究大模型 prompt 设计
- **价值**：⭐⭐⭐（高 star 但偏"泄露"性质，可能有版权风险）

### 9️⃣ ECC（70.3 · **231K ⭐** · 15.3% forks/stars）⚡ 流量王
- **作者**：affaan-m
- **GitHub**：https://github.com/affaan-m/ECC
- **简介**：agent harness 性能优化系统。Skills、instincts、memory、security、研究优先开发
- **适合**：优化 Claude Code 性能
- **价值**：⭐⭐⭐⭐（star 数恐怖，需进一步评估）

### 🔟 CLIProxyAPI（70.1 · 43K ⭐ · 15.7% forks/stars）
- **作者**：router-for-me
- **GitHub**：https://github.com/router-for-me/CLIProxyAPI
- **简介**：**包装 Antigravity/ChatGPT Codex/Claude Code/Grok Build 成 OpenAI/Gemini/Claude/Codex 兼容 API**——免费用 Gemini 3.1 Pro、GPT 5.5、Grok 4.3、Claude 模型
- **标签**：antigravity, claude-code, gemini, openai
- **适合**：想跨模型 API 但不想付费的用户
- **价值**：⭐⭐⭐⭐（实用工具，节省 API 费）

---

## 🥈 Tier 2 · 11-30 高分候选（score 60-70）

| 排名 | score | ⭐ | 仓库 | 一句话 |
|------|-------|----|------|------|
| 11 | 66.9 | 65K | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 🌊 Leading agent meta-harness（多 agent 编排） |
| 12 | 66.7 | 28K | [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | 一行命令 clone 任意网站 |
| 13 | 66.0 | 40K | [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) | Claude Code 可视化指南 |
| 14 | 65.8 | 79K | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | **生产级工程 skills**（addyosmani 是 Google Chrome 团队） |
| 15 | 65.6 | 107K | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | **设计智能 skill**（107K ⭐ 流量王） |
| 16 | 65.0 | 63K | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | 从 vibe coding 到 agentic engineering |
| 17 | 64.7 | 91K | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | AI 编程助手 skill 跨 Claude Code/Codex/OpenCode |
| 18 | 64.7 | 22K | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | **345 Claude Code skills**（巨型合集） |
| 19 | 64.4 | 48K | [CherryHQ/cherry-studio](https://github.com/CherryHQ/cherry-studio) | AI 生产力 studio，多模型聊天 + 自主 agent |
| 20 | 64.4 | 38K | [wshobson/agents](https://github.com/wshobson/agents) | **Multi-harness plugin marketplace** |
| 21 | 64.1 | 32K | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | **Anthropic 官方 plugins 目录** |
| 22 | 63.7 | 87K | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | **跨会话持久化上下文**（87K ⭐） |
| 23 | 63.6 | 52K | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | **跨 Reddit/X/YouTube 研究任何话题的 AI skill** |
| 24 | 63.6 | 17K | [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) | Google NotebookLM Python API + skill |
| 25 | 63.3 | 75K | [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | **把代码转成可教学的可视化图** |
| 26 | 63.2 | 66K | [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) | omo/lazycodex（token 节省派编码 agent） |
| 27 | 63.1 | 29K | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) | Claude Code 配置 + 监控 CLI |
| 28 | 63.0 | 58K | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | **让 AI agent 看见整个互联网**（Read & search） |
| 29 | 62.7 | 37K | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) | **多 agent 团队编排**（Claude Code） |
| 30 | 62.7 | 31K | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | **把任何 agent 变成 AI 科学家** |

---

## 🥉 Tier 3 · 31-75 简表（score 50-60）

| 排名 | 仓库 | ⭐ | 一句话 |
|------|------|---|------|
| 31 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | 30K | 24/7 OpenClaw/Hermes cowork 应用 |
| 32 | [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | 60K | **压缩工具输出 + 日志 + RAG**（省钱） |
| 33 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 65K | **给 AI 品味**（停止生成垃圾） |
| 34 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 38K | 学术研究全流程（research→write→publish） |
| 35 | [farion1231/cc-switch](https://github.com/farion1231/cc-switch) | 118K | **跨平台 Claude Code 全能桌面助手** |
| 36 | [codeaashu/claude-code](https://github.com/codeaashu/claude-code) | 3K | Claude Code 工具介绍（forks/stars 115% 高） |
| 37 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 90K | 🪨 **省 token 哲学**——少 token 干大事 |
| 38 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 86K | **让 AI 像资深懒工程师那样思考** |
| 39 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 25K | 持久化文件规划（长任务用） |
| 40 | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) | 25K | 编码 agent 制作精美 slides |
| 41 | [manaflow-ai/cmux](https://github.com/manaflow-ai/cmux) | 24K | Ghostty-based macOS 终端 |
| 42 | [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master) | 10K | **写准确 prompts 的 skill** |
| 43 | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | 14K | 转文档网站/GitHub/PDF → Claude Skills |
| 44 | [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) | 4K | 网文/小说写作 skill 全流程 |
| 45 | [oraios/serena](https://github.com/oraios/serena) | 26K | 强大 MCP 工具包（代码语义检索） |
| 46 | [gastownhall/beads](https://github.com/gastownhall/beads) | 25K | Agent 记忆升级 |
| 47 | JimLiu/baoyu-skills | 23K | （5 博主已知，已入 taxonomy） |
| 48 | [SnailSploit/Claude-Red](https://github.com/SnailSploit/Claude-Red) | 2K | **进攻性安全 skills 库**（红队/渗透） |
| 49 | [jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud) | 26K | Claude Code 实时 HUD 插件 |
| 50 | [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 3K | Bug 猎杀 + 外部红队 skill 包 |
| 51 | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills) | 10K | 66 个全栈工程师 skills |
| 52 | [NevaMind-AI/memU](https://github.com/NevaMind-AI/memU) | 14K | 跨 agent 个人记忆 |
| 53 | [nexu-io/html-anything](https://github.com/nexu-io/html-anything) | 7K | 本地 AI 写 HTML 的 agentic 编辑器 |
| 54 | [jangviktor-web/nihaixia](https://github.com/jangviktor-web/nihaixia) | 1K | **倪海厦中医 Agent Skill**（伤寒论/金匮要略/针灸） |
| 55 | [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog) | 1K | Claude Code blog skill 套件（30 子技能 + 5 agent） |
| 56 | [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude) | 3K | **Claude Skills/Agents/Hooks 中心** |
| 57 | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 10K | AI 研究 + 工程综合 skill 库 |
| 58 | [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) | 3K | **跨 CLI 的 Obsidian 第二大脑** |
| 59 | [aaron-he-zhu/aaron-marketing-skills](https://github.com/aaron-he-zhu/aaron-marketing-skills) | 2K | 120 个营销 skills + 8 commands |
| 60 | [nowork-studio/NotFair](https://github.com/nowork-studio/NotFair) | 3K | **SEO/GEO/Google Ads/Meta Ads skills** |
| 61 | [Hao0321/claude-skill-social-post](https://github.com/Hao0321/claude-skill-social-post) | 0.5K | **学习你的 Facebook 写作风格**（个人化） |
| 62 | [geekjourneyx/md2wechat-skill](https://github.com/geekjourneyx/md2wechat-skill) | 3K | MD→微信公众号一键（40+ 排版样式） |
| 63 | [feiskyer/claude-code-settings](https://github.com/feiskyer/claude-code-settings) | 1K | 精选 skills + sub-agents + 配置 |
| 64 | [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill) | 6K | 自然语言生成 draw.io 图（11 预设） |
| 65 | [anbeime/skill](https://github.com/anbeime/skill) | 3K | **中文技能商店**（72 个分类 skills） |
| 66 | op7418/guizang-social-card-skill | 5K | （5 博主已知，已入 taxonomy） |
| 67 | [chuspeeism/dashi-ppt-skill](https://github.com/chuspeeism/dashi-ppt-skill) | 3K | AI agent 生成浏览器可编辑 PPT |
| 68 | [isjiamu/gzh-design-skill](https://github.com/isjiamu/gzh-design-skill) | 2K | **MD → 公众号 HTML**（6 主题 + 双关卡校验） |
| 69 | [wesammustafa/Claude-Code-Everything-You-Need-to-Know](https://github.com/wesammustafa/Claude-Code-Everything-You-Need-to-Know) | 2K | Claude Code 实操指南 |
| 70 | [tt-a1i/archify](https://github.com/tt-a1i/archify) | 5K | **生成架构图**（dark/light theme + PNG/JPEG/SVG） |
| 71 | [Bhanunamikaze/Agentic-SEO-Skill](https://github.com/Bhanunamikaze/Agentic-SEO-Skill) | 0.7K | **LLM-first SEO 分析** |
| 72 | [bitwize-music-studio/claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills) | 0.3K | **人 + AI Suno 音乐制作工作流** |
| 73 | [rohitg00/pro-workflow](https://github.com/rohitg00/pro-workflow) | 2K | Claude Code **从你的纠错中学习** |
| 74 | [parcadei/Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | 3K | **Claude Code 上下文管理**（hooks） |
| 75 | [dzcmemory-web/bazi-ziwei-skill](https://github.com/dzcmemory-web/bazi-ziwei-skill) | 0.6K | **AI 八字 + 紫微斗数**（精准排盘 + 水墨风 HTML） |

---

## 🔍 按主题分类（75 个候选）

### 🤖 Agent 框架 / Harness（13 个）
hermes-agent(217K)、ECC(231K)、ruflo(65K)、CowAgent(46K)、nanobot(46K)、nanoclaw(30K)、oh-my-openagent(66K)、oh-my-claudecode(38K)、oh-story-claudecode(4K)、learn-claude-code(71K)、shareAI-lab 教程、Agent-Reach(58K)、JeecgBoot(47K)

### 🎨 UI / 设计 / 前端（9 个）
ui-ux-pro-max-skill(107K)、headroom(60K)、frontend-slides(25K)、html-anything(7K)、archify(5K)、drawio-skill(6K)、AionUi(30K)、cmux(24K)、taste-skill(65K)

### 📚 Skills 合集 / Marketplace（10 个）
agent-skills(addyosmani 79K)、claude-skills(alirezarezvani 22K)、claude-skills(Jeffallan 10K)、claude-plugins-official(anthropics 32K)、agents(wshobson 38K)、graphify(91K)、claude-code-templates(29K)、claude-code-settings(1K)、buildwithclaude(3K)、skill(anbeime 3K)

### 🧠 记忆 / 上下文 / 规划（5 个）
claude-mem(87K)、memU(14K)、planning-with-files(25K)、Continuous-Claude-v3(3K)、pro-workflow(2K)

### 📝 内容创作 / 公众号 / 写作（7 个）
md2wechat-skill(3K)、gzh-design-skill(2K)、claude-blog(1K)、prompt-master(10K)、dashi-ppt-skill(3K)、NotFair(3K)、claude-skill-social-post(0.5K)

### 🔬 研究 / 学习 / 教学（5 个）
academic-research-skills(38K)、AI-Research-SKILLs(10K)、Understand-Anything(75K)、scientific-agent-skills(31K)、claude-howto(40K)

### 🛠 工具 / 桥接 / 路由（6 个）
CLIProxyAPI(43K)、cc-switch(118K)、Career-Ops(60K)、serena(26K)、claude-hud(26K)、caveman(90K)

### 🎯 教程 / 最佳实践（4 个）
claude-code-best-practice(63K)、Claude-Code-Everything-You-Need-to-Know(2K)、Skill_Seekers(14K)、notebooklm-py(17K)

### 🔒 安全 / 攻击（2 个）
Claude-Red(2K)、Claude-BugHunter(3K)

### 🎭 特定垂直领域（4 个）
- **中医**：nihaixia(1K)
- **八字/紫微**：bazi-ziwei-skill(0.6K)
- **音乐**：claude-ai-music-skills(0.3K)
- **营销**：aaron-marketing-skills(2K)

### 🌐 跨 CLI 平台（多平台）
多数候选支持 Claude Code + Codex + OpenCode + Cursor + OpenClaw 多种平台

---

## ⚠️ 主动审查（潜在风险）

### 🚫 已知需排除的"伪 skill"
- **ComposioHQ/awesome-claude-skills**（68K ⭐）—— 是 awesome list 索引库
- **hesreallyhim/awesome-claude-code**（50K ⭐）—— 同上
- **shareAI-lab/learn-claude-code**（71K ⭐）—— 教程类，被分类但应该标 type=tutorial

### 🌟 高分低星潜在黑马（score ≥ 50 但 stars < 500）
- **nanoclaw**（72.6 分 · 30K ⭐）—— 已在 Top 5
- **CowAgent**（74.6 分 · 46K ⭐）—— 已在 Top 3
- 大部分高分候选都是高 star，没"暗黑马"

### 💡 低分高 forks/stars（用户真正用过）
- **claude-code**（codeaashu，**forks/stars 115.3%**！）—— 排名 36 但分不高
- **archify**（tt-a1i，6.8% forks/stars）—— 排名 70
- **nihaixia**（19.4% forks/stars）—— 排名 54

---

## 🎯 推荐入库（Top 5 给 taxonomy v0.4）

如果你要选 5 个加入 taxonomy，推荐：

| 仓库 | 理由 |
|------|------|
| **affaan-m/ECC**（231K ⭐） | agent harness 性能优化，对标花叔 darwin-skill |
| **addyosmani/agent-skills**（79K ⭐） | 生产级工程 skills，对标 alirezarezvani/claude-skills |
| **Alirezarezvani/claude-skills**（22K ⭐） | 345 个 skills 巨型合集 |
| **thedotmack/claude-mem**（87K ⭐） | 跨会话记忆，对标你现有缺位 |
| **HKUDS/nanobot**（46K ⭐） | 学术级轻量 agent |

---

## ⏭ 下一步建议

| 选项 | 操作 |
|------|------|
| **🅰 Top 5-10 入库 taxonomy v0.4** | 重跑 dedup.py 看新视图 |
| **🅱 全部 75 入库 taxonomy v0.4** | taxonomy 变 123 skill |
| **🅲 维持现状，仅作为发现清单** | taxonomy 锁定 48 skill |
| **🅳 加更细的过滤规则** | 排除特定类型（如 marketing/red-team）|

**走哪条？** 👇