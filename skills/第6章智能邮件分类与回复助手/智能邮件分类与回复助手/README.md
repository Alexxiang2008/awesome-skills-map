# 智能邮件分类与回复助手

收件箱零焦虑 - 让 AI 帮你处理邮件

## 功能特性

- **邮件优先级分类**: 自动将邮件分为紧急/重要/可延后三个级别
- **智能回复生成**: 根据邮件内容生成多个版本的回复草稿
- **待办事项提取**: 自动识别邮件中的行动项和会议安排
- **多邮箱支持**: QQ邮箱、163邮箱、Gmail、Outlook 等
- **文件导入**: 支持 .eml 和 .mbox 格式

## 快速开始

### 在 Claude Code 中使用

```
/email-triage
```

或

```
/邮件分类
```

### 命令行使用

```bash
# 连接 QQ 邮箱
python main.py --email your@qq.com --auth-code xxxxxxxxxxxxxxxx --limit 10

# 解析 EML 文件
python main.py --file email.eml

# 解析 MBOX 文件
python main.py --file emails.mbox --limit 20

# 测试邮箱连接
python main.py --email your@qq.com --auth-code xxxxxxxx --test-connection
```

## 邮箱配置指南

### QQ 邮箱

1. 登录 QQ 邮箱网页版
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启 IMAP/SMTP 服务
4. 发送短信验证，获取 16 位授权码

### 163 邮箱

1. 登录 163 邮箱网页版
2. 设置 → POP3/SMTP/IMAP
3. 开启 IMAP/SMTP 服务
4. 设置客户端授权密码

### Gmail

1. 登录 Google 账户
2. 安全性 → 两步验证 → 应用专用密码
3. 生成应用专用密码

## 目录结构

```
email-triage/
├── skill.yaml          # Skill 配置
├── skill.md            # Skill 主逻辑
├── main.py             # 命令行入口
├── prompts/
│   ├── classify.md     # 分类 prompt
│   ├── reply.md        # 回复生成 prompt
│   └── extract_todos.md # 待办提取 prompt
└── lib/
    ├── __init__.py
    ├── email_client.py # 邮箱客户端
    ├── email_parser.py # 文件解析器
    ├── processor.py    # LLM 处理器
    └── report.py       # 报告生成器
```

## 输出示例

### 单封邮件

```
📧 邮件分析

主题: 项目验收问题 - 需今日回复
发件人: 张经理 <zhang@client.com>
优先级: 🔴 紧急

摘要: 客户对交付物有疑问，要求今天下班前回复

待办事项:
- [ ] 核实交付物问题 (截止: 今天 16:00)
- [ ] 准备问题说明文档

建议回复:
> 张经理您好，感谢您的反馈。关于您提到的问题，
> 我们已经在核实中，预计今天下午 4 点前给您详细答复。
```

### 批量报告

```
📬 邮件分析报告

概览:
- 总计: 25 封
- 🔴 紧急: 3 封
- 🟡 重要: 8 封
- 🟢 可延后: 14 封

待办汇总:
- [ ] 🔴 回复客户报价单 | 截止: 今天 18:00
- [ ] 🟡 审阅周报 | 截止: 明天
- [ ] 🟢 更新文档 | 无特定时限
```

## 安全说明

- 授权码仅用于本次连接，不会被存储
- 邮件内容仅在本地处理
- 建议使用专用授权码而非登录密码

## License

MIT
