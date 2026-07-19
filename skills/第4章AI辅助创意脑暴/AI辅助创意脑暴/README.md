# AI辅助创意脑暴 Skill 使用说明

## 功能介绍

输入一个模糊的想法，自动生成 10 个可执行的创意方案，包含：
- 联网搜索竞品和最佳实践
- SCAMPER 方法多维度发散
- ICE 可行性评分（影响力 × 信心 × 容易度）
- 资源需求估算（人力、预算、周期）
- 方案对比表和下一步建议

## 安装方法

1. 将 `creative-brainstorm` 文件夹复制到 `~/.claude/skills/` 目录下
2. 将 `commands` 文件夹中的 `brainstorm.md` 和 `脑暴.md` 复制到 `~/.claude/commands/` 目录下
3. 重启 Claude Code

```bash
# 复制 Skill
cp -r creative-brainstorm ~/.claude/skills/

# 复制命令
cp commands/brainstorm.md ~/.claude/commands/
cp commands/脑暴.md ~/.claude/commands/
```

## 使用方法

```
/脑暴 <你的想法>
```

或

```
/brainstorm <你的想法>
```

## 使用示例

```
/脑暴 我想做一个帮助程序员提高效率的工具
/脑暴 如何让我的咖啡店吸引更多年轻人
/脑暴 解决团队远程协作效率低的问题
/brainstorm 书籍上市后的促销推广方案
```

## 文件结构

```
creative-brainstorm/
├── SKILL.md                 # 主文件
└── references/
    ├── scamper.md          # SCAMPER 发散方法
    └── scoring-guide.md    # ICE 评分指南

commands/
├── brainstorm.md           # /brainstorm 命令
└── 脑暴.md                  # /脑暴 命令
```
