"""
邮件处理器 - 使用 LLM 进行分类、回复生成和待办提取
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path

from .email_client import EmailMessage


@dataclass
class ClassificationResult:
    """分类结果"""
    priority: str  # urgent, important, defer
    confidence: float
    reason: str
    category: str
    suggested_deadline: str
    keywords: List[str]
    needs_reply: bool
    summary: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClassificationResult":
        return cls(
            priority=data.get("priority", "important"),
            confidence=data.get("confidence", 0.5),
            reason=data.get("reason", ""),
            category=data.get("category", "其他"),
            suggested_deadline=data.get("suggested_deadline", ""),
            keywords=data.get("keywords", []),
            needs_reply=data.get("needs_reply", False),
            summary=data.get("summary", ""),
        )


@dataclass
class ReplyDraft:
    """回复草稿"""
    version: str
    subject: str
    body: str
    tone: str
    word_count: int


@dataclass
class ReplyResult:
    """回复生成结果"""
    replies: List[ReplyDraft]
    suggested_attachments: List[str]
    follow_up_reminder: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplyResult":
        replies = []
        for r in data.get("replies", []):
            replies.append(ReplyDraft(
                version=r.get("version", ""),
                subject=r.get("subject", ""),
                body=r.get("body", ""),
                tone=r.get("tone", ""),
                word_count=r.get("word_count", 0),
            ))
        return cls(
            replies=replies,
            suggested_attachments=data.get("suggested_attachments", []),
            follow_up_reminder=data.get("follow_up_reminder", ""),
        )


@dataclass
class ActionItem:
    """待办事项"""
    task: str
    priority: str
    deadline: str
    deadline_type: str
    assignee: str
    collaborators: List[str]
    source_quote: str
    context: str


@dataclass
class Meeting:
    """会议信息"""
    title: str
    time: str
    duration: str
    location: str
    preparation_needed: List[str]


@dataclass
class TodoResult:
    """待办提取结果"""
    has_action_items: bool
    action_items: List[ActionItem]
    meetings: List[Meeting]
    follow_ups: List[Dict[str, str]]
    fyi_items: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoResult":
        action_items = []
        for item in data.get("action_items", []):
            action_items.append(ActionItem(
                task=item.get("task", ""),
                priority=item.get("priority", "medium"),
                deadline=item.get("deadline", ""),
                deadline_type=item.get("deadline_type", "none"),
                assignee=item.get("assignee", "me"),
                collaborators=item.get("collaborators", []),
                source_quote=item.get("source_quote", ""),
                context=item.get("context", ""),
            ))

        meetings = []
        for m in data.get("meetings", []):
            meetings.append(Meeting(
                title=m.get("title", ""),
                time=m.get("time", ""),
                duration=m.get("duration", ""),
                location=m.get("location", ""),
                preparation_needed=m.get("preparation_needed", []),
            ))

        return cls(
            has_action_items=data.get("has_action_items", False),
            action_items=action_items,
            meetings=meetings,
            follow_ups=data.get("follow_ups", []),
            fyi_items=data.get("fyi_items", []),
        )


@dataclass
class ProcessedEmail:
    """处理后的邮件"""
    email: EmailMessage
    classification: Optional[ClassificationResult] = None
    reply: Optional[ReplyResult] = None
    todos: Optional[TodoResult] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "email": self.email.to_dict(),
        }
        if self.classification:
            result["classification"] = {
                "priority": self.classification.priority,
                "confidence": self.classification.confidence,
                "reason": self.classification.reason,
                "category": self.classification.category,
                "suggested_deadline": self.classification.suggested_deadline,
                "keywords": self.classification.keywords,
                "needs_reply": self.classification.needs_reply,
                "summary": self.classification.summary,
            }
        if self.todos:
            result["todos"] = {
                "has_action_items": self.todos.has_action_items,
                "action_items": [
                    {
                        "task": item.task,
                        "priority": item.priority,
                        "deadline": item.deadline,
                        "assignee": item.assignee,
                    }
                    for item in self.todos.action_items
                ],
                "meetings": [
                    {
                        "title": m.title,
                        "time": m.time,
                        "location": m.location,
                    }
                    for m in self.todos.meetings
                ],
            }
        return result


class EmailProcessor:
    """邮件处理器"""

    def __init__(self, prompts_dir: Optional[Path] = None):
        """初始化处理器"""
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent.parent / "prompts"
        self.prompts_dir = prompts_dir
        self._load_prompts()

    def _load_prompts(self):
        """加载 prompt 模板"""
        self.classify_prompt = self._read_prompt("classify.md")
        self.reply_prompt = self._read_prompt("reply.md")
        self.extract_todos_prompt = self._read_prompt("extract_todos.md")

    def _read_prompt(self, filename: str) -> str:
        """读取 prompt 文件"""
        prompt_path = self.prompts_dir / filename
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return ""

    def format_email_for_llm(self, email: EmailMessage) -> str:
        """格式化邮件内容供 LLM 处理"""
        body_preview = email.body_text[:2000] if email.body_text else "(无正文)"

        return f"""发件人: {email.sender}
主题: {email.subject}
时间: {email.date_str}
正文:
{body_preview}
"""

    def build_classify_prompt(self, email: EmailMessage) -> str:
        """构建分类 prompt"""
        email_content = self.format_email_for_llm(email)
        return f"""{self.classify_prompt}

---

请分析以下邮件：

{email_content}

请严格按照 JSON 格式输出分类结果。"""

    def build_reply_prompt(
        self,
        email: EmailMessage,
        tone: str = "formal",
        language: str = "auto",
        key_points: Optional[List[str]] = None
    ) -> str:
        """构建回复生成 prompt"""
        email_content = self.format_email_for_llm(email)

        # 自动检测语言
        if language == "auto":
            if re.search(r'[\u4e00-\u9fff]', email.body_text):
                language = "中文"
            else:
                language = "English"

        points_str = ""
        if key_points:
            points_str = f"\n- 要点: {', '.join(key_points)}"

        return f"""{self.reply_prompt}

---

原始邮件：
{email_content}

回复要求：
- 风格: {tone}
- 语言: {language}{points_str}

请生成 2-3 个不同版本的回复草稿，严格按照 JSON 格式输出。"""

    def build_extract_todos_prompt(self, email: EmailMessage) -> str:
        """构建待办提取 prompt"""
        email_content = self.format_email_for_llm(email)
        return f"""{self.extract_todos_prompt}

---

请分析以下邮件并提取待办事项：

{email_content}

请严格按照 JSON 格式输出结果。"""

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析 LLM 返回的 JSON"""
        # 尝试提取 JSON 块
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = response

        # 清理可能的问题
        json_str = json_str.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 尝试修复常见问题
            # 移除尾部逗号
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)

            try:
                return json.loads(json_str)
            except:
                return {}

    def process_classification_response(self, response: str) -> ClassificationResult:
        """处理分类响应"""
        data = self.parse_json_response(response)
        return ClassificationResult.from_dict(data)

    def process_reply_response(self, response: str) -> ReplyResult:
        """处理回复生成响应"""
        data = self.parse_json_response(response)
        return ReplyResult.from_dict(data)

    def process_todos_response(self, response: str) -> TodoResult:
        """处理待办提取响应"""
        data = self.parse_json_response(response)
        return TodoResult.from_dict(data)


def get_priority_emoji(priority: str) -> str:
    """获取优先级对应的 emoji"""
    return {
        "urgent": "🔴",
        "important": "🟡",
        "defer": "🟢",
    }.get(priority, "⚪")


def get_priority_label(priority: str) -> str:
    """获取优先级中文标签"""
    return {
        "urgent": "紧急",
        "important": "重要",
        "defer": "可延后",
    }.get(priority, "未知")
