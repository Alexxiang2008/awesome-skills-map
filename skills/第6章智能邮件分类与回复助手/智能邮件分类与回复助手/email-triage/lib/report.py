"""
报告生成器 - 生成 Markdown 格式的邮件分析报告
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .processor import ProcessedEmail, get_priority_emoji, get_priority_label


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.generated_at = datetime.now()

    def generate_summary_report(
        self,
        processed_emails: List[ProcessedEmail],
        title: str = "邮件分析报告"
    ) -> str:
        """生成汇总报告"""
        # 统计
        total = len(processed_emails)
        urgent_count = sum(1 for e in processed_emails if e.classification and e.classification.priority == "urgent")
        important_count = sum(1 for e in processed_emails if e.classification and e.classification.priority == "important")
        defer_count = sum(1 for e in processed_emails if e.classification and e.classification.priority == "defer")

        # 收集所有待办
        all_todos = []
        all_meetings = []
        for pe in processed_emails:
            if pe.todos:
                for item in pe.todos.action_items:
                    all_todos.append({
                        "task": item.task,
                        "priority": item.priority,
                        "deadline": item.deadline,
                        "from_email": pe.email.subject,
                    })
                for meeting in pe.todos.meetings:
                    all_meetings.append({
                        "title": meeting.title,
                        "time": meeting.time,
                        "location": meeting.location,
                        "from_email": pe.email.subject,
                    })

        report = f"""# 📬 {title}

生成时间: {self.generated_at.strftime("%Y-%m-%d %H:%M")}

## 📊 概览

| 类别 | 数量 |
|------|------|
| 总计 | {total} 封 |
| 🔴 紧急 | {urgent_count} 封 |
| 🟡 重要 | {important_count} 封 |
| 🟢 可延后 | {defer_count} 封 |

---

"""
        # 按优先级分组输出
        if urgent_count > 0:
            report += self._generate_priority_section(processed_emails, "urgent", "紧急邮件 (需立即处理)")

        if important_count > 0:
            report += self._generate_priority_section(processed_emails, "important", "重要邮件 (需认真对待)")

        if defer_count > 0:
            report += self._generate_priority_section(processed_emails, "defer", "可延后邮件")

        # 待办汇总
        if all_todos:
            report += self._generate_todos_section(all_todos)

        # 会议汇总
        if all_meetings:
            report += self._generate_meetings_section(all_meetings)

        return report

    def _generate_priority_section(
        self,
        processed_emails: List[ProcessedEmail],
        priority: str,
        section_title: str
    ) -> str:
        """生成某个优先级的邮件列表"""
        emoji = get_priority_emoji(priority)
        filtered = [e for e in processed_emails if e.classification and e.classification.priority == priority]

        if not filtered:
            return ""

        section = f"## {emoji} {section_title}\n\n"

        for i, pe in enumerate(filtered, 1):
            email = pe.email
            classification = pe.classification

            section += f"### {i}. {email.subject}\n\n"
            section += f"**发件人:** {email.sender_name} <{email.sender_email}>  \n"
            section += f"**时间:** {email.date_str}  \n"

            if classification:
                section += f"**分类理由:** {classification.reason}  \n"
                if classification.suggested_deadline:
                    section += f"**建议处理时间:** {classification.suggested_deadline}  \n"
                section += f"**摘要:** {classification.summary}\n\n"

            # 待办事项
            if pe.todos and pe.todos.action_items:
                section += "**待办事项:**\n"
                for item in pe.todos.action_items:
                    deadline_str = f" (截止: {item.deadline})" if item.deadline else ""
                    section += f"- [ ] {item.task}{deadline_str}\n"
                section += "\n"

            section += "---\n\n"

        return section

    def _generate_todos_section(self, todos: List[Dict[str, Any]]) -> str:
        """生成待办汇总"""
        section = "## 📋 待办事项汇总\n\n"

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_todos = sorted(todos, key=lambda x: priority_order.get(x.get("priority", "medium"), 1))

        for todo in sorted_todos:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.get("priority", "medium"), "⚪")
            deadline_str = f" | 截止: {todo['deadline']}" if todo.get("deadline") else ""
            section += f"- [ ] {priority_emoji} {todo['task']}{deadline_str}\n"
            section += f"  - 来源: {todo['from_email']}\n"

        section += "\n---\n\n"
        return section

    def _generate_meetings_section(self, meetings: List[Dict[str, Any]]) -> str:
        """生成会议汇总"""
        section = "## 📅 会议安排\n\n"

        for meeting in meetings:
            section += f"### {meeting['title']}\n"
            section += f"- **时间:** {meeting.get('time', '待定')}\n"
            if meeting.get('location'):
                section += f"- **地点:** {meeting['location']}\n"
            section += f"- **来源邮件:** {meeting['from_email']}\n\n"

        section += "---\n\n"
        return section

    def generate_single_email_report(self, processed_email: ProcessedEmail) -> str:
        """生成单封邮件的详细报告"""
        email = processed_email.email
        classification = processed_email.classification
        reply = processed_email.reply
        todos = processed_email.todos

        emoji = get_priority_emoji(classification.priority) if classification else "📧"
        priority_label = get_priority_label(classification.priority) if classification else ""

        report = f"""# {emoji} 邮件分析: {email.subject}

## 基本信息

| 字段 | 内容 |
|------|------|
| 发件人 | {email.sender_name} <{email.sender_email}> |
| 时间 | {email.date_str} |
| 主题 | {email.subject} |
"""

        if classification:
            report += f"""
## 📊 分类结果

| 字段 | 内容 |
|------|------|
| 优先级 | {emoji} {priority_label} |
| 置信度 | {classification.confidence:.0%} |
| 分类理由 | {classification.reason} |
| 类别 | {classification.category} |
| 建议处理时间 | {classification.suggested_deadline or "无特定时限"} |
| 需要回复 | {"是" if classification.needs_reply else "否"} |

**摘要:** {classification.summary}

"""

        if todos and todos.has_action_items:
            report += "## 📋 待办事项\n\n"
            for item in todos.action_items:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.priority, "⚪")
                report += f"- [ ] {priority_emoji} **{item.task}**\n"
                if item.deadline:
                    report += f"  - 截止时间: {item.deadline}\n"
                if item.source_quote:
                    report += f"  - 原文: \"{item.source_quote}\"\n"
                report += "\n"

        if todos and todos.meetings:
            report += "## 📅 会议\n\n"
            for meeting in todos.meetings:
                report += f"### {meeting.title}\n"
                report += f"- 时间: {meeting.time}\n"
                report += f"- 时长: {meeting.duration}\n"
                if meeting.location:
                    report += f"- 地点: {meeting.location}\n"
                if meeting.preparation_needed:
                    report += f"- 需要准备:\n"
                    for prep in meeting.preparation_needed:
                        report += f"  - {prep}\n"
                report += "\n"

        if reply and reply.replies:
            report += "## ✉️ 建议回复\n\n"
            for i, draft in enumerate(reply.replies, 1):
                report += f"### 版本 {i}: {draft.version}\n\n"
                report += f"**主题:** {draft.subject}\n\n"
                report += f"```\n{draft.body}\n```\n\n"

        # 原文预览
        report += "## 📄 原文预览\n\n"
        report += f"```\n{email.body_text[:1000]}{'...' if len(email.body_text) > 1000 else ''}\n```\n"

        return report

    def generate_json_output(self, processed_emails: List[ProcessedEmail]) -> Dict[str, Any]:
        """生成 JSON 格式输出"""
        return {
            "generated_at": self.generated_at.isoformat(),
            "total_count": len(processed_emails),
            "summary": {
                "urgent": sum(1 for e in processed_emails if e.classification and e.classification.priority == "urgent"),
                "important": sum(1 for e in processed_emails if e.classification and e.classification.priority == "important"),
                "defer": sum(1 for e in processed_emails if e.classification and e.classification.priority == "defer"),
            },
            "emails": [e.to_dict() for e in processed_emails],
        }


def save_report(content: str, output_path: Path):
    """保存报告到文件"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
