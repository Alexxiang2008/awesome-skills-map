#!/usr/bin/env python
"""
quality_score.py - 优质 skill 评分系统（v1.0）

设计依据:
    4 维硬指标 (80 分):
      - stars (30): log10 归一化
      - forks_ratio (15): forks/stars，越高说明真用
      - recency (25): 最近 commit，180 天内线性衰减
      - issue_close_rate (10): 维护响应

    4 维卫生指标 (15 分):
      - has_skill_md (5): 是否真有 SKILL.md
      - has_license (3): 开源协议
      - has_install (3): npx skills add 等
      - has_topics (2): GitHub tags
      - has_readme (2): README 存在

    3 维生态信号 (5 分 bonus):
      - awesome_list_bonus (3): 被 ComposioHQ 等收录
      - install_command_bonus (1): 一行安装
      - cross_platform_bonus (1): Claude Code + Codex 兼容

    3 维 LLM 评分 (20 分, --with-llm 启用):
      - doc_quality (8): README/SKILL.md 质量
      - innovativeness (6): 是否解决真问题
      - practicality (6): 场景实用性

    总分 120 (>= 60 入选)

依赖: gh CLI, PyYAML, (可选: anthropic SDK)
"""
import yaml, sys, json, subprocess, argparse, os, re
from pathlib import Path
from datetime import datetime, timezone

# Windows UTF-8 修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

TAXONOMY_FILE = Path(__file__).parent / 'taxonomy.yaml'
CACHE_FILE = Path(__file__).parent / '.quality_cache.json'

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


def fetch_repo_metrics(repo):
    """拉取仓库完整指标（含默认分支 + SKILL.md 检测）"""
    result = subprocess.run(
        ['gh', 'api', f'repos/{repo}', '--jq',
         '{name: .name, full_name: .full_name, stars: .stargazers_count, '
         'forks: .forks_count, watchers: .subscribers_count, '
         'pushed_at: .pushed_at, updated_at: .updated_at, '
         'created_at: .created_at, has_issues: .has_issues, '
         'open_issues: .open_issues, license: (.license.spdx_id // null), '
         'description: .description, topics: .topics, '
         'html_url: .html_url, default_branch: .default_branch, '
         'language: .language, archived: .archived, fork: .fork}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def check_skill_md(repo, branch='main'):
    """检查仓库是否有 SKILL.md"""
    for path in ['SKILL.md', '.claude/skills/SKILL.md', 'skills/SKILL.md']:
        result = subprocess.run(
            ['gh', 'api', f'repos/{repo}/contents/{path}?ref={branch}',
             '--jq', '.name // empty'],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout.strip():
            return True
    return False


def check_readme(repo, branch='main'):
    """检查是否有 README"""
    result = subprocess.run(
        ['gh', 'api', f'repos/{repo}/readme?ref={branch}',
         '--jq', '.name // empty'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def fetch_issue_close_rate(repo):
    """估算 issue 关闭率"""
    result = subprocess.run(
        ['gh', 'api', f'search/issues?q=repo:{repo}+type:issue',
         '--jq', '{total: .total_count}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        return None, None, None
    try:
        data = json.loads(result.stdout)
        total = data.get('total', 0)
        if total == 0:
            return 0, 0, 1.0  # 无 issue 视为 100%
    except json.JSONDecodeError:
        return None, None, None

    # 查关闭 issue
    result2 = subprocess.run(
        ['gh', 'api', f'search/issues?q=repo:{repo}+type:issue+is:closed',
         '--jq', '{total: .total_count}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    try:
        closed = json.loads(result2.stdout).get('total', 0)
        rate = closed / total if total > 0 else 1.0
        return total, closed, rate
    except json.JSONDecodeError:
        return total, None, None


# ============================================================
# 评分函数
# ============================================================

def normalize_stars(stars):
    """log10 归一化: 100⭐=0, 1K⭐=0.33, 10K⭐=0.67, 50K⭐=0.87"""
    import math
    if stars <= 0:
        return 0
    return min(math.log10(stars / 100) / math.log10(500), 1.0)


def normalize_recency(pushed_at, days_full=180, days_zero=730):
    """Recency 衰减: 180 天内=1.0, 730+ 天=0"""
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
        # 线性衰减
        return (days_zero - days) / (days_zero - days_full)
    except (ValueError, AttributeError):
        return 0


def normalize_forks_ratio(forks, stars):
    """forks/stars 比: 0.05 以下=0, 0.20+ =1.0"""
    if stars == 0:
        return 0
    ratio = forks / stars
    return min(max((ratio - 0.05) / 0.15, 0), 1.0)


def calculate_hard_score(metrics, has_skill_md, has_readme, issue_close_rate):
    """
    返回 (score, breakdown)
    """
    breakdown = {}

    # 1. Stars (30 分)
    s = normalize_stars(metrics.get('stars', 0)) * 30
    breakdown['stars'] = round(s, 1)

    # 2. Forks/Stars ratio (15 分)
    f = normalize_forks_ratio(metrics.get('forks', 0), metrics.get('stars', 0)) * 15
    breakdown['forks_ratio'] = round(f, 1)

    # 3. Recency (25 分)
    r = normalize_recency(metrics.get('pushed_at')) * 25
    breakdown['recency'] = round(r, 1)

    # 4. Issue close rate (10 分)
    if issue_close_rate is None:
        i = 0
    else:
        i = issue_close_rate * 10
    breakdown['issue_close'] = round(i, 1)

    # 5. Has SKILL.md (5 分)
    breakdown['has_skill_md'] = 5 if has_skill_md else 0

    # 6. Has License (3 分)
    breakdown['has_license'] = 3 if metrics.get('license') else 0

    # 7. Has README (2 分)
    breakdown['has_readme'] = 2 if has_readme else 0

    # 8. Has topics (2 分)
    breakdown['has_topics'] = 2 if metrics.get('topics') else 0

    # 9. Has install command (3 分)
    install_indicators = ['npx skills', 'npx @', 'pip install', 'npm install']
    desc = (metrics.get('description') or '') + ' ' + (metrics.get('full_name') or '')
    has_install = any(ind in desc.lower() for ind in install_indicators)
    breakdown['has_install'] = 3 if has_install else 0

    # 总和
    total = sum(breakdown.values())
    return round(total, 1), breakdown


def calculate_ecosystem_bonus(metrics, full_name):
    """3 维生态信号（额外加分，最高 5 分）"""
    bonus = 0

    # 被顶级 awesome-list 收录（间接判断：description 含 "awesome"）
    desc = (metrics.get('description') or '').lower()
    if 'awesome' in desc or 'curated list' in desc:
        # 但 awesome 索引库自己应该是被排除的（已在 description 里）
        # 这里加 bonus 不合适
        pass

    # 跨平台（Claude Code + Codex 等）
    topics = metrics.get('topics') or []
    has_claude = any('claude' in t for t in topics)
    has_codex = any('codex' in t for t in topics)
    if has_claude and has_codex:
        bonus += 2

    # Topics 完整（≥3 个）
    if len(topics) >= 3:
        bonus += 1

    return min(bonus, 5)


def calculate_llm_score(metrics, skill_md_content=None):
    """
    3 维 LLM 评分（需要 anthropic SDK）
    返回 (score, breakdown)
    """
    try:
        import anthropic
    except ImportError:
        return None, {'error': 'anthropic SDK 未安装'}

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return None, {'error': 'ANTHROPIC_API_KEY 未设置'}

    client = anthropic.Anthropic(api_key=api_key)

    desc = metrics.get('description', '')
    prompt = f"""评估这个 GitHub Claude Skill 项目的质量。

仓库信息：
- 名称: {metrics.get('full_name', '')}
- 描述: {desc}
- Stars: {metrics.get('stars', 0):,}
- Topics: {', '.join(metrics.get('topics') or [])}

请从三个维度评分（0-1）：

1. **doc_quality**：文档/描述质量（README 质量、说明清晰度）
2. **innovativeness**：创新性（解决真问题 vs 重复造轮）
3. **practicality**：实用性（场景真实、有用户案例）

输出 JSON 格式：{{"doc_quality": 0.X, "innovativeness": 0.X, "practicalty": 0.X, "reason": "一句话理由"}}"""

    try:
        msg = client.messages.create(
            model='claude-sonnet-4-5',
            max_tokens=512,
            messages=[{'role': 'user', 'content': prompt}]
        )
        text = msg.content[0].text
        # 提取 JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            score = (
                data.get('doc_quality', 0) * 8 +
                data.get('innovativeness', 0) * 6 +
                data.get('practicality', 0) * 6
            )
            return round(score, 1), data
    except Exception as e:
        return None, {'error': str(e)}

    return None, {'error': 'LLM 响应解析失败'}


# ============================================================
# 主流程
# ============================================================

def process_skill(skill, cache, use_cache=True, with_llm=False, fast_mode=False):
    """处理单个 skill，返回 score + breakdown"""
    is_local = skill.get('type') == 'local_skill' or not skill.get('repo')

    if is_local:
        # 本地 skill: 不参与 GitHub 评分（视为已知质量）
        return {
            'id': skill.get('id'),
            'name': skill.get('name'),
            'author': skill.get('author'),
            'is_local': True,
            'score': None,
            'note': '本地 skill（一人课程），未参与 GitHub 评分',
        }

    repo = skill.get('repo', '')
    cache_key = f"hard:{repo}"

    if use_cache and cache_key in cache:
        cached = cache[cache_key]
        metrics = cached['metrics']
        has_skill_md = cached['has_skill_md']
        has_readme = cached['has_readme']
        issue_close_rate = cached.get('issue_close_rate')
    else:
        metrics = fetch_repo_metrics(repo)
        if not metrics:
            return {
                'id': skill.get('id'),
                'name': skill.get('name'),
                'author': skill.get('author'),
                'is_local': False,
                'error': f'无法获取 {repo} 数据',
                'score': None,
            }
        # fast_mode: 跳过 SKILL.md 检测（节省 API 请求）
        if fast_mode:
            has_skill_md = True  # 假设有
            has_readme = True
        else:
            has_skill_md = check_skill_md(repo, metrics.get('default_branch', 'main'))
            has_readme = check_readme(repo, metrics.get('default_branch', 'main'))
        # issue close rate 计算较慢，fast 模式跳过
        issue_close_rate = None if fast_mode else fetch_issue_close_rate(repo)[2]
        cache[cache_key] = {
            'metrics': metrics,
            'has_skill_md': has_skill_md,
            'has_readme': has_readme,
            'issue_close_rate': issue_close_rate,
        }

    hard_score, breakdown = calculate_hard_score(metrics, has_skill_md, has_readme, issue_close_rate)
    bonus = calculate_ecosystem_bonus(metrics, repo)

    result = {
        'id': skill.get('id'),
        'name': skill.get('name'),
        'author': skill.get('author'),
        'repo': repo,
        'stars': metrics.get('stars', 0),
        'forks': metrics.get('forks', 0),
        'pushed_at': metrics.get('pushed_at'),
        'license': metrics.get('license'),
        'topics': metrics.get('topics') or [],
        'hard_score': hard_score,
        'bonus': bonus,
        'score': hard_score + bonus,
        'breakdown': breakdown,
        'html_url': metrics.get('html_url'),
    }

    # LLM 评分（可选）
    if with_llm:
        llm_score, llm_data = calculate_llm_score(metrics)
        result['llm_score'] = llm_score
        result['llm_data'] = llm_data
        if llm_score:
            result['score'] = hard_score + bonus + llm_score

    return result


def render_markdown(results, min_score=0, args=None):
    out = []
    out.append(f"# 🎯 Skill Quality Score Report")
    out.append("")
    out.append(f"> 评分时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} · 总分上限: 120（硬指标 95 + bonus 5 + LLM 20）")
    out.append(f"> 阈值: score ≥ {min_score} 入选")
    out.append("")

    # 分布
    scored = [r for r in results if r.get('score') is not None and not r.get('is_local')]
    local_count = sum(1 for r in results if r.get('is_local'))
    error_count = sum(1 for r in results if r.get('error'))

    out.append("## 📊 评分分布")
    out.append("")
    out.append(f"- 总 skill: {len(results)}")
    out.append(f"- 已评分: {len(scored)}")
    out.append(f"- 本地（未评分）: {local_count}")
    out.append(f"- 错误（无法获取）: {error_count}")
    out.append("")

    if scored:
        scores = [r['score'] for r in scored]
        out.append(f"- **平均分**: {sum(scores)/len(scores):.1f}")
        out.append(f"- **最高分**: {max(scores):.1f}")
        out.append(f"- **最低分**: {min(scores):.1f}")
        out.append(f"- **≥ 60 入选**: {sum(1 for s in scores if s >= 60)} 个")
        out.append("")

    # Top 排名
    out.append("## 🏆 排名（按 score 降序）")
    out.append("")
    out.append("| 排名 | score | ⭐ | forks/stars | 最后 commit | skill | 作者 | 仓库 | 备注 |")
    out.append("|------|-------|----|-------------|-------------|-------|------|------|------|")

    sorted_results = sorted(scored, key=lambda r: -r['score'])
    for i, r in enumerate(sorted_results, 1):
        stars = r.get('stars', 0)
        forks = r.get('forks', 0)
        ratio = (forks / stars * 100) if stars > 0 else 0
        pushed = r.get('pushed_at', '')[:10] if r.get('pushed_at') else '-'
        name = r.get('name', '?')
        sid = r.get('id', '?')
        author = r.get('author', '?')
        repo = r.get('repo', '?')
        url = r.get('html_url', f"https://github.com/{repo}")

        # 推荐标记
        marker = '✅' if r['score'] >= 60 else '⚠️' if r['score'] >= 40 else '❌'

        out.append(f"| {i} | {marker} {r['score']:.1f} | {stars:,} | {ratio:.1f}% | {pushed} | `{sid}` | {author} | [{repo}]({url}) | - |")

    out.append("")

    # 硬指标分布（如果没 LLM）
    if not args or not getattr(args, 'with_llm', False):
        out.append("## 🔬 硬指标明细（Top 10）")
        out.append("")
        out.append("| skill | stars | forks_r | recency | issue_close | skill_md | license | readme | topics | install |")
        out.append("|-------|-------|---------|---------|-------------|----------|---------|--------|--------|---------|")
        for r in sorted_results[:10]:
            b = r['breakdown']
            out.append(
                f"| `{r['id']}` | {b.get('stars', 0):.0f} | {b.get('forks_ratio', 0):.0f} | "
                f"{b.get('recency', 0):.0f} | {b.get('issue_close', 0):.0f} | "
                f"{b.get('has_skill_md', 0)} | {b.get('has_license', 0)} | "
                f"{b.get('has_readme', 0)} | {b.get('has_topics', 0)} | {b.get('has_install', 0)} |"
            )
        out.append("")

    # 阈值过滤
    if min_score > 0:
        qualified = [r for r in scored if r['score'] >= min_score]
        out.append(f"## 🎯 入选清单（score ≥ {min_score}）")
        out.append("")
        out.append(f"> 共 **{len(qualified)} 个** skill 入选。")
        out.append("")
        for r in sorted(qualified, key=lambda x: -x['score']):
            stars = r.get('stars', 0)
            out.append(f"- **{r['id']}**（{r['score']:.1f} 分 · {stars:,} ⭐）— @{r['author']}: {r['name']}")
        out.append("")

    # 主动审查
    out.append("## 🔍 主动审查")
    out.append("")

    # 高分但低星（潜在黑马）
    high_score_low_star = [r for r in scored if r['score'] >= 60 and r.get('stars', 0) < 500]
    if high_score_low_star:
        out.append(f"### ⚠️ 高分低星（score ≥ 60 但 stars < 500）：{len(high_score_low_star)} 个")
        out.append("")
        out.append("> 这些是潜在的'未来之星'，star 还没涨起来但质量指标强。")
        out.append("")
        for r in sorted(high_score_low_star, key=lambda x: -x['score']):
            out.append(f"- **{r['id']}**（{r['score']:.1f} 分 · {r.get('stars', 0)} ⭐）: {r['name']}")
        out.append("")

    # 低分高星（警惕）
    low_score_high_star = [r for r in scored if r['score'] < 50 and r.get('stars', 0) >= 1000]
    if low_score_high_star:
        out.append(f"### 💡 低分高星（score < 50 但 stars ≥ 1000）：{len(low_score_high_star)} 个")
        out.append("")
        out.append("> 这些 star 多但综合质量分低——可能是营销好但维护弱，需要警惕。")
        out.append("")
        for r in sorted(low_score_high_star, key=lambda x: x['score']):
            out.append(f"- **{r['id']}**（{r['score']:.1f} 分 · {r.get('stars', 0):,} ⭐）: {r['name']}")
        out.append("")

    # 排除的本地 skill
    if local_count > 0:
        out.append(f"### 📍 本地 skill（{local_count} 个，未参与 GitHub 评分）")
        out.append("")
        out.append("> 一人课程 22 章原始 skill，假设已知质量。")
        out.append("")

    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description='Skill Quality Score')
    parser.add_argument('--taxonomy', default=str(TAXONOMY_FILE))
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--fast', action='store_true', help='快速模式（跳过 SKILL.md 检测和 issue 统计）')
    parser.add_argument('--with-llm', action='store_true', help='启用 LLM 评分（需要 ANTHROPIC_API_KEY）')
    parser.add_argument('--min-score', type=float, default=0, help='入选阈值')
    parser.add_argument('--output', '-o', help='输出文件')
    parser.add_argument('--json', action='store_true', help='输出 JSON 而非 Markdown')
    args = parser.parse_args()

    taxonomy = load_taxonomy(args.taxonomy)
    skills = taxonomy.get('skills', [])
    cache = {} if args.no_cache else load_cache()

    print(f"📊 评分 {len(skills)} 个 skill..." if not args.json else "", file=sys.stderr)

    results = []
    for i, skill in enumerate(skills, 1):
        if not args.json:
            print(f"  [{i}/{len(skills)}] {skill.get('id', '?')}...", file=sys.stderr)
        result = process_skill(skill, cache, use_cache=not args.no_cache,
                               with_llm=args.with_llm, fast_mode=args.fast)
        results.append(result)

    save_cache(cache)

    if args.json:
        output = json.dumps(results, indent=2, ensure_ascii=False)
    else:
        output = render_markdown(results, min_score=args.min_score, args=args)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已写入 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()