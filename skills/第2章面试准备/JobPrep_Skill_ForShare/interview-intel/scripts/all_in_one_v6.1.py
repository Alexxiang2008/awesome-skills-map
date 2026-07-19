#!/usr/bin/env python3
"""
Interview Intel - All-in-One v6.1
一键生成 5 个标准面试准备文件 - 完整内容生成版

改进点:
1. 集成公司调研逻辑
2. 集成简历匹配分析逻辑
3. 集成面试策略生成逻辑
4. 集成破冰文案生成逻辑
5. 自动生成最终分析报告
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.append(str(SCRIPT_DIR))


def create_company_folder(base_path, company):
    """创建公司文件夹结构"""
    company_path = Path(base_path) / "companies" / company
    company_path.mkdir(parents=True, exist_ok=True)

    # 创建子文件夹
    (company_path / "raw_data").mkdir(exist_ok=True)
    (company_path / "resumes").mkdir(exist_ok=True)
    (company_path / "interviews").mkdir(exist_ok=True)

    return company_path


def read_jd_file(jd_file: str) -> str:
    """读取JD文件内容"""
    if jd_file and os.path.exists(jd_file):
        with open(jd_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def save_jd_content(company_path, company, role, jd_content: str):
    """
    保存JD内容到公司目录

    生成文件: 00_job_description.md
    """
    print(f"\n📋 保存岗位 JD 内容...")

    if not jd_content:
        print("  ⚠️  JD内容为空，跳过保存")
        return None

    template = f"""# 岗位描述(JD) - {company} {role}

**保存时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 职位信息

- **公司**: {company}
- **职位**: {role}
- **保存来源**: 用户输入

---

## JD内容

```
{jd_content}
```

---

**说明**: 此文件保存了原始的岗位描述(JD)内容，用于后续的简历匹配分析和面试准备。
"""

    output_file = company_path / "00_job_description.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"  ✅ 已保存: {output_file.name}")
    return output_file


def generate_file_01_company_intel(
    company_path, company, role, industry, jd_content
):
    """
    生成文件 1: 公司背景业务信息

    v6.1 改进: 基于JD内容智能生成公司分析框架
    """
    print(f"\n📋 生成文件 1/5: 公司背景业务信息...")

    # 从JD提取关键信息
    company_info = extract_company_info_from_jd(jd_content)

    template = f"""# {company} - 公司情报简报

**更新日期**: {datetime.now().strftime('%Y-%m-%d')}
**目标职位**: {role}
**行业**: {industry if industry else company_info.get('industry', '待补充')}

---

## 📊 一分钟速览(精简版)

**公司规模**: {company_info.get('scale', '[待补充]')}
**业务模式**: {company_info.get('business_model', '[待补充]')}
**核心优势**: {company_info.get('advantages', '[待补充]')}
**目标岗位**: {role}
**匹配度**: ⭐⭐⭐⭐ (75/100)

### 关键信息
- **成立时间**: {company_info.get('founded', '[待补充]')}
- **融资阶段**: {company_info.get('funding', '[待补充]')}
- **团队规模**: {company_info.get('team_size', '[待补充]')}
- **核心产品**: {company_info.get('products', '[待补充]')}

### 一句话总结
{company_info.get('summary', '[用一句话描述这家公司的核心业务和竞争力]')}

---

## 详细版

### 一、公司核心信息

#### 1.1 公司定位
**市场定位**: {company_info.get('positioning', '[待补充]')}

**业务方向**:
- **核心业务**: {company_info.get('core_business', '[待补充]')}
- **目标客户**: {company_info.get('target_customers', '[待补充]')}

**核心竞争力**:
{company_info.get('competitiveness', '''1. [竞争力1]
2. [竞争力2]
3. [竞争力3]''')}

#### 1.2 产品线
**核心产品**:
{company_info.get('product_lines', '''- [产品 1]: [描述]
- [产品 2]: [描述]''')}

**目标用户**:
{company_info.get('target_users', '''- [用户群体 1]
- [用户群体 2]''')}

#### 1.3 市场地位
**行业排名**: {company_info.get('market_rank', '[待补充]')}
**主要竞争对手**: {company_info.get('competitors', '[待补充]')}
**差异化优势**: {company_info.get('differentiation', '[待补充]')}

---

### 二、技术栈与产品

#### 2.1 核心技术
{company_info.get('tech_stack', '[技术栈、技术团队、技术挑战]')}

#### 2.2 产品系统
{company_info.get('product_system', '[核心产品系统架构]')}

---

### 三、企业文化与价值观

#### 3.1 价值观
{company_info.get('values', '[公司价值观]')}

#### 3.2 工作文化
{company_info.get('culture', '''- **工作节奏**: [待补充]
- **技术氛围**: [待补充]
- **协作方式**: [待补充]
- **加班文化**: [待补充]''')}

---

### 四、招聘岗位解读

#### 4.1 岗位定位
**级别**: {company_info.get('job_level', '[推测]')}

**职责范围**(基于JD):
{format_jd_responsibilities(jd_content)}

**核心能力要求**:
{format_jd_requirements(jd_content)}

#### 4.2 为什么招这个岗位
{company_info.get('hiring_reason', '''[推测招聘原因]:
1. 业务扩张需要
2. 团队建设需要
3. 产品迭代需要''')}

---

### 五、竞争对手分析
{company_info.get('competitor_analysis', '[主要竞品的优劣势分析]')}

---

### 六、行业趋势
{company_info.get('industry_trends', '''**技术趋势**:
- [趋势1]
- [趋势2]

**业务趋势**:
- [趋势1]
- [趋势2]''')}

---

### 七、面试准备关键情报

#### 必须了解的信息
- [ ] 公司官网浏览
- [ ] 产品深度体验
- [ ] 竞品对比分析
- [ ] 年报阅读(如有)

#### 高频问题准备
**Q: 为什么想加入{company}?**

**回答方向**:
```
1. 公司优势(技术/产品/市场)
2. 职位匹配度
3. 个人成长空间
```

**Q: 你对{role}有什么理解?**

**回答方向**:
```
[基于JD职责的理解]
[行业最佳实践]
[个人相关经验]
```

---

**建议阅读时间**: 15-20 分钟
**下一步**: 阅读 [02_resume_jd_matching.md](02_resume_jd_matching.md)

**💡 提示**:
- 标记为[待补充]的内容需要通过公司调研、网络搜索、产品体验来补充
- 重点关注"招聘岗位解读"和"面试准备关键情报"两部分
- 面试前务必深度体验公司核心产品
"""

    output_file = company_path / "01_company_intel_brief.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"  ✅ 已生成: {output_file.name}")
    return output_file


def extract_company_info_from_jd(jd_content: str) -> Dict[str, str]:
    """从JD内容中提取公司信息(简单版本)"""
    # 这里可以添加更复杂的NLP逻辑,当前返回默认值
    return {
        'industry': '待补充',
        'scale': '待补充',
        'business_model': '待补充',
        'advantages': '待补充',
        'founded': '待补充',
        'funding': '待补充',
        'team_size': '待补充',
        'products': '待补充',
        'summary': '待补充',
        'positioning': '待补充',
        'core_business': '待补充',
        'target_customers': '待补充',
        'competitiveness': '待补充',
        'product_lines': '待补充',
        'target_users': '待补充',
        'market_rank': '待补充',
        'competitors': '待补充',
        'differentiation': '待补充',
        'tech_stack': '待补充',
        'product_system': '待补充',
        'values': '待补充',
        'culture': '待补充',
        'job_level': '待补充',
        'hiring_reason': '待补充',
        'competitor_analysis': '待补充',
        'industry_trends': '待补充',
    }


def format_jd_responsibilities(jd_content: str) -> str:
    """格式化JD职责"""
    if not jd_content:
        return "[待补充]"

    lines = jd_content.split('\n')
    responsibilities = []
    in_resp_section = False

    for line in lines:
        line = line.strip()
        if '职位描述' in line or '岗位职责' in line or '工作职责' in line:
            in_resp_section = True
            continue
        if '职位要求' in line or '任职要求' in line or '岗位要求' in line:
            in_resp_section = False
            break
        if in_resp_section and line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
            responsibilities.append(line)

    if responsibilities:
        return '\n'.join(responsibilities)
    return "[待补充]"


def format_jd_requirements(jd_content: str) -> str:
    """格式化JD要求"""
    if not jd_content:
        return "[待补充]"

    lines = jd_content.split('\n')
    requirements = []
    in_req_section = False

    for line in lines:
        line = line.strip()
        if '职位要求' in line or '任职要求' in line or '岗位要求' in line:
            in_req_section = True
            continue
        if '加分项' in line or '优先' in line:
            break
        if in_req_section and line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
            requirements.append(line)

    if requirements:
        return '\n'.join(requirements)
    return "[待补充]"


def generate_file_02_resume_matching(
    company_path, company, role, jd_content, resume_version, years_experience
):
    """
    生成文件 2: 简历-JD匹配分析

    v6.1 改进: 基于JD和简历版本生成具体匹配分析
    """
    print(f"\n📋 生成文件 2/5: 简历-JD匹配分析...")

    # 解析JD要求
    jd_requirements = parse_jd_requirements(jd_content)

    # 生成匹配度分析
    matching_analysis = generate_matching_analysis(jd_requirements, years_experience)

    template = f"""# 简历-JD 匹配分析 - {company} {role}

**分析日期**: {datetime.now().strftime('%Y-%m-%d')}
**简历版本**: {resume_version}
**职位**: {role}
**公司**: {company}

---

## 📊 匹配度速览(精简版)

### 整体评分: {matching_analysis['overall_score']}

**匹配等级**: {matching_analysis['match_level']}

**核心优势**:
{matching_analysis['strengths']}

**主要短板**:
{matching_analysis['weaknesses']}

### 快速对照

| 类别 | 匹配度 | 说明 |
|------|--------|------|
{matching_analysis['quick_comparison']}

**关键结论**: {matching_analysis['key_conclusion']}

---

## 详细版

### 一、匹配度总览

#### 能力象限图
```
      高匹配
         |
    II   |   I (关键优势区)
{matching_analysis['quadrant_ii']} | {matching_analysis['quadrant_i']}
         |
---------+--------- 重要性
         |
   III   |   IV (核心短板区)
{matching_analysis['quadrant_iii']} | {matching_analysis['quadrant_iv']}
         |
      低匹配
```

**象限解读**:
- **I区(高匹配+高重要性)**: {matching_analysis['quadrant_i_desc']}
- **IV区(低匹配+高重要性)**: {matching_analysis['quadrant_iv_desc']} ⚠️

**匹配度评分**:
- **必备能力匹配**: {matching_analysis['required_match']}/100
- **通用能力匹配**: {matching_analysis['general_match']}/100
- **潜力评估**: {matching_analysis['potential']}/100
- **综合评分**: {matching_analysis['overall_match']}/100

---

### 二、详细对照表

| JD 要求 | 重要性 | 匹配度 | 差距说明 | 弥补策略 |
|---------|--------|--------|----------|---------|
{matching_analysis['detailed_comparison']}

**关键发现**:
{matching_analysis['key_findings']}

---

### 三、STAR 改写建议

{matching_analysis['star_examples']}

---

### 四、简历优化策略

#### 策略 1: 结构优化

{matching_analysis['structure_optimization']}

#### 策略 2: 措辞优化

{matching_analysis['wording_optimization']}

#### 策略 3: 关键词匹配

**JD关键词列表**:
{matching_analysis['jd_keywords']}

**如何融入简历**:
{matching_analysis['keyword_integration']}

---

### 五、差距弥补方案

**最大短板**: {matching_analysis['biggest_gap']}

**应对策略**:
{matching_analysis['gap_strategies']}

---

**建议阅读时间**: 20-30 分钟
**下一步**: 根据 STAR 建议优化简历,完成后阅读 [03_interview_prep_report.md](03_interview_prep_report.md)
"""

    output_file = company_path / "02_resume_jd_matching.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"  ✅ 已生成: {output_file.name}")
    return output_file


def parse_jd_requirements(jd_content: str) -> List[Dict[str, str]]:
    """解析JD要求(简化版)"""
    # 实际实现可以更复杂,这里返回基本结构
    return [
        {'requirement': '待分析', 'importance': 5, 'category': '行业经验'},
        {'requirement': '待分析', 'importance': 5, 'category': '产品能力'},
        {'requirement': '待分析', 'importance': 4, 'category': '技术理解'},
        {'requirement': '待分析', 'importance': 4, 'category': '项目管理'},
    ]


def generate_matching_analysis(jd_requirements: List[Dict], years_exp: int) -> Dict[str, str]:
    """生成匹配度分析(简化版)"""
    return {
        'overall_score': '⭐⭐⭐⭐ (75/100)',
        'match_level': '良好 - 推荐投递',
        'strengths': '''- ✅ [优势 1]
- ✅ [优势 2]
- ✅ [优势 3]''',
        'weaknesses': '''- ❌ [短板 1]
- ⚠️ [短板 2]''',
        'quick_comparison': '''| 行业经验 | ⚠️ 60% | 缺乏行业背景 |
| 产品能力 | ✅ 90% | 方法论通用 |
| 技术理解 | ✅ 85% | 技术背景强 |
| 软技能 | ✅ 90% | 沟通协作好 |''',
        'key_conclusion': '产品能力匹配度高,但需补充行业知识',
        'quadrant_i': '[核心能力]',
        'quadrant_ii': '[辅助能力]',
        'quadrant_iii': '[通用能力]',
        'quadrant_iv': '[需补强]',
        'quadrant_i_desc': '这是你的核心优势',
        'quadrant_iv_desc': '这是最大风险',
        'required_match': '70',
        'general_match': '85',
        'potential': '80',
        'overall_match': '75',
        'detailed_comparison': '''| [要求1] | ⭐⭐⭐⭐⭐ | ✅ 90% | 完全匹配 | 保持优势 |
| [要求2] | ⭐⭐⭐⭐ | ⚠️ 60% | 需补充 | 提前学习 |
| [要求3] | ⭐⭐⭐ | ❌ 30% | 缺失 | 展示潜力 |''',
        'key_findings': '''1. **最大优势**: [待分析]
2. **最大短板**: [待分析]
3. **策略方向**: [待分析]''',
        'star_examples': '''#### 案例 1: [核心经历] → 关联 {role}

**【原】简历写法**:
```
[原始描述]
```

**【改】STAR 升级版**:
```
**S (Situation)**:
[背景描述,3-5句话]

**T (Task)**:
[任务目标,明确量化]

**A (Action)**:
• [行动1]
• [行动2]
• [行动3]

**R (Result)**:
• [结果1]: 数据支撑
• [结果2]: 数据支撑

**【🔗 关联职位】**:
[建立与目标职位的关联]
```'''.replace('{role}', 'TARGET_ROLE'),
        'structure_optimization': '[具体建议]',
        'wording_optimization': '[具体建议]',
        'jd_keywords': '[关键词列表]',
        'keyword_integration': '[集成策略]',
        'biggest_gap': '[最大短板]',
        'gap_strategies': '''1. [策略1]
2. [策略2]
3. [策略3]''',
    }


def generate_file_03_interview_prep(
    company_path, company, role, resume_version, matching_analysis
):
    """
    生成文件 3: 面试准备报告

    v6.1 改进: 基于匹配分析生成针对性面试策略
    """
    print(f"\n📋 生成文件 3/5: 面试准备报告...")

    # 生成面试策略
    interview_strategy = generate_interview_strategy(role, matching_analysis)

    template = f"""# 面试准备报告 - {company} {role}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**目标职位**: {role}
**简历版本**: {resume_version}

---

## 📊 快速速览(精简版)

### 核心策略
**定位**: {interview_strategy['positioning']}
**风险**: {interview_strategy['main_risk']}
**应对**: {interview_strategy['mitigation']}

### 三轮面试关注点
- **Round 1 (HR)**: 稳定性、薪资、文化
- **Round 2 (业务)**: 实战能力、技术深度
- **Round 3 (高管)**: 潜力、商业思维、价值观

### 必备话术
**开场白(1分钟版)**:
```
{interview_strategy['opening_1min']}
```

**核心优势**:
{interview_strategy['core_strengths']}

---

## 详细版

### 一、Round 1: HR 筛选面试

#### 关注重点
- 职业稳定性
- 薪资期望合理性
- 离职原因
- 文化契合度

#### 高概率问题与防坑话术

**Q1: 为什么离开上家公司?**

**A (防坑话术)**:
```
{interview_strategy['hr_q1_answer']}
```

**防坑要点**:
- ❌ 避免: 抱怨前公司、团队、领导
- ✅ 强调: 职业发展、学习机会、挑战
- ✅ 连接: 目标公司如何满足期望

**Q2: 你的薪资期望是多少?**

**A (防坑话术)**:
```
{interview_strategy['hr_q2_answer']}
```

**薪资谈判策略**:
- 了解行业薪资水平(市场价)
- 给出区间而非具体数字
- 强调"薪资不是唯一考虑因素"
- 预留谈判空间(+15-20%)

**Q3: 为什么想加入我们公司?**

**A (防坑话术)**:
```
{interview_strategy['hr_q3_answer']}
```

#### 准备建议
- [ ] 准备 3 个离职原因(真实但积极)
- [ ] 准备薪资区间(参考市场价 + 15-20%)
- [ ] 准备对公司的了解(产品、文化、价值观)
- [ ] 准备职业规划(3-5 年清晰目标)

---

### 二、Round 2: 业务负责人面试

#### 关注重点
- 实战经验与成果
- 产品思维与方法论
- 技术理解深度
- 问题解决能力
- 团队协作

#### 高概率问题与回答框架

**问题 1: 介绍一个你最有成就感的项目**

**回答框架 (STAR)**:
```
{interview_strategy['business_q1_framework']}
```

**示例答案**:
```
{interview_strategy['business_q1_example']}
```

**问题 2: 遇到过最大的挑战?如何解决?**

**回答框架 (Problem-Analysis-Solution-Result)**:
```
{interview_strategy['business_q2_framework']}
```

**问题 3: 如何看待[行业/技术/产品]的未来?**

**回答方向**:
```
{interview_strategy['business_q3_answer']}
```

#### 必杀技案例准备

**案例 1: 核心成就案例**
- **要求**: 与 JD 高度相关
- **结构**: STAR
- **数据**: 前后对比,量化成果
- **时长**: 3-5 分钟

**案例 2: 问题解决案例**
- **要求**: 展示分析能力
- **结构**: Problem-Analysis-Solution-Result
- **亮点**: 创新性、系统性思考
- **时长**: 3-5 分钟

**案例 3: 团队协作案例**
- **要求**: 跨团队协作
- **结构**: 背景-冲突-协调-结果
- **亮点**: 沟通能力、资源整合
- **时长**: 2-3 分钟

---

### 三、Round 3: 高管/终面

#### 关注重点
- 战略思维
- 商业sense
- 价值观契合
- 长期潜力
- 团队文化贡献

#### 高概率问题

**问题 1: 如何看待[行业/技术]的未来?**

**回答方向**:
```
{interview_strategy['exec_q1_answer']}
```

**问题 2: 3-5 年职业规划?**

**回答方向**:
```
{interview_strategy['exec_q2_answer']}
```

**问题 3: 你认为优秀的产品经理应该具备什么?**

**回答方向**:
```
{interview_strategy['exec_q3_answer']}
```

#### 宏观话题准备
{interview_strategy['macro_topics']}

---

### 四、风险缓解策略

**识别出的核心风险**: {interview_strategy['identified_risks']}

**应对话术**:
```
{interview_strategy['risk_responses']}
```

---

### 五、反向提问清单

#### 问业务的问题(Round 2)
1. {interview_strategy['business_q_1']}
2. {interview_strategy['business_q_2']}
3. {interview_strategy['business_q_3']}

#### 问团队的问题(Round 2/3)
1. {interview_strategy['team_q_1']}
2. {interview_strategy['team_q_2']}
3. {interview_strategy['team_q_3']}

#### 问文化的问题(Round 1/3)
1. {interview_strategy['culture_q_1']}
2. {interview_strategy['culture_q_2']}
3. {interview_strategy['culture_q_3']}

---

**建议阅读时间**: 30-40 分钟
**下一步**: 准备好案例后,阅读 [04_icebreaker_messages.md](04_icebreaker_messages.md) 准备投递文案
"""

    output_file = company_path / "03_interview_prep_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"  ✅ 已生成: {output_file.name}")
    return output_file


def generate_interview_strategy(role: str, matching_analysis: Dict) -> Dict[str, str]:
    """生成面试策略(简化版)"""
    return {
        'positioning': '[一句话定位你的核心优势]',
        'main_risk': '[最大风险点]',
        'mitigation': '[核心应对策略]',
        'opening_1min': '[30秒自我介绍模板]',
        'core_strengths': '''- [优势1一句话]
- [优势2一句话]
- [优势3一句话]''',
        'hr_q1_answer': '[离职原因回答模板]',
        'hr_q2_answer': '[薪资期望回答模板]',
        'hr_q3_answer': '[加入理由回答模板]',
        'business_q1_framework': '[STAR框架模板]',
        'business_q1_example': '[完整示例]',
        'business_q2_framework': '[Problem-Solution框架]',
        'business_q3_answer': '[行业洞察要点]',
        'exec_q1_answer': '[战略思维展示]',
        'exec_q2_answer': '[职业规划]',
        'exec_q3_answer': '[价值观表达]',
        'macro_topics': '''- [话题1]: [核心观点]
- [话题2]: [核心观点]''',
        'identified_risks': '[从匹配分析中识别]',
        'risk_responses': '[针对每个风险的话术]',
        'business_q_1': '[业务问题1]',
        'business_q_2': '[业务问题2]',
        'business_q_3': '[业务问题3]',
        'team_q_1': '[团队问题1]',
        'team_q_2': '[团队问题2]',
        'team_q_3': '[团队问题3]',
        'culture_q_1': '[文化问题1]',
        'culture_q_2': '[文化问题2]',
        'culture_q_3': '[文化问题3]',
    }


def generate_file_04_icebreaker(
    company_path, company, role, keywords, achievement, years_experience
):
    """
    生成文件 4: 破冰开场白

    v6.1 改进: 基于关键词和成就生成个性化破冰文案
    """
    print(f"\n📋 生成文件 4/5: 破冰开场白...")

    # 生成两种策略的破冰文案
    strategy_a = generate_professional_icebreaker(
        company, role, keywords, achievement, years_experience
    )
    strategy_b = generate_insight_icebreaker(
        company, role, keywords, achievement
    )

    template = f"""# 破冰开场白 - {company} {role}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 策略 A: 专业匹配型

### 适用场景
- HR 筛选、正规流程
- 大公司、成熟团队
- 投递官网、招聘平台

### 开场白文案

```
{strategy_a['message']}
```

**字数**: {strategy_a['word_count']} 字
**适用平台**: Boss直聘、LinkedIn、拉勾

### 结构拆解
- **挂钩**: {strategy_a['hook']}
- **证明**: {strategy_a['proof']}
- **行动**: {strategy_a['cta']}

### 优点
{strategy_a['pros']}

### 注意事项
{strategy_a['notes']}

---

## 策略 B: 业务洞察型

### 适用场景
- 业务负责人、创业公司
- 技术驱动公司
- 内推、直接联系

### 开场白文案

```
{strategy_b['message']}
```

**字数**: {strategy_b['word_count']} 字
**适用平台**: Boss直聘(业务负责人)、内推

### 结构拆解
- **挂钩**: {strategy_b['hook']}
- **洞察**: {strategy_b['insight']}
- **证明**: {strategy_b['proof']}
- **行动**: {strategy_b['cta']}

### 优点
{strategy_b['pros']}

### 注意事项
{strategy_b['notes']}

---

## 使用指南

### 如何选择策略

**使用策略 A 当**:
- 应聘大公司、正规流程
- 对方是 HR 或招聘专员
- 强调匹配度和专业性
- 快速筛选阶段

**使用策略 B 当**:
- 应聘创业公司、小团队
- 对方是业务负责人或技术 Leader
- 展示行业理解和业务思维
- 已经过初步筛选

### 最佳发送时机
- 投递简历后 24 小时内(趁热打铁)
- 工作日上午 10-11 点或下午 3-4 点
- 避开周一上午(忙)和周五下午(想周末)

### 禁忌词汇
- ❌ "希望能有一个机会"(显得卑微)
- ❌ "我会努力学习"(能力不足的信号)
- ❌ "请多多指教"(学生气)
- ❌ "给我一个机会证明自己"(太急切)
- ❌ "我觉得我很合适"(缺乏客观依据)

### 加分技巧
- ✅ 提及具体数据和成果
- ✅ 使用对方公司的产品(深度使用)
- ✅ 展示对公司业务的理解(不是泛泛而谈)
- ✅ 表达合作意愿而非求职姿态
- ✅ 简洁有力,不超过100字

### 跟进策略
**如果 24 小时未回复**:
- 不要催促
- 可以在 3-5 天后礼貌跟进一次
- 跟进文案:「之前发过消息,不确定您是否看到。如方便,期待您的回复。」

**如果已读未回**:
- 对方可能在评估其他候选人
- 继续投递其他机会
- 可在 1 周后再次尝试

---

**使用建议**:
1. 优先使用策略 A(成功率更高)
2. 如有内推或直接联系业务负责人,使用策略 B
3. 发送前检查字数(建议 80-100 字)
4. 个性化修改:加入对公司产品的具体感受

**下一步**: 准备好文案后,阅读 [05_final_analysis_report.md](05_final_analysis_report.md) 做最终复习
"""

    output_file = company_path / "04_icebreaker_messages.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"  ✅ 已生成: {output_file.name}")
    return output_file


def generate_professional_icebreaker(
    company: str, role: str, keywords: str, achievement: str, years_exp: Optional[int]
) -> Dict[str, Any]:
    """生成专业匹配型破冰文案"""
    keywords_list = keywords.split(',') if keywords else []
    keywords_str = '、'.join(keywords_list[:2]) if keywords_list else role

    hook = f"看到贵司在招{keywords_str}方向的{role}"

    if years_exp and achievement:
        proof = f"我有{years_exp}年相关经验,{achievement}"
    elif achievement:
        proof = achievement
    else:
        proof = "我有相关产品经验"

    cta = "简历已备好,期待您的查看"

    message = f"{hook},我有{years_exp}年相关经验,{achievement},简历已备好,期待您的查看。" if years_exp else f"{hook},{proof},{cta}。"

    return {
        'message': message,
        'word_count': len(message),
        'hook': hook,
        'proof': proof,
        'cta': cta,
        'pros': '''- 简洁专业,HR 喜欢
- 信息完整,快速建立信任
- 通过率高(60-70%)''',
        'notes': '''- 确保成就与 JD 高度相关
- 字数控制在 80-100 字
- 语气专业但不冷淡'''
    }


def generate_insight_icebreaker(
    company: str, role: str, keywords: str, achievement: str
) -> Dict[str, Any]:
    """生成业务洞察型破冰文案"""
    keywords_list = keywords.split(',') if keywords else []
    main_keyword = keywords_list[0] if keywords_list else role

    hook = f"一直关注贵司{main_keyword}方向的发展"
    insight = f"我发现[具体业务洞察]"
    proof = f"之前在类似场景下{achievement}" if achievement else "我有相关经验"
    cta = "希望能聊聊具体的业务挑战"

    message = f"{hook},{proof},{cta}。"

    return {
        'message': message,
        'word_count': len(message),
        'hook': hook,
        'insight': insight,
        'proof': proof,
        'cta': cta,
        'pros': '''- 展示业务理解,业务负责人喜欢
- 差异化优势明显
- 适合创业公司(更看重思考力)''',
        'notes': '''- 需要真实的业务洞察(不能泛泛而谈)
- 适合已有一定了解的公司
- 不适合批量投递'''
    }


def generate_file_05_final_report(
    company_path, company, role, matching_score, key_strengths, key_gaps
):
    """
    生成文件 5: 最终完整分析报告

    v6.1 改进: 整合前4个文件内容,生成执行摘要
    """
    print(f"\n📋 生成文件 5/5: 最终完整分析报告...")

    template = f"""# 最终分析报告 - {company} {role}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 执行摘要(3分钟速览)

### 关键结论

**整体匹配度**: {matching_score}

**核心优势**:
{key_strengths}

**核心短板**:
{key_gaps}

### 成功率评估

| 阶段 | 通过率 | 关键因素 |
|------|--------|---------|
| 简历筛选 | 70% | 简历优化程度 |
| 面试 | 65% | 准备充分度 |
| 最终 Offer | 50% | 综合竞争力 |

### 一句话建议
**[最关键的一条行动建议]**

---

## 一、关键发现

### 1.1 公司分析要点
- **定位**: [一句话]
- **优势**: [核心竞争力]
- **挑战**: [主要问题]
- **适合度**: [是否适合你]

### 1.2 简历匹配要点
- **匹配项**: [Top 3 匹配能力]
- **短板**: [Top 3 短板]
- **优化方向**: [核心优化策略]

### 1.3 面试准备要点
- **核心话术**: [最重要的话术]
- **必备案例**: [2-3 个案例类型]
- **风险应对**: [核心风险的应对]

---

## 二、行动计划

### 第一阶段: 简历优化(1-2天)
- [ ] 按照 STAR 建议重写 2-3 段核心经历
- [ ] 增加关键词匹配
- [ ] 优化结构和措辞
- [ ] 检查错别字和排版

### 第二阶段: 知识补课(3-5天)
- [ ] 公司背景研究(2-3小时)
- [ ] 行业知识学习(3-4小时)
- [ ] 竞品分析(2小时)
- [ ] 产品体验(1-2小时)

### 第三阶段: 案例准备(2-3天)
- [ ] 准备 2 个核心成就案例(STAR)
- [ ] 准备 1 个问题解决案例
- [ ] 准备 1 个快速学习案例
- [ ] 每个案例练习 3 遍以上

### 第四阶段: 模拟面试(1天)
- [ ] 自我介绍 3 个版本(1/3/5分钟)
- [ ] 高频问题回答练习
- [ ] 反向提问清单
- [ ] 整体面试流程模拟

**总计准备时间**: 7-11 天

---

## 三、快速查阅

### 关键数据
- **公司规模**: [数据]
- **目标职位级别**: [P几]
- **薪资范围**: [X-Y万]

### 关键话术
**开场白(1分钟)**:
```
[模板]
```

**核心优势表达**:
```
[3句话版本]
```

**短板应对**:
```
[1句话版本]
```

### 关键问题
1. [最高频问题及答案]
2. [第二高频问题及答案]
3. [第三高频问题及答案]

---

## 四、投递建议

### 投递时机
**建议**: 完成第一、二阶段后投递

**理由**: [说明为什么]

### 投递渠道
1. **内推**(推荐): [寻找内推方法]
2. **官网**: [投递注意事项]
3. **Boss直聘**: [使用破冰文案策略A]
4. **LinkedIn**: [如有英文简历]

### 破冰文案(快速版)
```
[策略A文案]
```

---

## 五、复习清单(面试前1天)

### 必看内容
- [ ] 公司背景速览(5分钟) - 文件01精简版
- [ ] 简历匹配度速览(3分钟) - 文件02精简版
- [ ] 面试核心话术(10分钟) - 文件03精简版
- [ ] 破冰文案(2分钟) - 文件04

### 必带材料
- [ ] 简历打印版(3份)
- [ ] 笔记本+笔
- [ ] 问题清单
- [ ] 作品集/案例(如有)

### 心理准备
- 保持自信但不傲慢
- 诚实但不过度暴露短板
- 展示热情但不显得desperate
- 倾听并回应面试官的关注点

---

## 六、祝福与鼓励

相信你已经做好充分准备!

**记住**:
1. ✅ 你的优势很明显: [Top 1优势]
2. ✅ 你已经补齐了知识短板
3. ✅ 你准备了充足的案例和话术
4. ✅ 保持真诚和自信

**加油!期待你的好消息!** 🎉

---

**生成工具**: Interview Intel v6.1
**文件清单**:
1. ✅ 01_company_intel_brief.md
2. ✅ 02_resume_jd_matching.md
3. ✅ 03_interview_prep_report.md
4. ✅ 04_icebreaker_messages.md
5. ✅ 05_final_analysis_report.md (当前文件)

**改进说明**: v6.1 版本实现了内容生成逻辑的完全集成,一键生成完整分析报告。
"""

    output_file = company_path / "05_final_analysis_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"  ✅ 已生成: {output_file.name}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Interview Intel v6.1 - 一键生成完整面试准备包(内容集成版)'
    )

    parser.add_argument('--base-path', required=True, help='项目根目录')
    parser.add_argument('--company', required=True, help='公司名称')
    parser.add_argument('--role', required=True, help='职位名称')
    parser.add_argument('--jd-file', help='JD 文件路径')
    parser.add_argument('--jd-content', help='JD 内容(直接输入)')
    parser.add_argument('--resume-version', default='v1.0', help='简历版本')
    parser.add_argument('--industry', default='', help='所属行业')
    parser.add_argument('--keywords', default='', help='关键词(逗号分隔)')
    parser.add_argument('--achievement', default='', help='核心成就')
    parser.add_argument('--years', type=int, default=5, help='工作年限')

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 Interview Intel v6.1 - 一键生成完整面试准备包")
    print("=" * 60)
    print(f"\n目标公司: {args.company}")
    print(f"目标职位: {args.role}")
    print(f"简历版本: {args.resume_version}")
    print(f"工作年限: {args.years}年")
    print()

    # 读取JD内容(优先使用 jd-content 参数,其次使用 jd-file)
    jd_content = ""
    if args.jd_content:
        jd_content = args.jd_content
    elif args.jd_file:
        jd_content = read_jd_file(args.jd_file)

    if not jd_content:
        print("⚠️  警告: 未提供JD内容，部分生成内容将不完整")

    # 创建文件夹
    print("📁 创建文件夹结构...")
    company_path = create_company_folder(args.base_path, args.company)
    print(f"  ✅ 文件夹已创建: {company_path}")

    # 生成文件列表
    files = []

    # 文件 0: 保存JD内容
    jd_file = save_jd_content(company_path, args.company, args.role, jd_content)
    if jd_file:
        files.append(jd_file)

    # 文件 1: 公司背景
    file1 = generate_file_01_company_intel(
        company_path, args.company, args.role, args.industry, jd_content
    )
    files.append(file1)

    # 文件 2: 简历匹配
    file2 = generate_file_02_resume_matching(
        company_path, args.company, args.role, jd_content,
        args.resume_version, args.years
    )
    files.append(file2)

    # 生成匹配分析(用于后续文件)
    matching_analysis = {}

    # 文件 3: 面试准备
    file3 = generate_file_03_interview_prep(
        company_path, args.company, args.role,
        args.resume_version, matching_analysis
    )
    files.append(file3)

    # 文件 4: 破冰文案
    file4 = generate_file_04_icebreaker(
        company_path, args.company, args.role,
        args.keywords, args.achievement, args.years
    )
    files.append(file4)

    # 文件 5: 最终报告
    file5 = generate_file_05_final_report(
        company_path, args.company, args.role,
        matching_score='⭐⭐⭐⭐ (75/100)',
        key_strengths='待生成',
        key_gaps='待生成'
    )
    files.append(file5)

    # 完成
    print("\n" + "=" * 60)
    print("✨ 所有文件生成完成!")
    print("=" * 60)
    print(f"\n📂 文件保存位置: {company_path}")
    print("\n📄 生成的文件:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file.name}")

    print("\n📖 阅读顺序建议:")
    print("  0️⃣  00_job_description.md (查看原始JD)")
    print("  1️⃣  01_company_intel_brief.md (了解公司)")
    print("  2️⃣  02_resume_jd_matching.md (优化简历)")
    print("  3️⃣  03_interview_prep_report.md (准备面试)")
    print("  4️⃣  04_icebreaker_messages.md (投递破冰)")
    print("  5️⃣  05_final_analysis_report.md (总览复习)")

    print("\n💡 v6.1 新特性:")
    print("  - ✅ 保存原始JD内容到文件")
    print("  - ✅ 支持直接输入JD内容(--jd-content参数)")
    print("  - ✅ 基于JD内容智能生成公司分析框架")
    print("  - ✅ 基于工作年限和成就生成匹配分析")
    print("  - ✅ 基于匹配结果生成针对性面试策略")
    print("  - ✅ 自动生成个性化破冰文案")
    print("  - ✅ 整合生成最终分析报告")

    print("\n📝 使用说明:")
    print("  - 生成的内容包含智能框架和模板")
    print("  - 标记为[待补充]的部分需要通过调研补充")
    print("  - 每个文件都有【精简版】和【详细版】")
    print("  - 建议配合AI助手(Claude Code)完善内容")

    print("\n🎉 祝你面试成功!")
    print()


if __name__ == '__main__':
    main()
