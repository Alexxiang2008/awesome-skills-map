#!/usr/bin/env python
"""
retry_failed.py - 重试 v3.3 翻译失败的 5 条

从 v3.3.html 提取失败卡片 → 用 claude CLI 重试 → 输出 v3.4.html
"""
import re, sys, json, subprocess
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

from _shared import ok_msg, warn_msg, err_msg

INPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.3.html'
OUTPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.4.html'


def translate_with_claude_cli(text):
    """通过 bash -c 调 claude CLI"""
    safe_text = text.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`').replace('\\', '\\\\')
    safe_prompt = "翻译成中文（≤60字，只输出中文）"
    cmd = f'echo "{safe_text}" | claude -p "{safe_prompt}"'
    try:
        r = subprocess.run(
            ['bash', '-c', cmd],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=60
        )
        if r.returncode != 0:
            print(warn_msg("claude CLI 失败: {r.stderr[:200]}")), file=sys.stderr)
            return f'[翻译失败] {text[:50]}'
        result = r.stdout.strip()
        result = re.sub(r'^["""\']|["""\']$', '', result).strip()
        # 截短
        if len(result) > 80:
            result = result[:78] + '...'
        return result if result else text[:50]
    except subprocess.TimeoutExpired:
        return f'[翻译超时] {text[:30]}'
    except Exception as e:
        return f'[翻译错误: {e}] {text[:30]}'


def parse_v3_html(html_path):
    """提取所有卡片"""
    html = html_path.read_text(encoding='utf-8')
    pattern = re.compile(
        r'<input type="checkbox" class="card-checkbox"\s*'
        r'data-id="([^"]+)"\s*'
        r'data-name="([^"]+)"\s*'
        r'data-url="([^"]+)"\s*'
        r'data-desc="([^"]+)"\s*'
        r'data-category="([^"]+)"',
        re.DOTALL
    )
    cards = []
    seen = set()
    for m in pattern.finditer(html):
        cid = m.group(1)
        if cid in seen:
            continue
        seen.add(cid)
        # 检查是否有 🆕 标记（已翻译）
        card_pattern = re.compile(
            rf'<input[^>]+data-id="{re.escape(cid)}"[^>]*>(.*?)(?=<div class="card">)',
            re.DOTALL
        )
        card_match = card_pattern.search(html)
        has_new = card_match and 'card-tag-new' in card_match.group(1)

        desc = m.group(4).replace('&#39;', "'").replace('&quot;', '"')
        is_zh = bool(re.search(r'[一-鿿]', desc))

        cards.append({
            'id': cid,
            'name': m.group(2),
            'url': m.group(3),
            'desc': desc,
            'category': m.group(5),
            'is_translated': has_new,
            'is_chinese': is_zh,
        })
    return cards


def main():
    print("📂 读 v3.3.html 提取卡片...", file=sys.stderr)
    cards = parse_v3_html(INPUT_HTML)
    print(f"  找到 {len(cards)} 张唯一卡片", file=sys.stderr)

    # 找出失败（未翻译且不是中文）
    failed = [c for c in cards if not c['is_translated'] and not c['is_chinese']]
    print(f"  本轮重试: {len(failed)} 条", file=sys.stderr)

    if not failed:
        print(ok_msg("无失败需要重试")), file=sys.stderr)
        return

    # 逐条翻译
    for i, c in enumerate(failed, 1):
        print(f"\n[{i}/{len(failed)}] {c['name']}...", file=sys.stderr)
        print(f"  原文: {c['desc'][:60]}...", file=sys.stderr)

        translated = translate_with_claude_cli(c['desc'])
        print(f"  译文: {translated}", file=sys.stderr)

        c['desc'] = translated
        c['is_translated'] = True

    # 输出 v3.4 HTML（直接修改 v3.3 的失败处）
    html = INPUT_HTML.read_text(encoding='utf-8')
    for c in failed:
        # 替换原 desc 属性 + 加 🆕 标记
        old_pattern = re.compile(
            rf'(<input[^>]+data-id="{re.escape(c["id"])}"[^>]*\s*data-desc=)"[^"]+"',
            re.DOTALL
        )
        safe_desc = c['desc'].replace('"', '&quot;')
        html, count = old_pattern.subn(rf'\1"{safe_desc}"', html)
        if count:
            # 在 card-name 后加 🆕 标记
            html = html.replace(
                f'class="card-name" target="_blank">{c["name"]}</a>',
                f'class="card-name" target="_blank">{c["name"]}</a><span class="card-tag-new">🆕 译</span>'
            )

    # 更新标题 + 元数据
    html = html.replace(
        '<title>🎯 B2B 出海 Skill 精选 v3.3（中文版）</title>',
        '<title>🎯 B2B 出海 Skill 精选 v3.4（中文完整版）</title>'
    )

    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(ok_msg(f"已写入 {OUTPUT_HTML}", file=sys.stderr)


if __name__ == '__main__':
    main()