"""
邮件文件解析器 - 支持 EML、MBOX 格式
"""

import email
import mailbox
from email.header import decode_header
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import List, Optional, Union
import re

from .email_client import EmailMessage


class EmailFileParser:
    """邮件文件解析器"""

    @staticmethod
    def parse_eml(file_path: Union[str, Path]) -> EmailMessage:
        """解析单个 EML 文件"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "rb") as f:
            raw_email = f.read()

        return EmailFileParser._parse_raw_email(raw_email, file_path.name)

    @staticmethod
    def parse_mbox(file_path: Union[str, Path], limit: Optional[int] = None) -> List[EmailMessage]:
        """解析 MBOX 文件（批量邮件）"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        mbox = mailbox.mbox(str(file_path))
        results = []

        for i, msg in enumerate(mbox):
            if limit and i >= limit:
                break

            try:
                # 将 mailbox.mboxMessage 转换为 bytes
                raw_email = msg.as_bytes()
                parsed = EmailFileParser._parse_raw_email(raw_email, f"mbox_{i}")
                results.append(parsed)
            except Exception as e:
                print(f"解析邮件 {i} 失败: {e}")
                continue

        return results

    @staticmethod
    def parse_text(text: str, subject: str = "粘贴的邮件") -> EmailMessage:
        """解析纯文本邮件内容"""
        # 尝试从文本中提取发件人和主题
        sender = "未知发件人"
        extracted_subject = subject
        body = text

        lines = text.strip().split("\n")
        body_start = 0

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            if line_lower.startswith("from:") or line_lower.startswith("发件人:"):
                sender = line.split(":", 1)[1].strip()
                body_start = i + 1
            elif line_lower.startswith("subject:") or line_lower.startswith("主题:"):
                extracted_subject = line.split(":", 1)[1].strip()
                body_start = i + 1
            elif line.strip() == "" and body_start > 0:
                # 空行后是正文
                body = "\n".join(lines[i+1:])
                break

        if body_start == 0:
            body = text

        return EmailMessage(
            id="text_input",
            subject=extracted_subject,
            sender=sender,
            sender_name=sender,
            sender_email="",
            recipients=[],
            date=None,
            date_str="",
            body_text=body.strip(),
            body_html="",
            attachments=[],
            raw_headers={}
        )

    @staticmethod
    def _parse_raw_email(raw_email: bytes, email_id: str) -> EmailMessage:
        """解析原始邮件字节"""
        msg = email.message_from_bytes(raw_email)

        # 解析主题
        subject = EmailFileParser._decode_header(msg.get("Subject", ""))

        # 解析发件人
        sender_raw = EmailFileParser._decode_header(msg.get("From", ""))
        sender_name, sender_email = EmailFileParser._parse_address(sender_raw)

        # 解析收件人
        recipients = []
        for header in ["To", "Cc"]:
            if msg.get(header):
                recipients.extend(EmailFileParser._decode_header(msg.get(header)).split(","))

        # 解析日期
        date_str = msg.get("Date", "")
        date = None
        try:
            date = parsedate_to_datetime(date_str)
        except:
            pass

        # 提取正文
        body_text, body_html = EmailFileParser._extract_body(msg)

        # 提取附件信息
        attachments = EmailFileParser._extract_attachments(msg)

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

    @staticmethod
    def _decode_header(header: str) -> str:
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

    @staticmethod
    def _parse_address(address: str) -> tuple:
        """解析邮件地址"""
        match = re.match(r'^"?([^"<]*)"?\s*<?([^>]+@[^>]+)>?$', address.strip())
        if match:
            name = match.group(1).strip()
            email_addr = match.group(2).strip()
            return (name or email_addr, email_addr)
        return (address, address)

    @staticmethod
    def _extract_body(msg) -> tuple:
        """提取邮件正文"""
        body_text = ""
        body_html = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

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
                        body_text = EmailFileParser._html_to_text(text)
                    else:
                        body_text = text
            except:
                pass

        if not body_text and body_html:
            body_text = EmailFileParser._html_to_text(body_html)

        return (body_text.strip(), body_html.strip())

    @staticmethod
    def _html_to_text(html: str) -> str:
        """HTML 转纯文本"""
        text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<p[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    @staticmethod
    def _extract_attachments(msg) -> list:
        """提取附件信息"""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = EmailFileParser._decode_header(filename)

                    attachments.append({
                        "filename": filename or "unnamed",
                        "content_type": part.get_content_type(),
                        "size": len(part.get_payload(decode=True) or b""),
                    })

        return attachments


def detect_file_type(file_path: Union[str, Path]) -> str:
    """检测邮件文件类型"""
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".eml":
        return "eml"
    elif suffix == ".mbox":
        return "mbox"
    else:
        # 尝试通过内容判断
        with open(file_path, "rb") as f:
            header = f.read(100)

        if b"From " in header[:10]:
            return "mbox"
        elif b"From:" in header or b"Subject:" in header:
            return "eml"

    return "unknown"


def parse_email_file(file_path: Union[str, Path], limit: Optional[int] = None) -> List[EmailMessage]:
    """自动检测并解析邮件文件"""
    file_type = detect_file_type(file_path)

    if file_type == "eml":
        return [EmailFileParser.parse_eml(file_path)]
    elif file_type == "mbox":
        return EmailFileParser.parse_mbox(file_path, limit)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")
