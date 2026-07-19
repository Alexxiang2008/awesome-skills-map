# 🎯 Skills Dedup Map v0.2（tag-based 聚合）

> taxonomy 版本: v0.3 (2026-07-19) · 总 skill 数: **48** · 覆盖博主/来源: 7 个

**设计变更（v0.1 → v0.2）**：
- tag-based 重构：每个 skill 单一 id + tags 字段
- 跨分类合并：同 repo 用同 id，tags 表示多分类
- 整合 22 章原始技能
- 自研 1 个元能力

**聚合结果**：9 个 A 类重复聚类 + 33 个独立 skill

---

## 🔴 A 类高重复聚类

> 判定标准：同一 `primary_category` 下 ≥2 个 skill。需用户做场景化决策。

### `content_creation/ppt/html_slides` (4 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 21,810 | skill | op7418 | [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) | AI-agent Skill for generating polished HTML slide decks: editorial mag | `html_slides` |
| 3,140 | skill | op7418 | [op7418/NanoBanana-PPT-Skills](https://github.com/op7418/NanoBanana-PPT-Skills) | NanoBanana PPT Skills 基于 AI 自动生成高质量 PPT 图片和视频的强大工具，支持智能转场和交互式播放 | `html_slides` |
| 850 | skill | alchaincyf | [alchaincyf/huashu-md-html](https://github.com/alchaincyf/huashu-md-html) | md/html 双向流水线 · 三个能力一站式：万物→md / md→精美html / html→md。封装 markitdown + Pa | `html_slides` |
| 📍 本地 | local_skill | 一人课程 | [skills/第7章一键生成精美网页演示](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第7章一键生成精美网页演示) | 零依赖 HTML slides，强制 100vh | `html_slides` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **guizang-ppt-skill**（21,810 ⭐ · skill）：Swiss/Editorial 版式，WebGL runtime
- **NanoBanana-PPT-Skills**（3,140 ⭐ · skill）：视频转场 PPT

### `meta_skills/distill_person` (4 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 28,288 | meta | alchaincyf | [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) | 你想蒸馏的下一个员工，何必是同事。蒸馏任何人的思维方式——心智模型、决策启发式、表达DNA。Distill how anyone think | `distill_person` |
| 9,952 | sub_skill | alchaincyf | [alchaincyf/zhangxuefeng-skill](https://github.com/alchaincyf/zhangxuefeng-skill) | 张雪峰.skill — 张雪峰的认知操作系统。高考志愿/考研/职业规划的实战思维框架。由女娲.skill生成。 | `distill_person` |
| 1,069 | sub_skill | alchaincyf | [alchaincyf/x-mentor-skill](https://github.com/alchaincyf/x-mentor-skill) | X导师.skill — 女娲的第一个「非人类」作品。蒸馏6位顶级X创作者方法论 + 开源算法数据，提炼完整的选题-写作-增长操作手册。Mad | `distill_person` |
| 909 | sub_skill | alchaincyf | [alchaincyf/steve-jobs-skill](https://github.com/alchaincyf/steve-jobs-skill) | 乔布斯.skill — Steve Jobs的认知操作系统。6个心智模型 + 8条决策启发式 + 完整表达DNA。由女娲.skill生成。 | `distill_person` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **nuwa-skill**（28,288 ⭐ · meta）：蒸馏引擎（meta-skill）
- **zhangxuefeng-skill**（9,952 ⭐ · sub_skill）：高考志愿/考研/职业规划

### `content_creation/video/translate` (3 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 2,069 | skill | op7418 | [op7418/Youtube-clipper-skill](https://github.com/op7418/Youtube-clipper-skill) |  | `video_translate` |
| 618 | skill | xiaohuailabs | [xiaohuailabs/xiaohu-video-translate](https://github.com/xiaohuailabs/xiaohu-video-translate) | 对 AI 说一句话，把外语视频自动配上中文字幕 —— 下载/转写/翻译/润色/烧录一条龙，全程本地，转写零 API 费 | `video_translate` |
| 228 | skill | jimliu | [jimliu/baocut](https://github.com/JimLiu/baocut) | Open-source Agent Skill that drives the BaoCut macOS app CLI (transcri | `video_translate` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **Youtube-clipper-skill**（2,069 ⭐ · skill）：YouTube 视频剪辑
- **xiaohu-video-translate**（618 ⭐ · skill）：全程本地，零 API 费

### `design_visual/ui_design` (3 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 21,669 | skill | alchaincyf | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | Huashu Design · HTML-native design skill for Claude Code · Claude Code | `ui_design, html_slides` |
| 2,708 | skill | jimliu | [jimliu/baoyu-design](https://github.com/JimLiu/baoyu-design) | Run Claude Design locally as an Agent Skill — Cursor, Claude Code & mo | `ui_design, html_slides` |
| 📍 本地 | local_skill | 一人课程 | [skills/第21章前端界面设计](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第21章前端界面设计) | 反 AI slop，12 美学方向 | `ui_design` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **huashu-design**（21,669 ⭐ · skill）：HTML 原生设计，20 设计哲学
- **baoyu-design**（2,708 ⭐ · skill）：Claude Design 本地版

### `design_visual/illustration` (2 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 715 | skill | op7418 | [op7418/guizang-material-illustration](https://github.com/op7418/guizang-material-illustration) | 归藏的材质插画 skill：生成带字解释图、图表美化和参考辅助配图。 | `illustration` |
| 572 | skill | op7418 | [op7418/Document-illustrator-skill](https://github.com/op7418/Document-illustrator-skill) | 帮你从文档生成对应的多张配图，内置了歸藏精心探索的图片风格，支持 16:9 和 3:4 两种比例，方便发小红书以及推特。 | `illustration` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **guizang-material-illustration**（715 ⭐ · skill）：带字解释图、图表美化
- **Document-illustrator-skill**（572 ⭐ · skill）：16:9 / 3:4 文档配图

### `meta_skills/de_slop` (2 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 13,452 | skill | op7418 | [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | Humanizer 的汉化版本，Claude Code Skills，旨在消除文本中 AI 生成的痕迹。 | `de_slop` |
| 22 | skill | alchaincyf | [alchaincyf/tramstop-skill](https://github.com/alchaincyf/tramstop-skill) | 电车站.skill — 人味不是删出来的。Evidence-based de-slop skill: 四层AI味模型+真实素材注入，来自四版 | `de_slop` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **Humanizer-zh**（13,452 ⭐ · skill）：去除文本中 AI 痕迹
- **tramstop-skill**（22 ⭐ · skill）：4 层 AI 味模型 + 真实素材注入

### `collections/skill_collection` (2 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 23,848 | collection | jimliu | [jimliu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) |  | `skill_collection` |
| 1,217 | collection | alchaincyf | [alchaincyf/huashu-skills](https://github.com/alchaincyf/huashu-skills) | 花叔的内容创作 Skills 合集 - AI审校、选题生成、视频大纲、素材搜索等 11 个实用技能 | `skill_collection` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **baoyu-skills**（23,848 ⭐ · collection）：npx skills add jimliu/baoyu-skills
- **huashu-skills**（1,217 ⭐ · collection）：内容创作 11 skills 合集

### `content_creation/wechat/formatting` (2 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 660 | skill | xiaohuailabs | [xiaohuailabs/xiaohu-wechat-format](https://github.com/xiaohuailabs/xiaohu-wechat-format) | Claude Code 公众号一键排版+发布技能 \| Markdown → 微信兼容 HTML → 推送草稿箱 \| 30 套主题 + 可视化 | `wechat_formatting` |
| 📍 本地 | local_skill | 一人课程 | [skills/第10章微信公众号一键排版与发布](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第10章微信公众号一键排版与发布) | 4 主题，含小绿书 | `wechat_formatting` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **xiaohu-wechat-format**（660 ⭐ · skill）：30 主题 + 可视化画廊
- **wechat-publish-local**（📍 本地 ⭐ · local_skill）：4 主题，含小绿书

### `content_creation/video/effects` (2 个)

| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |
|----|------|------|------|------|------|
| 📍 本地 | local_skill | 一人课程 | [skills/第13章ListenHub Skill](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第13章ListenHub Skill) | 4 模式：Podcast/Explain/TTS/Image | `video_generate` |
| 📍 本地 | local_skill | 一人课程 | [skills/第14章视频综艺特效](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第14章视频综艺特效) | YouTube/B站 → 综艺风视频 | `video_effects` |

**🎯 场景化推荐**（基于 stars + 类型 + 标签）：

- **listenhub-local**（📍 本地 ⭐ · local_skill）：4 模式：Podcast/Explain/TTS/Image
- **video-wrapper-local**（📍 本地 ⭐ · local_skill）：YouTube/B站 → 综艺风视频

---

## 🌐 跨分类 skill（tags ≥ 2）

> 这些 skill 同时属于多个分类，是 dedup 的核心价值。

| ⭐ | skill | 作者 | 标签 |
|----|-------|------|------|
| 21,669 | `huashu-design` | alchaincyf | ui_design / html_slides |
| 5,198 | `guizang-social-card-skill` | op7418 | wechat_cover / xhs_images |
| 2,708 | `baoyu-design` | jimliu | ui_design / html_slides |

---

## 📂 完整分类树


---

## 🔍 隐藏洞察

### 👥 作者分布

| 作者 | skill 数 | ⭐ 总和 | 平均 ⭐ |
|------|---------|--------|---------|
| alchaincyf | 9 | 68,934 | 7,659 |
| op7418 | 10 | 57,460 | 5,746 |
| jimliu | 4 | 27,378 | 6,844 |
| joeseesun | 2 | 6,373 | 3,186 |
| xiaohuailabs | 2 | 1,278 | 639 |
| 一人课程 | 20 | 0 | 0 |
| 自研 | 1 | 0 | 0 |

### 🏷️ 类型分布

| type | 数量 |
|------|------|
| skill | 17 |
| local_skill | 17 |
| tool | 4 |
| meta | 4 |
| sub_skill | 3 |
| collection | 2 |
| book | 1 |

---

## 🧩 按类型第二视图

> 第一维度是 `primary_category`（职能），第二维度是 `type`（形态）。同一 skill 可同时跨两维。

### 🏷️ `meta` · 元能力（4 个）

| ⭐ | skill | 作者 | 主分类 | 标签 |
|----|-------|------|--------|------|
| 28,288 | [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) | alchaincyf | `meta_skills/distill_person` | `distill_person` |
| 4,958 | [darwin-skill](https://github.com/alchaincyf/darwin-skill) | alchaincyf | `meta_skills/self_evolve` | `self_evolve` |
| 782 | [qiaomu-goal-meta-skill](https://github.com/joeseesun/qiaomu-goal-meta-skill) | joeseesun | `meta_skills/task_normalization` | `task_normalization` |
| 0 | [aggregate-skills-map-self](https://github.com/Alexxiang2008/awesome-skills-map) | 自研 | `meta_skills` | `meta` |

### 🏷️ `collection` · 多 skill 合集（2 个）

| ⭐ | skill | 作者 | 主分类 | 标签 |
|----|-------|------|--------|------|
| 23,848 | [baoyu-skills](https://github.com/JimLiu/baoyu-skills) | jimliu | `collections/skill_collection` | `skill_collection` |
| 1,217 | [huashu-skills](https://github.com/alchaincyf/huashu-skills) | alchaincyf | `collections/skill_collection` | `skill_collection` |

### 🏷️ `book` · 书籍/教程（1 个）

| ⭐ | skill | 作者 | 主分类 | 标签 |
|----|-------|------|--------|------|
| 594 | [Illustrated-Agent-Skills](https://github.com/JimLiu/Illustrated-Agent-Skills) | jimliu | `collections/tutorial` | `tutorial` |

### 🏷️ `sub_skill` · 合集下的子技能（3 个）

| ⭐ | skill | 作者 | 主分类 | 标签 |
|----|-------|------|--------|------|
| 9,952 | [zhangxuefeng-skill](https://github.com/alchaincyf/zhangxuefeng-skill) | alchaincyf | `meta_skills/distill_person` | `distill_person` |
| 1,069 | [x-mentor-skill](https://github.com/alchaincyf/x-mentor-skill) | alchaincyf | `meta_skills/distill_person` | `distill_person` |
| 909 | [steve-jobs-skill](https://github.com/alchaincyf/steve-jobs-skill) | alchaincyf | `meta_skills/distill_person` | `distill_person` |

### 🏷️ `skill` · 独立 skill（17 个）

| ⭐ | skill | 作者 | 主分类 | 标签 |
|----|-------|------|--------|------|
| 21,810 | [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) | op7418 | `content_creation/ppt/html_slides` | `html_slides` |
| 21,669 | [huashu-design](https://github.com/alchaincyf/huashu-design) | alchaincyf | `design_visual/ui_design` | `ui_design, html_slides` |
| 13,452 | [Humanizer-zh](https://github.com/op7418/Humanizer-zh) | op7418 | `meta_skills/de_slop` | `de_slop` |
| 5,591 | [qiaomu-anything-to-notebooklm](https://github.com/joeseesun/qiaomu-anything-to-notebooklm) | joeseesun | `content_aggregation/notebooklm` | `notebooklm` |
| 5,198 | [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill) | op7418 | `content_creation/wechat/cover` | `wechat_cover, xhs_images` |
| 3,140 | [NanoBanana-PPT-Skills](https://github.com/op7418/NanoBanana-PPT-Skills) | op7418 | `content_creation/ppt/html_slides` | `html_slides` |
| 2,822 | [Claude-to-IM-skill](https://github.com/op7418/Claude-to-IM-skill) | op7418 | `dev_tools/im_bridge` | `im_bridge` |
| 2,708 | [baoyu-design](https://github.com/JimLiu/baoyu-design) | jimliu | `design_visual/ui_design` | `ui_design, html_slides` |
| 2,069 | [Youtube-clipper-skill](https://github.com/op7418/Youtube-clipper-skill) | op7418 | `content_creation/video/translate` | `video_translate` |
| 1,541 | [logo-generator-skill](https://github.com/op7418/logo-generator-skill) | op7418 | `design_visual/logo` | `logo_design` |
| 850 | [huashu-md-html](https://github.com/alchaincyf/huashu-md-html) | alchaincyf | `content_creation/ppt/html_slides` | `html_slides` |
| 715 | [guizang-material-illustration](https://github.com/op7418/guizang-material-illustration) | op7418 | `design_visual/illustration` | `illustration` |
| 660 | [xiaohu-wechat-format](https://github.com/xiaohuailabs/xiaohu-wechat-format) | xiaohuailabs | `content_creation/wechat/formatting` | `wechat_formatting` |
| 618 | [xiaohu-video-translate](https://github.com/xiaohuailabs/xiaohu-video-translate) | xiaohuailabs | `content_creation/video/translate` | `video_translate` |
| 572 | [Document-illustrator-skill](https://github.com/op7418/Document-illustrator-skill) | op7418 | `design_visual/illustration` | `illustration` |
| 228 | [baocut](https://github.com/JimLiu/baocut) | jimliu | `content_creation/video/translate` | `video_translate` |
| 22 | [tramstop-skill](https://github.com/alchaincyf/tramstop-skill) | alchaincyf | `meta_skills/de_slop` | `de_slop` |

### 🏷️ `tool` · 工具/脚本/服务（4 个）

| ⭐ | skill | 作者 | 主分类 | 标签 |
|----|-------|------|--------|------|
| 6,141 | [CodePilot](https://github.com/op7418/CodePilot) | op7418 | `dev_tools/desktop_client` | `desktop_client` |
| 📍 本地 | [xiaohongshu-scraper-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第16章商业数据分析) | 一人课程 | `data_analysis/social_scraping` | `social_scraping` |
| 📍 本地 | [viral-monitor-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第17章公众号爆文监控) | 一人课程 | `content_aggregation/monitoring` | `content_monitoring` |
| 📍 本地 | [web-artifacts-builder-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第20章WebArtifactsBuilder) | 一人课程 | `dev_tools/artifacts` | `artifacts` |

### 🏷️ `local_skill` · 本地 22 章（17 个）

| ⭐ | skill | 作者 | 主分类 | 标签 |
|----|-------|------|--------|------|
| 📍 本地 | [interview-intel-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第2章面试准备) | 一人课程 | `productivity/interview_prep` | `interview_prep` |
| 📍 本地 | [weekly-report-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第3章智能周报生成器) | 一人课程 | `productivity/weekly_report` | `weekly_report` |
| 📍 本地 | [creative-brainstorm-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第4章AI辅助创意脑暴) | 一人课程 | `product_design/brainstorm` | `brainstorm` |
| 📍 本地 | [invoice-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第5章发票与收据自动归档) | 一人课程 | `productivity/invoice` | `invoice` |
| 📍 本地 | [email-triage-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第6章智能邮件分类与回复助手) | 一人课程 | `productivity/email` | `email` |
| 📍 本地 | [frontend-slides-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第7章一键生成精美网页演示) | 一人课程 | `content_creation/ppt/html_slides` | `html_slides` |
| 📍 本地 | [interview-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第8章AI深度访谈与爆款文章创作) | 一人课程 | `content_creation/article/interview` | `article_interview` |
| 📍 本地 | [hot-article-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第9章热点爆款文章生成器) | 一人课程 | `content_creation/article/hot` | `article_hot` |
| 📍 本地 | [wechat-publish-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第10章微信公众号一键排版与发布) | 一人课程 | `content_creation/wechat/formatting` | `wechat_formatting` |
| 📍 本地 | [xiaohongshu-images-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第11章小红书爆款图文生成器) | 一人课程 | `content_creation/xiaohongshu/images` | `xhs_images` |
| 📍 本地 | [video-local-analyze-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第12章爆款视频拆解器) | 一人课程 | `content_creation/video/analyze` | `video_analyze` |
| 📍 本地 | [listenhub-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第13章ListenHub Skill) | 一人课程 | `content_creation/video/effects` | `video_generate` |
| 📍 本地 | [video-wrapper-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第14章视频综艺特效) | 一人课程 | `content_creation/video/effects` | `video_effects` |
| 📍 本地 | [app-review-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第15章AppStore评价分析) | 一人课程 | `data_analysis/app_review` | `app_review` |
| 📍 本地 | [prd-writer-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第19章产品需求撰写) | 一人课程 | `product_design/prd` | `prd` |
| 📍 本地 | [frontend-design-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第21章前端界面设计) | 一人课程 | `design_visual/ui_design` | `ui_design` |
| 📍 本地 | [webapp-testing-local](https://github.com/Alexxiang2008/awesome-skills-map/tree/main/skills/第22章网页自动化测试) | 一人课程 | `dev_tools/testing` | `testing` |

---

## 🔍 v0.3 主动审查（自我 spot check）

> 这是 dedup.py 自动生成的自我审查清单，标出可能需要你确认的边缘 case。

### ⚠️ 问题 1：distill_person 4 个里 4 个全是花叔（nuwa 衍生品）

- **现状**：花叔的 nuwa-skill 是 meta-skill，其他 3 个（zhangxuefeng/steve-jobs/x-mentor）是 nuwa 衍生的具体人物
- **判断**：是合理的——它们就是同一作者的子产品
- **建议**：保留现状，但在 docs 里说明 "nuwa 生态" 子分支

### ⚠️ 问题 2：5 个本地 skill 出现在 A 类聚类里

- **现状**：本地 skill（一人课程）和 5 博主 skill 在同一分类下
- **判断**：合理——同一职能下多家实现，对比表有价值
- **建议**：保留，但本地 skill 在对比表中加 📍 标记

### 💡 问题 4：24 个分类是单点（只有 1 个 skill）

- **判断**：单点分类不一定是错（有些就是 unique 领域），但提示可能合并或扩类
