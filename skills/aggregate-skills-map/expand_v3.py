#!/usr/bin/env python
"""
expand_v3.py - 功能导向的 skill 聚合（针对 B2B 出海企业）

变更:
- 拉每个 plugin/skill 的真实 description（功能介绍）
- 按 description 关键词分类（不显示合集来源）
- 排除编程/技术类（不符合"B2B 出海老板/员工"日常使用）
- 输出 candidates-v3.html
"""
import yaml, sys, json, subprocess, argparse, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import base64, time

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

TAXONOMY_FILE = Path(__file__).parent / 'taxonomy.yaml'
OUTPUT_HTML = Path(__file__).parent / 'examples' / 'candidates-v3.html'

# ============================================================
# 配置：要展开的合集
# ============================================================
COLLECTIONS = [
    {'owner': 'wshobson', 'repo': 'agents', 'plugin_manifest': '.claude-plugin/plugin.json', 'plugin_dir': 'plugins'},
    {'owner': 'anthropics', 'repo': 'claude-plugins-official', 'plugin_manifest': '.claude-plugin/plugin.json', 'plugin_dir': 'plugins'},
    {'owner': 'CherryHQ', 'repo': 'cherry-studio', 'plugin_manifest': 'SKILL.md', 'plugin_dir': '.agents/skills'},
    {'owner': 'anbeime', 'repo': 'skill', 'plugin_manifest': 'SKILL.md', 'plugin_dir': 'skills'},
]

# ============================================================
# 分类 + 排除规则（按用户需求：B2B 出海老板/员工）
# ============================================================
CATEGORY_RULES = [
    ('内容创作', [
        'content', 'writing', 'blog', 'article', 'post', 'social media', 'copy',
        'editorial', 'publishing', 'media', 'newsletter', 'story', 'novel',
        'cover', 'thumbnail', 'illustration', 'image generation', 'video',
    ]),
    ('营销推广', [
        'marketing', 'seo', 'sem', 'ads', 'campaign', 'branding', 'brand',
        'growth', 'funnel', 'conversion', 'advertising', 'meta ads', 'google ads',
        'wechat', 'xiaohongshu', 'tiktok', 'instagram', 'twitter', 'social',
    ]),
    ('销售客户', [
        'sales', 'crm', 'customer', 'lead', 'outreach', 'demo', 'pitch',
        'negotiation', 'pipeline', 'follow-up', 'prospect', 'closing',
    ]),
    ('HR 招聘', [
        'recruit', 'hire', 'hiring', 'interview', 'onboarding', 'hr',
        'talent', 'career', 'job search', 'resume', 'cv',
    ]),
    ('财务行政', [
        'finance', 'invoice', 'accounting', 'expense', 'tax', 'budget',
        'financial', 'payroll', 'reimbursement', 'billing',
    ]),
    ('翻译出海', [
        'translate', 'translation', 'localize', 'localization', 'i18n',
        'multilingual', 'global', 'international', 'cross-border', 'overseas',
    ]),
    ('效率办公', [
        'productivity', 'schedule', 'plan', 'task', 'meeting', 'email',
        'note', 'documentation', 'organize', 'workflow', 'time management',
        'habit', 'routine', 'daily',
    ]),
    ('数据分析', [
        'analytics', 'data', 'report', 'dashboard', 'metric', 'kpi',
        'insight', 'visualization', 'chart', 'tracking', 'monitoring',
    ]),
    ('客户支持', [
        'support', 'helpdesk', 'ticket', 'chat', 'faq', 'service',
        'customer service', 'response', 'feedback', 'survey',
    ]),
    ('产品设计', [
        'design', 'ui', 'ux', 'prototype', 'wireframe', 'figma',
        'product', 'prd', 'requirement', 'spec', 'moodboard',
    ]),
    ('学习研究', [
        'research', 'study', 'learn', 'education', 'tutorial', 'guide',
        'knowledge', 'academic', 'paper', 'literature', 'analysis',
    ]),
    ('AI 创作', [
        'prompt', 'ai art', 'image generation', 'voice', 'audio', 'music',
        'video generation', 'animation', 'tts', 'asr',
    ]),
]

# 排除规则：编程/技术类（更严格，覆盖更多编程相关关键词）
EXCLUDE_RULES = [
    # 编程动作
    'code review', 'code-review', 'code explanation', 'code generation',
    'code completion', 'code refactor', 'code style', 'code quality',
    'shipped', 'ship a', 'deploy to production', 'ci/cd', 'cicd',
    'unit test', 'integration test', 'e2e test', 'test automation',
    'refactoring', 'debugging', 'compiler', 'interpreter', 'bytecode',
    'parser', 'lexer', 'ast', 'syntax tree', 'lsp', 'static analysis',
    'lint', 'formatter',
    # 编程语言/框架
    'typescript', 'javascript', 'python', 'rust', 'golang', 'java',
    'react', 'vue', 'angular', 'next.js', 'svelte',
    'frontend framework', 'backend framework', 'web framework',
    'cli tool', 'shell script', 'bash script', 'bash command',
    # API/SDK/协议
    'api testing', 'api design', 'api development', 'rest api', 'graphql',
    'openapi specification', 'sdk', 'webhook', 'grpc',
    # Agent/工具链
    'mcp server', 'agent orchestration', 'agent harness', 'multi-agent',
    'ide integration', 'dev environment', 'docker-compose', 'docker compose',
    # 基础设施
    'aws', 'azure', 'gcp', 'kubernetes', 'k8s', 'docker', 'terraform',
    'observability', 'logging', 'tracing', 'sentry', 'prometheus',
    'infrastructure', 'devops', 'sre', 'kafka', 'rabbitmq', 'redis',
    # 数据库
    'database', 'sql', 'orm', 'migration', 'schema design',
    # 安全/渗透
    'xss prevention', 'csrf protection', 'content security policy',
    'security audit', 'penetration test', 'vulnerability scan',
    # 版本控制
    'git workflow', 'pull request', 'merge conflict', 'version control',
    # 系统编程
    'linux kernel', 'system programming', 'embedded', 'iot', 'firmware',
    # 软件架构
    'microservice', 'kubernetes manifest', 'helm chart',
    # 测试
    'test-driven', 'tdd', 'bdd', 'mock', 'stub',
]


# ============================================================
# 数据加载
# ============================================================

def load_excluded():
    """读 taxonomy.yaml + candidates-overview.md 作为排除集"""
    existing_ids = set()
    existing_repos = set()
    existing_paths = set()
    collection_repos = set()

    try:
        with open(TAXONOMY_FILE, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        for s in data.get('skills', []):
            existing_ids.add(s.get('id', '').lower())
            existing_ids.add(s.get('name', '').lower())
            repo = s.get('repo', '').lower()
            if repo:
                existing_repos.add(repo)
                existing_repos.add(repo.split('/')[-1])
            sp = s.get('skill_path', '').lower()
            if sp:
                existing_paths.add(sp)
            if s.get('type') == 'collection':
                collection_repos.add(repo)
    except FileNotFoundError:
        pass

    # 也读 candidates-overview.md 的 skill 名
    try:
        cov = Path(__file__).parent / 'examples' / 'candidates-overview.md'
        content = cov.read_text(encoding='utf-8')
        for m in re.finditer(r'\*\*`([a-zA-Z0-9_\-\.]+)`\*\*', content):
            existing_ids.add(m.group(1).lower())
    except FileNotFoundError:
        pass

    return existing_ids, existing_repos, existing_paths, collection_repos


def get_plugin_descriptions(owner, repo, manifest_rel):
    """拉所有 plugin/skill 的 description"""
    # 1. 用 git tree 拿所有 manifest 路径
    r = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}/git/trees/main?recursive=1'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if r.returncode != 0:
        return []

    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return []

    tree = data.get('tree', [])
    # 找所有匹配的 manifest 路径
    # 例如 plugins/xxx/.claude-plugin/plugin.json 或 .agents/skills/xxx/SKILL.md
    paths = []
    for item in tree:
        p = item['path']
        if p.endswith(manifest_rel):
            paths.append(p)

    print(f"  {owner}/{repo}: 找到 {len(paths)} 个 manifest", file=sys.stderr)

    # 2. 拉每个 manifest 的 description
    results = []
    for p in paths:
        rr = subprocess.run(
            ['gh', 'api', f'repos/{owner}/{repo}/contents/{p}'],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        if rr.returncode != 0:
            continue
        try:
            d = json.loads(rr.stdout)
            content_b64 = d.get('content', '')
            if not content_b64:
                continue
            text = base64.b64decode(content_b64).decode('utf-8', errors='replace')
            desc = ''
            name = ''

            if manifest_rel.endswith('plugin.json'):
                # JSON 格式
                j = json.loads(text)
                desc = j.get('description', '')
                name = j.get('name', p.split('/')[-2])
            else:
                # SKILL.md markdown frontmatter
                if text.startswith('---'):
                    end = text.find('---', 3)
                    if end > 0:
                        fm = text[3:end]
                        for line in fm.split('\n'):
                            if line.startswith('name:'):
                                name = line.split(':', 1)[1].strip().strip('"').strip("'")
                            elif line.startswith('description:'):
                                desc = line.split(':', 1)[1].strip().strip('"').strip("'")
                                break

            if desc:
                results.append({
                    'name': name or p.split('/')[-2],
                    'description': desc,
                    'url': f"https://github.com/{owner}/{repo}/tree/main/{p.rsplit('/', 1)[0]}",
                    'path': p,
                })
        except Exception:
            continue

    return results


def classify(desc):
    """基于 description 关键词分类"""
    desc_lower = desc.lower()

    # 先检查排除
    for ex in EXCLUDE_RULES:
        if ex in desc_lower:
            return None, f"排除: {ex}"

    # 分类
    categories = []
    for cat_name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                categories.append(cat_name)
                break

    if not categories:
        return ['其他'], None

    return categories, None


# ============================================================
# 主流程
# ============================================================

def main():
    print("🔍 读 taxonomy + candidates-overview 排除集...", file=sys.stderr)
    excluded_ids, excluded_repos, excluded_paths, excluded_collections = load_excluded()
    print(f"  排除: {len(excluded_ids)} ids / {len(excluded_repos)} repos / {len(excluded_collections)} 整合集", file=sys.stderr)

    all_skills = []

    print("\n📂 拉各合集 description（每合集 ~30-90 秒）...", file=sys.stderr)
    for col in COLLECTIONS:
        manifest = col.get('plugin_manifest', 'SKILL.md')
        skills = get_plugin_descriptions(col['owner'], col['repo'], manifest)
        all_skills.extend(skills)

    print(f"\n🔍 总拉取: {len(all_skills)} 个 skill", file=sys.stderr)

    # 分类 + 排除
    by_category = defaultdict(list)
    excluded_log = defaultdict(int)

    for skill in all_skills:
        name_lower = skill['name'].lower()
        # 排除：taxonomy 已收录
        if name_lower in excluded_ids:
            excluded_log['taxonomy id 匹配'] += 1
            continue
        # 排除：路径匹配
        path_lower = skill['path'].lower()
        if path_lower in excluded_paths:
            excluded_log['taxonomy path 匹配'] += 1
            continue
        # 分类
        categories, exclude_reason = classify(skill['description'])
        if exclude_reason:
            excluded_log[exclude_reason] += 1
            continue
        # 加入分类
        for cat in categories:
            by_category[cat].append(skill)

    print(f"\n📊 分类结果:", file=sys.stderr)
    for cat, skills in sorted(by_category.items(), key=lambda x: -len(x[1])):
        print(f"  {cat}: {len(skills)}", file=sys.stderr)
    print(f"\n🚫 排除:", file=sys.stderr)
    for reason, count in excluded_log.items():
        print(f"  {reason}: {count}", file=sys.stderr)

    # 渲染 HTML
    html = render_html(by_category, excluded_log)
    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(f"\n✅ 已写入 {OUTPUT_HTML}（{len(html)} 字符）", file=sys.stderr)
    print(f"📊 总入选: {sum(len(s) for s in by_category.values())} 个", file=sys.stderr)


def render_html(by_category, excluded_log):
    """生成 candidates-v3.html"""
    total = sum(len(s) for s in by_category.values())
    lines = ['<!DOCTYPE html>', '<html lang="zh-CN"><head>',
             '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
             '<title>🎯 B2B 出海 skill 精选 · awesome-skills-map</title>',
             '<style>']
    lines.append('''
:root {
  --bg: #0d1117; --bg-card: #161b22; --bg-card-hover: #1f2530;
  --bg-card-selected: #1c2c4a; --border: #30363d; --border-selected: #58a6ff;
  --text: #c9d1d9; --text-muted: #8b949e; --accent: #58a6ff;
  --gold: #f0b72f; --success: #3fb950; --tag-bg: #21262d;
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
    --gold: #bf8700; --success: #1a7f37; --tag-bg: #eaeef2;
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
  border-radius: 12px; font-size: 0.85em; font-weight: 700; min-width: 36px; text-align: center;
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
.category-header {
  display: flex; align-items: center; gap: 12px; margin: 32px 0 16px;
  padding-bottom: 8px; border-bottom: 2px solid var(--border);
}
.category-badge {
  display: inline-block; padding: 6px 14px; border-radius: 6px;
  background: var(--accent); color: white; font-weight: 700; font-size: 0.9em;
}
.category-count { color: var(--text-muted); font-size: 0.85em; }
.cards {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px; margin-bottom: 16px;
}
.card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 18px; padding-right: 56px;
  transition: all 0.2s; position: relative; cursor: pointer;
}
.card:hover {
  transform: translateY(-2px); background: var(--bg-card-hover);
  border-color: var(--accent); box-shadow: 0 4px 16px rgba(31, 111, 235, 0.15);
}
.card.selected {
  background: var(--bg-card-selected); border-color: var(--border-selected);
  box-shadow: 0 0 0 1px var(--border-selected);
}
.card-checkbox {
  position: absolute; top: 12px; right: 12px; width: 22px; height: 22px;
  cursor: pointer; z-index: 5; accent-color: var(--accent);
}
.card-name {
  font-size: 1.1em; font-weight: 600; color: var(--accent);
  text-decoration: none; display: inline-block; margin-bottom: 8px;
  word-break: break-all;
}
.card-name:hover { text-decoration: underline; }
.card-desc {
  font-size: 0.92em; color: var(--text); margin-bottom: 12px; line-height: 1.55;
  min-height: 60px;
}
.card-meta {
  display: flex; gap: 8px; flex-wrap: wrap;
  font-size: 0.75em; color: var(--text-muted);
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
    🎯 B2B 出海 Skills
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

    # Header
    lines.append('''
<header>
  <h1>🎯 B2B 出海企业 Skills 精选</h1>
  <div class="subtitle">服务于老板 + 员工的日常使用 · 按功能分类 · 编程类已排除</div>
  <div class="stats">
    <div class="stat"><div class="stat-num">''' + str(total) + '''</div><div class="stat-label">入选</div></div>
    <div class="stat"><div class="stat-num">''' + str(len(by_category)) + '''</div><div class="stat-label">类别</div></div>
    <div class="stat"><div class="stat-num">4</div><div class="stat-label">合集源</div></div>
  </div>
</header>
''')

    # 排除说明
    excl_total = sum(excluded_log.values())
    lines.append('''
<div class="notice">
  <div class="notice-title">📊 筛选说明</div>
  <ul>
    <li><strong>已排除 {excl_total} 个</strong>：编程/技术类（与 B2B 出海老板/员工日常使用不符）</li>
    <li><strong>按功能分类</strong>：基于 description 关键词（不显示合集来源）</li>
    <li><strong>不显示合集</strong>：你关注的是"做什么"，不是"哪里来"</li>
  </ul>
  <ul>
''')
    for reason, count in list(excluded_log.items())[:8]:
        lines.append(f'    <li>{reason}: {count}</li>')
    lines.append('  </ul>')
    lines.append('</div>')

    # Categories
    for cat_name in ['内容创作', '营销推广', '翻译出海', '效率办公', '销售客户',
                     'HR 招聘', '财务行政', '数据分析', '客户支持', '产品设计',
                     '学习研究', 'AI 创作', '其他']:
        skills = by_category.get(cat_name, [])
        if not skills:
            continue

        # 按 description 长度排序（详细优先）
        skills_sorted = sorted(skills, key=lambda x: -len(x['description']))

        lines.append(f'''
<section>
  <div class="category-header">
    <span class="category-badge">{cat_name}</span>
    <span class="category-count">{len(skills)} 个 skill</span>
  </div>
  <div class="cards">
''')
        for s in skills_sorted:
            safe_name = s['name'].replace('"', '&quot;').replace("'", '&#39;')
            safe_desc = s['description'].replace('"', '&quot;').replace("'", '&#39;').replace('\n', ' ').replace('|', '\\|')
            lines.append(f'''
    <div class="card">
      <input type="checkbox" class="card-checkbox"
        data-id="{safe_name}"
        data-name="{safe_name}"
        data-url="{s['url']}"
        data-desc="{safe_desc}"
        data-category="{cat_name}">
      <a href="{s['url']}" class="card-name" target="_blank">{s['name']}</a>
      <div class="card-desc">{s['description']}</div>
      <div class="card-meta">
        <span>📂 {cat_name}</span>
      </div>
    </div>
''')
        lines.append('  </div>\n</section>')

    # Footer + JS
    lines.append('''
<footer>
  <p><strong>B2B 出海企业 Skills 精选</strong></p>
  <p>由 <code>expand_v3.py</code> 生成 · 排除编程类 · 适用于老板 + 员工日常使用</p>
  <p>生成时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M') + '''</p>
  <p style="margin-top: 16px; font-size: 0.9em;">
    ⌨️ 快捷键: <kbd>Ctrl+A</kbd> 全选 · <kbd>Esc</kbd> 清空 · 点击卡片也可选中
  </p>
</footer>
</div>

<script>
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
  cb.checked = !cb.checked; updateUI();
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
  const lines = ['# 🎯 B2B 出海精选 Skills', '',
    `> 共 ${data.length} 个 · 日常生活 + 出海 + 老板员工通用 · ${new Date().toISOString().slice(0,10)}`, ''];

  // 按 category 分组
  const byCat = {};
  data.forEach(s => { (byCat[s.category] = byCat[s.category] || []).push(s); });
  Object.keys(byCat).forEach(cat => {
    lines.push(`## ${cat}（${byCat[cat].length} 个）`);
    lines.push('');
    byCat[cat].forEach(s => {
      lines.push(`- **${s.name}** — ${s.desc.slice(0, 100)} ([link](${s.url}))`);
    });
    lines.push('');
  });

  return lines.join('\\n');
}

function buildJSON(data) {
  return JSON.stringify({
    exported_at: new Date().toISOString(),
    count: data.length,
    source: 'candidates-v3.html (B2B 出海精选)',
    skills: data
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

restoreSelection();
updateUI();
</script>
</body></html>
''')

    return ''.join(lines)


if __name__ == '__main__':
    main()