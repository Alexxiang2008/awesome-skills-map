"""AI分析模块"""
import os
import json
from typing import Dict, Any, List, Optional
from collections import Counter


class ArticleAnalyzer:
    """文章分析器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def analyze_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析文章"""
        if not articles:
            return {}

        # 取TOP10进行详细分析
        top_articles = sorted(
            articles,
            key=lambda x: x.get('metrics', {}).get('viral_score', 0),
            reverse=True
        )[:10]

        analysis = {
            'top_articles_analysis': [],
            'topic_trends': self._analyze_topic_trends(articles),
            'title_formulas': self._extract_title_formulas(articles),
            'content_suggestions': self._generate_suggestions(articles)
        }

        # 分析每篇TOP文章
        for article in top_articles:
            article_analysis = self._analyze_single_article(article)
            analysis['top_articles_analysis'].append(article_analysis)

        return analysis

    def _analyze_single_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """分析单篇文章"""
        title = article.get('title', '')
        stats = article.get('stats', {})
        metrics = article.get('metrics', {})

        # 分析标题类型
        title_type = self._classify_title(title)

        # 分析选题角度
        topic_angles = self._extract_topic_angles(title, article.get('digest', ''))

        # 提取标题公式
        title_formula = self._extract_title_formula(title)

        # 分析爆款因素
        viral_factors = self._analyze_viral_factors(article)

        return {
            'title': title,
            'url': article.get('url', ''),
            'account_name': article.get('account_name', ''),
            'stats': stats,
            'metrics': metrics,
            'analysis': {
                'topic_type': title_type,
                'topic_angles': topic_angles,
                'title_formula': title_formula,
                'viral_factors': viral_factors,
                'replicable_elements': self._get_replicable_elements(title_type, viral_factors)
            }
        }

    def _classify_title(self, title: str) -> str:
        """分类标题类型"""
        # 对比冲突型
        if any(kw in title for kw in ['vs', 'VS', '对比', '还是', '不用学了', '慌了', '替代']):
            return '对比冲突型'

        # 数字效果型
        if any(char.isdigit() for char in title) and any(kw in title for kw in ['个', '篇', '条', '倍', '分钟', '小时', '天']):
            return '数字效果型'

        # 痛点解决型
        if any(kw in title for kw in ['终于', '解决', '搞定', '不再', '告别', '如何']):
            return '痛点解决型'

        # 新奇发现型
        if any(kw in title for kw in ['发现', '原来', '竟然', '居然', '没想到', '隐藏']):
            return '新奇发现型'

        # 工具测评型
        if any(kw in title for kw in ['测评', '实测', '体验', '试用', '评测', '发布']):
            return '工具测评型'

        # 教程指南型
        if any(kw in title for kw in ['教程', '指南', '攻略', '方法', '步骤', '流程', '怎么']):
            return '教程指南型'

        return '其他'

    def _extract_topic_angles(self, title: str, digest: str) -> List[str]:
        """提取选题角度"""
        angles = []
        text = title + ' ' + digest

        # 关键词映射
        angle_keywords = {
            '新工具发布': ['发布', '上线', '推出', '更新', '升级', '新版'],
            '效率提升': ['效率', '提升', '倍', '快', '省时', '自动'],
            '降低门槛': ['不用学', '零基础', '小白', '简单', '一键', '傻瓜式'],
            '实战案例': ['实战', '案例', '实测', '亲测', '体验', '使用'],
            '对比分析': ['对比', 'vs', '区别', '选择', '哪个好'],
            '趋势洞察': ['趋势', '未来', '预测', '变化', '风口'],
            '避坑指南': ['避坑', '踩坑', '注意', '别', '不要', '错误'],
            '资源合集': ['合集', '汇总', '整理', '推荐', '清单', '工具箱']
        }

        for angle, keywords in angle_keywords.items():
            if any(kw in text for kw in keywords):
                angles.append(angle)

        return angles[:5] if angles else ['通用内容']

    def _extract_title_formula(self, title: str) -> str:
        """提取标题公式"""
        # 对比型: X发布，Y不用学了
        if '不用学了' in title or '不用了' in title:
            return '{新工具}发布，{旧工具}不用学了'

        # 数字型: 我用X做了N个Y
        if '我用' in title and any(char.isdigit() for char in title):
            return '我用{工具}做了{数字}个{结果}'

        # 效率型: X分钟/小时完成Y
        if any(kw in title for kw in ['分钟', '小时', '天内']):
            return '{时间}内完成{任务}'

        # 实测型: X实测：效率提升N倍
        if '实测' in title or '测评' in title:
            return '{工具}实测：{效果描述}'

        # 发现型: 发现了X的隐藏功能
        if '发现' in title or '原来' in title:
            return '发现了{工具}的{特点}'

        # 问句型
        if '？' in title or '吗' in title:
            return '{疑问句引发好奇}'

        return '{主题} + {亮点/效果}'

    def _analyze_viral_factors(self, article: Dict[str, Any]) -> List[str]:
        """分析爆款因素"""
        factors = []
        title = article.get('title', '')
        metrics = article.get('metrics', {})

        # 时效性
        if any(kw in title for kw in ['发布', '上线', '更新', '最新', '刚刚']):
            factors.append('时效性强（新工具/新功能发布）')

        # 实用性
        if any(kw in title for kw in ['教程', '方法', '步骤', '如何', '怎么']):
            factors.append('实用性高（可操作的教程）')

        # 数据支撑
        if any(char.isdigit() for char in title):
            factors.append('数据支撑（具体数字增加可信度）')

        # 痛点共鸣
        if any(kw in title for kw in ['终于', '解决', '不再', '告别']):
            factors.append('痛点共鸣（解决常见问题）')

        # 好奇心
        if any(kw in title for kw in ['竟然', '居然', '没想到', '原来', '？']):
            factors.append('好奇心驱动（引发探索欲）')

        # 对比冲突
        if any(kw in title for kw in ['vs', '对比', '不用学了', '替代']):
            factors.append('对比冲突（制造话题性）')

        # 高互动率
        if metrics.get('interaction_rate', 0) > 40:
            factors.append('高互动率（内容引发共鸣）')

        # 高传播性
        if metrics.get('spread_index', 0) > 30:
            factors.append('高传播性（值得分享给他人）')

        # 高收藏率
        if metrics.get('content_value', 0) > 15:
            factors.append('高收藏价值（内容值得保存）')

        return factors if factors else ['综合质量较高']

    def _get_replicable_elements(self, title_type: str, viral_factors: List[str]) -> List[str]:
        """获取可复制要素"""
        elements = []

        # 根据标题类型
        type_elements = {
            '对比冲突型': ['使用对比公式标题', '新旧工具对比结构', '明确的结论建议'],
            '数字效果型': ['标题包含具体数字', '展示实际成果', '量化效果描述'],
            '痛点解决型': ['开头描述痛点场景', '提供具体解决方案', '分步骤讲解'],
            '新奇发现型': ['制造信息差', '展示独特发现', '引导读者尝试'],
            '工具测评型': ['客观评价优缺点', '提供实测数据', '给出使用建议'],
            '教程指南型': ['清晰的步骤编号', '配图说明', '提供可下载资源']
        }

        elements.extend(type_elements.get(title_type, ['内容结构清晰']))

        # 根据爆款因素
        if '时效性强' in str(viral_factors):
            elements.append('追踪热点快速产出')
        if '数据支撑' in str(viral_factors):
            elements.append('用数字增强说服力')
        if '痛点共鸣' in str(viral_factors):
            elements.append('从用户痛点切入')

        return list(dict.fromkeys(elements))[:5]

    def _analyze_topic_trends(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析选题趋势"""
        # 统计关键词出现频率
        keyword_counter = Counter()
        keyword_metrics = {}

        for article in articles:
            keyword = article.get('keyword', '')
            if keyword:
                keyword_counter[keyword] += 1
                if keyword not in keyword_metrics:
                    keyword_metrics[keyword] = []
                keyword_metrics[keyword].append(article.get('metrics', {}))

        # 计算每个关键词的平均指标
        trends = []
        for keyword, count in keyword_counter.most_common(10):
            metrics_list = keyword_metrics.get(keyword, [])
            if metrics_list:
                avg_interaction = sum(m.get('interaction_rate', 0) for m in metrics_list) / len(metrics_list)
                avg_spread = sum(m.get('spread_index', 0) for m in metrics_list) / len(metrics_list)
            else:
                avg_interaction = 0
                avg_spread = 0

            trends.append({
                'keyword': keyword,
                'count': count,
                'avg_interaction_rate': round(avg_interaction, 2),
                'avg_spread_index': round(avg_spread, 2),
                'heat_level': self._get_heat_level(count, avg_interaction)
            })

        return trends

    def _get_heat_level(self, count: int, avg_interaction: float) -> str:
        """获取热度等级"""
        score = count * 10 + avg_interaction
        if score > 100:
            return '🔥🔥🔥 极热'
        elif score > 60:
            return '🔥🔥 很热'
        elif score > 30:
            return '🔥 较热'
        else:
            return '📊 一般'

    def _extract_title_formulas(self, articles: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """提取标题公式库"""
        formulas = {
            '对比冲突型': [],
            '数字效果型': [],
            '痛点解决型': [],
            '新奇发现型': [],
            '工具测评型': [],
            '教程指南型': []
        }

        for article in articles:
            title = article.get('title', '')
            title_type = self._classify_title(title)
            formula = self._extract_title_formula(title)

            if title_type in formulas and formula not in formulas[title_type]:
                formulas[title_type].append(formula)

        # 每种类型最多保留5个
        for key in formulas:
            formulas[key] = formulas[key][:5]

        return formulas

    def _generate_suggestions(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成选题建议"""
        suggestions = []

        # 找出高潜力文章
        top_articles = sorted(
            articles,
            key=lambda x: x.get('metrics', {}).get('viral_score', 0),
            reverse=True
        )[:5]

        for i, article in enumerate(top_articles):
            title = article.get('title', '')
            title_type = self._classify_title(title)
            metrics = article.get('metrics', {})

            # 生成建议标题
            suggested_title = self._generate_suggested_title(title, title_type)

            suggestions.append({
                'rank': i + 1,
                'reference_title': title,
                'suggested_title': suggested_title,
                'title_type': title_type,
                'reason': self._get_suggestion_reason(title_type, metrics),
                'content_structure': self._get_content_structure(title_type),
                'expected_interaction_rate': f"{metrics.get('interaction_rate', 0):.1f}‰"
            })

        return suggestions

    def _generate_suggested_title(self, reference_title: str, title_type: str) -> str:
        """生成建议标题"""
        # 这里返回一个模板，实际使用时需要填充
        templates = {
            '对比冲突型': '"{新工具}来了，{旧工具}要被替代了？"',
            '数字效果型': '"我用{工具}做了{数字}个{成果}，效率提升{倍数}倍"',
            '痛点解决型': '"终于解决了{痛点}，方法竟然这么简单"',
            '新奇发现型': '"发现{工具}的隐藏功能，90%的人不知道"',
            '工具测评型': '"{工具}深度实测：优缺点全面分析"',
            '教程指南型': '"{任务}完整教程：从入门到精通只需{时间}"'
        }
        return templates.get(title_type, '"根据热点自定义标题"')

    def _get_suggestion_reason(self, title_type: str, metrics: Dict[str, float]) -> str:
        """获取建议理由"""
        reasons = {
            '对比冲突型': f'对比类内容话题性强，预计互动率{metrics.get("interaction_rate", 0):.1f}‰',
            '数字效果型': f'数字增强可信度，预计传播指数{metrics.get("spread_index", 0):.1f}‰',
            '痛点解决型': f'解决实际问题，预计收藏率较高',
            '新奇发现型': f'好奇心驱动点击，预计阅读量较高',
            '工具测评型': f'实用性强，预计互动率{metrics.get("interaction_rate", 0):.1f}‰',
            '教程指南型': f'可操作性强，预计收藏价值{metrics.get("content_value", 0):.1f}‰'
        }
        return reasons.get(title_type, '综合质量较高')

    def _get_content_structure(self, title_type: str) -> str:
        """获取内容结构建议"""
        structures = {
            '对比冲突型': '引入背景 → 新旧对比 → 实测数据 → 结论建议',
            '数字效果型': '成果展示 → 工具介绍 → 操作步骤 → 效果总结',
            '痛点解决型': '痛点描述 → 解决方案 → 步骤拆解 → 效果验证',
            '新奇发现型': '发现过程 → 功能介绍 → 使用方法 → 延伸思考',
            '工具测评型': '工具背景 → 核心功能 → 优缺点 → 适用场景',
            '教程指南型': '目标说明 → 准备工作 → 分步教程 → 常见问题'
        }
        return structures.get(title_type, '开头 → 主体 → 结尾')
