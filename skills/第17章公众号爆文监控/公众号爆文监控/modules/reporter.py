"""报告生成模块"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import yaml


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_dir = Path(__file__).parent.parent
        self.daily_dir = self.base_dir / config.get('output', {}).get('daily_dir', 'daily')
        self.analysis_dir = self.base_dir / config.get('output', {}).get('analysis_dir', 'analysis')

        # 确保目录存在
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        (self.analysis_dir / 'weekly').mkdir(exist_ok=True)
        (self.analysis_dir / 'monthly').mkdir(exist_ok=True)

    def generate_daily_report(
        self,
        articles: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> str:
        """生成日报"""
        today = datetime.now().strftime('%Y-%m-%d')
        md_filename = f"{today}.md"
        html_filename = f"{today}.html"
        md_filepath = self.daily_dir / md_filename
        html_filepath = self.daily_dir / html_filename

        # 计算统计数据
        total_articles = len(articles)
        if articles:
            avg_read = sum(a.get('stats', {}).get('read', 0) for a in articles) / total_articles
            avg_interaction = sum(a.get('metrics', {}).get('interaction_rate', 0) for a in articles) / total_articles
            avg_spread = sum(a.get('metrics', {}).get('spread_index', 0) for a in articles) / total_articles
        else:
            avg_read = avg_interaction = avg_spread = 0

        stats = {
            'total': total_articles,
            'avg_read': avg_read,
            'avg_interaction': avg_interaction,
            'avg_spread': avg_spread
        }

        # 生成Markdown报告
        md_content = self._generate_daily_content(
            date=today,
            articles=articles,
            analysis=analysis,
            stats=stats
        )

        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        # 生成HTML报告
        html_content = self._generate_html_report(
            date=today,
            articles=articles,
            analysis=analysis,
            stats=stats
        )

        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(md_filepath)

    def _generate_html_report(
        self,
        date: str,
        articles: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        stats: Dict[str, Any]
    ) -> str:
        """生成2026前沿风格HTML报告 - Liquid Glass + Bento Grid"""
        from .html_template import HTML_TEMPLATE, ARTICLE_CARD_TEMPLATE, TREND_ITEM_TEMPLATE, SUGGESTION_CARD_TEMPLATE
        
        top_articles = analysis.get('top_articles_analysis', [])[:10]
        topic_trends = analysis.get('topic_trends', [])[:5]
        suggestions = analysis.get('content_suggestions', [])[:3]

        # 生成文章卡片
        article_cards = ""
        for i, article in enumerate(top_articles):
            a_stats = article.get('stats', {})
            metrics = article.get('metrics', {})
            a_analysis = article.get('analysis', {})

            tags_html = ""
            for factor in a_analysis.get('viral_factors', [])[:3]:
                tags_html += f'<span class="tag">{factor}</span>'

            article_cards += ARTICLE_CARD_TEMPLATE.format(
                rank=i+1,
                url=article.get('url', '#'),
                title=article.get('title', ''),
                account=article.get('account_name', '-'),
                topic_type=a_analysis.get('topic_type', '-'),
                read=f"{a_stats.get('read', 0):,}",
                zan=f"{a_stats.get('zan', 0):,}",
                looking=f"{a_stats.get('looking', 0):,}",
                share=f"{a_stats.get('share_num', 0):,}",
                collect=f"{a_stats.get('collect_num', 0):,}",
                interaction_rate=f"{metrics.get('interaction_rate', 0):.1f}",
                spread_index=f"{metrics.get('spread_index', 0):.1f}",
                viral_score=f"{metrics.get('viral_score', 0):.1f}",
                title_formula=a_analysis.get('title_formula', '-'),
                tags=tags_html
            )

        # 生成趋势列表
        trends_html = ""
        rank_icons = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
        for i, trend in enumerate(topic_trends):
            trends_html += TREND_ITEM_TEMPLATE.format(
                rank_icon=rank_icons[i] if i < 5 else str(i+1),
                keyword=trend.get('keyword', ''),
                count=trend.get('count', 0),
                heat_level=trend.get('heat_level', ''),
                interaction_rate=f"{trend.get('avg_interaction_rate', 0):.1f}"
            )

        # 生成选题建议
        suggestions_html = ""
        for s in suggestions:
            suggestions_html += SUGGESTION_CARD_TEMPLATE.format(
                title=s.get('suggested_title', ''),
                type=s.get('title_type', ''),
                rate=s.get('expected_interaction_rate', '-'),
                reference=s.get('reference_title', '')[:50] + '...',
                structure=s.get('content_structure', '')
            )

        # 填充主模板
        html = HTML_TEMPLATE.format(
            date=date,
            keywords=', '.join(self.config.get('keywords', [])),
            total=stats['total'],
            avg_read=f"{stats['avg_read']:,.0f}",
            avg_interaction=f"{stats['avg_interaction']:.1f}",
            avg_spread=f"{stats['avg_spread']:.1f}",
            article_cards=article_cards,
            trends_html=trends_html,
            suggestions_html=suggestions_html,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M')
        )

        return html

    def _generate_daily_content(
        self,
        date: str,
        articles: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        stats: Dict[str, Any]
    ) -> str:
        """生成日报内容"""
        lines = []

        # YAML frontmatter
        lines.append('---')
        lines.append(f'date: {date}')
        lines.append(f'total_articles: {stats["total"]}')
        lines.append(f'avg_read: {stats["avg_read"]:.0f}')
        lines.append(f'avg_interaction_rate: {stats["avg_interaction"]:.2f}')
        lines.append(f'keywords: {self.config.get("keywords", [])}')
        lines.append('---')
        lines.append('')

        # 标题
        lines.append(f'# 公众号爆文监控 - {date}')
        lines.append('')

        # 核心数据
        lines.append('## 📊 核心数据')
        lines.append('')
        lines.append('| 指标 | 数值 |')
        lines.append('|------|------|')
        lines.append(f'| 新增爆文 | {stats["total"]}篇 |')
        lines.append(f'| 平均阅读量 | {stats["avg_read"]:,.0f} |')
        lines.append(f'| 平均互动率 | {stats["avg_interaction"]:.1f}‰ |')
        lines.append(f'| 平均传播指数 | {stats["avg_spread"]:.1f}‰ |')
        lines.append('')

        # 今日爆文榜TOP10
        lines.append('---')
        lines.append('')
        lines.append('## 🔥 今日爆文榜 TOP10')
        lines.append('')

        top_articles = analysis.get('top_articles_analysis', [])[:10]
        for i, article in enumerate(top_articles):
            lines.extend(self._format_article_section(i + 1, article))
            lines.append('')

        # 选题方向分析
        lines.append('---')
        lines.append('')
        lines.append('## 💡 选题方向分析')
        lines.append('')

        topic_trends = analysis.get('topic_trends', [])
        for i, trend in enumerate(topic_trends[:5]):
            rank_emoji = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][i] if i < 5 else f'{i+1}.'
            lines.append(f'### {rank_emoji} {trend["keyword"]} ({trend["count"]}篇)')
            lines.append('')
            lines.append(f'**热度**: {trend["heat_level"]}')
            lines.append(f'**平均互动率**: {trend["avg_interaction_rate"]:.1f}‰')
            lines.append(f'**平均传播指数**: {trend["avg_spread_index"]:.1f}‰')
            lines.append('')

        # 标题公式库
        lines.append('---')
        lines.append('')
        lines.append('## 📝 标题公式库')
        lines.append('')

        title_formulas = analysis.get('title_formulas', {})
        for formula_type, formulas in title_formulas.items():
            if formulas:
                lines.append(f'### {formula_type}')
                lines.append('')
                for formula in formulas[:3]:
                    lines.append(f'- `{formula}`')
                lines.append('')

        # 选题建议
        lines.append('---')
        lines.append('')
        lines.append('## 🎯 立即可做的选题')
        lines.append('')

        suggestions = analysis.get('content_suggestions', [])
        for suggestion in suggestions[:3]:
            lines.append(f'### {suggestion["rank"]}. {suggestion["suggested_title"]}')
            lines.append('')
            lines.append(f'**参考文章**: {suggestion["reference_title"]}')
            lines.append(f'**标题类型**: {suggestion["title_type"]}')
            lines.append(f'**推荐理由**: {suggestion["reason"]}')
            lines.append(f'**内容结构**: {suggestion["content_structure"]}')
            lines.append('')

        # 原始数据
        lines.append('---')
        lines.append('')
        lines.append('## 📚 原始数据')
        lines.append('')
        lines.append('<details>')
        lines.append(f'<summary>点击展开完整文章列表（{len(articles)}篇）</summary>')
        lines.append('')
        lines.append('| # | 标题 | 公众号 | 阅读 | 互动率 | 链接 |')
        lines.append('|---|------|--------|------|--------|------|')

        for i, article in enumerate(articles):
            title = article.get('title', '')[:30] + ('...' if len(article.get('title', '')) > 30 else '')
            account = article.get('account_name', '-')
            read = article.get('stats', {}).get('read', 0)
            interaction = article.get('metrics', {}).get('interaction_rate', 0)
            url = article.get('url', '')
            lines.append(f'| {i+1} | {title} | {account} | {read:,} | {interaction:.1f}‰ | [链接]({url}) |')

        lines.append('')
        lines.append('</details>')
        lines.append('')

        # 页脚
        lines.append('---')
        lines.append('')
        lines.append(f'*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')

        return '\n'.join(lines)

    def _format_article_section(self, rank: int, article: Dict[str, Any]) -> List[str]:
        """格式化单篇文章"""
        lines = []
        title = article.get('title', '')
        url = article.get('url', '')
        account = article.get('account_name', '-')
        stats = article.get('stats', {})
        metrics = article.get('metrics', {})
        analysis = article.get('analysis', {})

        lines.append(f'### {rank}. {title}')
        lines.append('')
        lines.append(f'**公众号**: {account}')
        lines.append(f'**链接**: [原文]({url})')
        lines.append('')

        # 数据表格
        lines.append('| 阅读 | 点赞 | 在看 | 转发 | 收藏 | 评论 |')
        lines.append('|------|------|------|------|------|------|')
        lines.append(f'| {stats.get("read", 0):,} | {stats.get("zan", 0):,} | {stats.get("looking", 0):,} | {stats.get("share_num", 0):,} | {stats.get("collect_num", 0):,} | {stats.get("comment_count", 0):,} |')
        lines.append('')

        # 核心指标
        lines.append('**核心指标**:')
        lines.append(f'- 互动率: {metrics.get("interaction_rate", 0):.1f}‰')
        lines.append(f'- 传播指数: {metrics.get("spread_index", 0):.1f}‰')
        lines.append(f'- 内容价值: {metrics.get("content_value", 0):.1f}‰')
        lines.append(f'- 爆文潜力分: {metrics.get("viral_score", 0):.1f}')
        lines.append('')

        # AI分析
        if analysis:
            lines.append('**AI分析**:')
            lines.append(f'- **选题类型**: {analysis.get("topic_type", "-")}')
            lines.append(f'- **选题角度**: {", ".join(analysis.get("topic_angles", []))}')
            lines.append(f'- **标题公式**: `{analysis.get("title_formula", "-")}`')

            viral_factors = analysis.get('viral_factors', [])
            if viral_factors:
                lines.append('- **爆款因素**:')
                for factor in viral_factors[:3]:
                    lines.append(f'  - {factor}')

            replicable = analysis.get('replicable_elements', [])
            if replicable:
                lines.append('- **可复制要素**:')
                for element in replicable[:3]:
                    lines.append(f'  - {element}')

        return lines

    def update_index(self) -> None:
        """更新README索引"""
        readme_path = self.base_dir / 'README.md'

        # 获取所有日报文件
        daily_files = sorted(self.daily_dir.glob('*.md'), reverse=True)

        lines = []
        lines.append('# 公众号爆文监控')
        lines.append('')
        lines.append('自动监控公众号爆文，AI分析选题方向，生成可复制的标题公式。')
        lines.append('')
        lines.append('## 使用方法')
        lines.append('')
        lines.append('```bash')
        lines.append('# 配置')
        lines.append('python viral_monitor.py --setup')
        lines.append('')
        lines.append('# 采集今日爆文')
        lines.append('python viral_monitor.py')
        lines.append('')
        lines.append('# 生成周报')
        lines.append('python viral_monitor.py --weekly')
        lines.append('```')
        lines.append('')
        lines.append('## 日报列表')
        lines.append('')

        for f in daily_files[:30]:  # 最近30天
            date = f.stem
            # 尝试读取统计数据
            try:
                content = f.read_text(encoding='utf-8')
                # 简单提取文章数
                if 'total_articles:' in content:
                    total = content.split('total_articles:')[1].split('\n')[0].strip()
                else:
                    total = '-'
            except:
                total = '-'

            lines.append(f'- [{date}](daily/{f.name}) ({total}篇)')

        lines.append('')
        lines.append('## 周报列表')
        lines.append('')

        weekly_files = sorted((self.analysis_dir / 'weekly').glob('*.md'), reverse=True)
        for f in weekly_files[:10]:
            lines.append(f'- [{f.stem}](analysis/weekly/{f.name})')

        lines.append('')
        lines.append('---')
        lines.append(f'*最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def generate_weekly_report(self) -> Optional[str]:
        """生成周报"""
        # 获取本周的日报
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_num = today.strftime('%Y-W%W')

        # 收集本周数据
        weekly_articles = []
        weekly_stats = []

        for i in range(7):
            date = (week_start + timedelta(days=i)).strftime('%Y-%m-%d')
            daily_file = self.daily_dir / f'{date}.md'

            if daily_file.exists():
                # 解析日报数据
                try:
                    content = daily_file.read_text(encoding='utf-8')
                    # 提取frontmatter
                    if content.startswith('---'):
                        parts = content.split('---')
                        if len(parts) >= 3:
                            frontmatter = yaml.safe_load(parts[1])
                            weekly_stats.append({
                                'date': date,
                                'total': frontmatter.get('total_articles', 0),
                                'avg_read': frontmatter.get('avg_read', 0),
                                'avg_interaction': frontmatter.get('avg_interaction_rate', 0)
                            })
                except:
                    pass

        if not weekly_stats:
            return None

        # 生成周报
        filename = f'{week_num}.md'
        filepath = self.analysis_dir / 'weekly' / filename

        lines = []
        lines.append(f'# 周报 - {week_num}')
        lines.append('')
        lines.append(f'**统计周期**: {week_start.strftime("%Y-%m-%d")} ~ {today.strftime("%Y-%m-%d")}')
        lines.append('')

        # 汇总数据
        total_articles = sum(s['total'] for s in weekly_stats)
        avg_read = sum(s['avg_read'] for s in weekly_stats) / len(weekly_stats) if weekly_stats else 0
        avg_interaction = sum(s['avg_interaction'] for s in weekly_stats) / len(weekly_stats) if weekly_stats else 0

        lines.append('## 📊 本周汇总')
        lines.append('')
        lines.append('| 指标 | 数值 |')
        lines.append('|------|------|')
        lines.append(f'| 采集天数 | {len(weekly_stats)}天 |')
        lines.append(f'| 总文章数 | {total_articles}篇 |')
        lines.append(f'| 平均阅读量 | {avg_read:,.0f} |')
        lines.append(f'| 平均互动率 | {avg_interaction:.1f}‰ |')
        lines.append('')

        # 每日数据
        lines.append('## 📅 每日数据')
        lines.append('')
        lines.append('| 日期 | 文章数 | 平均阅读 | 平均互动率 |')
        lines.append('|------|--------|----------|------------|')
        for s in weekly_stats:
            lines.append(f'| {s["date"]} | {s["total"]} | {s["avg_read"]:,.0f} | {s["avg_interaction"]:.1f}‰ |')
        lines.append('')

        lines.append('---')
        lines.append(f'*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return str(filepath)
