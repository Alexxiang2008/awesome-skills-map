#!/usr/bin/env python
"""
discover.py - 搜索 GitHub 上更多 Claude skill 候选 + 评分

工作流:
1. 用 gh search 拉多个 topic 的仓库（claude-skill / claude-code / agent-skill）
2. 排除索引库（awesome-* / curated list / 框架工具）
3. 对候选跑 quality_score（fast 模式）
4. 输出 score ≥ 阈值的"待入库"清单
"""
import yaml, sys, json, subprocess, argparse
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

from _shared import ok_msg, warn_msg, err_msg

CACHE_FILE = Path(__file__).parent / '.discover_cache.json'


# ============================================================
# 搜索
# ============================================================

def gh_search_repos(query, limit=50):
    """调用 gh search repos（注意 gh search 不支持 topics/htmlUrl 等字段）"""
    result = subprocess.run(
        ['gh', 'search', 'repos', query, '--limit', str(limit),
         '--json', 'name,fullName,description,stargazersCount,forksCount,'
         'pushedAt,isArchived,isFork,url,owner'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def search_candidates():
    """拉多个 topic 的候选"""
    all_repos = {}
    queries = [
        'topic:claude-skill stars:>100',
        'topic:claude-code skill stars:>500',
        'topic:agent-skill stars:>100',
        'topic:claude-skills stars:>100',
    ]
    for q in queries:
        print(f"🔍 搜索: {q}", file=sys.stderr)
        repos = gh_search_repos(q, limit=50)
        for r in repos:
            full_name = r.get('fullName')
            if full_name and full_name not in all_repos:
                all_repos[full_name] = r
    return list(all_repos.values())


# ============================================================
# 过滤
# ============================================================

EXCLUDE_KEYWORDS = [
    'awesome-', 'awesome/', 'curated list', 'awesome list',
    'awesome_claude', 'awesome-claude',
    'framework', ' boilerplate', ' starter kit',
]


def is_index_or_list(repo):
    """检测是否是索引库/awesome list/课程（应该排除）"""
    name = (repo.get('name') or '').lower()
    full = (repo.get('fullName') or '').lower()
    desc = (repo.get('description') or '').lower()

    # 关键词排除
    for kw in EXCLUDE_KEYWORDS:
        if kw in name or kw in full or kw in desc:
            return True

    # fork/archived 排除
    if repo.get('isFork') or repo.get('isArchived'):
        return True

    # 极低 stars
    if repo.get('stargazersCount', 0) < 100:
        return True

    return False


def is_likely_skill(repo):
    """检测是否是真正的 skill（而非通用工具/库）"""
    name = (repo.get('name') or '').lower()
    desc = (repo.get('description') or '').lower()

    # 至少一个 skill 关键词（name 或 desc）
    skill_signals = ['skill', 'agent', 'claude-code', 'claude code']
    if any(s in name or s in desc for s in skill_signals):
        return True

    return False


# ============================================================
# 评分（简化版：直接用 gh 数据算硬指标）
# ============================================================

def normalize_stars(stars):
    import math
    if stars <= 0:
        return 0
    return min(math.log10(stars / 100) / math.log10(500), 1.0)


def normalize_recency(pushed_at, days_full=180, days_zero=730):
    from datetime import datetime, timezone
    if not pushed_at:
        return 0
    try:
        pushed = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        days = (now - pushed).days
        if days <= days_full:
            return 1.0
        if days >= days_zero:
            return 0.0
        return (days_zero - days) / (days_zero - days_full)
    except (ValueError, AttributeError):
        return 0


def normalize_forks_ratio(forks, stars):
    if stars == 0:
        return 0
    ratio = forks / stars
    return min(max((ratio - 0.05) / 0.15, 0), 1.0)


def quick_score(repo):
    """快速硬指标评分（0-95）"""
    stars = repo.get('stargazersCount', 0)
    forks = repo.get('forksCount', 0)
    pushed = repo.get('pushedAt')

    score = 0
    score += normalize_stars(stars) * 30
    score += normalize_forks_ratio(forks, stars) * 15
    score += normalize_recency(pushed) * 25

    # 卫生指标（gh search 没 license/topics，给保底分）
    # 没有 license/topics 数据时，给 0 分（不可推断）
    # 但为了避免所有候选都低分，给 5 分基础分（有 description 就算）
    if repo.get('description'):
        score += 5

    return round(score, 1), {
        'stars': stars,
        'forks': forks,
        'pushed_at': pushed,
    }


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-score', type=float, default=50)
    parser.add_argument('--limit', type=int, default=200, help='每个 topic 拉取上限')
    parser.add_argument('--output', '-o', default='examples/discover-candidates.md')
    args = parser.parse_args()

    # 1. 搜索候选
    print(f"📡 搜索 GitHub Claude skill 候选...", file=sys.stderr)
    candidates = search_candidates()
    print(f"  原始候选: {len(candidates)}", file=sys.stderr)

    # 2. 排除索引库
    filtered = [r for r in candidates if not is_index_or_list(r)]
    print(f"  排除索引库/低星: {len(filtered)}", file=sys.stderr)

    # 3. 过滤非 skill
    likely_skills = [r for r in filtered if is_likely_skill(r)]
    print(f"  真 skill 候选: {len(likely_skills)}", file=sys.stderr)

    # 4. 评分
    scored = []
    for repo in likely_skills:
        score, breakdown = quick_score(repo)
        scored.append({
            'name': repo.get('name'),
            'full_name': repo.get('fullName'),
            'description': repo.get('description'),
            'url': repo.get('url'),
            'score': score,
            **breakdown,
        })

    scored.sort(key=lambda x: -x['score'])

    # 5. 输出
    out = []
    out.append(f"# 🔍 Claude Skills 候选清单（自动发现 v0.1）\n")
    out.append(f"> 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    out.append(f"> 数据源: GitHub search（topic: claude-skill/claude-code/agent-skill/claude-skills）")
    out.append(f"> 阈值: score ≥ {args.min_score}\n")
    out.append("---")
    out.append("")
    out.append("## 📊 扫描统计")
    out.append("")
    out.append(f"- 原始候选: {len(candidates)}")
    out.append(f"- 排除索引库/低星: {len(filtered)}")
    out.append(f"- 真 skill 候选: {len(likely_skills)}")
    out.append(f"- **≥ {args.min_score} 入选: {sum(1 for s in scored if s['score'] >= args.min_score)} 个**")
    out.append("")

    qualified = [s for s in scored if s['score'] >= args.min_score]
    out.append(f"## 🎯 入选清单（score ≥ {args.min_score}）\n")
    out.append("| 排名 | score | ⭐ | forks/stars | 最后 commit | skill | 仓库 | 简介 |")
    out.append("|------|-------|----|-------------|-------------|-------|------|------|")
    for i, s in enumerate(qualified, 1):
        stars = s['stars']
        forks = s['forks']
        ratio = (forks / stars * 100) if stars > 0 else 0
        pushed = s['pushed_at'][:10] if s['pushed_at'] else '-'
        desc = (s.get('description') or '')[:60].replace('|', '\\|').replace('\n', ' ')
        out.append(f"| {i} | {s['score']:.1f} | {stars:,} | {ratio:.1f}% | {pushed} | `{s['name']}` | [{s['full_name']}]({s['url']}) | {desc} |")
    out.append("")

    # 排除的低分候选（参考）
    below = [s for s in scored if s['score'] < args.min_score][:20]
    if below:
        out.append(f"## 📋 候选池（score < {args.min_score}，前 20）\n")
        out.append("> 这些是有潜力的低分候选，可能 star 没涨起来。")
        out.append("")
        for s in below:
            stars = s['stars']
            out.append(f"- `{s['name']}`（{s['score']:.1f} · {stars:,} ⭐）— {s['full_name']}")

    out.append("")
    out.append("---")
    out.append("")
    out.append("## 🔬 主动审查")
    out.append("")

    # 高分但低星（黑马）
    dark_horses = [s for s in qualified if s['stars'] < 500]
    if dark_horses:
        out.append(f"### 🌟 高分低星（score ≥ {args.min_score} 但 stars < 500）：{len(dark_horses)} 个潜在黑马")
        out.append("")
        for s in dark_horses:
            out.append(f"- **{s['name']}**（{s['score']:.1f} · {s['stars']:,} ⭐）: {(s.get('description') or '')[:80]}")
        out.append("")

    # 排除的 awesome 索引库
    excluded_index = [r for r in candidates if is_index_or_list(r) and 'awesome' in (r.get('name') or '').lower()]
    if excluded_index:
        out.append(f"### 🚫 已排除的索引库（{len(excluded_index)} 个）")
        out.append("")
        out.append("> 这些是 awesome list 索引库（不是真正的 skill）。")
        out.append("")
        for r in excluded_index[:10]:
            out.append(f"- `{r.get('fullName')}`（{r.get('stargazersCount', 0):,} ⭐）: {(r.get('description') or '')[:60]}")
        out.append("")

    output = '\n'.join(out)
    Path(args.output).write_text(output, encoding='utf-8')
    print(ok_msg("已写入 {args.output}（入选 {len(qualified)} 个）")), file=sys.stderr)
    print(output)


if __name__ == '__main__':
    main()