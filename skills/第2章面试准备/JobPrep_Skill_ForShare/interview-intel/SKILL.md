---
name: interview-intel
description: 面试准备与求职策略 Skill。用于根据公司名、职位、JD 和候选人简历生成完整面试准备包，包括公司情报、简历与 JD 匹配、面试策略、破冰话术和最终行动计划。适用于用户说“我想应聘...”“帮我准备面试”“分析这个 JD 和我的简历匹配度”“生成面试准备包”等场景。
---

# Interview Intel

这是一个面试准备 Skill。目标是让候选人输入公司、职位、JD 和简历后，生成一套可直接使用的面试准备材料。

## 输出文件

每个公司会在 `companies/[公司名]/` 下生成 5 个标准文件：

1. `01_company_intel_brief.md`：公司背景、业务、产品、竞争格局、职位切入点。
2. `02_resume_jd_matching.md`：简历与 JD 匹配度、优势、差距、应对话术。
3. `03_interview_prep_report.md`：HR、业务、终面/高管面试策略与 STAR 案例。
4. `04_icebreaker_messages.md`：30 秒、1 分钟、2 分钟自我介绍和破冰开场白。
5. `05_final_analysis_report.md`：综合评估、准备优先级、行动计划和复习清单。

## 推荐入口

优先使用项目根目录下的 Claude Code 斜杠命令：

```text
/jobprep 公司名 职位名

JD: [粘贴 JD 内容]
简历: resumes/我的简历.pdf
```

如果用户没有提供简历路径，先在 `resumes/` 目录里查找 PDF 简历。如果找不到，需要询问用户简历位置。

## 关键原则

1. 先读取真实简历，再生成内容。不要让子任务或后续推理凭空猜测候选人经历。
2. 所有 STAR 案例、自我介绍、优劣势分析，都必须基于真实简历信息。
3. 公司信息和行业信息需要尽量使用最新公开资料；如果无法联网或信息不足，要明确标注不确定性。
4. 输出要具体、可背诵、可执行，避免泛泛而谈。
5. 生成后要做一致性检查：姓名、学历、公司经历、年限、核心项目不能互相矛盾。

## 工作流程

### 1. 解析输入

从用户消息中提取：

- `company`：公司名称
- `role`：目标职位
- `jd`：职位描述
- `resume_path`：简历路径
- `industry`：行业，可从 JD 推断
- `years`：工作年限，可从简历或用户输入推断

### 2. 读取简历

先读取 PDF 简历文本。优先使用系统已有的 PDF 文本提取工具；如果失败，再尝试 Python PDF 库。

需要提取：

- 候选人姓名
- 学历和专业
- 工作年限
- 工作经历列表
- 核心技能
- 主要项目和量化成果
- 可用于 STAR 案例的 3-5 个真实成就

如果简历读取失败，不要继续生成完整材料；先请用户提供可读取的 PDF、Word 或纯文本简历。

### 3. 公司和 JD 分析

分析内容包括：

- 公司简介、核心产品、业务模式、融资或上市情况
- 最近动态、行业趋势、主要竞争对手
- JD 中的硬性要求、软性要求、加分项
- 职位的真实诉求和可能面试重点
- 候选人与职位之间的优势和风险点

详细方法可按需参考：

- `references/company_research_guide.md`
- `references/jd_analysis_framework.md`
- `references/resume_jd_mapping.md`

### 4. 生成面试准备包

将结果写入 `companies/[公司名]/`。如果目录不存在，先创建目录。

可使用 `assets/` 下的模板控制输出结构：

- `assets/company_intel_brief_template.md`
- `assets/interview_prep_report_template.md`
- `assets/star_rewrite_template.md`
- `assets/interview_round_notes_template.md`
- `assets/resume_changelog_template.md`

也可以使用统一脚本生成基础框架：

```bash
python3 interview-intel/scripts/all_in_one_v6.1.py \
  --base-path . \
  --company "公司名" \
  --role "职位名" \
  --jd-content "JD 内容" \
  --resume-version "简历文件名或版本" \
  --years 5
```

脚本主要用于生成标准文件框架。最终内容仍应结合真实简历、公司调研和 JD 分析补全。

### 5. 交叉验证

生成后检查：

- 5 个文件中的候选人信息是否一致。
- 学历、公司、职位、项目是否与原始简历一致。
- 是否出现简历里没有的经历、数字或公司名。
- 输出目录是否为 `companies/[公司名]/`。

发现不一致时，使用简历原文和用户输入覆盖错误内容。

## 最佳实践

- 先读 `05_final_analysis_report.md`，把握整体策略。
- 再读 `01_company_intel_brief.md` 和 `02_resume_jd_matching.md`，明确公司诉求与自身匹配。
- 面试前重点背诵 `03_interview_prep_report.md` 里的关键问题和 STAR 案例。
- 投递或联系招聘方时使用 `04_icebreaker_messages.md`。

## 文件夹约定

```text
.
├── .claude/commands/jobprep.md
├── resumes/
├── companies/
└── interview-intel/
    ├── SKILL.md
    ├── scripts/all_in_one_v6.1.py
    ├── assets/
    └── references/
```

## 依赖

- Python 3.8+
- 读取 PDF 时可能需要 `pdfplumber`、`PyMuPDF` 或系统 `pdftotext`

缺少依赖时，可以先尝试安装：

```bash
python3 -m pip install pdfplumber --user
```
