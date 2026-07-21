"""
_shared.py - 5 个 HTML 生成脚本的公共代码

抽取内容（避免 DRY 违反）：
1. HTML 工具栏（toolbar）+ 计数徽章 + 6 个按钮
2. 卡片渲染（card）
3. CSS 主题变量
4. JS 交互（getSelected / updateUI / buildMarkdown / buildJSON / copyToClipboard / downloadFile）
5. Toast 提示

被以下脚本 import：
- expand_v3.py
- expand_v3_refine.py
- expand_v32.py
- expand_v33.py
- expand_collections.py
- dedup_v35.py
"""
from typing import List, Dict, Optional


# ============================================================
# CSS 主题（暗色/亮色模式 + 统一变量）
# ============================================================

CSS_VARS = """
:root {
  --bg: #0d1117; --bg-card: #161b22; --bg-card-hover: #1f2530; --bg-card-selected: #1c2c4a;
  --border: #30363d; --border-selected: #58a6ff; --text: #c9d1d9; --text-muted: #8b949e;
  --accent: #58a6ff; --success: #3fb950; --tag-bg: #21262d;
  --toolbar-h: 64px;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #fff; --bg-card: #f6f8fa; --bg-card-hover: #eaeef2;
    --bg-card-selected: #dbeafe; --border: #d0d7de; --border-selected: #0969da; --text: #1f2328;
    --text-muted: #656d76; --accent: #0969da; --success: #1a7f37; --tag-bg: #eaeef2;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.55; padding-top: var(--toolbar-h);
}
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
.toolbar { position: fixed; top: 0; left: 0; right: 0; height: var(--toolbar-h);
  background: rgba(13,17,23,0.92); backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border); display: flex; align-items: center;
  justify-content: space-between; padding: 0 24px; z-index: 100; gap: 12px; }
@media (prefers-color-scheme: light) { .toolbar { background: rgba(255,255,255,0.92); } }
.toolbar-title { font-weight: 600; font-size: 0.95em; display: flex; align-items: center; gap: 8px; }
.count-badge { background: var(--accent); color: white; padding: 3px 10px;
  border-radius: 12px; font-size: 0.85em; font-weight: 700; min-width: 36px; text-align: center; }
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
"""

# ============================================================
# Toolbar HTML（统一 6 按钮 + 计数徽章）
# ============================================================

TOOLBAR_HTML = """
<div class="toolbar">
  <div class="toolbar-title">
    🎯 Skills
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
"""


# ============================================================
# Card HTML 渲染（单张卡片）
# ============================================================

def render_card_html(
    skill_id: str,
    name: str,
    url: str,
    desc: str,
    category: str,
    extra_badge: str = '',
    repo: str = '',
) -> str:
    """渲染单张卡片 HTML

    Args:
        skill_id: 唯一 ID（用于 data-id 和 data-name）
        name: 显示名
        url: 仓库 URL
        desc: 描述（已 < 80 字符）
        category: 分类
        extra_badge: 额外 badge HTML（如 🆕 译）
        repo: 完整 owner/repo 字符串（可选）
    """
    # 转义引号（防止 HTML attribute 破坏）
    def esc(s: str) -> str:
        return s.replace('"', '&quot;').replace("'", '&#39;')
    name_safe = esc(name)
    desc_safe = esc(desc)
    cat_safe = esc(category)
    repo_html = f'<a href="{repo}" class="card-name" target="_blank">{name}</a>' if repo else f'<a href="{url}" class="card-name" target="_blank">{name}</a>'

    return f'''<div class="card">
      <input type="checkbox" class="card-checkbox"
        data-id="{name_safe}"
        data-name="{name_safe}"
        data-url="{url}"
        data-desc="{desc_safe}"
        data-category="{cat_safe}">
      {repo_html}{extra_badge}
      <div class="card-desc">{desc}</div>
      <div class="card-meta">📂 {category}</div>
    </div>'''


# ============================================================
# JS 交互（统一 updateUI / getSelected / 导出）
# ============================================================

JS_INTERACTION = """
const STORAGE_KEY = 'b2b-skills.selected';
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

document.addEventListener('change', e => {
  if (e.target.classList && e.target.classList.contains('card-checkbox')) updateUI();
});
// ⭐ 关键修复：点 checkbox 时让原生 change 处理，不重复 toggle
document.addEventListener('click', e => {
  if (e.target.closest && e.target.closest('a')) return;
  if (e.target.classList && e.target.classList.contains('card-checkbox')) return;
  if (e.target.closest && e.target.closest('.card-checkbox-wrap')) return;
  const card = e.target.closest && e.target.closest('.card');
  if (!card) return;
  const cb = card.querySelector('.card-checkbox');
  if (!cb) return;
  cb.checked = !cb.checked;
  updateUI();
});

document.getElementById('btn-select-all').addEventListener('click', () => {
  ALL_CHECKBOXES().forEach(cb => cb.checked = true); updateUI();
});
document.getElementById('btn-clear').addEventListener('click', () => {
  ALL_CHECKBOXES().forEach(cb => cb.checked = false); updateUI();
});

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
    e.preventDefault(); ALL_CHECKBOXES().forEach(cb => cb.checked = true); updateUI();
  }
  if (e.key === 'Escape') {
    ALL_CHECKBOXES().forEach(cb => cb.checked = false); updateUI();
  }
});

function getSelectedData() {
  return getSelected().map(cb => ({
    id: cb.dataset.id, name: cb.dataset.name, url: cb.dataset.url,
    category: cb.dataset.category, desc: cb.dataset.desc,
  }));
}

function buildMarkdown(data) {
  const lines = ['# 🎯 我精选的 Skills', '',
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
    skills: data}, null, 2);
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
  downloadFile(buildMarkdown(getSelectedData()), `skills-${new Date().toISOString().slice(0,10)}.md`);
  showToast(`⬇️ 已下载 MD`);
});
document.getElementById('btn-copy-json').addEventListener('click', async () => {
  const ok = await copyToClipboard(buildJSON(getSelectedData()));
  showToast(ok ? '✅ 已复制 JSON' : '❌ 复制失败', !ok);
});
document.getElementById('btn-download-json').addEventListener('click', () => {
  downloadFile(buildJSON(getSelectedData()), `skills-${new Date().toISOString().slice(0,10)}.json`, 'application/json');
  showToast(`⬇️ 已下载 JSON`);
});

restoreSelection();
updateUI();
"""


# ============================================================
# 缓存 key 工具（统一命名：`<type>:<value>`）
# ============================================================

def cache_key(key_type: str, value: str) -> str:
    """统一缓存 key 格式：`<type>:<value>`

    支持的 type：
    - 'desc': 翻译缓存（按原文 hash）
    - 'repo': 去重缓存（按 owner/repo）
    - 'hard': 评分缓存（按 owner/repo）
    - 'metrics': 质量指标（按 owner/repo）
    """
    return f"{key_type}:{value}"


# ============================================================
# 统一错误消息风格（✅ ❌ ⚠️）
# ============================================================

def err_msg(msg: str) -> str:
    """统一错误消息前缀：❌"""
    return f"❌ {msg}"


def warn_msg(msg: str) -> str:
    """统一警告消息前缀：⚠️"""
    return f"⚠️ {msg}"


def ok_msg(msg: str) -> str:
    """统一成功消息前缀：✅"""
    return f"✅ {msg}"