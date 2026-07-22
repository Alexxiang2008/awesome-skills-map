# 🗺️ Awesome Skills Map

> **89 个 Claude Skill 的统一目录**——服务于 B2B 出海企业老板/员工的日常使用。
>
> 22 章本地原始 skill（开箱即用）+ 41 个精选 skill（GitHub 远程）+ 5 位高产博主原创 + 26 个其他类。
>
> [![Skills](https://img.shields.io/badge/Skills-89-blue)]()
> [![License](https://img.shields.io/badge/License-MIT-green)]()
> [![Claude Code](https://img.shields.io/badge/Claude_Code-Skills-purple)]()
> [![B2B 出海](https://img.shields.io/badge/Use_Case-B2B_出海-orange)]()

## 🎯 3 秒钟了解本仓库

| 想做什么？ | 看哪 | 装什么 |
|----------|------|------|
| 公众号/SEO/PPT 一键生成 | [§内容创作](#-内容创作-25) | `wechat-hotspot-publisher` / `ppt-generator` |
| 视频/数字人带货 | [§内容创作](#-内容创作-25) | `infinitetalk-shopping-avatar` / `video-creation-pro` |
| 面试/简历/合同 | [§HR 招聘 / 工具](#-hr-招聘) | `tailored-resume-generator` / `contract-review` |
| 快速开发原型 | [§meta / 工具](#-meta-skills) | `nuwa-skill`（蒸馏引擎）/ `daisyUI-v4` |
| 直接拿一份完整 skill 库开始用 | [§一键安装](#-一键安装) | 整批 clone |

---

## 📦 一键安装

### 方案 A：装全部 89 个 skill（推荐）

```bash
# 1. clone 本仓库
git clone https://github.com/Alexxiang2008/awesome-skills-map.git /tmp/skills
cd /tmp/skills

# 2. 复制 22 个本地原始 skill 到 Claude Code 全局 skills 目录
for d in skills/第*章*; do
  skill_name=$(basename "$d")
  # 找 SKILL.md 所在的最深层目录
  skill_md=$(find "$d" -name "SKILL.md" -type f | head -1)
  if [ -n "$skill_md" ]; then
    skill_dir=$(dirname "$skill_md")
    cp -r "$skill_dir" ~/.claude/skills/"$skill_name"
  fi
done

# 3. 安装聚合 meta-skill
cp -r skills/aggregate-skills-map ~/.claude/skills/
echo "✅ 已安装 23 个 skill（含 22 原始 + 1 meta）"

# 4. 安装 41 个精选 skill（从 GitHub 远程仓库）
# 这些 skill 在 taxonomy.yaml 里，但代码在外部仓库
# 你可以挑想用的装：

# 工具型（一键装）
npx skills add alireza-rezvani/claude-skills            # wshobson/agents 的 91 个插件
npx skills add anthropics/claude-plugins-official      # 官方 38 个插件

# 内容型
git clone https://github.com/anbeime/skill.git /tmp/anbeime
# 看 /tmp/anbeime/skills/ 里的目录，挑想用的
cp -r /tmp/anbeime/skills/<skill-name> ~/.claude/skills/
```

### 方案 B：按需挑

```bash
# 1. 看所有可用的 skill（89 个）
cat skills/aggregate-skills-map/taxonomy.yaml | grep "^- id:"

# 2. 挑你想要的，按以下方式装：
#    - 本地 skill（22 章原始）：cp -r skills/第N章... ~/.claude/skills/
#    - 远程 skill：npx skills add <owner>/<repo> 或 git clone
```

### 方案 C：只用一个 meta-skill（推荐新手）

```bash
# 装 aggregate-skills-map（聚合器）
cp -r skills/aggregate-skills-map ~/.claude/skills/

# 在 Claude Code 中：
# 输入 /aggregate-skills-map 来拉新博主 + 选 skill
```

---

## 🗂️ 89 个 Skill 按类别速查

### 📝 内容创作 (25)

| 类别 | 代表 Skill | 安装源 |
|------|------------|--------|
| 公众号 | **wechat-hotspot-publisher** | `anbeime/skill/skills/wechat-hotspot-publisher` |
| | **baoyu-post-to-wechat** | `anbeime/skill`（baoyu-skills 子模块） |
| | **gzh-design-skill** | `anbeime/skill` |
| | **md2wechat-skill** | `anbeime/skill` |
| | **content-creation-publisher** | `anbeime/skill` |
| SEO | **seo-content-creation** | `wshobson/agents/plugins/seo-content-creation` |
| | **seo-analysis-monitoring** | `wshobson/agents/plugins/seo-analysis-monitoring` |
| | **seo-technical-optimization** | `wshobson/agents/plugins/seo-technical-optimization` |
| 视频/PPT | **ppt-generator** | `anbeime/skill` |
| | **ppt-roadshow-generator** | `anbeime/skill` |
| | **video-creation-suite** | `anbeime/skill` |
| | **viral-video-copywriting** | `anbeime/skill` |
| 文章/采访 | **interview-local** | 本地 `skills/第8章AI深度访谈与爆款文章创作` |
| | **hot-article-local** | 本地 `skills/第9章热点爆款文章生成器` |

### 🛍️ 内容汇聚 (25，含"其他"类电商营销)

| 类别 | 代表 Skill | 安装源 |
|------|------------|--------|
| 电商 | **wechat-hotspot-publisher** | `anbeime/skill` |
| | **digital-avatar-shopping-video** | `anbeime/skill` |
| | **pet-commerce-creator** | `anbeime/skill` |
| | **ecommerce-copywriter** | `anbeime/skill` |
| | **ecommerce-video-marketing** | `anbeime/skill` |
| 监控 | **viral-monitor-local** | 本地 `skills/第17章公众号爆文监控` |
| | **app-review-local** | 本地 `skills/第15章AppStore评价分析` |
| 笔记 | **qiaomu-anything-to-notebooklm** | `joeseesun/qiaomu-anything-to-notebooklm` |

### 🎨 设计/视觉 (12)

| 类别 | 代表 Skill | 安装源 |
|------|------------|--------|
| UI 设计 | **frontend-design-local** | 本地 `skills/第21章前端界面设计` |
| | **web-design-analyzer** | `anbeime/skill` |
| 视觉 | **pop-up-book-illustration** | `anbeime/skill` |
| | **article-illustrator** | `anbeime/skill` |
| 插画 | **document-illustrator** | `wshobson/agents` |
| | **guizang-material-illustration** | `op7418/agents` |

### 🧠 元能力 (9)

| 类别 | 代表 Skill | 安装源 |
|------|------------|--------|
| 人物蒸馏 | **nuwa-skill** | `alchaincyf/nuwa-skill` |
| | **zhangxuefeng-skill** | `alchaincyf/zhangxuefeng-skill` |
| | **steve-jobs-skill** | `alchaincyf/steve-jobs-skill` |
| 进化 | **darwin-skill** | `alchaincyf/darwin-skill` |
| 反 slop | **Humanizer-zh** | `op7418/Humanizer-zh` |
| 任务规范化 | **qiaomu-goal-meta-skill** | `joeseesun/qiaomu-goal-meta-skill` |

### ⏰ 效率办公 (7)

| 类别 | 代表 Skill | 安装源 |
|------|------------|--------|
| 周报 | **weekly-report-local** | 本地 `skills/第3章智能周报生成器` |
| 邮件 | **email-triage-local** | 本地 `skills/第6章智能邮件分类与回复助手` |
| 发票 | **invoice-local** | 本地 `skills/第5章发票与收据自动归档` |
| 面试 | **interview-intel-local** | 本地 `skills/第2章面试准备` |
| 脑暴 | **creative-brainstorm-local** | 本地 `skills/第4章AI辅助创意脑暴` |

### 🛠️ 工具/合集/数据分析 (10)

| 类别 | 代表 Skill | 安装源 |
|------|------------|--------|
| 桌面 | **CodePilot** | `op7418/CodePilot` |
| IM | **Claude-to-IM-skill** | `op7418/agents` |
| 视频 | **video-local-analyze** | 本地 `skills/第12章爆款视频拆解器` |
| 视频特效 | **video-wrapper-local** | 本地 `skills/第14章视频综艺特效` |
| 网页演示 | **frontend-slides-local** | 本地 `skills/第7章一键生成精美网页演示` |
| 产品需求 | **prd-writer-local** | 本地 `skills/第19章产品需求撰写` |
| 网页构建 | **web-artifacts-builder-local** | 本地 `skills/第20章WebArtifactsBuilder` |
| 网页测试 | **webapp-testing-local** | 本地 `skills/第22章网页自动化测试` |
| 商业数据 | **xiaohongshu-scraper-local** | 本地 `skills/第16章商业数据分析` |
| ListenHub | **listenhub-local** | 本地 `skills/第13章ListenHub Skill` |

**完整 89 skill 列表**：`skills/aggregate-skills-map/taxonomy.yaml`

---

## 🎯 怎么选 skill

按你的角色：

### 👔 B2B 出海老板

| 场景 | 装这些 |
|------|--------|
| 公众号矩阵运营 | wechat-hotspot-publisher + baoyu-post-to-wechat + gzh-design-skill |
| 跨境电商直播 | digital-avatar-shopping-video + infinitetalk-shopping-avatar + product-video-creator |
| SEO 流量获客 | seo-content-creation + seo-analysis-monitoring + seo-technical-optimization |
| 品牌内容 | ppt-roadshow-generator + viral-video-copywriting + article-illustrator |
| 团队管理 | interview-intel-local + contract-review + weekly-report-local |

### 👨‍💻 员工日常

| 场景 | 装这些 |
|------|--------|
| 写公众号文章 | hot-article-local + seo-content-creation + baoyu-post-to-wechat |
| 做 PPT 给客户 | ppt-generator + ppt-roadshow-generator + frontend-slides-local |
| 视频内容 | video-creation-suite + video-local-analyze + viral-video-copywriting |
| 数据报告 | app-review-local + viral-monitor-local + business-analytics |
| 邮件/发票 | email-triage-local + invoice-local |

### 🛠️ 开发者

| 场景 | 装这些 |
|------|--------|
| 快速原型 | web-artifacts-builder-local + webapp-testing-local + frontend-design-local |
| Skill 元能力 | nuwa-skill + darwin-skill + aggregate-skills-map |
| 跨平台 Agent | anbeime/skill 全套 + wshobson/agents 全套 |

---

## 🗺️ 三层技能地图架构

```
┌─────────────────────────────────────────────┐
│  Layer 1: 本仓库代码（22 原始 + 1 meta）         │
│  → 立即可用，cp -r skills/第*章 ~/.claude/skills/  │
└─────────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────┐
│  Layer 2: GitHub 远程仓库（5 位博主原创 26 个）     │
│  → npx skills add <owner>/<repo> 或 git clone     │
└─────────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────┐
│  Layer 3: 用户精选（41 个，含聚合 meta-skill）     │
│  → 在 taxonomy.yaml 里，但代码在外部仓库          │
│  → aggregate-skills-map meta 帮你拉+分类+入库     │
└─────────────────────────────────────────────┘
```

**taxonomy.yaml** 是核心数据源（89 个 skill 的统一目录），按 9 大类组织：
- 内容创作 (25) / 内容汇聚 (25) / 设计视觉 (12) / 元能力 (9) / 效率办公 (7) / 工具合集 (10)

---

## 🔧 维护/贡献

### 测试 + CI

```bash
cd skills/aggregate-skills-map
pip install pyyaml pytest beautifulsoup4
python -m pytest test_shared.py -v

# GitHub Actions 自动跑：.github/workflows/test.yml
```

### 添加新 Skill

```bash
# 1. 选个合适的 primary_category（参考 taxonomy.yaml 现有分类）
# 2. 编辑 taxonomy.yaml，加 YAML 节点：
#    - id: unique-name
#    - name: 显示名
#    - author: github-username
#    - repo: owner/repo
#    - tags: [keyword1, keyword2]
#    - primary_category: content_creation/article
#    - type: skill
# 3. 跑测试：
python -m pytest test_shared.py::test_taxonomy_no_duplicate_ids -v
python -m pytest test_shared.py::test_taxonomy_required_fields -v
# 4. Commit + push（CI 自动验证）
```

### 详细文档

- `skills/aggregate-skills-map/README.md` — 89 skill 详细使用说明（191 行）
- `skills/aggregate-skills-map/taxonomy.yaml` — 89 skill 数据源
- `skills/aggregate-skills-map/SKILL.md` — aggregate-skills-map meta-skill 定义
- `skills/aggregate-skills-map/_shared.py` — 公共代码（CSS/JS/缓存/消息）
- `.github/workflows/test.yml` — CI 配置

---

## 📊 仓库结构

```
awesome-skills-map/
├── README.md                          ← 你正在看
├── LICENSE                             ← MIT
├── .github/workflows/test.yml          ← CI
├── archives/                           ← 22 章原始 zip（保留）
└── skills/
    ├── aggregate-skills-map/           ← Meta-skill：89 skill 聚合
    │   ├── SKILL.md
    │   ├── taxonomy.yaml               ← 89 skill 数据源
    │   ├── README.md                   ← 详细使用说明
    │   ├── _shared.py                  ← 公共代码
    │   ├── aggregate.sh                ← 拉博主 ≥500⭐
    │   ├── dedup_v35.py                ← 去重
    │   ├── expand_v3*.py               ← HTML 生成
    │   ├── quality_score.py            ← 评分
    │   └── test_shared.py               ← 12 pytest 测试
    ├── 第2章面试准备/                  ← 22 章本地 skill（可装）
    ├── 第3章智能周报生成器/
    ├── ...
    └── 第22章网页自动化测试/
```

## 🙋 关于

- **作者**：[Alexxiang2008](https://github.com/Alexxiang2008)
- **目标用户**：B2B 出海企业老板/员工、Claude Code 用户
- **使用场景**：内容创作、电商营销、SEO、视频、HR、财务、日常效率
- **License**：MIT
