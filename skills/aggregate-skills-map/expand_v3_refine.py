#!/usr/bin/env python
"""
expand_v3_refine.py - 二次过滤（从 candidates-v3.html 重新分类，不重新拉数据）

问题：v3 中 EXCLUDE_RULES 用 'api' 等宽关键词，误伤了"公众号 API"等 B2B 正经工具
解决：读 v3 HTML 的 182 个卡片，按更精确的"编程核心"模式重过滤
"""
import re, sys, json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

INPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.html'
OUTPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3-refined.html'

# 更精确的排除（核心编程 + 技术对象，不误伤正当 API）
# 必须同时包含"动作"和"对象"才排除
EXCLUDE_PATTERNS_STRICT = [
    # 编程动作 + 技术对象
    (r'\b(code|debug|compile|parse|test|deploy|build|run)\b.*\b(codebase|git|repository|repo|pull request|PR|build|test|unit test)',
     '编程动作+技术对象'),
    (r'\b(developer|dev environment|ide|terminal|cli tool)\b',
     '开发者工具'),
    (r'\b(framework|sdk|library|api client|http client)\b',
     '技术框架/SDK'),
    (r'\b(openapi|graphql|grpc|webhook|rest api)\b',
     'API 技术'),
    (r'\b(shipped|ship a|deploy to production|production deployment)\b',
     '代码 ship 流程'),
    (r'\b(docker|kubernetes|k8s|terraform|aws|gcp|azure|ci/cd|cicd)\b',
     '基础设施'),
    (r'\b(codebase|git workflow|pull request|merge conflict|version control|rebase)\b',
     '代码管理'),
    (r'\b(refactor|debugging|unit test|integration test|e2e test|tdd|bdd)\b',
     '软件测试'),
    (r'\b(typescript|javascript|python |rust |golang|^java|react |vue |angular)\b',
     '编程语言'),
    (r'\b(html playground|code explanation|technical writing|code generation)\b',
     '代码生成'),
    (r'\b(database|sql|orm|migration|schema design)\b',
     '数据库'),
    (r'\b(observability|monitoring|tracing|logging|sentry|prometheus)\b',
     '运维监控'),
    (r'\b(security audit|penetration test|vulnerability scan|xss|csrf)\b',
     '安全/渗透'),
    (r'\b(mcp server|agent orchestration|agent harness|multi-agent)\b',
     'Agent 框架'),
    (r'\b(linux kernel|embedded|firmware|iot)\b',
     '系统编程'),
]

# 保留（正当 B2B 工具用法，避免误伤）
KEEP_OVERRIDE = [
    'Posts content to',  # 公众号发布
    'posts to social',  # 社媒发布
    'publish to',
    'create.*article',
    'create.*blog',
    'create.*post',
    'generate.*content',
    'create.*video',
    'create.*image',
    'generate.*image',
]


def is_excluded_strict(desc):
    """严格排除判断"""
    desc_lower = desc.lower()

    # 1. 保留白名单优先（防止误伤）
    for kw in KEEP_OVERRIDE:
        if re.search(kw, desc_lower):
            return False, None

    # 2. 检查严格排除模式
    for pattern, reason in EXCLUDE_PATTERNS_STRICT:
        if re.search(pattern, desc_lower, re.IGNORECASE):
            return True, reason

    return False, None


def parse_v3_html():
    """从 candidates-v3.html 提取所有卡片数据"""
    html = INPUT_HTML.read_text(encoding='utf-8')
    # 找 section → category
    cards = []
    # 匹配 <input ... data-...> 和后续 <a> name + <div> desc
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


def render_html(filtered, excluded_log, total):
    """生成 v3-refined.html"""
    lines = ['<!DOCTYPE html>', '<html lang="zh-CN"><head>',
             '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
             '<title>🎯 B2B 出海 Skills 精选 v3.1（精细过滤）</title>',
             '<style>']
    # CSS（与 v3 相同，简化版）
    lines.append('''
:root { --bg: #0d1117; --bg-card: #161b22; --bg-card-hover: #1f2530; --bg-card-selected: #1c2c4a;
  --border: #30363d; --border-selected: #58a6ff; --text: #c9d1d9; --text-muted: #8b949e;
  --accent: #58a6ff; --success: #3fb950; --tag-bg: #21262d; --toolbar-h: 64px; }
@media (prefers-color-scheme: light) { :root { --bg: #fff; --bg-card: #f6f8fa; --bg-card-hover: #eaeef2;
  --bg-card-selected: #dbeafe; --border: #d0d7de; --border-selected: #0969da; --text: #1f2328;
  --text-muted: #656d76; --accent: #0969da; --success: #1a7f37; --tag-bg: #eaeef2; } }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6; padding-top: var(--toolbar-h); }
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
  box-shadow: 0 8px 24px rgba(0,0,0,0.3); z-index: 200;
  transition: transform 0.3s ease; font-weight: 500; font-size: 0.9em; }
.toast.show { transform: translateX(-50%) translateY(0); }
.toast.error { background: #f85149; }
header { text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
  border-radius: 16px; margin-bottom: 32px; color: white;
  box-shadow: 0 8px 32px rgba(31,111,235,0.3); }
header h1 { font-size: 2.5em; margin-bottom: 12px; }
header .subtitle { font-size: 1.1em; opacity: 0.95; margin-bottom: 16px; }
header .stats { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; margin-top: 20px; }
header .stat { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
  padding: 12px 20px; border-radius: 12px; min-width: 100px; }
header .stat-num { font-size: 1.8em; font-weight: 700; }
header .stat-label { font-size: 0.85em; opacity: 0.9; }
.notice { background: var(--bg-card); border-left: 4px solid var(--accent);
  padding: 16px 20px; border-radius: 0 8px 8px 0; margin-bottom: 24px; }
.notice-title { font-weight: 600; margin-bottom: 8px; color: var(--accent); }
.notice ul { padding-left: 24px; color: var(--text-muted); }
.notice li { margin-bottom: 6px; }
.category-header { display: flex; align-items: center; gap: 12px; margin: 32px 0 16px;
  padding-bottom: 8px; border-bottom: 2px solid var(--border); }
.category-badge { display: inline-block; padding: 6px 14px; border-radius: 6px;
  background: var(--accent); color: white; font-weight: 700; font-size: 0.9em; }
.category-count { color: var(--text-muted); font-size: 0.85em; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px; margin-bottom: 16px; }
.card { background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 18px; padding-right: 56px;
  transition: all 0.2s; position: relative; cursor: pointer; }
.card:hover { transform: translateY(-2px); background: var(--bg-card-hover);
  border-color: var(--accent); box-shadow: 0 4px 16px rgba(31,111,235,0.15); }
.card.selected { background: var(--bg-card-selected); border-color: var(--border-selected);
  box-shadow: 0 0 0 1px var(--border-selected); }
.card-checkbox { position: absolute; top: 12px; right: 12px; width: 22px; height: 22px;
  cursor: pointer; z-index: 5; accent-color: var(--accent); }
.card-name { font-size: 1.1em; font-weight: 600; color: var(--accent);
  text-decoration: none; display: inline-block; margin-bottom: 8px; word-break: break-all; }
.card-name:hover { text-decoration: underline; }
.card-desc { font-size: 0.92em; color: var(--text); margin-bottom: 12px; line-height: 1.55;
  min-height: 60px; }
.card-meta { display: flex; gap: 8px; flex-wrap: wrap; font-size: 0.75em; color: var(--text-muted); }
footer { text-align: center; padding: 32px 20px; color: var(--text-muted);
  font-size: 0.85em; border-top: 1px solid var(--border); margin-top: 40px; }
@media (max-width: 640px) { header h1 { font-size: 1.8em; } .cards { grid-template-columns: 1fr; }
  .toolbar { padding: 8px 12px; flex-wrap: wrap; } }
    ''')
    lines.append('</style></head><body>')
    lines.append('''
<div class="toolbar">
  <div class="toolbar-title">
    🎯 B2B 出海 Skills v3.1
    <span class="count-badge" id="count-badge" data-count="0">0</span>
    <span style="font-weight: 400; color: var(--text-muted); font-size: 0.85em;">已选</span>
  </div>
  <div class="toolbar-actions">
    <button class="btn" id="btn-select-all">☑️ 全选</button>
    <button class="btn" id="btn-clear">🗑️ 清空</button>
    <button class="btn primary" id="btn-copy-md" disabled>📋 复制 MD</button>
    <button class="btn primary" id="btn-download-md" disabled>⬇️ 下载 MD</button>
    <button class="btn" id="btn-copy-json" disabled>📋 JSON</button>
    <button class="btn" id="btn-download-json" disabled>⬇️ JSON</button>
  </div>
</div>
<div class="toast" id="toast"></div>
<div class="container">
''')

    excl_total = sum(excluded_log.values())
    lines.append('''
<header>
  <h1>🎯 B2B 出海 Skills 精选 v3.1</h1>
  <div class="subtitle">v3 二次过滤（精细排除编程/技术类 + 保留公众号 API 等正当工具）</div>
  <div class="stats">
    <div class="stat"><div class="stat-num">''' + str(total) + '''</div><div class="stat-label">入选</div></div>
    <div class="stat"><div class="stat-num">''' + str(excl_total) + '''</div><div class="stat-label">本轮排除</div></div>
    <div class="stat"><div class="stat-num">''' + str(total + excl_total) + '''</div><div class="stat-label">原 v3 总数</div></div>
  </div>
</header>
<div class="notice">
  <div class="notice-title">🔧 v3.1 改进</div>
  <ul>
    <li><strong>更精确的排除</strong>：从关键词匹配改为"动作+对象"复合模式</li>
    <li><strong>保留白名单</strong>："Posts content to WeChat" 等正当 API 工具不被误伤</li>
    <li><strong>本轮排除 ''' + str(excl_total) + ''' 个</strong> 编程/技术类</li>
  </ul>
</div>
''')

    # 按类别输出
    for cat_name in ['内容创作', '营销推广', '翻译出海', '效率办公', '销售客户',
                     'HR 招聘', '财务行政', '数据分析', '客户支持', '产品设计',
                     '学习研究', 'AI 创作', '其他']:
        skills = filtered.get(cat_name, [])
        if not skills:
            continue
        skills_sorted = sorted(skills, key=lambda x: -len(x['desc']))

        lines.append('''
<section>
  <div class="category-header">
    <span class="category-badge">''' + cat_name + '''</span>
    <span class="category-count">''' + str(len(skills)) + ''' 个 skill</span>
  </div>
  <div class="cards">
''')
        for s in skills_sorted:
            safe_name = s['name'].replace('"', '&quot;').replace("'", '&#39;')
            safe_desc = s['desc'].replace('"', '&quot;').replace("'", '&#39;').replace('\n', ' ').replace('|', '\\|')
            lines.append('''
    <div class="card">
      <input type="checkbox" class="card-checkbox"
        data-id="''' + safe_name + '''"
        data-name="''' + safe_name + '''"
        data-url="''' + s['url'] + '''"
        data-desc="''' + safe_desc + '''"
        data-category="''' + cat_name + '''">
      <a href="''' + s['url'] + '''" class="card-name" target="_blank">''' + s['name'] + '''</a>
      <div class="card-desc">''' + s['desc'] + '''</div>
      <div class="card-meta"><span>📂 ''' + cat_name + '''</span></div>
    </div>
''')
        lines.append('  </div>\n</section>')

    lines.append('''
<footer>
  <p><strong>v3.1 二次过滤 · 保留正当 API 工具 + 排除编程</strong></p>
  <p>由 <code>expand_v3_refine.py</code> 从 v3 二次过滤生成</p>
  <p>生成时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M') + '''</p>
</footer>
</div>

<script>
const STORAGE_KEY = 'b2b-skills-v31.selected';
const ALL_CHECKBOXES = () => Array.from(document.querySelectorAll('.card-checkbox'));
function getSelected() { return ALL_CHECKBOXES().filter(cb => cb.checked); }
function updateUI() {
  const n = getSelected().length;
  const badge = document.getElementById('count-badge');
  badge.textContent = n; badge.dataset.count = n;
  ['btn-copy-md', 'btn-download-md', 'btn-copy-json', 'btn-download-json']
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
  const lines = ['# 🎯 B2B 出海精选 Skills (v3.1)', '',
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
    source: 'candidates-v3-refined.html', skills: data}, null, 2);
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
document.getElementById('btn-download-json').addEventListener('click', () => {
  downloadFile(buildJSON(getSelectedData()), `b2b-skills-${new Date().toISOString().slice(0,10)}.json`, 'application/json');
  showToast(`⬇️ 已下载 JSON`);
});
restoreSelection(); updateUI();
</script>
</body></html>
''')

    return ''.join(lines)


def main():
    print("📂 读 candidates-v3.html 提取卡片...", file=sys.stderr)
    cards = parse_v3_html()
    print(f"  找到 {len(cards)} 个卡片", file=sys.stderr)

    # 二次过滤
    filtered = defaultdict(list)
    excluded_log = defaultdict(int)
    for card in cards:
        excluded, reason = is_excluded_strict(card['desc'])
        if excluded:
            excluded_log[reason] += 1
            continue
        filtered[card['category']].append(card)

    total = sum(len(s) for s in filtered.values())
    print(f"\n📊 二次过滤后: {total} 个", file=sys.stderr)
    print(f"\n🚫 本轮排除:", file=sys.stderr)
    for reason, count in excluded_log.items():
        print(f"  {reason}: {count}", file=sys.stderr)

    # 输出 HTML
    html = render_html(filtered, excluded_log, total)
    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(f"\n✅ 已写入 {OUTPUT_HTML}（{len(html)} 字符）", file=sys.stderr)


if __name__ == '__main__':
    main()