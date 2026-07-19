#!/usr/bin/env python
"""
dedup.py - 按 taxonomy.yaml 自动聚合 GitHub skills，输出分类视图 + 重复聚类对比表

用法:
    ./dedup.py                                  # 用默认 taxonomy
    ./dedup.py --no-cache                       # 跳过缓存
    ./dedup.py --min-stars 100                  # 自定义阈值
    ./dedup.py --output dedup-map.md            # 写入文件

设计依据:
    - A 类高重复（≥2 skill 同分类）→ 出对比表
    - B 类中重复 → 出"分工建议"
    - C 类低重复（仅 1 个）→ 普通列表
    - taxonomy 4 级层级来自认知科学 7±2 + GitHub awesome 模板

依赖: gh CLI 已登录、PyYAML
"""
import yaml, sys, json, subprocess, argparse
from pathlib import Path
from collections import defaultdict

# Windows 编码修复：stdout 强制 utf-8，支持 emoji + 中文
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

TAXONOMY_FILE = Path(__file__).parent / 'taxonomy.yaml'
CACHE_FILE = Path(__file__).parent / '.dedup_cache.json'

# ============================================================
# 数据加载
# ============================================================

def load_taxonomy(path=TAXONOMY_FILE):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache):
    CACHE_FILE.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def fetch_repo_data(owner_repo):
    """通过 gh API 拉仓库最新数据"""
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner_repo}', '--jq',
         '{name: .name, full_name: .full_name, stars: .stargazers_count, '
         'desc: .description, topics: .topics, html_url: .html_url, '
         'updated_at: .updated_at, fork: .fork}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        return None
    if not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def find_all_skills(node, path=''):
    """递归找 taxonomy 中所有 skill 节点，返回 [(path, skill), ...]"""
    skills = []
    if isinstance(node, dict):
        if 'skills' in node and isinstance(node['skills'], list):
            for skill in node['skills']:
                if isinstance(skill, dict):
                    skills.append((path, skill))
        for k, v in node.items():
            if k in ('skills', 'name', 'description'):
                continue
            if isinstance(v, dict):
                skills.extend(find_all_skills(v, f"{path}/{k}" if path else k))
    return skills


def collect_skills_data(taxonomy, cache, use_cache=True):
    """为每个 skill 拉最新数据"""
    enriched = []
    for path, skill in find_all_skills(taxonomy.get('skills', {})):
        repo = skill.get('repo')
        if not repo:
            continue
        if use_cache and repo in cache:
            data = cache[repo]
        else:
            data = fetch_repo_data(repo)
            if data:
                cache[repo] = data
        if data:
            enriched.append({**skill, 'data': data, '_path': path})
    return enriched


# ============================================================
# 渲染
# ============================================================

def render_repeat_table(path, skills):
    """A 类高重复：出对比表 + 场景推荐"""
    out = []
    sorted_skills = sorted(skills, key=lambda x: -x['data']['stars'])
    out.append(f"### 🔴 A 类高重复 · `{path}`（{len(skills)} 个 skill）\n")
    out.append("| ⭐ | 作者 | 仓库 | 简介 | 备注 |")
    out.append("|----|------|------|------|------|")
    for s in sorted_skills:
        stars = s['data']['stars']
        desc = (s['data'].get('desc') or '')[:100]
        note = s.get('note', '')
        out.append(f"| {stars:,} | {s['author']} | "
                   f"[{s['data']['full_name']}]({s['data']['html_url']}) | "
                   f"{desc} | {note} |")
    out.append("")
    out.append("**🎯 场景化推荐**（基于 stars + 备注启发）：")
    out.append("")
    for s in sorted_skills[:2]:  # top 2 简述
        out.append(f"- **{s['data']['full_name']}**（{s['data']['stars']:,} ⭐）"
                   f"：{(s.get('note') or s['data'].get('desc') or '（无描述）')[:80]}")
    out.append("")
    return '\n'.join(out)


def render_tree(node, out, indent=0, skills_by_path=None):
    """递归渲染分类树"""
    name = node.get('name', '')
    desc = node.get('description', '')
    if name:
        prefix = "  " * indent + "- "
        suffix = f" — {desc}" if desc else ""
        out.append(f"{prefix}**{name}**{suffix}")

    if 'skills' in node and isinstance(node['skills'], list):
        for skill in node['skills']:
            prefix = "  " * (indent + 1) + "- "
            sid = skill.get('id', '?')
            note = skill.get('note', '')
            author = skill.get('author', '?')
            star_str = ''
            if skills_by_path is not None:
                path_key = skill.get('_lookup_path', '')
                if path_key in skills_by_path:
                    star_str = f" ({skills_by_path[path_key]['data']['stars']:,} ⭐)"
            extra = f" — {note}" if note else ""
            out.append(f"{prefix}`{sid}`{star_str} · @{author}{extra}")

    for k, v in node.items():
        if k in ('skills', 'name', 'description'):
            continue
        if isinstance(v, dict):
            render_tree(v, out, indent + 1, skills_by_path)


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='按 taxonomy 聚合 GitHub skills')
    parser.add_argument('--no-cache', action='store_true', help='跳过缓存，强制重新拉数据')
    parser.add_argument('--output', '-o', help='输出文件路径（默认 stdout）')
    parser.add_argument('--taxonomy', default=str(TAXONOMY_FILE), help='taxonomy.yaml 路径')
    args = parser.parse_args()

    taxonomy = load_taxonomy(args.taxonomy)
    cache = {} if args.no_cache else load_cache()
    skills_data = collect_skills_data(taxonomy, cache, use_cache=not args.no_cache)
    save_cache(cache)

    # 按 path 聚合
    by_path = defaultdict(list)
    for skill in skills_data:
        by_path[skill['_path']].append(skill)

    # 找出 A 类（≥2 同 path）
    duplicates = {p: ss for p, ss in by_path.items() if len(ss) >= 2}
    singles = {p: ss for p, ss in by_path.items() if len(ss) == 1}

    out = []
    out.append("# 🎯 Skills Dedup Map（按 taxonomy 聚合）\n")
    meta = taxonomy.get('meta', {})
    out.append(f"> taxonomy 版本: v{meta.get('version', '?')} ({meta.get('date', '?')})"
               f" · 总 skill 数: **{len(skills_data)}**"
               f" · 覆盖博主: {len(meta.get('authors', {}))} 位")
    out.append("")
    out.append(f"**聚合结果**：{len(duplicates)} 个重复聚类（A 类）+ "
               f"{len(singles)} 个独立 skill")
    out.append("")
    out.append("---")
    out.append("")

    # A 类高重复
    if duplicates:
        out.append("## 🔴 重复聚类（A 类 · 高重复）")
        out.append("")
        out.append("> 判定标准：同一分类下 ≥2 个 skill 候选。基于 stars + 备注给场景化推荐。")
        out.append("")
        for path in sorted(duplicates.keys(), key=lambda p: -len(duplicates[p])):
            out.append(render_repeat_table(path, duplicates[path]))

    # 完整分类树（含 stars）
    out.append("---")
    out.append("")
    out.append("## 📂 完整分类树")
    out.append("")
    out.append("> 4 级层级：内容创作 / 设计视觉 / 元能力 / 内容汇聚 / 开发工具 / 合集教程")
    out.append("")
    out.append("### 关键指标速览")
    out.append("")
    out.append("| 分类 | skill 数 | 总 ⭐ | 作者数 |")
    out.append("|------|---------|-------|--------|")
    for path, ss in sorted(by_path.items()):
        authors = set(s['author'] for s in ss)
        total_stars = sum(s['data']['stars'] for s in ss)
        out.append(f"| `{path}` | {len(ss)} | {total_stars:,} | {len(authors)} |")
    out.append("")
    out.append("### 层级结构")
    out.append("")
    render_tree(taxonomy.get('skills', {}), out, indent=0)

    # 隐藏洞察
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 🔍 隐藏洞察（数据说话）")
    out.append("")
    if duplicates:
        largest = max(duplicates.items(), key=lambda x: len(x[1]))
        out.append(f"- **最大重复聚类**：`{largest[0]}` 有 {len(largest[1])} 个 skill 候选")
        out.append(f"  → 用户面临 **{len(largest[1])} 选 1** 的决策，对比表价值最高")
    top_author = defaultdict(int)
    for s in skills_data:
        top_author[s['author']] += s['data']['stars']
    if top_author:
        king = max(top_author.items(), key=lambda x: x[1])
        out.append(f"- **⭐ 之王**：{king[0]}（{king[1]:,} ⭐ 总和）")
    out.append(f"- **唯一性**：{len(singles)}/{len(skills_data)} 个分类是单作者独占（{len(singles)*100//max(len(skills_data),1)}%）")
    out.append("")

    output = '\n'.join(out)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已写入 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()