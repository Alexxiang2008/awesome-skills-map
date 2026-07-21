#!/usr/bin/env python
"""
expand_v33.py - 用 LLM 把 v3.2 的英文 description 翻译成中文

依赖：
- claude CLI（已安装在 PATH: /d/nvm4w/nodejs/claude）
- 或 anthropic SDK + ANTHROPIC_API_KEY

工作流：
1. 读 v3.2.html → 提取 152 条 description
2. 判断是否中文（含 [一-鿿]）
3. 英文 → 用 claude CLI 翻译（Prompt：简洁中文 ≤ 50 字）
4. 已中文 → 保留
5. 输出 v3.3.html
"""
import re, sys, json, subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import concurrent.futures

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

INPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.2.html'
OUTPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.3.html'
CACHE_FILE = Path(__file__).parent / '.translate_cache.json'


def is_chinese(text):
    """判断是否中文（含中文字符）"""
    return bool(re.search(r'[一-鿿]', text))


def translate_with_claude_cli(text):
    """用 Git Bash + claude CLI 翻译英文 → 简洁中文"""
    # 转义单/双引号避免 bash 命令破坏
    safe_text = text.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`').replace('\\', '\\\\')
    safe_prompt = "翻译成中文（≤50字，只输出中文，不要任何解释）"
    cmd = f'echo "{safe_text}" | claude -p "{safe_prompt}"'
    try:
        r = subprocess.run(
            ['bash', '-c', cmd],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=30
        )
        result = r.stdout.strip()
        # 去除可能的引号
        result = re.sub(r'^["""\']|["""\']$', '', result).strip()
        # 截短（防止超过 80 字）
        if len(result) > 80:
            result = result[:78] + '...'
        return result
    except subprocess.TimeoutExpired:
        return text[:50]
    except Exception as e:
        print(f"  ⚠️ 翻译异常: {e}", file=sys.stderr)
        return text[:50]


def parse_v3_html():
    """从 v3.2.html 提取卡片"""
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
    by_category = defaultdict(list)
    for c in cards:
        by_category[c['category']].append(c)

    total = len(cards)
    zh_count = sum(1 for c in cards if c.get('is_translated', False))

    lines = ['<!DOCTYPE html>', '<html lang="zh-CN"><head>',
             '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
             '<title>🎯 B2B 出海 Skill 精选 v3.3（中文版）</title>',
             '<style>']
    # 复用 v3.2 CSS
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
  text-decoration: none; display: inline-block; word-break: break-all; padding-right: 20px; }
.card-name:hover { text-decoration: underline; }
.card-desc { font-size: 0.95em; color: var(--text); line-height: 1.55; flex: 1; }
.card-meta { font-size: 0.72em; color: var(--text-muted); }
.card-tag-new { background: var(--accent); color: white; padding: 1px 6px;
  border-radius: 3px; font-size: 0.7em; margin-left: 6px; }
footer { text-align: center; padding: 24px 20px; color: var(--text-muted);
  font-size: 0.85em; border-top: 1px solid var(--border); margin-top: 32px; }
@media (max-width: 640px) { header h1 { font-size: 1.6em; } .cards { grid-template-columns: 1fr; }
  .toolbar { padding: 8px 12px; flex-wrap: wrap; } }
    ''')
    lines.append('</style></head><body>')
    lines.append('''
<div class="toolbar">
  <div class="toolbar-title">
    🎯 B2B 出海 Skills v3.3
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
  <h1>🎯 B2B 出海 Skill 精选 v3.3</h1>
  <div class="subtitle">所有 description 已翻译成中文 · 简洁（≤80字）· B2B 出海老板/员工日常使用</div>
  <div class="stats">
    <div class="stat"><div class="stat-num">''' + str(total) + '''</div><div class="stat-label">总入选</div></div>
    <div class="stat"><div class="stat-num">''' + str(zh_count) + '''</div><div class="stat-label">本次翻译</div></div>
    <div class="stat"><div class="stat-num">''' + str(len(by_category)) + '''</div><div class="stat-label">类别</div></div>
  </div>
</header>
<div class="notice">
  <div class="notice-title">🌏 v3.3 改进</div>
  <ul>
    <li>所有英文 description 已翻译成简体中文（LLM 调用）</li>
    <li>已中文的 description 保留</li>
    <li>描述中带 🆕 标记 = 本次新翻译</li>
  </ul>
</div>
''')

    for cat_name in ['内容创作', '营销推广', '翻译出海', '效率办公', '销售客户',
                     'HR 招聘', '财务行政', '数据分析', '客户支持', '产品设计',
                     '学习研究', 'AI 创作', '其他']:
        skills = by_category.get(cat_name, [])
        if not skills:
            continue
        # 翻译后的优先排前
        skills_sorted = sorted(skills, key=lambda x: (not x.get('is_translated', False), -len(x['desc'])))

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
            safe_desc = s['desc'].replace('"', '&quot;').replace("'", '&#39;').replace('|', '\\|')
            new_tag = '<span class="card-tag-new">🆕 译</span>' if s.get('is_translated', False) else ''
            lines.append('''
    <div class="card">
      <input type="checkbox" class="card-checkbox"
        data-id="''' + safe_name + '''"
        data-name="''' + safe_name + '''"
        data-url="''' + s['url'] + '''"
        data-desc="''' + safe_desc + '''"
        data-category="''' + cat_name + '''">
      <a href="''' + s['url'] + '''" class="card-name" target="_blank">''' + s['name'] + '''</a>''' + new_tag + '''
      <div class="card-desc">''' + s['desc'] + '''</div>
      <div class="card-meta">📂 ''' + cat_name + '''</div>
    </div>
''')
        lines.append('  </div>\n</section>')

    lines.append('''
<footer>
  <p>v3.3 · 英文 description 已翻译为简体中文</p>
  <p>生成时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M') + '''</p>
</footer>
</div>

<script>
const STORAGE_KEY = 'b2b-skills-v33.selected';
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
  const lines = ['# 🎯 B2B 出海精选 Skills (v3.3 中文)', '',
    `> 共 ${data.length} 个 · ${new Date().toISOString().slice(0,10)}`, ''];
  const byCat = {};
  data.forEach(s => { (byCat[s.category] = byCat[s.category] || []).push(s); });
  Object.keys(byCat).forEach(cat => {
    lines.push(`## ${cat}（${byCat[cat].length} 个）`); lines.push('');
    byCat[cat].forEach(s => {
      lines.push(`- **${s.name}** — ${s.desc} ([link](${s.url}))`);
    });
    lines.push('');
  });
  return lines.join('\\n');
}
function buildJSON(data) {
  return JSON.stringify({exported_at: new Date().toISOString(), count: data.length,
    source: 'candidates-v3.3.html', skills: data}, null, 2);
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
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['cli', 'sdk'], default='cli', help='翻译模式')
    p.add_argument('--limit', type=int, default=0, help='最多翻译多少条（0=全部）')
    p.add_argument('--parallel', type=int, default=4, help='并行数（cli 模式）')
    p.add_argument('--no-cache', action='store_true')
    args = p.parse_args()

    print("📂 读 v3.2.html 提取卡片...", file=sys.stderr)
    cards = parse_v3_html()
    print(f"  找到 {len(cards)} 张卡片", file=sys.stderr)

    # 统计
    en_cards = [c for c in cards if not is_chinese(c['desc'])]
    zh_cards = [c for c in cards if is_chinese(c['desc'])]
    print(f"  英文: {len(en_cards)} (需翻译)", file=sys.stderr)
    print(f"  中文: {len(zh_cards)} (保留)", file=sys.stderr)

    # 翻译
    cache = {} if args.no_cache else (json.loads(CACHE_FILE.read_text(encoding='utf-8'))
                                       if CACHE_FILE.exists() else {})
    translated = 0
    to_translate = en_cards[:args.limit] if args.limit else en_cards

    print(f"\n🌐 翻译模式: {args.mode}", file=sys.stderr)
    print(f"   待翻译: {len(to_translate)} 条", file=sys.stderr)

    if args.mode == 'cli':
        # 用 subprocess + 并行调 claude CLI
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as ex:
            futures = {}
            for c in to_translate:
                if c['desc'] in cache:
                    c['desc'] = cache[c['desc']]
                    c['is_translated'] = True
                    translated += 1
                    continue
                future = ex.submit(translate_with_claude_cli, c['desc'])
                futures[future] = c

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                c = futures[future]
                try:
                    translated_text = future.result()
                    # 保存到缓存
                    old_desc = c['desc']
                    if is_chinese(translated_text) and len(translated_text) > 0:
                        cache[old_desc] = translated_text
                        c['desc'] = translated_text
                        c['is_translated'] = True
                        translated += 1
                    else:
                        # 翻译失败，保持原文
                        c['is_translated'] = False
                except Exception as e:
                    c['is_translated'] = False
                # 进度
                if translated % 10 == 0:
                    print(f"  ✓ {translated}/{len(to_translate)} 条已翻译", file=sys.stderr)
    else:
        # SDK 模式
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("❌ --mode sdk 需要 ANTHROPIC_API_KEY 环境变量", file=sys.stderr)
            sys.exit(1)
        for c in to_translate:
            if c['desc'] in cache:
                c['desc'] = cache[c['desc']]
                c['is_translated'] = True
                continue
            new = translate_with_anthropic_sdk(c['desc'], api_key)
            if is_chinese(new):
                cache[c['desc']] = new
                c['desc'] = new
                c['is_translated'] = True
            translated += 1

    # 保存缓存
    CACHE_FILE.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding='utf-8')

    # 输出 HTML
    html = render_html(cards)
    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(f"\n✅ 已写入 {OUTPUT_HTML}（{len(html)} 字符）", file=sys.stderr)
    print(f"📊 翻译完成: {translated} 条", file=sys.stderr)


if __name__ == '__main__':
    main()