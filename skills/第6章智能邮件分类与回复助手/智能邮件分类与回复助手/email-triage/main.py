#!/usr/bin/env python3
"""
智能邮件分类与回复助手 - 命令行入口

使用示例:
    # 连接 QQ 邮箱
    python main.py --email your@qq.com --auth-code xxxxxxxxxxxxxxxx

    # 解析 EML 文件
    python main.py --file email.eml

    # 解析 MBOX 文件
    python main.py --file emails.mbox --limit 20
"""

import argparse
import json
import sys
from pathlib import Path

# 添加 lib 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from lib import (
    EmailClient,
    EmailFileParser,
    EmailProcessor,
    ReportGenerator,
    ProcessedEmail,
    parse_email_file,
    get_supported_providers,
)


def process_with_llm(processor: EmailProcessor, email, llm_callback):
    """
    使用 LLM 处理邮件

    llm_callback: 一个函数，接收 prompt 字符串，返回 LLM 响应字符串
    """
    # 分类
    classify_prompt = processor.build_classify_prompt(email)
    classify_response = llm_callback(classify_prompt)
    classification = processor.process_classification_response(classify_response)

    # 提取待办
    todos_prompt = processor.build_extract_todos_prompt(email)
    todos_response = llm_callback(todos_prompt)
    todos = processor.process_todos_response(todos_response)

    # 生成回复（仅对需要回复的邮件）
    reply = None
    if classification.needs_reply:
        reply_prompt = processor.build_reply_prompt(email)
        reply_response = llm_callback(reply_prompt)
        reply = processor.process_reply_response(reply_response)

    return ProcessedEmail(
        email=email,
        classification=classification,
        reply=reply,
        todos=todos,
    )


def main():
    parser = argparse.ArgumentParser(
        description="智能邮件分类与回复助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 连接 QQ 邮箱获取最新 10 封邮件
  python main.py --email your@qq.com --auth-code xxxxxxxx --limit 10

  # 解析本地 EML 文件
  python main.py --file email.eml

  # 解析 MBOX 批量导出文件
  python main.py --file emails.mbox --limit 20

  # 列出支持的邮箱服务商
  python main.py --list-providers
        """
    )

    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--auth-code", help="授权码（非登录密码）")
    parser.add_argument("--file", help="邮件文件路径 (.eml 或 .mbox)")
    parser.add_argument("--limit", type=int, default=20, help="获取邮件数量限制 (默认 20)")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--list-providers", action="store_true", help="列出支持的邮箱服务商")
    parser.add_argument("--test-connection", action="store_true", help="仅测试邮箱连接")

    args = parser.parse_args()

    # 列出支持的服务商
    if args.list_providers:
        print("支持的邮箱服务商:")
        for provider in get_supported_providers():
            print(f"  - {provider}")
        return

    # 获取邮件
    emails = []

    if args.file:
        # 从文件解析
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"错误: 文件不存在 - {file_path}")
            sys.exit(1)

        print(f"正在解析文件: {file_path}")
        emails = parse_email_file(file_path, limit=args.limit)
        print(f"成功解析 {len(emails)} 封邮件")

    elif args.email and args.auth_code:
        # 从邮箱获取
        if args.test_connection:
            print(f"正在测试连接: {args.email}")
            try:
                with EmailClient(args.email, args.auth_code) as client:
                    folders = client.list_folders()
                    print(f"连接成功! 可用文件夹: {', '.join(folders[:5])}")
            except Exception as e:
                print(f"连接失败: {e}")
                sys.exit(1)
            return

        print(f"正在连接邮箱: {args.email}")
        try:
            with EmailClient(args.email, args.auth_code) as client:
                emails = client.fetch_emails(limit=args.limit)
                print(f"成功获取 {len(emails)} 封邮件")
        except Exception as e:
            print(f"获取邮件失败: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        print("\n错误: 请提供邮箱信息 (--email + --auth-code) 或文件路径 (--file)")
        sys.exit(1)

    if not emails:
        print("没有找到邮件")
        return

    # 输出邮件列表（不进行 LLM 处理，仅展示原始信息）
    print("\n" + "=" * 60)
    print("邮件列表 (按时间倒序)")
    print("=" * 60)

    for i, email in enumerate(emails, 1):
        print(f"\n[{i}] {email.subject}")
        print(f"    发件人: {email.sender_name} <{email.sender_email}>")
        print(f"    时间: {email.date_str}")
        preview = email.get_preview(100)
        if preview:
            print(f"    预览: {preview}")

    print("\n" + "=" * 60)
    print(f"共 {len(emails)} 封邮件")
    print("=" * 60)

    # 如果需要输出到文件
    if args.output:
        output_path = Path(args.output)

        if args.format == "json":
            data = {
                "total": len(emails),
                "emails": [e.to_dict() for e in emails]
            }
            output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            # 简单的 Markdown 列表
            lines = [f"# 邮件列表\n\n共 {len(emails)} 封邮件\n"]
            for i, email in enumerate(emails, 1):
                lines.append(f"## {i}. {email.subject}\n")
                lines.append(f"- 发件人: {email.sender}")
                lines.append(f"- 时间: {email.date_str}")
                lines.append(f"- 预览: {email.get_preview(200)}\n")
            output_path.write_text("\n".join(lines))

        print(f"\n已保存到: {output_path}")


if __name__ == "__main__":
    main()
