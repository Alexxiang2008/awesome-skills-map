---
name: aggregate-skills-map
description: 聚合 GitHub 博主/牛人技能地图。输入 GitHub 用户名列表，自动拉取其公开仓库，按 stars 排序并按职能分类，输出 Markdown 技能地图（含简介 + 仓库地址）。支持 fork 过滤、最小 star 阈值、主题筛选、JSON 输出。当用户说「聚合博主技能」「生成技能地图」「按作者聚合 skills」「我想看 X 的 skills」「跟踪大牛仓库」时触发。依赖：gh CLI 已登录。
license: MIT
---

# Aggregate Skills Map

> **按作者视角聚合 GitHub 技能地图** —— 输入博主列表，自动拉取 → 筛选 → 分类 → 输出。

## 🎯 解决什么

| 现有方案 | 本 Skill 的差异 |
|---------|---------------|
| ComposioHQ/awesome-claude-skills（68K ⭐）—— 按主题聚合 | **按作者聚合**（watchlist 驱动） |
| davepoon/buildwithclaude（3K ⭐）—— 已收录的 skills hub | **拉取原始仓库**，可包含 fork 但按 stars 过滤 |
| gh search repos—— 一次性搜索 | **多博主批量 + 自动分类 + Markdown 格式化** |

## 🚀 触发方式

- `/aggregate-skills-map alchaincyf` —— 单博主（默认只看 star≥500）
- `/aggregate-skills-map alchaincyf --skill-only` —— 进一步筛 skills 关键词
- `/aggregate-skills-map alchaincyf,davepoon,mrgoonie` —— 多博主
- `/aggregate-skills-map --json alchaincyf` —— 输出 JSON
- `/aggregate-skills-map --topic claude-skill alchaincyf` —— 只看相关主题

## 📦 依赖

```bash
gh auth status  # 必须已登录
jq --version    # JSON 解析（可选，用于 --json 输出）
```

## 📋 命令行参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `USERS`（位置参数） | （必填） | GitHub 用户名列表，逗号分隔 |
| `--min-stars N` | **500** | 最小 star 数阈值（默认只看 500+ 的高质量项目） |
| `--include-forks` | false | 是否包含 fork 的仓库（默认排除） |
| `--skill-only` | false | 只保留 name/desc 含 skill/nuwa/darwin 关键词的仓库 |
| `--topic TAG` | 无 | 限定主题（如 `claude-skill`、`claude-code`） |
| `--json` | false | 输出 JSON 而非 Markdown |
| `--output PATH` | stdout | 写入文件路径 |
| `--sort` | stars | stars / updated / name |
| `--limit N` | 0 | 单博主最多显示几个（0=全部） |

## 🎯 常用调用速查

```bash
# 默认：star≥500（推荐起点）
./aggregate.sh alchaincyf

# 高质量 skills 清单（star≥500 + 仅 skills 关键词）
./aggregate.sh alchaincyf --skill-only

# 放宽到 100 星，看更多候选
./aggregate.sh alchaincyf --min-stars 100

# 多博主批量
./aggregate.sh alchaincyf,davepoon,mrgoonie

# 主题筛选 + JSON 输出
./aggregate.sh alchaincyf --topic claude-skill --json --output map.json

# 完整画像（含 fork、低星）— 调试用
./aggregate.sh alchaincyf --min-stars 0 --include-forks
```

## ⚙️ 工作流程

### Phase 1：参数解析
- 拆分逗号分隔的用户名 → `users[]`
- 验证每个用户存在（`gh api users/<name>` → 404 即报错）

### Phase 2：批量拉取
- 对每个用户：`gh api users/<name>/repos?per_page=100`
- 收集：name / description / stargazers_count / html_url / topics / language / updated_at / fork

### Phase 3：过滤 & 排序
- 默认排除 fork（除非 `--include-forks`）
- 按 `--min-stars` 过滤
- 按 `--sort` 排序（默认 stars 降序）

### Phase 4：智能分类
基于 description + name 关键词自动归类（无需 LLM）：
- 🧠 **元能力 Skills** —— 含 `skill`, `optimization`, `distill`, `evolve`
- 👤 **人物蒸馏** —— 含人名（Steve Jobs / Musk / 芒格…）
- 🎨 **设计/视觉** —— 含 `design`, `html`, `slide`, `cover`, `visual`, `image`
- 📝 **内容创作** —— 含 `content`, `editor`, `writing`, `article`, `publish`
- 🛠 **开发工具** —— 含 `claude-code`, `cursor`, `mcp`, `cli`, `vibe`, `editor`
- 📚 **教程/电子书** —— 含 `book`, `guide`, `orange-book`, `tutorial`
- 🌐 **其他** —— 兜底分类

### Phase 5：输出
- **Markdown 表格**：每类一个分组表（仓库名 / ⭐ / 简介）
- **JSON**：`{user: {category: [{repo, stars, desc, url}]}}`

## 📤 输出格式（Markdown 示例）

```markdown
# 🎯 alchaincyf 技能地图

> 73 公开仓库 · 去 fork 后 47 个原创项目 · ⭐ 总和 ≈ 86K+

## 🏆 旗舰三件套（10K+ ⭐）

| 仓库 | ⭐ | 简介 |
|------|---|------|
| [**nuwa-skill**](https://github.com/alchaincyf/nuwa-skill) | 28,282 | 你想蒸馏的下一个员工... |
...
```

## 🛡 边界与限制

- **API 速率**：未认证 60/小时，认证 5000/小时。一次处理 ≤10 个博主安全
- **仓库上限**：每用户 100 个公开仓库（per_page 上限）；超过 100 用分页
- **隐私**：私有仓库需 token 有 repo 权限；本 skill 默认只看 public
- **分类启发式**：关键词简单规则，可能误分类；可用 LLM 后处理提升质量

## 📁 文件结构

```
aggregate-skills-map/
├── SKILL.md          ← 本文件
├── aggregate.sh      ← 主脚本（gh API 调用 + jq 解析 + Markdown 渲染）
├── classify.py       ← Python 分类器（可选，比 bash 关键词更精准）
└── examples/
    └── alchaincyf.md ← 实测输出样例
```

## 🔗 相关参考

- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) —— 主题聚合事实标准
- [anthropics/skills](https://github.com/anthropics/skills) —— 官方仓库
- [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude) —— Skills hub
- [claude-skills.com](https://claude-skills.com/) —— 官方 marketplace

## ⚖️ License

MIT