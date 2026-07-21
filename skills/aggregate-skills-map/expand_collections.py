#!/usr/bin/env python
"""
expand_collections.py - 展开 GitHub 上合集型仓库的子 skill 列表
并生成 candidates-expanded.html（含勾选 + 导出）

功能:
1. 读 taxonomy.yaml（48 个已存在 skill，作为排除集）
2. 拉 4 大合集仓库的子 skill 列表：
   - wshobson/agents/plugins/（91 plugins）
   - anthropics/claude-plugins-official/plugins/（38 plugins）
   - CherryHQ/cherry-studio/.agents/skills/（8 skills）
   - anbeime/skill/skills/（57 skills）
3. 去重 + 排除 taxonomy.yaml 已有的 48
4. 拉每个子 skill 的 SKILL.md 描述（frontmatter description）
5. 生成 candidates-expanded.html（1320 行，含勾选 + 导出）
"""
import yaml, sys, json, subprocess, argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

TAXONOMY_FILE = Path(__file__).parent / 'taxonomy.yaml'
OUTPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-expanded.html'

# ============================================================
# 配置：要展开的合集
# ============================================================
COLLECTIONS = [
    {
        'owner': 'wshobson',
        'repo': 'agents',
        'path': 'plugins',
        'description': 'Multi-harness plugin marketplace for Claude Code, Codex, Cursor',
        'weight': 1,  # 优先级
    },
    {
        'owner': 'anthropics',
        'repo': 'claude-plugins-official',
        'path': 'plugins',
        'description': 'Official, Anthropic-managed directory of high quality Claude',
        'weight': 1,
    },
    {
        'owner': 'CherryHQ',
        'repo': 'cherry-studio',
        'path': '.agents/skills',
        'description': 'Cherry Studio 内置 agent skills（cherry-pr-test, create-skill 等）',
        'weight': 2,
    },
    {
        'owner': 'anbeime',
        'repo': 'skill',
        'path': 'skills',
        'description': '中文技能商店 72 个分类（agent-team, anything-to-notebooklm 等）',
        'weight': 2,
    },
]


# ============================================================
# 工具函数
# ============================================================

def load_taxonomy_existing():
    """读 taxonomy.yaml，提取已存在的 skill 集合（用于去重）"""
    with open(TAXONOMY_FILE, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    existing_ids = set()
    existing_repos = set()
    existing_paths = set()  # 含 skill_path 的精确路径
    collection_repos = set()  # 整仓库级别的合集（如 baoyu-skills）

    for s in data.get('skills', []):
        existing_ids.add(s.get('id', ''))
        existing_ids.add(s.get('name', ''))
        repo = s.get('repo', '')
        if repo:
            existing_repos.add(repo.lower())
            existing_repos.add(repo.split('/')[-1].lower())
            # 如果是合集 type（含 skills），记录整仓库
            if s.get('type') == 'collection':
                collection_repos.add(repo.lower())
        # skill_path 字段（如 baoyu-skills/skills/baoyu-post-to-wechat）
        sp = s.get('skill_path', '')
        if sp:
            existing_paths.add(sp.lower())

    return {
        'ids': existing_ids,
        'repos': existing_repos,
        'paths': existing_paths,
        'collections': collection_repos,
    }


def gh_api_list_dir(owner, repo, path):
    """列目录（只取 dir 类型）"""
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}/contents/{path}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        items = json.loads(result.stdout)
        if not isinstance(items, list):
            return []
        return [it['name'] for it in items if it.get('type') == 'dir']
    except json.JSONDecodeError:
        return []


def gh_api_get_skill_md(owner, repo, path):
    """拉 SKILL.md frontmatter description"""
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}/contents/{path}/SKILL.md',
         '--jq', '.content'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0 or not result.stdout.strip():
        return ''
    try:
        import base64
        content_b64 = json.loads(result.stdout)
        text = base64.b64decode(content_b64).decode('utf-8', errors='replace')
        # 提取 frontmatter description
        if text.startswith('---'):
            end = text.find('---', 3)
            if end > 0:
                frontmatter = text[3:end]
                for line in frontmatter.split('\n'):
                    if line.startswith('description:'):
                        return line.split(':', 1)[1].strip().strip('"').strip("'")
        # fallback: 取前 100 字
        return text[:100].replace('\n', ' ')
    except Exception:
        return ''


def gh_api_repo_meta(owner, repo):
    """拉合集仓库元数据（stars）"""
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}',
         '--jq', '{stars: .stargazers_count}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        return 0
    try:
        return json.loads(result.stdout).get('stars', 0)
    except json.JSONDecodeError:
        return 0


# ============================================================
# 主流程
# ============================================================

def expand_collections():
    """展开所有合集（快速模式：只列目录名，不拉 SKILL.md）"""
    existing = load_taxonomy_existing()
    print(f"📚 已存在 skill: {len(existing['ids'])} ids / {len(existing['collections'])} 整合集", file=sys.stderr)

    all_expanded = []  # (collection, name, path, description, stars)

    for col in COLLECTIONS:
        owner = col['owner']
        repo = col['repo']
        path = col['path']

        print(f"\n📂 展开 {owner}/{repo}/{path}/", file=sys.stderr)
        sub_skills = gh_api_list_dir(owner, repo, path)
        print(f"  发现 {len(sub_skills)} 个子目录", file=sys.stderr)

        col_stars = gh_api_repo_meta(owner, repo)

        for name in sub_skills:
            full_path = f"{path}/{name}"
            # 简化：description 用合集描述 + skill 名推断
            desc = f"{col['description']} | 子模块: {name}"
            all_expanded.append({
                'collection': f"{owner}/{repo}",
                'collection_stars': col_stars,
                'name': name,
                'path': full_path,
                'url': f"https://github.com/{owner}/{repo}/tree/main/{full_path}",
                'description': desc[:200],
            })

    print(f"\n🔍 总展开: {len(all_expanded)} 个", file=sys.stderr)

    # 去重 + 排除（更精细的逻辑）
    filtered = []
    excluded_breakdown = defaultdict(int)

    for skill in all_expanded:
        collection = skill['collection'].lower()
        name = skill['name'].lower()
        path = skill['path'].lower()

        # 规则 1: 整合集已在 taxonomy（如 baoyu-skills）
        if collection in existing['collections']:
            excluded_breakdown[f"collection {collection} 已在 taxonomy"] += 1
            continue
        # 规则 2: skill id/name 完全匹配
        if name in existing['ids']:
            excluded_breakdown[f"name '{name}' 已在 taxonomy"] += 1
            continue
        # 规则 3: 精确路径匹配（如 taxonomy 里有 baoyu-post-to-wechat 的 skill_path）
        if path in existing['paths']:
            excluded_breakdown[f"path '{path}' 已在 taxonomy"] += 1
            continue
        # 规则 4: 仓库已被 taxonomy 收录（视为子集已包含）
        # 注释掉这个规则——除非 taxonomy 明确标 sub_skill，否则允许
        # if collection in existing['repos']:
        #     excluded_breakdown[f"repo {collection} 已在 taxonomy"] += 1
        #     continue

        filtered.append(skill)

    total_excluded = sum(excluded_breakdown.values())
    print(f"🚫 排除（已在 taxonomy）: {total_excluded} 个", file=sys.stderr)
    for reason, count in excluded_breakdown.items():
        print(f"   - {reason}: {count}", file=sys.stderr)
    print(f"✅ 新候选: {len(filtered)} 个", file=sys.stderr)

    return filtered, all_expanded, total_excluded


# ============================================================
# HTML 生成
# ============================================================

def render_html(new_skills, all_expanded, excluded_count):
    """生成 candidates-expanded.html（带勾选 + 导出 + 来源标记）"""
    lines = []
    lines.append('<!DOCTYPE html>')
    lines.append('<html lang="zh-CN"><head>')
    lines.append('<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">')
    lines.append('<title>🔬 合集展开的 Claude Skills · awesome-skills-map</title>')
    lines.append('<style>')
    # CSS（与 candidates-overview.html 类似，简化版）
    lines.append('''
:root {
  --bg: #0d1117; --bg-card: #161b22; --bg-card-hover: #1f2530;
  --bg-card-selected: #1c2c4a; --border: #30363d; --border-selected: #58a6ff;
  --text: #c9d1d9; --text-muted: #8b949e; --accent: #58a6ff;
  --gold: #f0b72f; --silver: #c0c0c0; --bronze: #cd7f32;
  --success: #3fb950; --tag-bg: #21262d;
  --tier-1: linear-gradient(135deg, #f0b72f 0%, #d97706 100%);
  --tier-2: linear-gradient(135deg, #6e7681 0%, #484f58 100%);
  --tier-3: linear-gradient(135deg, #cd7f32 0%, #6e7681 100%);
  --toolbar-h: 64px;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #ffffff; --bg-card: #f6f8fa; --bg-card-hover: #eaeef2;
    --bg-card-selected: #dbeafe; --border: #d0d7de; --border-selected: #0969da;
    --text: #1f2328; --text-muted: #656d76; --accent: #0969da;
    --gold: #bf8700; --silver: #6e7781; --bronze: #9a6700;
    --success: #1a7f37; --tag-bg: #eaeef2;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6;
  padding-top: var(--toolbar-h);
}
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
.toolbar {
  position: fixed; top: 0; left: 0; right: 0; height: var(--toolbar-h);
  background: rgba(13, 17, 23, 0.92); backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border); display: flex;
  align-items: center; justify-content: space-between;
  padding: 0 24px; z-index: 100; gap: 12px;
}
@media (prefers-color-scheme: light) {
  .toolbar { background: rgba(255, 255, 255, 0.92); }
}
.toolbar-title { font-weight: 600; font-size: 0.95em; display: flex; align-items: center; gap: 8px; }
.count-badge {
  background: var(--accent); color: white; padding: 3px 10px;
  border-radius: 12px; font-size: 0.85em; font-weight: 700;
  min-width: 36px; text-align: center;
}
.count-badge[data-count="0"] { background: var(--text-muted); }
.toolbar-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn {
  background: var(--bg-card); color: var(--text); border: 1px solid var(--border);
  padding: 8px 14px; border-radius: 6px; font-size: 0.85em;
  cursor: pointer; transition: all 0.15s; font-weight: 500; white-space: nowrap;
}
.btn:hover { background: var(--bg-card-hover); border-color: var(--accent); }
.btn.primary { background: var(--accent); color: white; border-color: var(--accent); }
.btn.primary:hover { filter: brightness(1.1); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.toast {
  position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%) translateY(100px);
  background: var(--success); color: white; padding: 12px 24px;
  border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  z-index: 200; transition: transform 0.3s ease; font-weight: 500; font-size: 0.9em;
}
.toast.show { transform: translateX(-50%) translateY(0); }
.toast.error { background: #f85149; }
header {
  text-align: center; padding: 40px 20px;
  background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
  border-radius: 16px; margin-bottom: 32px; color: white;
  box-shadow: 0 8px 32px rgba(31, 111, 235, 0.3);
}
header h1 { font-size: 2.5em; margin-bottom: 12px; }
header .subtitle { font-size: 1.1em; opacity: 0.95; margin-bottom: 16px; }
header .stats { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; margin-top: 20px; }
header .stat {
  background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px);
  padding: 12px 20px; border-radius: 12px; min-width: 100px;
}
header .stat-num { font-size: 1.8em; font-weight: 700; }
header .stat-label { font-size: 0.85em; opacity: 0.9; }
.notice {
  background: var(--bg-card); border-left: 4px solid var(--accent);
  padding: 16px 20px; border-radius: 0 8px 8px 0; margin-bottom: 24px;
}
.notice-title { font-weight: 600; margin-bottom: 8px; color: var(--accent); }
.notice ul { padding-left: 24px; color: var(--text-muted); }
.notice li { margin-bottom: 6px; }
.tier { margin-bottom: 40px; }
.tier-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
  padding-bottom: 8px; border-bottom: 2px solid var(--border);
}
.tier-badge {
  display: inline-block; padding: 4px 12px; border-radius: 6px;
  color: white; font-weight: 700; font-size: 0.9em;
}
.tier-badge.t1 { background: var(--tier-1); }
.tier-badge.t2 { background: var(--tier-2); }
.tier-badge.t3 { background: var(--tier-3); }
.tier-title { font-size: 1.3em; font-weight: 600; }
.cards {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}
.card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 18px; padding-right: 60px;
  transition: all 0.2s; position: relative; overflow: hidden; cursor: pointer;
}
.card:hover {
  transform: translateY(-2px); background: var(--bg-card-hover);
  border-color: var(--accent); box-shadow: 0 4px 16px rgba(31, 111, 235, 0.15);
}
.card.selected {
  background: var(--bg-card-selected); border-color: var(--border-selected);
  box-shadow: 0 0 0 1px var(--border-selected);
}
.card-source {
  position: absolute; top: 12px; right: 12px;
  background: var(--tag-bg); color: var(--text-muted);
  padding: 3px 10px; border-radius: 12px; font-size: 0.75em; pointer-events: none;
}
.card.t1 .card-source { background: var(--gold); color: #000; }
.card.t2 .card-source { background: var(--silver); color: #000; }
.card.t3 .card-source { background: var(--bronze); color: #000; }
.card-checkbox {
  position: absolute; top: 38px; right: 12px; width: 22px; height: 22px;
  cursor: pointer; z-index: 5; accent-color: var(--accent);
}
.card-name {
  font-size: 1.05em; font-weight: 600; color: var(--accent);
  text-decoration: none; display: inline-block; margin-bottom: 6px;
  word-break: break-all;
}
.card-name:hover { text-decoration: underline; }
.card-collection {
  font-size: 0.8em; color: var(--text-muted);
  margin-bottom: 8px; font-family: ui-monospace, monospace;
}
.card-desc {
  font-size: 0.9em; color: var(--text); margin-bottom: 12px; line-height: 1.5;
}
.card-meta {
  display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px;
  padding-top: 12px; border-top: 1px solid var(--border);
  font-size: 0.8em; color: var(--text-muted);
}
.card-meta-item strong { color: var(--text); font-weight: 600; }
.card-tags {
  display: flex; flex-wrap: wrap; gap: 4px; margin-top: 10px;
}
.tag {
  background: var(--tag-bg); color: var(--text-muted);
  padding: 2px 8px; border-radius: 4px; font-size: 0.75em;
}
footer {
  text-align: center; padding: 32px 20px; color: var(--text-muted);
  font-size: 0.85em; border-top: 1px solid var(--border); margin-top: 40px;
}
@media (max-width: 640px) {
  header h1 { font-size: 1.8em; }
  .cards { grid-template-columns: 1fr; }
  .toolbar { padding: 8px 12px; flex-wrap: wrap; }
}
    ''')
    lines.append('</style></head><body>')

    # Toolbar
    lines.append('''
<div class="toolbar">
  <div class="toolbar-title">
    🔬 展开的合集 Skills
    <span class="count-badge" id="count-badge" data-count="0">0</span>
    <span style="font-weight: 400; color: var(--text-muted); font-size: 0.85em;">已选</span>
  </div>
  <div class="toolbar-actions">
    <button class="btn" id="btn-select-all">☑️ 全选</button>
    <button class="btn" id="btn-clear">🗑️ 清空</button>
    <button class="btn primary" id="btn-copy-md" disabled>📋 复制 MD</button>
    <button class="btn primary" id="btn-download-md" disabled>⬇️ 下载 MD</button>
    <button class="btn" id="btn-copy-json" disabled>📋 复制 JSON</button>
    <button class="btn" id="btn-download-json" disabled>⬇️ JSON</button>
  </div>
</div>
<div class="toast" id="toast"></div>
<div class="container">
''')

    # Header
    lines.append('''
<header>
  <h1>🔬 合集展开的 Claude Skills</h1>
  <div class="subtitle">从顶级合集仓库拉取的子 skill 列表（已排除已入库的）</div>
  <div class="stats">
    <div class="stat"><div class="stat-num" id="stat-total">''' + str(len(all_expanded)) + '''</div><div class="stat-label">总展开</div></div>
    <div class="stat"><div class="stat-num" id="stat-new">''' + str(len(new_skills)) + '''</div><div class="stat-label">新候选</div></div>
    <div class="stat"><div class="stat-num" id="stat-excluded">''' + str(excluded_count) + '''</div><div class="stat-label">已排除</div></div>
    <div class="stat"><div class="stat-num">4</div><div class="stat-label">合集源</div></div>
  </div>
</header>
''')

    # 主动审查
    lines.append('''
<div class="notice">
  <div class="notice-title">📊 来源说明</div>
  <ul>
    <li><strong>wshobson/agents</strong>：91 个 plugins（multi-harness marketplace）</li>
    <li><strong>anthropics/claude-plugins-official</strong>：38 个官方 plugins</li>
    <li><strong>CherryHQ/cherry-studio</strong>：8 个内置 agent skills</li>
    <li><strong>anbeime/skill</strong>：57 个中文技能商店</li>
    <li><strong>已排除</strong>：''' + str(excluded_count) + ''' 个（已在 taxonomy.yaml 的 48 个或衍生品）</li>
  </ul>
</div>
''')

    # Cards: 按合集分组
    by_collection = defaultdict(list)
    for s in new_skills:
        by_collection[s['collection']].append(s)

    tier_idx = 1
    for col in COLLECTIONS:
        col_id = f"{col['owner']}/{col['repo']}"
        skills_in = by_collection.get(col_id, [])
        if not skills_in:
            continue

        tier_class = f"t{tier_idx}"
        tier_label = f"tier-{tier_idx}"
        lines.append(f'''
<section class="tier">
  <div class="tier-header">
    <span class="tier-badge {tier_class}">📦 Tier {tier_idx}</span>
    <span class="tier-title">{col_id}（{len(skills_in)} 个）</span>
  </div>
  <div class="cards">
''')

        for s in skills_in:
            safe_id = s['name'].replace('"', '&quot;').replace("'", '&#39;')
            safe_desc = s['description'].replace('"', '&quot;').replace("'", '&#39;').replace('\n', ' ')
            lines.append(f'''
    <div class="card {tier_label}" data-tier="{tier_idx}">
      <div class="card-source">{col_id.split('/')[1]}</div>
      <input type="checkbox" class="card-checkbox"
        data-id="{safe_id}"
        data-name="{safe_id}"
        data-url="{s['url']}"
        data-author="{col_id}"
        data-desc="{safe_desc}"
        data-stars="{s['collection_stars']}"
        data-score="0">
      <a href="{s['url']}" class="card-name" target="_blank">{s['name']}</a>
      <div class="card-collection">📁 {s['path']}</div>
      <div class="card-desc">{s['description']}</div>
      <div class="card-meta">
        <span class="card-meta-item">⭐ <strong>{s['collection_stars']:,}</strong> (合集)</span>
        <span class="card-meta-item">📦 <strong>合集路径</strong></span>
      </div>
    </div>
''')

        lines.append('  </div>\n</section>\n')
        tier_idx += 1

    # JS（与 candidates-overview.html 类似，简化）
    lines.append('''
<footer>
  <p><strong>合集展开的 Claude Skills</strong></p>
  <p>由 <code>expand_collections.py</code> 自动展开</p>
  <p>展开时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M') + '''</p>
  <p style="margin-top: 16px; font-size: 0.9em;">
    ⌨️ 快捷键: <kbd>Ctrl+A</kbd> 全选 · <kbd>Esc</kbd> 清空 · 点击卡片也可选中
  </p>
</footer>
</div>

<script>
const STORAGE_KEY = 'skillsexp.selected';
const ALL_CHECKBOXES = () => Array.from(document.querySelectorAll('.card-checkbox'));

function getSelected() { return ALL_CHECKBOXES().filter(cb => cb.checked); }

function updateUI() {
  const n = getSelected().length;
  const badge = document.getElementById('count-badge');
  badge.textContent = n;
  badge.dataset.count = n;
  ['btn-copy-md', 'btn-download-md', 'btn-copy-json', 'btn-download-json']
    .forEach(id => document.getElementById(id).disabled = n === 0);
  ALL_CHECKBOXES().forEach(cb => {
    cb.closest('.card').classList.toggle('selected', cb.checked);
  });
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(getSelected().map(cb => cb.dataset.id)));
  } catch (e) {}
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
  if (e.target.classList.contains('card-checkbox')) updateUI();
});

document.addEventListener('click', e => {
  if (e.target.closest('a')) return;
  const card = e.target.closest('.card');
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
    author: cb.dataset.author, desc: cb.dataset.desc,
    stars: parseInt(cb.dataset.stars || '0', 10),
    score: parseFloat(cb.dataset.score || '0'),
  }));
}

function buildMarkdown(data) {
  const lines = ['# 🎯 我精选的合集 Skills', '',
    `> 共 ${data.length} 个 · 来自合集展开 · ${new Date().toISOString().slice(0, 10)}`, '',
    '| 排名 | ⭐ (合集) | name | 来源 | 仓库 | 简介 |',
    '|------|----------|------|------|------|------|'];
  data.forEach((s, i) => {
    const desc = (s.desc || '').replace(/\\|/g, '\\\\|').replace(/\\n/g, ' ');
    lines.push(`| ${i + 1} | ${s.stars.toLocaleString()} | **${s.name}** | ${s.author} | [${s.url.replace('https://github.com/', '')}](${s.url}) | ${desc} |`);
  });
  lines.push('', '## 📦 Markdown 列表');
  lines.push('', '```bash');
  data.forEach(s => {
    const m = s.url.match(/github\\.com\\/([^\\/]+)\\/([^\\/]+)\\/(?:tree\\/[^\\/]+\\/)?(.+)/);
    if (m) lines.push(`# ${s.name}  (${m[1]}/${m[2]}/${m[3]})`);
  });
  lines.push('```');
  return lines.join('\\n');
}

function buildJSON(data) {
  return JSON.stringify({
    exported_at: new Date().toISOString(), count: data.length,
    source: 'candidates-expanded.html', skills: data
  }, null, 2);
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
  const md = buildMarkdown(getSelectedData());
  const ok = await copyToClipboard(md);
  showToast(ok ? `✅ 已复制 ${getSelected().length} 个 skill（MD）` : '❌ 复制失败', !ok);
});
document.getElementById('btn-download-md').addEventListener('click', () => {
  downloadFile(buildMarkdown(getSelectedData()), `my-collection-skills-${new Date().toISOString().slice(0, 10)}.md`);
  showToast(`⬇️ 已下载 MD`);
});
document.getElementById('btn-copy-json').addEventListener('click', async () => {
  const ok = await copyToClipboard(buildJSON(getSelectedData()));
  showToast(ok ? `✅ 已复制 JSON` : '❌ 复制失败', !ok);
});
document.getElementById('btn-download-json').addEventListener('click', () => {
  downloadFile(buildJSON(getSelectedData()), `my-collection-skills-${new Date().toISOString().slice(0, 10)}.json`, 'application/json');
  showToast(`⬇️ 已下载 JSON`);
});

restoreSelection();
updateUI();
</script>
</body></html>
''')
    return ''.join(lines)


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-push', action='store_true', help='不推送 GitHub（默认）')
    args = parser.parse_args()

    print("🔍 读 taxonomy.yaml（已存在 skill 排除集）...", file=sys.stderr)
    new_skills, all_expanded, total_excluded = expand_collections()

    print(f"\n📝 生成 candidates-expanded.html ...", file=sys.stderr)
    html = render_html(new_skills, all_expanded, total_excluded)
    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(f"✅ 已写入 {OUTPUT_HTML}（{len(html)} 字符）", file=sys.stderr)

    # 简明统计
    print(f"\n📊 最终统计:", file=sys.stderr)
    print(f"  总展开: {len(all_expanded)}", file=sys.stderr)
    print(f"  排除（已存在）: {total_excluded}", file=sys.stderr)
    print(f"  新候选: {len(new_skills)}", file=sys.stderr)


if __name__ == '__main__':
    main()