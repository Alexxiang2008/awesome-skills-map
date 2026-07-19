# JobPrep Skill

这是一个精简版面试准备 Skill。把简历、公司名、职位和 JD 提供给 Claude Code 后，它会生成一套完整面试准备包。

## 使用方式

1. 用 Claude Code 打开这个文件夹。
2. 把简历 PDF 放到 `resumes/` 目录。
3. 输入：

```text
/jobprep 公司名 职位名

JD: [粘贴职位描述]
简历: resumes/我的简历.pdf
```

生成结果会保存在 `companies/[公司名]/`。

## 输出内容

```text
companies/[公司名]/
├── 01_company_intel_brief.md
├── 02_resume_jd_matching.md
├── 03_interview_prep_report.md
├── 04_icebreaker_messages.md
└── 05_final_analysis_report.md
```

## 目录说明

```text
.claude/commands/jobprep.md        # Claude Code 斜杠命令入口
interview-intel/SKILL.md           # Skill 说明
interview-intel/scripts/           # 一键生成脚本
interview-intel/assets/            # 输出模板
interview-intel/references/        # 分析参考
resumes/                           # 放简历
companies/                         # 放生成结果
```

## 手动脚本入口

如果不使用 `/jobprep`，也可以运行：

```bash
python3 interview-intel/scripts/all_in_one_v6.1.py \
  --base-path . \
  --company "公司名" \
  --role "职位名" \
  --jd-content "JD 内容" \
  --resume-version "简历文件名" \
  --years 5
```

脚本会生成标准文件框架。为了得到更完整的内容，推荐使用 `/jobprep`。
