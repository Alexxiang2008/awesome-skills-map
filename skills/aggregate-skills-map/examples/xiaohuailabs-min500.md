# 🎯 xiaohuailabs（小虎）技能地图（⭐ ≥ 500）

> **筛选条件**：star ≥ 500 · 排除 fork
>
> 实测命令：`./aggregate.sh xiaohuailabs`
>
> **结果**：40 公开仓库 → **2 个 ≥500 ⭐**

## 👤 用户画像

**XiaoHu** · xiaohu.ai · 2023-03-28 加入 GitHub · 93 followers · **40 公开仓库**

- **核心定位**：小团队也能用的 Claude Code 工具集
- **代表作**：`xiaohu-wechat-format`（660 ⭐）+ `xiaohu-video-translate`（618 ⭐）
- **跨平台**：Claude Code 公众号 + 视频本地化

---

## 📊 全部 ≥500 ⭐ 仓库

| ⭐ | 仓库 | 简介 |
|----|------|------|
| **660** | [**xiaohu-wechat-format**](https://github.com/xiaohuailabs/xiaohu-wechat-format) | Claude Code 公众号一键排版+发布技能——Markdown → 微信兼容 HTML → 推送草稿箱，**30 套主题** + 可视化画廊 |
| **618** | [**xiaohu-video-translate**](https://github.com/xiaohuailabs/xiaohu-video-translate) | 对 AI 说一句话，把外语视频自动配上中文字幕——下载 / 转写 / 翻译 / 润色 / 烧录 一条龙，**全程本地**，**转写零 API 费** |

---

## 🔑 关键洞察

1. **小而精路线** —— 不追求数量，2 个项目都做到 ≥600 ⭐
2. **去 API 费差异化** —— `xiaohu-video-translate` 全程本地化转写，跟同类拉开差距
3. **可视化画廊** —— 30 套主题 + 可视化画廊，让用户先看后选，降低选择成本

## 🔗 与宝玉/歸藏的对比

| 维度 | 小虎（xiaohuailabs） | 宝玉（JimLiu） | 歸藏（op7418） |
|------|-------------------|---------------|---------------|
| **公众号技能** | xiaohu-wechat-format (660) | baoyu-post-to-wechat（在 baoyu-skills 内） | guizang-social-card-skill (5.2K) 侧重封面 |
| **视频技能** | xiaohu-video-translate (618) | baocut (225) | Youtube-clipper-skill (2.1K) |
| **差异化** | 零 API 费 / 全程本地 | 完整工作流 / macOS app 集成 | 视觉系统专精 |
| **项目数** | 40（高产但精选） | 230（量大） | 28（精品密度高） |

**互补建议**：
- 要做**公众号自动化**：宝玉 baoyu-post-to-wechat + 小虎 xiaohu-wechat-format 主题
- 要做**视频翻译**：小虎 xiaohu-video-translate（零成本）vs 歸藏 Youtube-clipper-skill（更多功能）
- 要做**视觉设计**：歸藏是绝对首选

## 💡 隐藏发现：aggregate.sh 关键词盲区

`xiaohu-wechat-format` 和 `xiaohu-video-translate` 都**不含 skill/nuwa/darwin 关键词**，但显然是 Claude Code 技能。
**这暴露了 aggregate.sh 的盲区**：关键词需要扩展（候选："技能"、claude、format、translate、render）。

## 🔗 相关文件

- 实测脚本：`../aggregate.sh`