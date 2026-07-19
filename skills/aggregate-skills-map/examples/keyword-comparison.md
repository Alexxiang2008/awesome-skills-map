# 🔬 关键词扩展对比分析

> **背景**：aggregate.sh 的 `--skill-only` 默认关键词 `skill|nuwa|darwin` 存在盲区——无法匹配中文"技能"或单复数变体
>
> **修复**：扩展为 `skill|skills|nuwa|darwin|技能`
>
> **验证**：5 博主对比实测（star≥500，去 fork）

---

## 📊 实测对比矩阵

| 博主 | star≥500 总数 | 旧关键词匹配 | 新关键词匹配 | 增量 |
|------|--------------|-------------|-------------|------|
| alchaincyf（花叔） | 14 | 8 | 8 | 0 |
| JimLiu（宝玉） | 4 | 3 | 3 | 0 |
| op7418（歸藏） | 11 | 10 | 10 | 0 |
| **xiaohuailabs（小虎）** | 2 | **0** | **1** | **+1** ⭐ |
| joeseesun（乔木） | 2 | 2 | 2 | 0 |
| **总计** | **33** | **23** | **24** | **+1** |

---

## 🔍 关键发现

### 1. jq test() 子串匹配特性
`test("skill"; "i")` 自动匹配 `skills`（子串），所以旧关键词其实**已经覆盖单复数变体**。例如 CodePilot 描述 "with MCP & skills" 在旧关键词下也匹配。

### 2. 真正的盲区是**中文"技能"**
小虎的 `xiaohu-wechat-format` 描述含"Claude Code 公众号一键排版+发布**技能**"，但仓库名不含 skill/nuwa/darwin。
- 旧关键词：0 匹配
- 新关键词（含中文"技能"）：1 匹配 ✅

### 3. 其他博主没变化的原因
- **花叔**：所有 skill 仓库名都含 `nuwa` 或 `skill`（如 darwin-skill, nuwa-skill, x-mentor-skill）
- **宝玉**：3 个 ≥500 ⭐ 仓库名都含 `skill` 或描述含 Claude Skills（`Illustrated-Agent-Skills`）
- **歸藏**：10 个匹配仓库名都含 `-skill` 后缀
- **乔木**：2 个匹配仓库名都含 `meta-skill`

---

## 💡 经验教训

| 教训 | 改进方向 |
|------|---------|
| 关键词不能仅依赖英文 | 必须包含目标语言（本例中文"技能"） |
| 子串匹配 ≠ 词根匹配 | jq test() 会把 "skill" 匹配 "skills"，但不会匹配 "skilling" |
| 命名约定很重要 | `-skill` 后缀几乎成了 Claude Skills 的事实标准 |
| description 是金矿 | 仓库名不含 skill 但 description 提"Claude Code 技能"也应该被识别 |

## 🎯 关键词扩展决策表

| 关键词 | 捕获场景 | 风险 |
|--------|---------|------|
| `skill` | 英文 `*-skill` 后缀 | 无（业界惯例） |
| `skills` | 复数变体（其实 `skill` 已覆盖） | 无 |
| `nuwa\|darwin` | 花叔特有生态 | 低（特有名词） |
| `技能` | **中文"技能"** | 低（中文 AI 圈常用） |
| `claude.code` | 任何 Claude Code 项目 | ⚠️ 中（可能误判 awesome-claude-code 这种索引库） |
| `codex` | Codex 平台 skill | ⚠️ 中（同上） |

**当前策略**：保守扩展（仅加 `技能`），避免误判。
**激进方案**：可加 `claude.code|codex`，但需要人工 review。

## 🔧 进一步优化建议

1. **加白名单机制**：`--whitelist path/to/whitelist.txt` 让用户手动指定要追踪的仓库名
2. **加 LLM 后处理**：用 Claude 自身判断"这是不是 skill"（准确率可达 95%+）
3. **加 topic 优先**：优先看 GitHub repo 的 `topics` 字段（如 `claude-skill`），更精确

## 🔗 实测命令

```bash
# 旧关键词效果
./aggregate.sh xiaohuailabs --skill-only
# → 0 个匹配

# 新关键词效果（已应用）
./aggregate.sh xiaohuailabs --skill-only
# → 1 个匹配（xiaohu-wechat-format）

# 5 博主批量验证
for u in alchaincyf JimLiu op7418 xiaohuailabs joeseesun; do
  echo "=== $u ==="
  ./aggregate.sh "$u" --skill-only 2>&1 | grep -E "过滤后 \*\*[0-9]+\*\*"
done
```