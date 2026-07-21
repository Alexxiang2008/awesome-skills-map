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
    lines.append('''
:root { --bg: #0d1117; --bg-card: #161b22; --bg-card-hover: #1f2530; --bg-card-selected: #1c2c4a;
  --border: #30363d; --border-selected: #58a6ff; --text: #c9d1d9; --text-muted: #8b949e;
  --accent: #58a6ff; --success: #3fb950; --tag-bg: #21262d; --toolbar-h: 64px; }
@media (prefers-color-scheme: light) { :root { --bg: #fff; --bg-card: #f6f8fa; --bg-card-hover: #eaeef2;
  --bg-card-selected: #dbeafe; --border: #d0d7de; --border-selected: #0969da; --text: #1f2328;
  --text-muted: #656d76; --accent: #0969da; --success: #1a7f37; --tag-bg: #eaeef2; } }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.55; padding-top: var(--toolbar-h); }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
.toolbar { position: fixed; top: 0; left: 0; right: 0; height: var(--toolbar-h);
  background: rgba(13,17,23,0.92); backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border); display: flex; align-items: center;
  justify-content: space-between; padding: 0 24px; z-index: 100; gap: 12px; }
@media (prefers-color-scheme: light) { .toolbar { background: rgba(255,255,255,0.92); } }
.toolbar-title { font-weight: 600; font-size: 0.95em; display: flex; align-items: center; gap: 8px; }
.count-badge { background: var(--accent); color: white; padding: 3px 10px; border-radius: 12px;
  font-size: 0.85em; font-weight: 700; min-width: 36px; text-align: center; }
.count-badge[data-count="0"] { background: var(--text-muted); }
.toolbar-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn { background: var(--bg-card); color: var(--text); border: 1px solid var(--border);
  padding: 8px 14px; border-radius: 6px; font-size: 0.85em; cursor: pointer;
  transition: all 0.15s; font-weight: 500; white-space: nowrap; }
.btn:hover { background: var(--bg-card-hover); border-color: var(--accent); }
.btn.primary { background: var(--accent); color: white; border-color: var(--accent); }
.btn.primary:hover { filter: brightness(1.1); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.toast { position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%) translateY(100px);
  background: var(--success); color: white; padding: 12px 24px; border-radius: 8px;
  z-index: 200; transition: transform 0.3s ease; font-weight: 500; font-size: 0.9em; }
.toast.show { transform: translateX(-50%) translateY(0); }
.toast.error { background: #f85149; }
header { text-align: center; padding: 32px 20px; background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
  border-radius: 16px; margin-bottom: 24px; color: white;
  box-shadow: 0 8px 32px rgba(31,111,235,0.3); }
header h1 { font-size: 2.2em; margin-bottom: 8px; }
header .subtitle { font-size: 1em; opacity: 0.95; margin-bottom: 12px; }
header .stats { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; }
header .stat { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
  padding: 10px 16px; border-radius: 10px; min-width: 90px; }
header .stat-num { font-size: 1.5em; font-weight: 700; }
header .stat-label { font-size: 0.85em; opacity: 0.9; }
.notice { background: var(--bg-card); border-left: 4px solid var(--accent);
  padding: 14px 20px; border-radius: 0 8px 8px 0; margin-bottom: 20px; }
.notice-title { font-weight: 600; margin-bottom: 6px; color: var(--accent); font-size: 0.95em; }
.notice ul { padding-left: 24px; color: var(--text-muted); font-size: 0.85em; }
.notice li { margin-bottom: 4px; }
.cat-header { display: flex; align-items: center; gap: 12px; margin: 24px 0 12px;
  padding-bottom: 6px; border-bottom: 2px solid var(--border); }
.cat-badge { display: inline-block; padding: 5px 12px; border-radius: 6px;
  background: var(--accent); color: white; font-weight: 700; font-size: 0.9em; }
.cat-count { color: var(--text-muted); font-size: 0.85em; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 14px; margin-bottom: 14px; }
.card { background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 14px 16px 14px 16px; padding-right: 50px;
  transition: all 0.2s; position: relative; cursor: pointer;
  display: flex; flex-direction: column; gap: 6px; min-height: 110px; }
.card:hover { transform: translateY(-2px); background: var(--bg-card-hover);
  border-color: var(--accent); box-shadow: 0 4px 16px rgba(31,111,235,0.15); }
.card.selected { background: var(--bg-card-selected); border-color: var(--border-selected);
  box-shadow: 0 0 0 1px var(--border-selected); }
.card-checkbox { position: absolute; top: 10px; right: 10px; width: 20px; height: 20px;
  cursor: pointer; z-index: 5; accent-color: var(--accent); }
.card-name { font-size: 1em; font-weight: 600; color: var(--accent);
  text-decoration: none; display: inline-block; word-break: break-all;
  padding-right: 20px; }
.card-name:hover { text-decoration: underline; }
.card-desc { font-size: 0.88em; color: var(--text); line-height: 1.45; flex: 1; }
.card-meta { font-size: 0.72em; color: var(--text-muted); }
footer { text-align: center; padding: 24px 20px; color: var(--text-muted);
  font-size: 0.85em; border-top: 1px solid var(--border); margin-top: 32px; }
@media (max-width: 640px) { header h1 { font-size: 1.6em; } .cards { grid-template-columns: 1fr; }
  .toolbar { padding: 8px 12px; flex-wrap: wrap; } }
    ''')
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
    print(f"\n✅ 已写入 {OUTPUT_HTML}（{len(html)} 字符）", file=sys.stderr)


if __name__ == '__main__':
    main()