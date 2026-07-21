#!/usr/bin/env python
"""
dedup_v35.py - 用 BeautifulSoup 去重 v3.4.html 重复 skill，输出 v3.5.html

策略：
- 用 BS4 解析 DOM（不靠脆弱正则）
- 按 (name, url) 唯一
- 保留 desc 最长的版本
"""
import re, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

INPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.4.html'
OUTPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.5.html'


def parse_with_bs4(html):
    """用 BS4 解析所有卡片，保留原始 HTML"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    cards = []
    for div in soup.find_all('div', class_='card'):
        cb = div.find('input', class_='card-checkbox')
        if not cb:
            continue
        cards.append({
            'html': str(div),  # 保留原始 HTML 块
            'id': cb.get('data-id', ''),
            'name': cb.get('data-name', ''),
            'url': cb.get('data-url', ''),
            'desc': cb.get('data-desc', '').replace('&#39;', "'").replace('&quot;', '"'),
            'category': cb.get('data-category', ''),
        })
    return cards


def main():
    print("📂 读 v3.4.html 用 BS4 解析...", file=sys.stderr)
    html = INPUT_HTML.read_text(encoding='utf-8')
    cards = parse_with_bs4(html)
    print(f"  原始: {len(cards)} 张卡片", file=sys.stderr)

    # 按 (name, url) 去重，保留 desc 最长
    by_key = {}
    for c in cards:
        key = (c['name'], c['url'])
        if key not in by_key or len(c['desc']) > len(by_key[key]['desc']):
            by_key[key] = c

    deduped = list(by_key.values())
    print(f"  去重后: {len(deduped)} 个 unique skill", file=sys.stderr)
    print(f"  移除重复: {len(cards) - len(deduped)} 条", file=sys.stderr)

    # 替换 HTML：用 BS4 重建
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # ⭐ 关键修复：记录要保留的 div 引用（不是 key 集合！）
    keep_divs = set()  # Python 对象 id 集合
    for c in deduped:
        # c 来自 cards 列表，每个是 soup.find_all 返回的 div
        keep_divs.add(id(c['html_obj']) if 'html_obj' in c else id(c))
    # 实际上 c 是 dict，没 div 引用；用 cards 原始 div
    keep_divs = set()
    for c in cards:
        cb_skill_id = None
        # 找匹配的 div——通过 (name, url) key
        key = (c['name'], c['url'])
        if key in by_key and by_key[key] is c:  # by_key 选了这个
            # 但 c 是 dict 不是 div object
            pass

    # 更简单方案：保留 by_key 选中的那些 div 引用
    # 重做：用 soup 解析得到 div 列表，直接保留 best 的
    cards_with_div = []
    for d in soup.find_all('div', class_='card'):
        cb = d.find('input', class_='card-checkbox')
        if cb:
            cards_with_div.append({
                'div': d,
                'id': cb.get('data-id', ''),
                'name': cb.get('data-name', ''),
                'url': cb.get('data-url', ''),
                'desc': cb.get('data-desc', ''),
            })

    by_key_div = {}
    for c in cards_with_div:
        key = (c['name'], c['url'])
        if key not in by_key_div or len(c['desc']) > len(by_key_div[key]['desc']):
            by_key_div[key] = c

    keep_divs = set(id(c['div']) for c in by_key_div.values())

    # 删除其他重复
    deleted = 0
    for c in cards_with_div:
        if id(c['div']) not in keep_divs:
            c['div'].decompose()
            deleted += 1
    print(f"  实际删除 div: {deleted}", file=sys.stderr)

    # 更新标题
    title = soup.find('title')
    if title:
        title.string = '🎯 B2B 出海 Skill 精选 v3.5（去重版）'

    # 更新 header 统计（找出"总入选"）
    header_stats = soup.find('header')
    if header_stats:
        # 找 <div class="stat-num"> 的第一个
        first_stat = header_stats.find('div', class_='stat-num')
        if first_stat:
            first_stat.string = str(len(deduped))

    # 更新 notice 里的数字（如有 "总展开"）
    notice = soup.find('div', class_='notice')
    if notice:
        # 找数字
        for div in notice.find_all('div', class_='stat-num'):
            div.string = str(len(deduped))

    # 输出
    remaining = soup.find_all('div', class_='card')
    print(f"  soup 剩余 div: {len(remaining)}", file=sys.stderr)
    OUTPUT_HTML.write_text(str(soup), encoding='utf-8')
    print(f"\n✅ 已写入 {OUTPUT_HTML}", file=sys.stderr)

    # 验证：重新读输出的 HTML 再查（不能用之前的 soup 状态）
    with open(OUTPUT_HTML, encoding='utf-8') as f:
        final_soup = BeautifulSoup(f.read(), 'html.parser')
    final_cards = final_soup.find_all('div', class_='card')
    zh = sum(1 for c in final_cards
             if c.find('input', class_='card-checkbox')
             and re.search(r'[一-鿿]', c.find('input', class_='card-checkbox').get('data-desc', '')))
    print(f"📊 最终: {len(final_cards)} 张卡片 / {zh} 中文", file=sys.stderr)

    # 抽查几个
    print(f"\n抽样（前 5 个）:")
    for c in final_cards[:5]:
        cb = c.find('input', class_='card-checkbox')
        if cb:
            print(f"  - {cb.get('data-name')}: {cb.get('data-desc')[:60]}")


if __name__ == '__main__':
    main()