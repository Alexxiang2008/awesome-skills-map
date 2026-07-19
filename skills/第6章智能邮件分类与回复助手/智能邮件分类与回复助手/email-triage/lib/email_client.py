"""
通用邮箱客户端 - 支持 QQ邮箱、163邮箱、Gmail、Outlook 等
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# IMAP 协议要求使用英文月份名称
IMAP_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@dataclass
class EmailConfig:
    """邮箱服务器配置"""
    imap_server: str
    imap_port: int = 993
    smtp_server: Optional[str] = None
    smtp_port: int = 465
    use_ssl: bool = True


# 预置邮箱配置
EMAIL_PROVIDERS: Dict[str, EmailConfig] = {
    # 国内邮箱
    "qq.com": EmailConfig(
        imap_server="imap.qq.com",
        smtp_server="smtp.qq.com",
        smtp_port=465
    ),
    "163.com": EmailConfig(
        imap_server="imap.163.com",
        smtp_server="smtp.163.com",
        smtp_port=465
    ),
    "126.com": EmailConfig(
        imap_server="imap.126.com",
        smtp_server="smtp.126.com",
        smtp_port=465
    ),
    "yeah.net": EmailConfig(
        imap_server="imap.yeah.net",
        smtp_server="smtp.yeah.net",
        smtp_port=465
    ),
    "sina.com": EmailConfig(
        imap_server="imap.sina.com",
        smtp_server="smtp.sina.com",
        smtp_port=465
    ),
    "sohu.com": EmailConfig(
        imap_server="imap.sohu.com",
        smtp_server="smtp.sohu.com",
        smtp_port=465
    ),
    "aliyun.com": EmailConfig(
        imap_server="imap.aliyun.com",
        smtp_server="smtp.aliyun.com",
        smtp_port=465
    ),
    # 国际邮箱
    "gmail.com": EmailConfig(
        imap_server="imap.gmail.com",
        smtp_server="smtp.gmail.com",
        smtp_port=587
    ),
    "outlook.com": EmailConfig(
        imap_server="outlook.office365.com",
        smtp_server="smtp.office365.com",
        smtp_port=587
    ),
    "hotmail.com": EmailConfig(
        imap_server="outlook.office365.com",
        smtp_server="smtp.office365.com",
        smtp_port=587
    ),
    "live.com": EmailConfig(
        imap_server="outlook.office365.com",
        smtp_server="smtp.office365.com",
        smtp_port=587
    ),
    "yahoo.com": EmailConfig(
        imap_server="imap.mail.yahoo.com",
        smtp_server="smtp.mail.yahoo.com",
        smtp_port=465
    ),
    "icloud.com": EmailConfig(
        imap_server="imap.mail.me.com",
        smtp_server="smtp.mail.me.com",
        smtp_port=587
    ),
}


@dataclass
class EmailMessage:
    """解析后的邮件对象"""
    id: str
    subject: str
    sender: str
    sender_name: str
    sender_email: str
    recipients: List[str]
    date: Optional[datetime]
    date_str: str
    body_text: str
    body_html: str
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    raw_headers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "subject": self.subject,
            "sender": self.sender,
            "sender_name": self.sender_name,
            "sender_email": self.sender_email,
            "recipients": self.recipients,
            "date": self.date.isoformat() if self.date else None,
            "date_str": self.date_str,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "attachments": self.attachments,
        }

    def get_preview(self, max_length: int = 200) -> str:
        """获取邮件预览"""
        text = self.body_text.strip()
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text


class EmailClient:
    """通用邮箱客户端"""

    def __init__(
        self,
        email_address: str,
        auth_code: str,
        config: Optional[EmailConfig] = None
    ):
        self.email_address = email_address
        self.auth_code = auth_code
        self.config = config or self._auto_detect_config()
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def _auto_detect_config(self) -> EmailConfig:
        """根据邮箱地址自动检测配置"""
        domain = self.email_address.split("@")[-1].lower()

        if domain in EMAIL_PROVIDERS:
            return EMAIL_PROVIDERS[domain]

        # 尝试通用配置
        return EmailConfig(
            imap_server=f"imap.{domain}",
            smtp_server=f"smtp.{domain}"
        )

    def connect(self) -> "EmailClient":
        """连接到邮箱服务器"""
        try:
            if self.config.use_ssl:
                self.connection = imaplib.IMAP4_SSL(
                    self.config.imap_server,
                    self.config.imap_port
                )
            else:
                self.connection = imaplib.IMAP4(
                    self.config.imap_server,
                    self.config.imap_port
                )

            self.connection.login(self.email_address, self.auth_code)
            return self
        except imaplib.IMAP4.error as e:
            raise ConnectionError(f"邮箱连接失败: {e}. 请检查邮箱地址和授权码是否正确。")

    def disconnect(self):
        """断开连接"""
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
            self.connection = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def list_folders(self) -> List[str]:
        """列出所有文件夹"""
        if not self.connection:
            raise ConnectionError("未连接到邮箱服务器")

        status, folders = self.connection.list()
        result = []
        for folder in folders:
            # 解析文件夹名称
            match = re.search(r'"([^"]+)"$|(\S+)$', folder.decode())
            if match:
                result.append(match.group(1) or match.group(2))
        return result

    def _format_imap_date(self, dt: datetime) -> str:
        """格式化日期为 IMAP 协议要求的格式 (DD-Mon-YYYY)"""
        return f"{dt.day:02d}-{IMAP_MONTHS[dt.month - 1]}-{dt.year}"

    def fetch_emails(
        self,
        folder: str = "INBOX",
        limit: int = 20,
        search_criteria: str = "ALL",
        since_date: Optional[datetime] = None
    ) -> List[EmailMessage]:
        """获取邮件列表

        默认获取最近30天内按日期排序的最新邮件。
        由于某些邮箱服务器的 IMAP ID 顺序与邮件实际日期不一致，
        需要先获取候选邮件，再按日期排序后取最新的。
        """
        if not self.connection:
            raise ConnectionError("未连接到邮箱服务器")

        # 选择文件夹
        status, _ = self.connection.select(folder, readonly=True)
        if status != "OK":
            raise ValueError(f"无法打开文件夹: {folder}")

        # 构建搜索条件
        # 如果没有指定 since_date，默认搜索最近30天的邮件
        if since_date:
            date_str = self._format_imap_date(since_date)
            criteria = f'SINCE {date_str}'
        elif search_criteria == "ALL" and limit:
            # 默认搜索最近30天，确保能获取到足够的最新邮件
            from datetime import timedelta
            default_since = datetime.now() - timedelta(days=30)
            date_str = self._format_imap_date(default_since)
            criteria = f'SINCE {date_str}'
        else:
            criteria = search_criteria

        # 搜索邮件
        status, messages = self.connection.search(None, criteria)
        if status != "OK":
            return []

        email_ids = messages[0].split()

        if not email_ids:
            return []

        # 获取所有候选邮件的内容
        results = []
        for eid in email_ids:
            try:
                status, msg_data = self.connection.fetch(eid, "(RFC822)")
                if status == "OK" and msg_data[0]:
                    raw_email = msg_data[0][1]
                    parsed = self._parse_email(raw_email, eid.decode())
                    results.append(parsed)
            except Exception as e:
                print(f"解析邮件 {eid} 失败: {e}")
                continue

        # 按实际日期排序（最新的在前）
        def get_sort_key(email_msg):
            if email_msg.date is None:
                return datetime.min
            # 移除时区信息以便统一比较
            if email_msg.date.tzinfo is not None:
                return email_msg.date.replace(tzinfo=None)
            return email_msg.date

        results.sort(key=get_sort_key, reverse=True)

        # 如果指定了 since_date，过滤掉早于该日期的邮件
        if since_date:
            since_naive = since_date.replace(tzinfo=None) if since_date.tzinfo else since_date
            results = [
                e for e in results
                if e.date and get_sort_key(e) >= since_naive
            ]

        # 返回指定数量的邮件
        return results[:limit] if limit else results

    def _parse_email(self, raw_email: bytes, email_id: str) -> EmailMessage:
        """解析原始邮件"""
        msg = email.message_from_bytes(raw_email)

        # 解析主题
        subject = self._decode_header(msg.get("Subject", ""))

        # 解析发件人
        sender_raw = self._decode_header(msg.get("From", ""))
        sender_name, sender_email = self._parse_address(sender_raw)

        # 解析收件人
        recipients = []
        for header in ["To", "Cc"]:
            if msg.get(header):
                recipients.extend(self._decode_header(msg.get(header)).split(","))

        # 解析日期
        date_str = msg.get("Date", "")
        date = None
        try:
            date = parsedate_to_datetime(date_str)
        except:
            pass

        # 提取正文
        body_text, body_html = self._extract_body(msg)

        # 提取附件信息
        attachments = self._extract_attachments(msg)

        return EmailMessage(
            id=email_id,
            subject=subject,
            sender=sender_raw,
            sender_name=sender_name,
            sender_email=sender_email,
            recipients=[r.strip() for r in recipients if r.strip()],
            date=date,
            date_str=date_str,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            raw_headers={
                "Message-ID": msg.get("Message-ID", ""),
                "In-Reply-To": msg.get("In-Reply-To", ""),
                "References": msg.get("References", ""),
            }
        )

    def _decode_header(self, header: str) -> str:
        """解码邮件头"""
        if not header:
            return ""

        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                try:
                    decoded_parts.append(part.decode(encoding or "utf-8", errors="ignore"))
                except:
                    decoded_parts.append(part.decode("utf-8", errors="ignore"))
            else:
                decoded_parts.append(part)

        return " ".join(decoded_parts)

    def _parse_address(self, address: str) -> tuple:
        """解析邮件地址，返回 (名称, 邮箱)"""
        # 格式: "Name <email@example.com>" 或 "email@example.com"
        match = re.match(r'^"?([^"<]*)"?\s*<?([^>]+@[^>]+)>?$', address.strip())
        if match:
            name = match.group(1).strip()
            email_addr = match.group(2).strip()
            return (name or email_addr, email_addr)
        return (address, address)

    def _extract_body(self, msg) -> tuple:
        """提取邮件正文，返回 (纯文本, HTML)"""
        body_text = ""
        body_html = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # 跳过附件
                if "attachment" in content_disposition:
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        text = payload.decode(charset, errors="ignore")

                        if content_type == "text/plain" and not body_text:
                            body_text = text
                        elif content_type == "text/html" and not body_html:
                            body_html = text
                except:
                    continue
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    text = payload.decode(charset, errors="ignore")

                    if msg.get_content_type() == "text/html":
                        body_html = text
                        # 简单提取纯文本
                        body_text = self._html_to_text(text)
                    else:
                        body_text = text
            except:
                pass

        # 如果只有 HTML，转换为纯文本
        if not body_text and body_html:
            body_text = self._html_to_text(body_html)

        return (body_text.strip(), body_html.strip())

    def _html_to_text(self, html: str) -> str:
        """简单的 HTML 转纯文本"""
        # 移除 style 和 script 标签
        text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # 替换常见标签
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<p[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<div[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '', text, flags=re.IGNORECASE)
        # 移除所有其他标签
        text = re.sub(r'<[^>]+>', '', text)
        # 解码 HTML 实体
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        # 清理多余空白
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def _extract_attachments(self, msg) -> List[Dict[str, Any]]:
        """提取附件信息"""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)

                    attachments.append({
                        "filename": filename or "unnamed",
                        "content_type": part.get_content_type(),
                        "size": len(part.get_payload(decode=True) or b""),
                    })

        return attachments


def get_supported_providers() -> List[str]:
    """获取支持的邮箱服务商列表"""
    return list(EMAIL_PROVIDERS.keys())


def test_connection(email_address: str, auth_code: str) -> bool:
    """测试邮箱连接"""
    try:
        with EmailClient(email_address, auth_code) as client:
            client.list_folders()
            return True
    except:
        return False
