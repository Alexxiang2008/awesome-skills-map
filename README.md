# 🗺️ Awesome Skills Map

> **22 章节 Claude Skills 全景图 + 完整源码** —— 按职能分类、自带作战矩阵、含一键部署指南。

[![Skills](https://img.shields.io/badge/Skills-22-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![Claude](https://img.shields.io/badge/Claude_Code-Skills-purple)]()

## 🎯 速读（100字）

6 大类、22 个技能、2.5MB 源码。**内容生产铁三角**：9 追热点 → 8 写爆款 → 10/11 分发（公众号+小红书），17 闭环监控。**最强单兵**：12 爆款视频拆解（豆包 8 维度）。**最大坑**：13 ListenHub 严禁直接 API 调用（脚本是唯一接口）。所有 zip 原档存于 `archives/`，解压源码在 `skills/`。

---

## 📦 仓库结构

```
awesome-skills-map/
├── README.md                  ← 你正在看的技能地图
├── LICENSE                    ← MIT
├── archives/                  ← 21 个原始 zip（按章节编号 ch02.zip ~ ch22.zip）
│   ├── ch02.zip  ~  ch22.zip
└── skills/                    ← 解压后的完整源码（按章节中文名分目录）
    ├── 第2章面试准备/
    ├── 第3章智能周报生成器/
    ├── ...（共 21 个）
    └── 第22章网页自动化测试/
```

**为什么同时保留 archives 和 skills？**
- `archives/`：原 zip 形态，方便下载分发（共享给团队）
- `skills/`：解压源码，便于直接 `cp` 到 `~/.claude/skills/` 启用

---

## 🚀 一键部署

### 方式 A：部署全部（21 个技能）

```bash
git clone https://github.com/Alexxiang2008/awesome-skills-map.git
cd awesome-skills-map

# 复制所有 skill 源码到 Claude 全局 skills 目录
cp -r skills/*/* ~/.claude/skills/    # 注意每章内层才是 skill 目录
```

### 方式 B：按需挑用

每个技能独立可用，进入对应目录查看 `SKILL.md`（或 `README.md`）了解触发命令。

---

## 🗂 技能地图（按职能分类）

### 1️⃣ 内容创作与发布（6 个）—— 自媒体 IP 主战场

| # | 技能 | 触发命令 | 输入 → 输出 | 技术依赖/坑 |
|---|------|---------|------------|-----------|
| **8** | **interview**（商业访谈写作） | `/interview` `/访谈` `/interview-转化` `/interview-传播` | 风格参考 + 多轮问答 → 爆款公众号长文 | 强制风格参考文件夹 `./风格参考/`；3 模式（销量/阅读/平衡） |
| **9** | **hot-article**（热点爆款） | `/hot` `/热点` `/爆款` | 热点主题 + 模板 → 公众号/小红书文 | 强制爆款模板文件夹 `./爆款模板/`；联网搜热点 |
| **10** | **wechat-publish**（公众号一键排版发布） | `/publish-wechat` | Markdown → 公众号草稿（4 主题，含小绿书） | 需配置微信 AppID/Secret；首次 `isInitialized()` 引导 |
| **11** | **xiaohongshu-images**（小红书图文） | `/xiaohongshu-images` | MD/HTML/文本 → 3:4 卡片图集 | 首次需 `.xiaohongshu-images/config.yaml` |
| **14** | **video-wrapper**（访谈视频综艺特效） | `/video-wrapper` | YouTube/B站链接或本地 → 综艺风视频 | 需 ffmpeg + Playwright + MoviePy；4 主题；分析→审批→渲染 |
| **17** | **公众号爆文监控** | `/爆文监控` `/viral-monitor` | 关键词 + 大家啦 API → 日报/周报 HTML | 依赖外部 API（dajiala.com）；`viral_monitor.py --setup` 向导 |

🔗 **内容铁三角**：9（选题）→ 8（深度）→ 10/11（分发），17（复盘）闭环。

### 2️⃣ 视频与多媒体（3 个）—— 短视频工业化

| # | 技能 | 触发命令 | 输入 → 输出 | 技术栈 |
|---|------|---------|------------|--------|
| **12** | **video-local-analyze**（爆款视频拆解 v3） | `/video-local` `/本地视频分析` | 本地视频 → HTML 报告 + 可复制模板 | ffmpeg + 豆包原生视频理解；**8 维拆解 + 5 进阶模块** |
| **13** | **listenhub**（AI 解说视频/播客） | 脚本调用 | 文本/URL/图片 → 播客/解说视频/TTS/图片 | ⚠️ **必须通过 scripts/*.sh 调用**；4 模式：Podcast/Explain/TTS/Image |
| **14** | video-wrapper（见上） | — | — | — |

🔗 **视频流水线**：13 造素材 → 12 拆解对标 → 14 加特效。

### 3️⃣ 求职与办公效率（4 个）

| # | 技能 | 触发命令 | 输入 → 输出 | 关键点 |
|---|------|---------|------------|--------|
| **2** | **interview-intel**（面试准备） | `/jobprep` | 公司+职位+JD+简历 → 5 份材料 | 强依赖真实简历（绝不编造）；`all_in_one_v6.1.py` 生成框架 |
| **3** | **智能周报生成器** | `/weekly-report`（推测） | 流水账 → STAR 周报（简洁/详细/汇报 3 版） | **无 SKILL.md**，用 command 文件实现；自动学习 `weekly-reports/` |
| **5** | **invoice**（发票自动归档） | `/invoice` `/发票` | 发票图片/PDF → Excel（明细+分类+月汇总） | 依赖百度 OCR API；7 类自动分类 |
| **6** | **email-triage**（邮件分类回复） | `/email-triage` `/邮件分类` `/收件箱` | 邮件源 → 3 级分类 + 回复草稿 + 待办 | 首次需 `~/.email-triage/config.json` |

### 4️⃣ 数据采集与分析（2 个）

| # | 技能 | 触发命令 | 输入 → 输出 | 部署形态 |
|---|------|---------|------------|---------|
| **15** | **app-review**（App Store 评价分析） | `/app-review` `/评价分析` | App ID → 简洁风 HTML 报告 + CSV | 抓取 ≤500 条评论 + 情感分析 |
| **16** | **小红书创作平台数据采集** | CLI（无 slash 命令） | 油猴脚本 → JSON/CSV 同步到本地 | ⚠️ **特殊形态**：Tampermonkey + Node 服务（`server.js` + `npm install`） |

### 5️⃣ 前端与设计（4 个）—— 设计师友好

| # | 技能 | 触发命令 | 输入 → 输出 | 技术栈/特点 |
|---|------|---------|------------|-----------|
| **7** | **frontend-slides**（精美网页演示） | Skill 触发 | 主题/PPT → 零依赖 HTML 演示文稿 | **强制 100vh 不滚动**；反 AI slop；支持 PPTX→HTML |
| **20** | **web-artifacts-builder** | `scripts/init-artifact.sh` | 项目名 → Claude.ai 多组件 Artifact | React 18 + TS + Vite + Parcel + Tailwind + shadcn/ui；40+ 组件 |
| **21** | **frontend-design**（前端界面设计） | Skill 触发 | UI 需求 → 创意前端代码 | **BOLD 美学 12 方向**；HTML/CSS/JS, React, Vue |
| **22** | **webapp-testing**（网页自动化测试） | `/webapp-test` `/测试网页` | URL/任务 → 截图 + 日志 + 验证 | Playwright Python；`scripts/with_server.py` 服务生命周期 |

🔗 **设计链路**：21 定美学 → 7 做演示 / 20 做复杂 Artifact → 22 自动化验证。

### 6️⃣ 产品与创意（3 个）

| # | 技能 | 触发命令 | 输入 → 输出 | 关键点 |
|---|------|---------|------------|--------|
| **4** | **creative-brainstorm**（AI 创意脑暴） | `/brainstorm` `/脑暴` | 模糊想法 → 10 个可执行方案 + 评分 + 资源估算 | 联网搜竞品 + SCAMPER 7 维发散 |
| **19** | **prd-writer / 产品需求** | `/prd` `/产品需求` | 产品想法 → PRD 路线图 + 3 个 ASCII 原型 | **3 阶段**：需求澄清 → 路线图 → ASCII 原型 |
| **20** | web-artifacts-builder（见上） | — | — | — |

---

## 🧠 跨技能作战矩阵

| 场景 | 推荐技能组合 |
|------|------------|
| 🚀 **做爆款自媒体 IP** | 9（追热点）→ 8（写深度）→ 10+11（公众号+小红书）→ 17（监控复盘） |
| 🎬 **短视频工业化** | 13（生成素材）→ 12（拆解对标）→ 14（加综艺特效） |
| 💼 **求职冲刺** | 2（面试全套）+ 19（PRD 思维写自我介绍） |
| 🛠 **产品从 0 到 1** | 4（脑暴）→ 19（写 PRD）→ 21/20（设计原型）→ 22（自动化测试） |
| ⚡ **个人效率提升** | 3（周报）+ 5（发票）+ 6（邮件） |
| 📊 **数据驱动决策** | 15（竞品 App 分析）+ 16（小红书数据采集）+ 17（公众号监控） |
| 🎤 **B 端路演/汇报** | 7（演示文稿）+ 20/21（视觉资产） |

---

## 🌟 跟踪的 GitHub 大牛（5 位核心 Skills 作者）

> 本仓库通过 `aggregate-skills-map` Skill（见 `skills/aggregate-skills-map/`）持续聚合高产作者的技能地图。
> **聚合规则**：star ≥ 500 · topics 优先（claude-skill/skills/codex、agent-skill/s）+ name/desc 关键词 fallback（skill|skills|nuwa|darwin|技能）

### 📊 大牛速览

| 博主 | 核心作品 | 生态 | 方向 | ≥500⭐ 数 | 身份 |
|------|---------|------|------|-----------|------|
| 🌸 [**花叔**](https://github.com/alchaincyf) alchaincyf | nuwa-skill (28K) | `nuwa-*` | 人物思维蒸馏 | 8 skills | AI Native Coder |
| 📕 [**宝玉**](https://github.com/JimLiu) JimLiu | baoyu-skills (24K) | `baoyu-*` | 内容创作工作流 | 3 skills | 博主 |
| 🎨 [**歸藏**](https://github.com/op7418) op7418 | guizang-ppt-skill (22K) | `guizang-*` | **设计/视觉/PPT** | **10 skills** ⭐ | 产品设计师 |
| 🐯 [**小虎**](https://github.com/xiaohuailabs) XiaoHu | xiaohu-wechat-format (660) | `xiaohu-*` | 公众号+视频本地化 | 1 skill | 独立开发者 |
| 🌳 [**乔木**](https://github.com/joeseesun) 向阳乔木 | qiaomu-anything-to-notebooklm (5.6K) | `qiaomu-*` | 工作流输入聚合 + 任务规范化 | 2 skills | PM |

### 📚 详细地图

- 🌸 [**花叔 (alchaincyf)**](skills/aggregate-skills-map/examples/alchaincyf-min500-skills.md) — 47 个原创项目 · 8 个高质量 skills
- 📕 [**宝玉 (JimLiu)**](skills/aggregate-skills-map/examples/jimliu-min500-skills.md) — 230 仓库 · 3 个核心 skills
- 🎨 [**歸藏 (op7418)**](skills/aggregate-skills-map/examples/op7418-min500.md) — **11 个 ≥500⭐（39% 密度，5 博主冠军）**
- 🐯 [**小虎 (xiaohuailabs)**](skills/aggregate-skills-map/examples/xiaohuailabs-min500.md) — 2 个精品
- 🌳 [**乔木 (joeseesun)**](skills/aggregate-skills-map/examples/joeseesun-min500.md) — 2 个 PM 视角 skills

### 🔬 关键词扩展研究

见 [keyword-comparison.md](skills/aggregate-skills-map/examples/keyword-comparison.md)：
- 5 博主关键词匹配对比矩阵
- jq test() 子串匹配特性分析（`skill` 已自动覆盖 `skills`）
- 中文"技能"扩展的真实价值（修复小虎 0→1 增量）
- 进一步优化建议（白名单 / LLM 后处理 / topics 优先）

### ⚡ 终极内容工作流（5 博主组合）

```
输入素材
  ↓
[歸藏 Document-illustrator-skill] → 配图
  ↓
[乔木 qiaomu-anything-to-notebooklm] → 汇总到 NotebookLM
  ↓
[花叔 nuwa-skill 蒸馏你的写作风格] → 风格统一
  ↓
[歸藏 Humanizer-zh] → 去除 AI 痕迹
  ↓
[宝玉 baoyu-post-to-wechat] 或 [小虎 xiaohu-wechat-format] → 发布公众号
  ↓
[歸藏 guizang-social-card-skill] → 生成封面
  ↓
[乔木 qiaomu-goal-meta-skill] → 任务规范化复盘
```

---

## ⚠️ 风险与踩坑清单

1. **第 3 章智能周报无 SKILL.md**——只有 command 文件，启用时用 command 而非 Skill。
2. **第 13 章 ListenHub 强约束**——直接 curl API 会报错（端点不公开），**必须通过 scripts/*.sh**。
3. **第 16 章非标准技能**——是「Tampermonkey + Node 服务」复合部署，无斜杠命令。
4. **第 19 章是别名**——`/产品需求` 是 `/prd` 的中文别名，真正干活的是 `prd-writer`。
5. **所有 zip 含 `__MACOSX/` 垃圾**——Mac 打包副产物，部署前要清理（仓库内已清理）。
6. **首启引导繁琐**——第 10/11/17 章需先配置文件（API 密钥/微信凭据/大家啦 key），首次预留 5 分钟。

---

## 📊 全局统计

- **总计**：22 章节 → 21 个 SKILL.md + 1 个 command-only（第 3 章）
- **需付费 API**：5（百度 OCR）、10（微信公众号）、12（豆包）、13（ListenHub/Marswave）、17（大家啦）、11（可选 AI 配图）
- **完全离线可用**：2/3/4/6/7/8/9/19/20/21/22
- **混合模式**：14（本地+可选联网）、15（公开 API）
- **非 Skill 形态**：16（油猴+Node）
- **仓库体积**：2.5 MB（解压源码 1.9 MB + 原始 zip 544 KB）

---

## 🤝 贡献

欢迎：
- 📝 补充各技能的最佳实践与避坑指南
- 🐛 报告 SKILL.md 与实际行为不符的 bug
- ✨ 提交新技能到 `skills/`（按相同结构组织）

请通过 Issue / PR 参与。

## 📜 License

MIT License —— 自由使用、修改、分发。原始技能版权归各原作者所有。