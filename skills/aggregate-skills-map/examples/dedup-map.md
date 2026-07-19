# 🎯 Skills Dedup Map v0.2（tag-based 聚合）

> taxonomy 版本: v0.2 (2026-07-19) · 总 skill 数: **48** · 覆盖博主/来源: 7 个

**设计变更（v0.1 → v0.2）**：
- tag-based 重构：每个 skill 单一 id + tags 字段
- 跨分类合并：同 repo 用同 id，tags 表示多分类
- 整合 22 章原始技能
- 自研 1 个元能力

**聚合结果**：8 个 A 类重复聚类 + 34 个独立 skill

---

## 🔴 A 类高重复聚类

> 判定标准：同一 `primary_category` 下 ≥2 个 skill。需用户做场景化决策。

### `content_creation/ppt/html_slides` (4 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 21,809 | op7418 | [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) | AI-agent Skill for generating polished HTML slide decks: editorial magazine and  | `html_slides` |
| 3,140 | op7418 | [op7418/NanoBanana-PPT-Skills](https://github.com/op7418/NanoBanana-PPT-Skills) | NanoBanana PPT Skills 基于 AI 自动生成高质量 PPT 图片和视频的强大工具，支持智能转场和交互式播放 | `html_slides` |
| 850 | alchaincyf | [alchaincyf/huashu-md-html](https://github.com/alchaincyf/huashu-md-html) | md/html 双向流水线 · 三个能力一站式：万物→md / md→精美html / html→md。封装 markitdown + Pandoc + htm | `html_slides` |
| 0 | 一人课程 | [一人/第7章一键生成精美网页演示](https://github.com/一人/第7章一键生成精美网页演示) | 零依赖 HTML slides，强制 100vh | `html_slides` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **guizang-ppt-skill**（21,809 ⭐）：Swiss/Editorial 版式，WebGL runtime
- **NanoBanana-PPT-Skills**（3,140 ⭐）：视频转场 PPT

### `meta_skills/distill_person` (4 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 28,286 | alchaincyf | [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) | 你想蒸馏的下一个员工，何必是同事。蒸馏任何人的思维方式——心智模型、决策启发式、表达DNA。Distill how anyone thinks. | `distill_person` |
| 9,952 | alchaincyf | [alchaincyf/zhangxuefeng-skill](https://github.com/alchaincyf/zhangxuefeng-skill) | 张雪峰.skill — 张雪峰的认知操作系统。高考志愿/考研/职业规划的实战思维框架。由女娲.skill生成。 | `distill_person` |
| 1,069 | alchaincyf | [alchaincyf/x-mentor-skill](https://github.com/alchaincyf/x-mentor-skill) | X导师.skill — 女娲的第一个「非人类」作品。蒸馏6位顶级X创作者方法论 + 开源算法数据，提炼完整的选题-写作-增长操作手册。Made with 女娲. | `distill_person` |
| 909 | alchaincyf | [alchaincyf/steve-jobs-skill](https://github.com/alchaincyf/steve-jobs-skill) | 乔布斯.skill — Steve Jobs的认知操作系统。6个心智模型 + 8条决策启发式 + 完整表达DNA。由女娲.skill生成。 | `distill_person` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **nuwa-skill**（28,286 ⭐）：蒸馏引擎（meta-skill）
- **zhangxuefeng-skill**（9,952 ⭐）：高考志愿/考研/职业规划

### `content_creation/video/translate` (3 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 2,069 | op7418 | [op7418/Youtube-clipper-skill](https://github.com/op7418/Youtube-clipper-skill) |  | `video_translate` |
| 618 | xiaohuailabs | [xiaohuailabs/xiaohu-video-translate](https://github.com/xiaohuailabs/xiaohu-video-translate) | 对 AI 说一句话，把外语视频自动配上中文字幕 —— 下载/转写/翻译/润色/烧录一条龙，全程本地，转写零 API 费 | `video_translate` |
| 228 | jimliu | [jimliu/baocut](https://github.com/jimliu/baocut) | Open-source Agent Skill that drives the BaoCut macOS app CLI (transcribe · subti | `video_translate` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **Youtube-clipper-skill**（2,069 ⭐）：YouTube 视频剪辑
- **xiaohu-video-translate**（618 ⭐）：全程本地，零 API 费

### `design_visual/ui_design` (3 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 21,668 | alchaincyf | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | Huashu Design · HTML-native design skill for Claude Code · Claude Code 里 HTML 原生 | `ui_design, html_slides` |
| 2,708 | jimliu | [jimliu/baoyu-design](https://github.com/jimliu/baoyu-design) | Run Claude Design locally as an Agent Skill — Cursor, Claude Code & more. Produc | `ui_design, html_slides` |
| 0 | 一人课程 | [一人/第21章前端界面设计](https://github.com/一人/第21章前端界面设计) | 反 AI slop，12 美学方向 | `ui_design` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **huashu-design**（21,668 ⭐）：HTML 原生设计，20 设计哲学
- **baoyu-design**（2,708 ⭐）：Claude Design 本地版

### `design_visual/illustration` (2 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 715 | op7418 | [op7418/guizang-material-illustration](https://github.com/op7418/guizang-material-illustration) | 归藏的材质插画 skill：生成带字解释图、图表美化和参考辅助配图。 | `illustration` |
| 572 | op7418 | [op7418/Document-illustrator-skill](https://github.com/op7418/Document-illustrator-skill) | 帮你从文档生成对应的多张配图，内置了歸藏精心探索的图片风格，支持 16:9 和 3:4 两种比例，方便发小红书以及推特。 | `illustration` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **guizang-material-illustration**（715 ⭐）：带字解释图、图表美化
- **Document-illustrator-skill**（572 ⭐）：16:9 / 3:4 文档配图

### `meta_skills/de_slop` (2 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 13,452 | op7418 | [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | Humanizer 的汉化版本，Claude Code Skills，旨在消除文本中 AI 生成的痕迹。 | `de_slop` |
| 22 | alchaincyf | [alchaincyf/tramstop-skill](https://github.com/alchaincyf/tramstop-skill) | 电车站.skill — 人味不是删出来的。Evidence-based de-slop skill: 四层AI味模型+真实素材注入，来自四版本盲测实验 | `de_slop` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **Humanizer-zh**（13,452 ⭐）：去除文本中 AI 痕迹
- **tramstop-skill**（22 ⭐）：4 层 AI 味模型 + 真实素材注入

### `collections/skill_collection` (2 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 23,846 | jimliu | [jimliu/baoyu-skills](https://github.com/jimliu/baoyu-skills) |  | `skill_collection, wechat_formatting, xhs_images` |
| 1,217 | alchaincyf | [alchaincyf/huashu-skills](https://github.com/alchaincyf/huashu-skills) | 花叔的内容创作 Skills 合集 - AI审校、选题生成、视频大纲、素材搜索等 11 个实用技能 | `skill_collection` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **baoyu-skills**（23,846 ⭐）：npx skills add jimliu/baoyu-skills
- **huashu-skills**（1,217 ⭐）：内容创作 11 skills 合集

### `content_creation/wechat/formatting` (2 个)

| ⭐ | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|
| 660 | xiaohuailabs | [xiaohuailabs/xiaohu-wechat-format](https://github.com/xiaohuailabs/xiaohu-wechat-format) | Claude Code 公众号一键排版+发布技能 \| Markdown → 微信兼容 HTML → 推送草稿箱 \| 30 套主题 + 可视化画廊 | `wechat_formatting` |
| 0 | 一人课程 | [一人/第10章微信公众号一键排版与发布](https://github.com/一人/第10章微信公众号一键排版与发布) | 4 主题，含小绿书 | `wechat_formatting` |

**🎯 场景化推荐**（基于 stars + 标签）：

- **xiaohu-wechat-format**（660 ⭐）：30 主题 + 可视化画廊
- **wechat-publish-local**（0 ⭐）：4 主题，含小绿书

---

## 🌐 跨分类 skill（tags ≥ 2）

> 这些 skill 同时属于多个分类，是 dedup 的核心价值。

| ⭐ | skill | 作者 | 标签 |
|----|-------|------|------|
| 23,846 | `baoyu-skills` | jimliu | skill_collection / wechat_formatting / xhs_images |
| 21,668 | `huashu-design` | alchaincyf | ui_design / html_slides |
| 5,197 | `guizang-social-card-skill` | op7418 | wechat_cover / xhs_images |
| 2,708 | `baoyu-design` | jimliu | ui_design / html_slides |

---

## 📂 完整分类树


---

## 🔍 隐藏洞察

### 👥 作者分布

| 作者 | skill 数 | ⭐ 总和 | 平均 ⭐ |
|------|---------|--------|---------|
| alchaincyf | 9 | 68,931 | 7,659 |
| op7418 | 10 | 57,458 | 5,745 |
| jimliu | 4 | 27,376 | 6,844 |
| joeseesun | 2 | 6,373 | 3,186 |
| xiaohuailabs | 2 | 1,278 | 639 |
| 一人课程 | 20 | 0 | 0 |
| 自研 | 1 | 0 | 0 |

### 🏷️ 类型分布

| type | 数量 |
|------|------|
| skill | 34 |
| tool | 4 |
| meta | 4 |
| sub_skill | 3 |
| collection | 2 |
| book | 1 |
