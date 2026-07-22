#!/usr/bin/env python
"""
expand_v32.py - v3.2 言简意赅：截短 description 到第一句（≤ 80 字），中文优先

读 v3-refined.html → 提取 152 张卡片 → 截短 description → 输出 v3.2 HTML
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

from _shared import CSS_VARS

INPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3-refined.html'
OUTPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.2.html'

MAX_DESC_LEN = 80  # 字符上限


def truncate_desc(desc):
    """截短到第一句，≤ 80 字符。

    规则：
    1. 找第一个句末符号（. ! ? ; 。 ！ ？ ）切第一句
    2. 若第一句 > 80 字，硬截到 80 字 + "..."
    3. 中文优先：跳过英文括号说明
    """
    desc = desc.strip()

    # 找第一个句号/问号/感叹号/分号
    m = re.search(r'[.!?;,。！？；]', desc)
    if m:
        first = desc[:m.end()].strip()
    else:
        first = desc

    # 去掉括号补充内容（更紧凑）
    first = re.sub(r'\s*\([^)]*\)\s*', ' ', first).strip()

    # 长度检查
    if len(first) > MAX_DESC_LEN:
        # 截到 78 字 + "..."
        first = first[:MAX_DESC_LEN - 2].rstrip() + '...'

    return first


def parse_v3_html():
    """从 v3-refined.html 提取所有卡片"""
    html = INPUT_HTML.read_text(encoding='utf-8')
    cards = []
    pattern = re.compile(
        r'<input type="checkbox" class="card-checkbox"\s*'
        r'data-id="([^"]+)"\s*'
        r'data-name="([^"]+)"\s*'
        r'data-url="([^"]+)"\s*'
        r'data-desc="([^"]+)"\s*'
        r'data-category="([^"]+)"',
        re.DOTALL
    )
    for m in pattern.finditer(html):
        cards.append({
            'id': m.group(1),
            'name': m.group(2),
            'url': m.group(3),
            'desc': m.group(4).replace('&#39;', "'").replace('&quot;', '"'),
            'category': m.group(5),
        })
    return cards


def render_html(cards):
    """生成 v3.2 HTML（用截短的 description）"""
    # 按 category 分组
    by_category = defaultdict(list)
    for c in cards:
        # 截短 description
        c['short_desc'] = truncate_desc(c['desc'])
        by_category[c['category']].append(c)

    total = len(cards)
    lines = ['<!DOCTYPE html>', '<html lang="zh-CN"><head>',
             '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
             '<title>🎯 B2B 出海 Skill 精选 v3.2</title>',
             '<style>']
    lines.append(CSS_VARS)
    lines.append('</style></head><body>')
    lines.append('''
<div class="toolbar">
  <div class="toolbar-title">
    🎯 B2B 出海 Skills v3.2
    <span class="count-badge" id="count-badge" data-count="0">0</span>
    <span style="font-weight: 400; color: var(--text-muted); font-size: 0.85em;">已选</span>
  </div>
  <div class="toolbar-actions">
    <button class="btn" id="btn-select-all">☑️ 全选</button>
    <button class="btn" id="btn-clear">🗑️ 清空</button>
    <button class="btn primary" id="btn-copy-md" disabled>📋 复制 MD</button>
    <button class="btn primary" id="btn-download-md" disabled>⬇️ MD</button>
    <button class="btn" id="btn-copy-json" disabled>📋 JSON</button>
  </div>
</div>
<div class="toast" id="toast"></div>
<div class="container">
''')

    lines.append('''
<header>
  <h1>🎯 B2B 出海 Skill 精选 v3.2</h1>
  <div class="subtitle">简介言简意赅（≤ 80 字）· 按类别整理 · 编程类已排除</div>
  <div class="stats">
    <div class="stat"><div class="stat-num">''' + str(total) + '''</div><div class="stat-label">入选</div></div>
    <div class="stat"><div class="stat-num">''' + str(len(by_category)) + '''</div><div class="stat-label">类别</div></div>
  </div>
</header>
<div class="notice">
  <div class="notice-title">💡 v3.2 改进</div>
  <ul>
    <li>每张卡片 description 截到 <strong>≤ 80 字第一句</strong>，一目了然</li>
    <li>剔除非核心信息（括号补充、技术细节）</li>
  </ul>
</div>
''')

    # 按类别输出
    for cat_name in ['内容创作', '营销推广', '翻译出海', '效率办公', '销售客户',
                     'HR 招聘', '财务行政', '数据分析', '客户支持', '产品设计',
                     '学习研究', 'AI 创作', '其他']:
        skills = by_category.get(cat_name, [])
        if not skills:
            continue
        skills_sorted = sorted(skills, key=lambda x: -len(x['short_desc']))

        lines.append('''
<section>
  <div class="cat-header">
    <span class="cat-badge">''' + cat_name + '''</span>
    <span class="cat-count">''' + str(len(skills)) + ''' 个</span>
  </div>
  <div class="cards">
''')
        for s in skills_sorted:
            safe_name = s['name'].replace('"', '&quot;').replace("'", '&#39;')
            safe_desc = s['short_desc'].replace('"', '&quot;').replace("'", '&#39;').replace('|', '\\|')
            lines.append('''
    <div class="card">
      <input type="checkbox" class="card-checkbox"
        data-id="''' + safe_name + '''"
        data-name="''' + safe_name + '''"
        data-url="''' + s['url'] + '''"
        data-desc="''' + safe_desc + '''"
        data-category="''' + cat_name + '''">
      <a href="''' + s['url'] + '''" class="card-name" target="_blank">''' + s['name'] + '''</a>
      <div class="card-desc">''' + s['short_desc'] + '''</div>
      <div class="card-meta">📂 ''' + cat_name + '''</div>
    </div>
''')
        lines.append('  </div>\n</section>')

    lines.append('''
<footer>
  <p>v3.2 · description 言简意赅（≤ 80 字）</p>
  <p>生成时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M') + '''</p>
</footer>
</div>

<script>
const STORAGE_KEY = 'b2b-skills-v32.selected';
const ALL_CHECKBOXES = () => Array.from(document.querySelectorAll('.card-checkbox'));
function getSelected() { return ALL_CHECKBOXES().filter(cb => cb.checked); }
function updateUI() {
  const n = getSelected().length;
  const badge = document.getElementById('count-badge');
  badge.textContent = n; badge.dataset.count = n;
  ['btn-copy-md', 'btn-download-md', 'btn-copy-json']
    .forEach(id => document.getElementById(id).disabled = n === 0);
  ALL_CHECKBOXES().forEach(cb => {
    cb.closest('.card').classList.toggle('selected', cb.checked);
  });
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(getSelected().map(cb => cb.dataset.id))); } catch (e) {}
}
function restoreSelection() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const ids = new Set(JSON.parse(raw));
    ALL_CHECKBOXES().forEach(cb => { if (ids.has(cb.dataset.id)) cb.checked = true; });
  } catch (e) {}
}
document.addEventListener('change', e => { if (e.target.classList.contains('card-checkbox')) updateUI(); });
document.addEventListener('click', e => {
  if (e.target.closest('a')) return;
  const card = e.target.closest('.card');
  if (!card) return;
  const cb = card.querySelector('.card-checkbox');
  if (!cb) return;
  cb.checked = !cb.checked; updateUI();
});
document.getElementById('btn-select-all').addEventListener('click', () => {
  ALL_CHECKBOXES().forEach(cb => cb.checked = true); updateUI();
});
document.getElementById('btn-clear').addEventListener('click', () => {
  ALL_CHECKBOXES().forEach(cb => cb.checked = false); updateUI();
});

function getSelectedData() {
  return getSelected().map(cb => ({
    id: cb.dataset.id, name: cb.dataset.name, url: cb.dataset.url,
    category: cb.dataset.category, desc: cb.dataset.desc,
  }));
}
function buildMarkdown(data) {
  const lines = ['# 🎯 B2B 出海精选 Skills (v3.2)', '',
    `> 共 ${data.length} 个 · ${new Date().toISOString().slice(0,10)}`, ''];
  const byCat = {};
  data.forEach(s => { (byCat[s.category] = byCat[s.category] || []).push(s); });
  Object.keys(byCat).forEach(cat => {
    lines.push(`## ${cat}（${byCat[cat].length} 个）`); lines.push('');
    byCat[cat].forEach(s => {
      lines.push(`- **${s.name}** — ${s.desc.slice(0,100)} ([link](${s.url}))`);
    });
    lines.push('');
  });
  return lines.join('\\n');
}
function buildJSON(data) {
  return JSON.stringify({exported_at: new Date().toISOString(), count: data.length,
    source: 'candidates-v3.2.html', skills: data}, null, 2);
}
function showToast(msg, isError = false) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.toggle('error', isError);
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}
async function copyToClipboard(text) {
  try { await navigator.clipboard.writeText(text); return true; }
  catch (e) {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); document.body.removeChild(ta); return true; }
    catch (e2) { document.body.removeChild(ta); return false; }
  }
}
function downloadFile(content, filename, mimeType = 'text/plain') {
  const blob = new Blob([content], {type: mimeType + ';charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
document.getElementById('btn-copy-md').addEventListener('click', async () => {
  const ok = await copyToClipboard(buildMarkdown(getSelectedData()));
  showToast(ok ? `✅ 已复制 ${getSelected().length} 个（MD）` : '❌ 复制失败', !ok);
});
document.getElementById('btn-download-md').addEventListener('click', () => {
  downloadFile(buildMarkdown(getSelectedData()), `b2b-skills-${new Date().toISOString().slice(0,10)}.md`);
  showToast(`⬇️ 已下载 MD`);
});
document.getElementById('btn-copy-json').addEventListener('click', async () => {
  const ok = await copyToClipboard(buildJSON(getSelectedData()));
  showToast(ok ? '✅ 已复制 JSON' : '❌ 复制失败', !ok);
});
restoreSelection(); updateUI();
</script>
</body></html>
''')

    return ''.join(lines)


def main():
    print("📂 读 v3-refined.html 提取卡片...", file=sys.stderr)
    cards = parse_v3_html()
    print(f"  找到 {len(cards)} 张卡片", file=sys.stderr)

    # 截短 description
    print(f"  截短每条 description 到 ≤ {MAX_DESC_LEN} 字...", file=sys.stderr)
    for c in cards:
        c['short_desc'] = truncate_desc(c['desc'])

    # 抽样看效果
    print("\n=== 抽样 5 条 ===", file=sys.stderr)
    for c in cards[:5]:
        print(f"\n  原: {c['desc'][:100]}", file=sys.stderr)
        print(f"  短: {c['short_desc']}", file=sys.stderr)

    # 输出 HTML
    html = render_html(cards)
    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(ok_msg(f"已写入 {OUTPUT_HTML}（{len(html)} 字符）", file=sys.stderr)


if __name__ == '__main__':
    main()