# aggregate-skills-map

> **89 个 Claude Skill 的统一目录 + 评分/筛选/可视化系统**。服务于 B2B 出海企业日常使用。

## 🎯 是什么

- **`taxonomy.yaml`**：89 个 Claude Skill 的统一分类（5 位博主原创 + 22 章原始技能 + 41 个用户精选入库）
- **评分/筛选系统**：4 维硬指标 + 卫生 + 生态 bonus
- **可视化系统**：生成可勾选 + 可导出的 HTML

## 📦 目录结构

```
skills/aggregate-skills-map/
├── taxonomy.yaml             # 89 个 skill 的统一分类（YAML 数据源）
├── SKILL.md                  # Claude Code skill 定义
├── _shared.py                # 公共代码（CSS、JS、cache_key、msg 函数）
├── aggregate.sh              # 从 GitHub 拉 5 位博主的 ≥500⭐ skill
├── dedup.py                  # taxonomy 内去重（v0.x）
├── dedup_v35.py              # v3.4 HTML 去重（按 name+repo）
├── discover.py               # gh search 多 topic 扫描
├── expand_collections.py     # 展开合集仓库的子 skill
├── expand_v3.py              # v3 — 拉合集 + 过滤编程 + 分类
├── expand_v3_refine.py       # v3.1 — 严格排除模式（防误伤正当 API）
├── expand_v32.py             # v3.2 — description 截短（≤80 字）
├── expand_v33.py             # v3.3 — LLM 翻译英文 → 中文
├── retry_failed.py           # 重试翻译失败的卡片
├── quality_score.py          # 4 维硬指标评分
├── test_shared.py            # 12 个 pytest 测试
├── examples/                 # 生成的 HTML（candidates-v3*.html, v3.5.html 等）
├── .dedup_cache.json         # dedup 缓存
├── .translate_cache.json     # 翻译缓存
└── .quality_cache.json       # 评分缓存
```

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install pyyaml pytest beautifulsoup4

# 2. 跑测试
cd skills/aggregate-skills-map
python -m pytest test_shared.py -v

# 3. 跑聚合（从 GitHub 拉博主 + 合集）
./aggregate.sh                                # 5 博主 ≥500⭐
./expand_collections.py                      # 展开合集子 skill
./expand_v3.py                                # 分类 + 过滤编程
./expand_v33.py --limit 5 --parallel 4       # LLM 翻译（limit 测速）

# 4. 看输出
open examples/candidates-v3.5.html           # 可勾选 + 导出
```

## 📝 taxonomy.yaml 格式

每个 skill 节点结构：

```yaml
- id: nuwa-skill                # 唯一 ID（小写 + 连字符）
  name: 女娲——人物思维蒸馏引擎   # 显示名
  author: alchaincyf            # 作者 GitHub 用户名
  repo: alchaincyf/nuwa-skill   # owner/repo
  path: ''                       # 子路径（合集内有效）
  stars: 28282                  # 用于排序
  note: 蒸馏引擎（meta-skill）  # 简短描述
  tags: [distill_person]         # 用于跨视图筛选
  primary_category: meta_skills/distill_person
  type: skill                    # skill / sub_skill / collection / book / tool / meta / local_skill
```

### 9 大分类

| 一级分类 | 数量 | 说明 |
|----------|------|------|
| `content_creation` | 16 | 公众号/小红书/PPT/视频/文章 |
| `marketing` | 8 | SEO/广告/电商 |
| `design_visual` | 6 | UI/Logo/插图 |
| `meta_skills` | 8 | 蒸馏/进化/规范化 |
| `content_aggregation` | 2 | 监控/NotebookLM |
| `dev_tools` | 2 | 客户端/IM |
| `collections` | 2 | 合集/教程 |
| `productivity` | 4 | 周报/邮件/发票/面试 |
| `data_analysis` | 2 | App 评论/社交数据 |
| `product_design` | 1 | PRD/脑暴 |
| `local_skill` | 20 | 本地 22 章原始 |
| `other` | 9 | B2B 工具（电商/营销）|

## ➕ 如何添加新 Skill

### 场景 1：从 GitHub 拉博主的新仓库

```bash
# 用 aggregate.sh 拉 + discover.py 扫
./aggregate.sh <github_user>     # 例如 ./aggregate.sh alchaincyf
./discover.py --min-score 50
```

### 场景 2：手动添加（如评测新 skill）

1. 选合适的 `primary_category`（参考 9 大分类）
2. 加 YAML 节点到 `taxonomy.yaml` 的 `skills` 列表
3. tags 用 `_<keyword>` 格式（如 `wechat`, `seo`, `video`）
4. 跑测试验证：
   ```bash
   python -m pytest test_shared.py::test_taxonomy_no_duplicate_ids -v
   python -m pytest test_shared.py::test_taxonomy_required_fields -v
   ```
5. commit 到本地（push 由你决定）

### 场景 3：从 candidates-overview 选 user_selected 的

```bash
# 1. 用户在 candidates-v3.5.html 勾选
# 2. 复制 MD 给我
# 3. 我用脚本批量加到 taxonomy.yaml：
#    - 推断 primary_category（按关键词）
#    - 加 tags（按 description）
#    - 加 type: skill
#    - 保留 user_selected 标记
```

## 🔧 配套脚本

### aggregate.sh
```bash
./aggregate.sh <github_user>  # 拉一个博主的 ≥500⭐ skill
# 输出：examples/<user>-min500-skills.md
```

### expand_v3*.py（HTML 生成流水线）
```bash
./expand_v3.py                 # 拉 4 大合集 + 分类 + 过滤
./expand_v3_refine.py          # 严格排除（防误伤正当 API）
./expand_v32.py                # 截短 description
./expand_v33.py                # LLM 翻译（需 ANTHROPIC_API_KEY 或 claude CLI）
./dedup_v35.py                 # 去重 + 修复 keep_divs bug
```

### 评分 / 筛选

```bash
./quality_score.py --min-stars 100       # 评分
./discover.py --min-score 50 --output candidates.md  # 搜索
```

## 🧪 测试 + CI

### 本地测试
```bash
cd skills/aggregate-skills-map
python -m pytest test_shared.py -v
```

### CI（GitHub Actions）
- 触发：push / PR 到 main
- 步骤：setup Python 3.13 → install pytest + beautifulsoup4 + pyyaml → 跑 test_shared.py
- 配置文件：`.github/workflows/test.yml`

## 🛠 维护指南

### 添加新 skill 的 3 步

1. **分类**：根据 `note` 和 `tags` 关键词推断 `primary_category`
2. **去重**：跑 dedup_v35.py 或先 grep `taxonomy.yaml` 看是否已存在
3. **测试**：跑 `test_taxonomy_no_duplicate_ids` + `test_taxonomy_required_fields`

### 缓存管理

| 缓存文件 | 何时删 |
|---------|--------|
| `.dedup_cache.json` | dedup 逻辑变更后 |
| `.translate_cache.json` | prompt 改变后 |
| `.quality_cache.json` | 评分公式变更后 |

### 升级流程

1. 改 `taxonomy.yaml` 顶部 `meta.version`
2. 跑测试
3. commit 到本地（不 push）
4. 网络恢复时 `git push origin main`

## 📜 License

MIT

## 🙋 联系

本仓库为 `awesome-skills-map`（Alexxiang2008 / awesome-skills-map）的一部分。
作者挑选的 41 个 B2B 出海场景 skill 来自 7 大 GitHub 仓库的 4 个合集。
