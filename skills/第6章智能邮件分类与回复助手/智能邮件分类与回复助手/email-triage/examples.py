#!/usr/bin/env python3
"""
使用示例 - 演示如何使用邮件分类助手

运行方式:
    python examples.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib import (
    EmailClient,
    EmailFileParser,
    EmailProcessor,
    ReportGenerator,
    ProcessedEmail,
    get_supported_providers,
)


def example_parse_text():
    """示例 1: 解析粘贴的邮件文本"""
    print("\n" + "=" * 60)
    print("示例 1: 解析粘贴的邮件文本")
    print("=" * 60)

    email_text = """
发件人: 张经理 <zhang@client.com>
主题: 项目验收问题 - 需今日回复

李工您好，

关于上周交付的系统，客户反馈了以下问题：

1. 登录页面加载较慢
2. 报表导出功能偶尔失败

请在今天下班前给我一个初步的排查结果，明天上午我需要回复客户。

另外，周五下午3点我们开个会讨论下一阶段的需求，请准备一下。

谢谢！
张经理
    """

    # 解析文本
    email = EmailFileParser.parse_text(email_text)

    print(f"\n解析结果:")
    print(f"  主题: {email.subject}")
    print(f"  发件人: {email.sender}")
    print(f"  正文预览: {email.get_preview(100)}")

    # 构建 LLM prompt
    processor = EmailProcessor()
    classify_prompt = processor.build_classify_prompt(email)

    print(f"\n分类 Prompt (前 500 字符):")
    print("-" * 40)
    print(classify_prompt[:500])
    print("...")


def example_mock_llm_response():
    """示例 2: 模拟 LLM 响应处理"""
    print("\n" + "=" * 60)
    print("示例 2: 模拟 LLM 响应处理")
    print("=" * 60)

    processor = EmailProcessor()

    # 模拟分类响应
    mock_classify_response = """
```json
{
  "priority": "urgent",
  "confidence": 0.92,
  "reason": "客户问题需要今日回复，有明确截止时间",
  "category": "客户",
  "suggested_deadline": "今天 18:00 前",
  "keywords": ["今天下班前", "客户反馈", "问题"],
  "needs_reply": true,
  "summary": "客户反馈系统问题，需要今日提供排查结果"
}
```
    """

    classification = processor.process_classification_response(mock_classify_response)
    print(f"\n分类结果:")
    print(f"  优先级: {classification.priority}")
    print(f"  置信度: {classification.confidence:.0%}")
    print(f"  理由: {classification.reason}")
    print(f"  建议处理时间: {classification.suggested_deadline}")

    # 模拟待办提取响应
    mock_todos_response = """
```json
{
  "has_action_items": true,
  "action_items": [
    {
      "task": "排查登录页面加载慢的问题",
      "priority": "high",
      "deadline": "今天 18:00",
      "deadline_type": "explicit",
      "assignee": "me",
      "collaborators": [],
      "source_quote": "请在今天下班前给我一个初步的排查结果",
      "context": "客户反馈的问题"
    },
    {
      "task": "排查报表导出功能失败问题",
      "priority": "high",
      "deadline": "今天 18:00",
      "deadline_type": "explicit",
      "assignee": "me",
      "collaborators": [],
      "source_quote": "报表导出功能偶尔失败",
      "context": "客户反馈的问题"
    },
    {
      "task": "准备下一阶段需求讨论材料",
      "priority": "medium",
      "deadline": "周五 15:00 前",
      "deadline_type": "implicit",
      "assignee": "me",
      "collaborators": [],
      "source_quote": "周五下午3点我们开个会讨论下一阶段的需求，请准备一下",
      "context": "会议准备"
    }
  ],
  "meetings": [
    {
      "title": "下一阶段需求讨论会",
      "time": "周五 15:00",
      "duration": "待定",
      "location": "待定",
      "preparation_needed": ["下一阶段需求材料"]
    }
  ],
  "follow_ups": [],
  "fyi_items": []
}
```
    """

    todos = processor.process_todos_response(mock_todos_response)
    print(f"\n待办事项:")
    for item in todos.action_items:
        print(f"  - [{item.priority}] {item.task} (截止: {item.deadline})")

    print(f"\n会议:")
    for meeting in todos.meetings:
        print(f"  - {meeting.title} @ {meeting.time}")


def example_list_providers():
    """示例 3: 列出支持的邮箱服务商"""
    print("\n" + "=" * 60)
    print("示例 3: 支持的邮箱服务商")
    print("=" * 60)

    providers = get_supported_providers()
    print("\n支持的邮箱:")
    for provider in providers:
        print(f"  - {provider}")


def example_generate_report():
    """示例 4: 生成报告"""
    print("\n" + "=" * 60)
    print("示例 4: 生成 Markdown 报告")
    print("=" * 60)

    from lib.email_client import EmailMessage
    from lib.processor import ClassificationResult, TodoResult, ActionItem, ProcessedEmail

    # 创建模拟数据
    email = EmailMessage(
        id="1",
        subject="项目验收问题",
        sender="张经理 <zhang@client.com>",
        sender_name="张经理",
        sender_email="zhang@client.com",
        recipients=["me@company.com"],
        date=None,
        date_str="2026-01-30 10:00",
        body_text="关于项目验收的问题...",
        body_html="",
    )

    classification = ClassificationResult(
        priority="urgent",
        confidence=0.92,
        reason="客户问题需要今日回复",
        category="客户",
        suggested_deadline="今天 18:00",
        keywords=["紧急", "客户"],
        needs_reply=True,
        summary="客户反馈系统问题，需要今日提供排查结果",
    )

    todos = TodoResult(
        has_action_items=True,
        action_items=[
            ActionItem(
                task="排查系统问题",
                priority="high",
                deadline="今天 18:00",
                deadline_type="explicit",
                assignee="me",
                collaborators=[],
                source_quote="请今天回复",
                context="",
            )
        ],
        meetings=[],
        follow_ups=[],
        fyi_items=[],
    )

    processed = ProcessedEmail(
        email=email,
        classification=classification,
        todos=todos,
    )

    # 生成报告
    generator = ReportGenerator()
    report = generator.generate_single_email_report(processed)

    print("\n生成的报告 (前 1000 字符):")
    print("-" * 40)
    print(report[:1000])
    print("...")


def example_connect_email():
    """示例 5: 连接邮箱 (需要真实凭据)"""
    print("\n" + "=" * 60)
    print("示例 5: 连接邮箱")
    print("=" * 60)

    print("""
要连接邮箱，请使用以下代码:

```python
from lib import EmailClient

# QQ 邮箱
client = EmailClient(
    email_address="your@qq.com",
    auth_code="xxxxxxxxxxxxxxxx"  # 16位授权码
)

with client:
    # 获取最新 10 封邮件
    emails = client.fetch_emails(limit=10)

    for email in emails:
        print(f"主题: {email.subject}")
        print(f"发件人: {email.sender}")
        print(f"时间: {email.date_str}")
        print("---")
```

获取授权码:
- QQ邮箱: 设置 → 账户 → 开启 IMAP → 生成授权码
- 163邮箱: 设置 → POP3/SMTP/IMAP → 开启 → 设置授权密码
    """)


if __name__ == "__main__":
    example_parse_text()
    example_mock_llm_response()
    example_list_providers()
    example_generate_report()
    example_connect_email()

    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)
