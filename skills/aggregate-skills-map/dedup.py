#!/usr/bin/env python
"""
dedup.py v0.2 - tag-based 聚合 + 跨分类 skill 去重

用法:
    ./dedup.py
    ./dedup.py --no-cache
    ./dedup.py --output dedup-map.md

设计依据:
    - 单一 id: 跨分类 skill 用 tags 表示多分类（消除 v0.1 的 -xhs/-ui 变体）
    - primary_category: 主分类用于直接聚合
    - tags: 次要分类用于跨视角展示
    - 4 级分类树: 认知科学 7±2 + GitHub awesome 模板

依赖: gh CLI 已登录、PyYAML
"""
import yaml, sys, json, subprocess, argparse
from pathlib import Path
from collections import defaultdict

# Windows 编码修复
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
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_cache(cache):
    CACHE_FILE.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def fetch_repo_data(owner_repo):
    """通过 gh API 拉仓库最新数据（用于 stars 字段更新）"""
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner_repo}', '--jq',
         '{name: .name, full_name: .full_name, stars: .stargazers_count, '
         'desc: .description, topics: .topics, html_url: .html_url, '
         'updated_at: .updated_at, fork: .fork}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def enrich_skills(skills, cache, use_cache=True, awesome_repo='Alexxiang2008/awesome-skills-map'):
    """为 skill 拉最新 stars + 处理本地 skill URL"""
    enriched = []
    for skill in skills:
        is_local = skill.get('type') == 'local_skill' or not skill.get('repo')

        if is_local:
            # 本地 skill：用 path 字段构造 awesome-skills-map 仓库 URL
            path = skill.get('path', '')
            url = f"https://github.com/{awesome_repo}/tree/main/{path}" if path else f"https://github.com/{awesome_repo}"
            skill = {**skill, 'live_stars': 0, 'is_local': True, 'live_url': url, 'stars_display': '📍 本地'}
        else:
            repo = skill.get('repo', '')
            from _shared import cache_key
            ck = cache_key('repo', repo)
            if use_cache and ck in cache:
                data = cache[ck]
            else:
                data = fetch_repo_data(repo)
                if data:
                    cache[ck] = data
            if data:
                stars = data.get('stars', 0)
                skill = {**skill, 'live': data, 'live_stars': stars,
                         'live_url': data.get('html_url', f"https://github.com/{repo}"),
                         'stars_display': f"{stars:,}"}
            else:
                skill = {**skill, 'live_stars': skill.get('stars', 0),
                         'live_url': f"https://github.com/{repo}",
                         'stars_display': f"{skill.get('stars', 0):,}"}
        enriched.append(skill)
    return enriched


# ============================================================
# 分类树遍历
# ============================================================

def find_leaves_with_tags(categories, path=''):
    """递归找所有叶子节点（带 tag 字段），返回 [(path, name, tag), ...]"""
    leaves = []
    if not isinstance(categories, dict):
        return leaves
    for k, v in categories.items():
        if k in ('name', 'description', 'children'):
            continue
        if isinstance(v, dict):
            current_path = f"{path}/{k}" if path else k
            if 'tag' in v:
                leaves.append((current_path, v.get('name', k), v['tag']))
            if 'children' in v:
                leaves.extend(find_leaves_with_tags(v['children'], current_path))
    return leaves


def find_category_nodes(categories, path=''):
    """找所有一级和二级节点（用于分类树显示）"""
    nodes = []
    if not isinstance(categories, dict):
        return nodes
    name = categories.get('name', '')
    desc = categories.get('description', '')
    if name:
        nodes.append((path or '(root)', name, desc, 'top'))
    for k, v in categories.items():
        if k in ('name', 'description', 'children'):
            continue
        if isinstance(v, dict):
            current_path = f"{path}/{k}" if path else k
            node_name = v.get('name', k)
            node_desc = v.get('description', '')
            tag = v.get('tag', '')
            kind = 'leaf' if tag else 'branch'
            nodes.append((current_path, node_name, node_desc, kind, tag))
            if 'children' in v:
                nodes.extend(find_category_nodes(v['children'], current_path))
    return nodes


# ============================================================
# 渲染
# ============================================================

def render_repeat_table(skills_in_cat, by_tag_count):
    """A 类高重复：出对比表"""
    out = []
    sorted_skills = sorted(skills_in_cat, key=lambda x: -x.get('live_stars', 0))
    out.append("| ⭐ | 类型 | 作者 | 仓库 | 简介 | 标签 |")
    out.append("|----|------|------|------|------|------|")
    for s in sorted_skills:
        stars_disp = s.get('stars_display', '0')
        author = s.get('author', '?')
        type_ = s.get('type', '?')
        if s.get('is_local'):
            path = s.get('path', '')
            repo_name = path or 'awesome-skills-map'
        else:
            repo_name = s.get('repo', '?')
        url = s.get('live_url', '')
        live = s.get('live', {})
        desc = (live.get('desc') if live else s.get('note', '')) or ''
        desc = desc[:70].replace('|', '\\|').replace('\n', ' ')
        tags_str = ', '.join(s.get('tags', []))
        out.append(f"| {stars_disp} | {type_} | {author} | [{repo_name}]({url}) | {desc} | `{tags_str}` |")
    out.append("")
    # 场景化推荐
    if sorted_skills:
        out.append("**🎯 场景化推荐**（基于 stars + 类型 + 标签）：")
        out.append("")
        for s in sorted_skills[:2]:
            sid = s.get('id', '?')
            stars_disp = s.get('stars_display', '0')
            note = s.get('note', '')[:60]
            type_ = s.get('type', '?')
            out.append(f"- **{sid}**（{stars_disp} ⭐ · {type_}）：{note}")
        out.append("")
    return '\n'.join(out)


def render_tree(categories, skills_by_primary, skills_by_tag, depth=0):
    """递归渲染分类树 + skill 列表"""
    out = []
    if not isinstance(categories, dict):
        return out

    name = categories.get('name', '')
    desc = categories.get('description', '')
    if name:
        prefix = "  " * depth
        suffix = f"  *# {desc}*" if desc else ""
        out.append(f"{prefix}**{name}**{suffix}")
        out.append("")

    if 'children' in categories:
        for k, v in categories['children'].items():
            if isinstance(v, dict):
                current_path = k
                tag = v.get('tag')
                node_name = v.get('name', k)

                if tag:
                    # 叶子节点：通过 tag 聚合 skill
                    primary_skills = skills_by_primary.get(current_path, [])
                    tag_skills = skills_by_tag.get(tag, [])
                    # 合并去重（避免重复显示）
                    seen = set()
                    all_skills = []
                    for s in primary_skills + tag_skills:
                        sid = s.get('id')
                        if sid not in seen:
                            seen.add(sid)
                            all_skills.append(s)

                    indent = "  " * (depth + 1)
                    if len(all_skills) >= 2:
                        out.append(f"{indent}🔴 **{node_name}**（{len(all_skills)} 个 skill，A 类重复）")
                    elif len(all_skills) == 1:
                        out.append(f"{indent}📦 **{node_name}**（{len(all_skills)} 个 skill）")
                    else:
                        out.append(f"{indent}⭕ **{node_name}**（暂无）")

                    # 列出每个 skill
                    for s in sorted(all_skills, key=lambda x: -x.get('live_stars', 0)):
                        sid = s.get('id', '?')
                        stars_disp = s.get('stars_display', '0')
                        note = s.get('note', '')[:50]
                        author = s.get('author', '?')
                        type_ = s.get('type', '?')
                        # 标记主分类外的额外分类
                        extra_tags = [t for t in s.get('tags', []) if t != tag]
                        extra_str = f" · 还属于: {', '.join(extra_tags)}" if extra_tags else ""
                        indent2 = "  " * (depth + 2)
                        out.append(f"{indent2}- `{sid}` · {stars_disp} ⭐ · [{type_}] · @{author} — {note}{extra_str}")
                    out.append("")
                else:
                    # 中间节点：递归
                    out.append(f"{indent}**{node_name}**")
                    out.append("")
                    out.extend(render_tree({'children': v}, skills_by_primary, skills_by_tag, depth + 1).split('\n'))

    return '\n'.join(line for line in out if line is not None)


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='按 taxonomy 聚合 GitHub skills (v0.2)')
    parser.add_argument('--no-cache', action='store_true', help='跳过缓存，强制重新拉数据')
    parser.add_argument('--output', '-o', help='输出文件路径（默认 stdout）')
    parser.add_argument('--taxonomy', default=str(TAXONOMY_FILE), help='taxonomy.yaml 路径')
    args = parser.parse_args()

    taxonomy = load_taxonomy(args.taxonomy)
    cache = {} if args.no_cache else load_cache()
    skills = enrich_skills(taxonomy.get('skills', []), cache, use_cache=not args.no_cache)
    save_cache(cache)

    # 索引
    skills_by_primary = defaultdict(list)
    skills_by_tag = defaultdict(list)
    for s in skills:
        pc = s.get('primary_category', '')
        if pc:
            skills_by_primary[pc].append(s)
        for t in s.get('tags', []):
            skills_by_tag[t].append(s)

    # A 类检测（同一 primary_category ≥2 个）
    duplicates = {p: ss for p, ss in skills_by_primary.items() if len(ss) >= 2}

    out = []
    meta = taxonomy.get('meta', {})
    out.append(f"# 🎯 Skills Dedup Map v0.2（tag-based 聚合）\n")
    out.append(f"> taxonomy 版本: v{meta.get('version', '?')} ({meta.get('date', '?')})"
               f" · 总 skill 数: **{len(skills)}**"
               f" · 覆盖博主/来源: {len(meta.get('authors', {}))} 个")
    out.append("")
    out.append("**设计变更（v0.1 → v0.2）**：")
    out.append("- tag-based 重构：每个 skill 单一 id + tags 字段")
    out.append("- 跨分类合并：同 repo 用同 id，tags 表示多分类")
    out.append("- 整合 22 章原始技能")
    out.append("- 自研 1 个元能力")
    out.append("")
    out.append(f"**聚合结果**：{len(duplicates)} 个 A 类重复聚类"
               f" + {len(skills) - sum(len(ss) for ss in duplicates.values()) + len(duplicates)} 个独立 skill")
    out.append("")
    out.append("---")
    out.append("")

    # A 类高重复
    if duplicates:
        out.append("## 🔴 A 类高重复聚类")
        out.append("")
        out.append("> 判定标准：同一 `primary_category` 下 ≥2 个 skill。需用户做场景化决策。")
        out.append("")
        # 按聚类大小排序
        for path in sorted(duplicates.keys(), key=lambda p: -len(duplicates[p])):
            skills_in = duplicates[path]
            out.append(f"### `{path}` ({len(skills_in)} 个)")
            out.append("")
            out.append(render_repeat_table(skills_in, defaultdict(int)))
        out.append("---")
        out.append("")

    # 跨分类 skill（tags 多个的）
    multi_tag_skills = [s for s in skills if len(s.get('tags', [])) >= 2]
    if multi_tag_skills:
        out.append("## 🌐 跨分类 skill（tags ≥ 2）")
        out.append("")
        out.append("> 这些 skill 同时属于多个分类，是 dedup 的核心价值。")
        out.append("")
        out.append("| ⭐ | skill | 作者 | 标签 |")
        out.append("|----|-------|------|------|")
        for s in sorted(multi_tag_skills, key=lambda x: -x.get('live_stars', 0)):
            stars = s.get('live_stars', 0)
            sid = s.get('id', '?')
            author = s.get('author', '?')
            tags_str = ' / '.join(s.get('tags', []))
            out.append(f"| {stars:,} | `{sid}` | {author} | {tags_str} |")
        out.append("")
        out.append("---")
        out.append("")

    # 完整分类树
    out.append("## 📂 完整分类树")
    out.append("")
    out.append(render_tree(taxonomy['categories'], skills_by_primary, skills_by_tag, depth=0))

    # 隐藏洞察
    out.append("---")
    out.append("")
    out.append("## 🔍 隐藏洞察")
    out.append("")

    # 作者维度
    by_author = defaultdict(lambda: {'count': 0, 'stars': 0})
    for s in skills:
        by_author[s.get('author', '?')]['count'] += 1
        by_author[s.get('author', '?')]['stars'] += s.get('live_stars', 0)

    out.append("### 👥 作者分布")
    out.append("")
    out.append("| 作者 | skill 数 | ⭐ 总和 | 平均 ⭐ |")
    out.append("|------|---------|--------|---------|")
    for author, stats in sorted(by_author.items(), key=lambda x: -x[1]['stars']):
        avg = stats['stars'] // max(stats['count'], 1)
        out.append(f"| {author} | {stats['count']} | {stats['stars']:,} | {avg:,} |")
    out.append("")

    # 类型分布
    by_type = defaultdict(int)
    for s in skills:
        by_type[s.get('type', 'skill')] += 1
    out.append("### 🏷️ 类型分布")
    out.append("")
    out.append("| type | 数量 |")
    out.append("|------|------|")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        out.append(f"| {t} | {n} |")
    out.append("")

    # 类型维度第二视图（v0.3 新增）
    out.append("---")
    out.append("")
    out.append("## 🧩 按类型第二视图")
    out.append("")
    out.append("> 第一维度是 `primary_category`（职能），第二维度是 `type`（形态）。同一 skill 可同时跨两维。")
    out.append("")

    type_descriptions = {
        'skill': '独立 skill',
        'sub_skill': '合集下的子技能',
        'collection': '多 skill 合集',
        'book': '书籍/教程',
        'tool': '工具/脚本/服务',
        'meta': '元能力',
        'local_skill': '本地 22 章',
    }

    for t in ['meta', 'collection', 'book', 'sub_skill', 'skill', 'tool', 'local_skill']:
        skills_of_type = [s for s in skills if s.get('type') == t]
        if not skills_of_type:
            continue
        desc = type_descriptions.get(t, t)
        out.append(f"### 🏷️ `{t}` · {desc}（{len(skills_of_type)} 个）")
        out.append("")
        out.append("| ⭐ | skill | 作者 | 主分类 | 标签 |")
        out.append("|----|-------|------|--------|------|")
        for s in sorted(skills_of_type, key=lambda x: -x.get('live_stars', 0)):
            stars_disp = s.get('stars_display', '0')
            sid = s.get('id', '?')
            url = s.get('live_url', '')
            author = s.get('author', '?')
            pc = s.get('primary_category', '?')
            tags_str = ', '.join(s.get('tags', []))
            out.append(f"| {stars_disp} | [{sid}]({url}) | {author} | `{pc}` | `{tags_str}` |")
        out.append("")

    # v0.3 主动审查区块
    out.append("---")
    out.append("")
    out.append("## 🔍 v0.3 主动审查（自我 spot check）")
    out.append("")
    out.append("> 这是 dedup.py 自动生成的自我审查清单，标出可能需要你确认的边缘 case。")
    out.append("")

    # 问题 1：distill_person 全是花叔
    distill_person = skills_by_tag.get('distill_person', [])
    alchaincyf_distill = [s for s in distill_person if s.get('author') == 'alchaincyf']
    if len(alchaincyf_distill) >= 3:
        out.append(f"### ⚠️ 问题 1：distill_person 4 个里 {len(alchaincyf_distill)} 个全是花叔（nuwa 衍生品）")
        out.append("")
        out.append("- **现状**：花叔的 nuwa-skill 是 meta-skill，其他 3 个（zhangxuefeng/steve-jobs/x-mentor）是 nuwa 衍生的具体人物")
        out.append("- **判断**：是合理的——它们就是同一作者的子产品")
        out.append("- **建议**：保留现状，但在 docs 里说明 \"nuwa 生态\" 子分支")
        out.append("")

    # 问题 2：本地 skill 跨多个 A 类
    local_a_class = []
    for path, ss in duplicates.items():
        for s in ss:
            if s.get('is_local'):
                local_a_class.append((path, s))
    if local_a_class:
        out.append(f"### ⚠️ 问题 2：{len(local_a_class)} 个本地 skill 出现在 A 类聚类里")
        out.append("")
        out.append("- **现状**：本地 skill（一人课程）和 5 博主 skill 在同一分类下")
        out.append("- **判断**：合理——同一职能下多家实现，对比表有价值")
        out.append("- **建议**：保留，但本地 skill 在对比表中加 📍 标记")
        out.append("")

    # 问题 3：跨分类 skill 是否有过度跨类
    cross_count = sum(1 for s in skills if len(s.get('tags', [])) >= 3)
    if cross_count:
        out.append(f"### ⚠️ 问题 3：{cross_count} 个 skill 有 ≥3 个 tags（跨多类）")
        out.append("")
        out.append("- **判断**：tags 多不等于分类错误，但要警惕\"什么都做\"的 skill")
        out.append("- **建议**：人工 review 每个跨类 skill，确认 primary_category 是否准确")
        out.append("")

    # 问题 4：单点分类
    single_categories = []
    for path, ss in skills_by_primary.items():
        if len(ss) == 1 and path:
            single_categories.append(path)
    out.append(f"### 💡 问题 4：{len(single_categories)} 个分类是单点（只有 1 个 skill）")
    out.append("")
    out.append("- **判断**：单点分类不一定是错（有些就是 unique 领域），但提示可能合并或扩类")
    if len(single_categories) <= 10:
        out.append("- **单点分类清单**：")
        for p in single_categories:
            out.append(f"  - `{p}`")
    out.append("")

    output = '\n'.join(out)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已写入 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()