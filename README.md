# 🗺️ Awesome Skills Map

> **三层技能地图体系** · 22 章原始 Claude Skill 源码 + 5 位高产博主聚合 + 48 skill 自动分类（taxonomy v0.3）
>
> [![Skills](https://img.shields.io/badge/Skills-48-blue)]()
> [![Version](https://img.shields.io/badge/taxonomy-v0.3-green)]()
> [![License](https://img.shields.io/badge/License-MIT-green)]()
> [![Claude](https://img.shields.io/badge/Claude_Code-Skills-purple)]()
> [![Topics](https://img.shields.io/badge/topics-15-orange)]()

## 🎯 速读（100 字）

本仓库 = **3 层技能地图**：
1. **第一层 · 22 章原始 Skill 源码**（解压即用，含 SKILL.md）
2. **第二层 · 5 博主聚合**（花叔 / 宝玉 / 歸藏 / 小虎 / 乔木，共 28 个 ≥500⭐ skill）
3. **第三层 · taxonomy v0.3 dedup 体系**（48 skill 跨博主 + 22 章统一分类，9 个 A 类重复聚类自动对比）

**核心元能力**：`aggregate-skills-map` skill（gh CLI + dedup.py + taxonomy.yaml）让你随时拉新博主、加新 skill，自动归类。

---

## 🆕 v0.3 最新更新（2026-07-19）

| 变更 | 内容 |
|------|------|
| **taxonomy.yaml v0.3** | tag-based 重构 + 整合 5 博主 + 22 章 = **48 skill** |
| **dedup.py v0.3** | 加 type 第二维度（meta/collection/book/skill/tool/local_skill）+ 主动 spot check |
| **本地 skill 修复** | URL 指向 awesome-skills-map 仓库 + stars 显示「📍 本地」 |
| **跨分类 skill** | tags ≥ 2 自动识别（如 `huashu-design`: ui_design + html_slides） |
| **主动审查** | dedup 自动列出 4 个潜在问题（distill_person 全花叔、24 个单点分类等） |

详见 [CHANGELOG](#-changelog) 和 `examples/dedup-map.md`。

---

## 📦 仓库结构

```
awesome-skills-map/
├── README.md                          ← 你正在看的（三层技能地图）
├── LICENSE                            ← MIT
├── .gitignore
│
├── archives/                          ← 第一层 · 22 章原始 zip（ch02.zip ~ ch22.zip）
│   └── ch02.zip ~ ch22.zip            原始压缩包，方便分发
│
├── skills/                            ← 第一层 · 22 章解压源码 + 第二层 aggregate skill
│   ├── 第2章面试准备/                 ← 一人一课程原始 skill
│   ├── 第3章智能周报生成器/
│   ├── ...
│   ├── 第22章网页自动化测试/
│   └── aggregate-skills-map/          ← 第二层 · 元能力（本仓库自研）
│       ├── SKILL.md                   skill 定义
│       ├── aggregate.sh               Bash 拉数据 + Markdown 渲染
│       ├── dedup.py                   Python 聚合 + 重复检测
│       ├── taxonomy.yaml              🆕 v0.3 分类树（48 skill）
│       └── examples/                  第三层 · dedup 输出
│           ├── alchaincyf-min500-skills.md
│           ├── jimliu-min500-skills.md
│           ├── op7418-min500.md
│           ├── xiaohuailabs-min500.md
│           ├── joeseesun-min500.md
│           ├── keyword-comparison.md
│           └── dedup-map.md            🆕 48 skill 聚合视图
│
└── (GitHub Topics: claude, claude-skills, awesome-list, skills-aggregator 等 15 个)
```

---

## 🚀 一键部署

### 方式 A：部署全部 22 章原始 skill

```bash
git clone https://github.com/Alexxiang2008/awesome-skills-map.git
cd awesome-skills-map

# 复制每个 skill 源码到 Claude 全局 skills 目录
cp -r "skills/第2章面试准备/interview-intel" ~/.claude/skills/
cp -r "skills/第10章微信公众号一键排版与发布/一键发布到公众号/skills/wechat-publish" ~/.claude/skills/
# ... 共 22 个
```

### 方式 B：只部署本仓库自研的元能力

```bash
cp -r skills/aggregate-skills-map ~/.claude/skills/
```

启用后在 Claude Code 中：

```bash
/aggregate-skills-map alchaincyf                   # 单博主技能地图
/aggregate-skills-map alchaincyf --skill-only      # 仅 skills
/aggregate-skills-map --dedup                      # 用 taxonomy v0.3 聚合
```

### 方式 C：查看文档不部署

直接浏览 `examples/` 下的 6 个 markdown 文件即可看效果。

---

## 🗂 三层技能地图架构

### 第一层 · 22 章原始技能（本地源码）

来自「一人」课程的 22 章节 Claude Skills 完整源码（缺第 1、18 章）：

| 章节 | skill | 触发命令 |
|------|-------|---------|
| 第 2 章 | 面试准备 | `/jobprep` |
| 第 3 章 | 智能周报生成器 | `/weekly-report` |
| 第 4 章 | AI 辅助创意脑暴 | `/brainstorm` |
| 第 5 章 | 发票与收据自动归档 | `/invoice` |
| 第 6 章 | 智能邮件分类与回复 | `/email-triage` |
| 第 7 章 | 一键生成精美网页演示 | `/frontend-slides` |
| 第 8 章 | AI 深度访谈与爆款文章 | `/interview` |
| 第 9 章 | 热点爆款文章生成器 | `/hot` |
| 第 10 章 | 微信公众号一键排版 | `/publish-wechat` |
| 第 11 章 | 小红书爆款图文生成器 | `/xiaohongshu-images` |
| 第 12 章 | 爆款视频拆解器 | `/video-local` |
| 第 13 章 | ListenHub AI 解说视频 | (脚本调用) |
| 第 14 章 | 视频综艺特效 | `/video-wrapper` |
| 第 15 章 | AppStore 评价分析 | `/app-review` |
| 第 16 章 | 小红书数据采集 | (CLI) |
| 第 17 章 | 公众号爆文监控 | `/爆文监控` |
| 第 19 章 | PRD 撰写 | `/prd` |
| 第 20 章 | WebArtifactsBuilder | (脚本调用) |
| 第 21 章 | 前端界面设计 | (Skill 触发) |
| 第 22 章 | 网页自动化测试 | `/webapp-test` |

详见 `archives/` 和 `skills/` 对应目录。

### 第二层 · 5 博主聚合（GitHub stars 监控）

| 博主 | 核心作品 | 生态 | ≥500⭐ skill 数 |
|------|---------|------|---------------|
| 🌸 **花叔** alchaincyf | nuwa-skill (28K) | `nuwa-*` | 8 |
| 📕 **宝玉** JimLiu | baoyu-skills (24K) | `baoyu-*` | 3 |
| 🎨 **歸藏** op7418 | guizang-ppt-skill (22K) | `guizang-*` | **10** |
| 🐯 **小虎** xiaohuailabs | xiaohu-wechat-format (660) | `xiaohu-*` | 1 |
| 🌳 **乔木** joeseesun | qiaomu-anything-to-notebooklm (5.6K) | `qiaomu-*` | 2 |

**详细地图**：[alchaincyf](skills/aggregate-skills-map/examples/alchaincyf-min500-skills.md) · [JimLiu](skills/aggregate-skills-map/examples/jimliu-min500-skills.md) · [op7418](skills/aggregate-skills-map/examples/op7418-min500.md) · [xiaohuailabs](skills/aggregate-skills-map/examples/xiaohuailabs-min500.md) · [joeseesun](skills/aggregate-skills-map/examples/joeseesun-min500.md)

### 第三层 · 48 skill 分类树（taxonomy v0.3）

`taxonomy.yaml` 是聚合 5 博主 + 22 章 = 48 skill 的统一分类树，按职能 + tag + type 三维度：

```
9 大职能分类:
├── 内容创作 (content_creation)      ← 公众号/小红书/PPT/视频/文章
├── 设计/视觉 (design_visual)        ← UI/Logo/插图
├── 元能力 (meta_skills)              ← 蒸馏/进化/规范化/去 slop
├── 内容汇聚 (content_aggregation)   ← NotebookLM/监控
├── 开发工具 (dev_tools)             ← 客户端/IM/MCP/测试/构件
├── 合集/教程 (collections)          ← skill 合集 + 教程书
├── 效率办公 (productivity)          ← 周报/邮件/发票/面试
├── 数据分析 (data_analysis)         ← App 评论/社交数据
└── 产品设计 (product_design)        ← PRD/脑暴

7 个 type 维度:
├── meta (4): 元能力（蒸馏/规范化等）
├── collection (2): 多 skill 合集
├── book (1): 书籍/教程
├── sub_skill (3): 合集下的子技能
├── skill (18): 独立 skill（5 博主）
├── tool (5): 工具/脚本/服务
└── local_skill (20): 本地 22 章
```

**完整视图**：见 `examples/dedup-map.md`（287 行，含 9 个 A 类聚类 + 跨分类 + type 第二视图 + 主动审查）

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

**终极内容工作流**（跨博主）：
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

## 🌟 跟踪的 GitHub 大牛（5 位核心作者）

通过 `aggregate-skills-map` skill 持续聚合，**star ≥ 500 · topics 优先 + name/desc 关键词 fallback**。

| 博主 | 核心作品 | 方向 | ≥500⭐ |
|------|---------|------|--------|
| 🌸 [**花叔**](https://github.com/alchaincyf) alchaincyf | nuwa-skill (28K) | 人物思维蒸馏 | 8 skills |
| 📕 [**宝玉**](https://github.com/JimLiu) JimLiu | baoyu-skills (24K) | 内容创作工作流 | 3 skills |
| 🎨 [**歸藏**](https://github.com/op7418) op7418 | guizang-ppt-skill (22K) | 设计/视觉/PPT | **10 skills** ⭐ |
| 🐯 [**小虎**](https://github.com/xiaohuailabs) XiaoHu | xiaohu-wechat-format (660) | 公众号+视频本地化 | 1 skill |
| 🌳 [**乔木**](https://github.com/joeseesun) 向阳乔木 | qiaomu-anything-to-notebooklm (5.6K) | 工作流输入聚合 | 2 skills |

**互补组合**：花叔做"AI 懂人"，宝玉做"AI 干活"，歸藏做"AI 漂亮"，小虎做"AI 省钱"，乔木做"AI 流程化"。

---

## 🔬 Dedup 系统（taxonomy v0.3 + dedup.py）

### 设计思想

**为什么需要 dedup？** 5 博主之间存在显著功能重复：

| 功能 | 重复次数 | 涉及 skill |
|------|---------|-----------|
| 公众号排版 | 3 家 | baoyu / xiaohu / guizang |
| 视频翻译/剪辑 | 3 家 | xiaohu / 歸藏 / baocut |
| PPT 生成 | 2 家 | guizang-ppt / NanoBanana-PPT |
| 设计/UI | 4 家 | baoyu-design / huashu-design / 歸藏 / 一人 |

**判定机制**（3 层）：
1. **重复类型分级** A/B/C/D（A 高重复 → 出对比表）
2. **tag-based 分类**（跨分类用 tags 表示，避免变体 id）
3. **type 第二维度**（meta/collection/book/skill/tool/local_skill）

### 9 个 A 类高重复聚类

dedup 自动识别出 9 个 A 类聚类（每类 ≥2 skill）：

| # | 分类 | 数量 | 主导 ⭐ |
|---|------|------|---------|
| 1 | `ppt/html_slides` | **4** | guizang-ppt-skill (21.8K) |
| 2 | `meta_skills/distill_person` | **4** | nuwa-skill (28.3K) |
| 3 | `video/translate` | **3** | Youtube-clipper (2.1K) |
| 4 | `design_visual/ui_design` | **3** | huashu-design (21.7K) |
| 5 | `design_visual/illustration` | **2** | guizang-material (715) |
| 6 | `meta_skills/de_slop` | **2** | Humanizer-zh (13.5K) |
| 7 | `collections/skill_collection` | **2** | baoyu-skills (23.8K) |
| 8 | `wechat/formatting` | **2** | baoyu-skills (23.8K) |
| 9 | `video/effects` | **2** | (本地 skill) |

详见 [examples/dedup-map.md](skills/aggregate-skills-map/examples/dedup-map.md) 完整对比表。

### 设计依据

| 维度 | 依据 |
|------|------|
| 4 级分类树 | GitHub awesome-list 模板 + 认知科学乔治·米勒 7±2 |
| tag 系统 | GitHub 自身用 topics，跨维度自然表达 |
| type 维度 | 软件架构单一职责 + 分层（基础/容器/工具/元） |
| 关键词过滤 | jq test() 子串匹配（`skill` 自动覆盖 `skills`） |
| 中文支持 | 加"技能"关键词，xiaohu-wechat-format 修复 0→1 增量 |

### 主动 Spot Check（dedup 自动生成）

dedup 自动列出 4 个潜在问题供人工 review：

1. **distill_person 4 个全是花叔**（nuwa 衍生品）→ 合理，建议说明"nuwa 生态"
2. **5 个本地 skill 出现在 A 类** → 合理，加 📍 标记（已实现）
3. **24 个分类是单点**（仅 1 个 skill）→ 提示合并/扩类
4. tags ≥ 3 的 skill（暂无）→ 待 review

---

## ⚠️ 风险与踩坑清单

1. **第 3 章智能周报无 SKILL.md**——只有 command 文件
2. **第 13 章 ListenHub 强约束**——直接 curl API 会报错（端点不公开），**必须通过 scripts/*.sh**
3. **第 16 章非标准技能**——是「Tampermonkey + Node 服务」复合部署，无斜杠命令
4. **第 19 章是别名**——`/产品需求` 是 `/prd` 的中文别名，真正干活的是 `prd-writer`
5. **所有 zip 含 `__MACOSX/` 垃圾**——Mac 打包副产物（仓库内已清理）
6. **首启引导繁琐**——第 10/11/17 章需先配置文件（API 密钥/微信凭据/大家啦 key）
7. **ListenHub 不开源**——Marswave API 私有，端点不公开（详 SKILL.md 警告）
8. **taxonomy.yaml 是手动维护**——新博主进来要更新分类树（社区 PR）

---

## 📊 全局统计

| 指标 | 数值 |
|------|------|
| 22 章原始技能 | 20 个 SKILL.md + 1 个 command-only + 1 个别名 |
| 5 博主聚合 | 28 个 ≥500⭐ skill |
| taxonomy v0.3 | **48 个 skill** 跨 9 大类 |
| A 类重复聚类 | 9 个（dedup 自动识别） |
| 跨分类 skill | 4 个（tags ≥ 2） |
| 仓库 commits | 13 |
| GitHub Topics | 15 个 |
| 仓库体积 | 2.5 MB |

### Type 分布（v0.3）

| type | 数量 | 代表 |
|------|------|------|
| meta | 4 | nuwa-skill, darwin-skill, qiaomu-goal, aggregate-skills-map |
| collection | 2 | baoyu-skills (23.8K), huashu-skills (1.2K) |
| book | 1 | Illustrated-Agent-Skills |
| sub_skill | 3 | steve-jobs, zhangxuefeng, x-mentor |
| skill | 18 | 5 博主独立 skill |
| tool | 5 | CodePilot, viral-monitor, web-artifacts-builder 等 |
| local_skill | 20 | 一人课程 22 章 |

### 作者分布

| 作者 | skill 数 | ⭐ 总和 | 平均 ⭐ |
|------|---------|--------|---------|
| alchaincyf (花叔) | 8 | 76,985 | 9,623 |
| jimliu (宝玉) | 4 | 26,873 | 6,718 |
| op7418 (歸藏) | 11 | 58,748 | 5,341 |
| 一人课程 | 20 | (本地) | - |
| xiaohuailabs (小虎) | 2 | 1,278 | 639 |
| joeseesun (乔木) | 2 | 6,372 | 3,186 |

---

## 🤝 贡献

欢迎：
- 📝 补充各技能的最佳实践与避坑指南
- 🐛 报告 SKILL.md 与实际行为不符的 bug
- ✨ 提交新技能到 `skills/`（按相同结构组织）
- 🔬 扩展 taxonomy.yaml（加新博主、新分类、新 tags）
- 🔄 提交 dedup.py bug 修复（Python 3.13 + Windows 兼容）

请通过 Issue / PR 参与。

## 📜 License

MIT License —— 自由使用、修改、分发。原始技能版权归各原作者所有。

## 📚 CHANGELOG

### v0.3（2026-07-19）
- taxonomy.yaml tag-based 重构 + 整合 22 章 = 48 skill
- dedup.py 加 type 维度第二视图 + 主动 spot check
- 修本地 skill URL + stars 显示
- 跨分类 skill 自动识别

### v0.2（2026-07-19）
- 5 博主聚合（花叔/宝玉/歸藏/小虎/乔木）
- aggregate.sh 默认 min-stars=500 + --skill-only 开关
- aggregate-skills-map skill 上线

### v0.1（2026-07-19）
- 22 章原始技能整理 + 技能地图 v1
- awesome-skills-map 仓库初始化

---

## 🔗 相关链接

- **GitHub**：https://github.com/Alexxiang2008/awesome-skills-map
- **ComposioHQ/awesome-claude-skills**：https://github.com/ComposioHQ/awesome-claude-skills（社区旗舰）
- **anthropics/skills**：https://github.com/anthropics/skills（官方）
- **Claude Code 文档**：https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview