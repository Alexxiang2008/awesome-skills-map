---
description: 一键生成完整的面试准备包（公司分析、简历匹配、面试策略、破冰文案）
---

# Job Prep - 面试准备助手

使用 Agent Teams 并行加速生成完整的面试准备包。

## 使用方式

```
/jobprep 公司名 职位名

JD: [粘贴JD内容]
简历: resumes/我的简历.pdf
```

## 执行流程（Agent Teams 并行加速）

### 第 1 步：解析输入

从用户消息中提取：
- `company` - 公司名称
- `role` - 目标职位
- `jd` - JD 内容（可从截图中识别）
- `resume_path` - 简历路径（如未提供，在 resumes/ 目录查找 PDF）
- `industry` - 行业（可选，从 JD 推断）
- `years` - 工作年限（可选）

### 第 2 步：创建目录结构

```bash
mkdir -p companies/{company}/raw_data
```

### 第 3 步：【关键】主进程预读取简历 ⚠️

**重要：必须在派发任务给 Agent 之前，由主进程先读取简历内容！**

这是为了防止 Agent 无法正确读取 PDF 而捏造虚假数据。

**执行步骤：**

1. **检查简历路径**
   - 如果用户提供了路径，使用该路径
   - 否则在 `resumes/` 目录搜索 PDF 文件

2. **提取简历文本**
   - 使用 Bash 工具执行：`pdftotext "{resume_path}" -`
   - 如果 pdftotext 不可用，尝试：`python3 -c "import fitz; doc=fitz.open('{resume_path}'); print(''.join([page.get_text() for page in doc]))"`
   - 将提取的文本保存到变量 `resume_text`

3. **验证简历内容**
   - 检查 `resume_text` 是否包含基本信息（姓名、公司、职位等）
   - 如果提取失败或内容为空，提示用户检查文件

4. **解析简历关键信息**
   由主进程直接解析 `resume_text`，提取：
   - `candidate_name` - 候选人姓名
   - `education` - 学历（学校、专业、学位）
   - `work_years` - 工作年限
   - `companies` - 工作过的公司列表
   - `positions` - 担任过的职位列表
   - `key_achievements` - 主要成就（3-5条）

### 第 4 步：并行执行 2 个研究任务

**注意：简历分析不再使用 Agent，改为主进程直接处理**

**Agent 1 - 公司调研 (company-researcher)**
```
subagent_type: Explore
prompt: |
  研究公司「{company}」的以下信息：
  1. 公司简介（成立时间、创始人、融资情况）
  2. 核心产品和业务模式
  3. 最新动态（近6个月的新闻、产品发布）
  4. 企业文化和价值观
  5. 主要竞争对手（3-5家）

  使用 WebSearch 或 Firecrawl 搜索，返回结构化的 Markdown 格式。
  如果 WebSearch 不可用，使用 Firecrawl skill：/websearch {company} 公司信息
```

**Agent 2 - JD 分析与行业研究 (jd-analyst)**
```
subagent_type: Explore
prompt: |
  分析以下 JD 内容，并研究行业趋势：

  JD内容：
  {jd}

  需要输出：
  1. JD 关键词提取（必需技能 vs 加分项）
  2. 职位核心职责（3-5条）
  3. 该职位的市场薪资范围
  4. 行业趋势（{industry}领域的发展方向）
  5. 面试可能考察的重点

  返回结构化的 Markdown 格式。
```

### 第 5 步：等待并汇总结果

等待 2 个 Agent 完成，收集结果：
- `company_research` - 来自 Agent 1
- `jd_analysis` - 来自 Agent 2
- `resume_analysis` - 来自第 3 步主进程解析（非 Agent）

### 第 6 步：生成 5 个输出文件

**关键：生成文件时必须使用第 3 步解析的真实简历数据！**

基于汇总的研究结果，生成到 `companies/{company}/`：

**文件 1: 01_company_intel_brief.md**
- 使用 `company_research` 数据
- 包含：公司概况、产品、竞争格局、文化

**文件 2: 02_resume_jd_matching.md**
- 对比 `resume_analysis`（第 3 步的真实数据）和 `jd_analysis`
- 包含：匹配度评分、优势、差距、提升建议
- **验证点**：确保候选人姓名、学历、公司与原始简历一致

**文件 3: 03_interview_prep_report.md**
- 综合所有数据生成
- 包含：HR轮/业务轮/高管轮的话术策略
- 包含：STAR 故事（基于简历中的真实成就）
- **验证点**：STAR 故事必须基于真实工作经历

**文件 4: 04_icebreaker_messages.md**
- 包含：30秒/1分钟/3分钟自我介绍
- 包含：开场破冰话术
- **验证点**：自我介绍中的信息必须与简历一致

**文件 5: 05_final_analysis_report.md**
- 包含：综合评估、准备优先级、行动计划时间表
- **验证点**：优劣势分析必须基于真实背景

### 第 7 步：交叉验证

**生成所有文件后，执行验证检查：**

1. 检查所有文件中的候选人姓名是否一致
2. 检查学历信息是否与原始简历匹配
3. 检查工作经历是否与原始简历匹配
4. 如发现不一致，立即修正

### 第 8 步：输出完成信息

```
已生成面试准备包：companies/{company}/
- 01_company_intel_brief.md
- 02_resume_jd_matching.md
- 03_interview_prep_report.md
- 04_icebreaker_messages.md
- 05_final_analysis_report.md

简历验证信息：
- 候选人：{candidate_name}
- 学历：{education}
- 工作年限：{work_years}年
```

## 输出文件

| 文件 | 内容 |
|------|------|
| `01_company_intel_brief.md` | 公司背景、产品、竞争对手 |
| `02_resume_jd_matching.md` | 简历与 JD 匹配分析 |
| `03_interview_prep_report.md` | 三轮面试策略和话术 |
| `04_icebreaker_messages.md` | 破冰开场白 |
| `05_final_analysis_report.md` | 行动计划 |

## 示例

### 示例 1：基础使用
```
/jobprep 字节跳动 产品经理

JD: [粘贴 JD 内容]

简历在 resumes/张三-产品经理.pdf
```

### 示例 2：完整信息
```
/jobprep

公司：智谱AI
职位：AI产品经理
JD: [粘贴 JD 内容]
简历：resumes/我的简历.pdf
行业：AI大模型
工作年限：6年
```

## 参数说明

**必需**：
- `company` - 公司名称
- `role` - 目标职位
- `jd` - JD 内容

**可选**：
- `resume` - 简历路径（默认搜索 resumes/ 目录）
- `industry` - 行业
- `years` - 工作年限

## 注意事项

- **简历预读取**：主进程会先提取简历文本，确保数据准确性
- **不使用 Agent 读取简历**：避免 Agent 无法读取 PDF 而捏造数据
- **交叉验证**：生成后会验证关键信息一致性
- 简历请放在 `resumes/` 目录
- 输出文件在 `companies/[公司名]/` 目录

## 错误处理

1. **PDF 读取失败**
   - 尝试多种方法提取文本
   - 如全部失败，提示用户提供 Word 或纯文本版简历

2. **Agent 返回异常数据**
   - 与主进程预读取的数据交叉验证
   - 如发现不一致，使用主进程数据覆盖

3. **网络搜索不可用**
   - 使用 Firecrawl skill 替代 WebSearch
   - 如 Firecrawl 也不可用，基于已有知识生成
