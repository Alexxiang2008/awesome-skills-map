"""数据采集模块"""
import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import re


class ArticleCollector:
    """文章采集器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config['api']['key']
        self.base_url = config['api']['base_url']
        self.filters = config.get('filters', {})
        self.cost_control = config.get('cost_control', {})
        self.base_dir = Path(__file__).parent.parent

        # 统计
        self.stats = {
            'api_39_calls': 0,
            'api_17_calls': 0,
            'api_38_calls': 0,
            'total_cost': 0.0
        }

    async def collect_viral_articles(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """采集爆文"""
        all_articles = []
        max_articles = self.cost_control.get('max_articles_per_day', 50)

        async with aiohttp.ClientSession() as session:
            for i, keyword in enumerate(keywords):
                if len(all_articles) >= max_articles:
                    print(f"   已达到每日上限 {max_articles} 篇，停止采集")
                    break

                print(f"   [{i+1}/{len(keywords)}] 采集关键词: {keyword}")

                try:
                    articles = await self._fetch_viral_by_keyword(session, keyword)
                    if articles:
                        all_articles.extend(articles)
                        print(f"       找到 {len(articles)} 篇")
                    else:
                        print(f"       未找到文章")
                except Exception as e:
                    print(f"       采集失败: {e}")

                # 避免请求过快
                await asyncio.sleep(0.5)

        # 按互动率排序，取前N篇
        all_articles = sorted(
            all_articles,
            key=lambda x: x.get('estimated_score', 0),
            reverse=True
        )[:max_articles]

        return all_articles

    async def _fetch_viral_by_keyword(
        self,
        session: aiohttp.ClientSession,
        keyword: str
    ) -> List[Dict[str, Any]]:
        """调用接口39获取爆文"""
        # 正确的URL（带www）
        url = "https://www.dajiala.com/fbmain/monitor/v3/hot_typical_search"

        # 时间范围映射
        time_range_map = {
            'today': 1,
            'week': 7,
            'month': 30
        }
        days = time_range_map.get(self.filters.get('time_range', 'today'), 1)

        # 计算日期范围
        end_time = datetime.now().strftime('%Y-%m-%d')
        start_time = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # 使用 multipart/form-data 格式（API要求）
        form_data = aiohttp.FormData()
        form_data.add_field('key', self.api_key)
        form_data.add_field('keyword', keyword)
        form_data.add_field('pub_type', '0')  # 图文
        form_data.add_field('category', '0')  # 全部分类
        form_data.add_field('page', '1')
        form_data.add_field('start_time', start_time)
        form_data.add_field('end_time', end_time)

        try:
            async with session.post(url, data=form_data, timeout=30) as response:
                self.stats['api_39_calls'] += 1

                if response.status != 200:
                    print(f"       HTTP错误: {response.status}")
                    return []

                data = await response.json()

                if data.get('code') != 0:
                    print(f"       API错误: {data.get('msg', 'unknown')}")
                    return []

                articles = data.get('data', [])
                cost = data.get('cost', 0)
                self.stats['total_cost'] += cost

                # 标准化数据格式
                result = []
                for article in articles:
                    result.append({
                        'title': article.get('title', ''),
                        'url': article.get('url', ''),
                        'account_name': article.get('mp_nickname', ''),
                        'publish_time': article.get('pub_time', ''),
                        'cover_url': article.get('cover', ''),
                        'digest': '',
                        'keyword': keyword,
                        'read_num': article.get('read_num', 0),
                        'zan_num': article.get('zan_num', 0),
                        'hot': article.get('hot', 0),
                        'avg': article.get('avg', 0),
                        'fans': article.get('fans', 0),
                        'category': article.get('category', ''),
                        'is_original': article.get('is_original', ''),
                        'estimated_score': article.get('read_num', 0),
                        'collected_at': datetime.now().isoformat()
                    })

                return result

        except asyncio.TimeoutError:
            print(f"       请求超时")
            return []
        except Exception as e:
            print(f"       请求错误: {e}")
            return []

    async def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重处理"""
        # 获取已有URL
        existing_urls = self._get_existing_urls()

        # 过滤重复
        new_articles = []
        seen_urls = set()

        for article in articles:
            url = article.get('url', '')
            if url and url not in existing_urls and url not in seen_urls:
                new_articles.append(article)
                seen_urls.add(url)

        return new_articles

    def _get_existing_urls(self) -> set:
        """从已有的daily文件中提取URL"""
        urls = set()
        daily_dir = self.base_dir / self.config.get('output', {}).get('daily_dir', 'daily')

        if not daily_dir.exists():
            return urls

        # 只检查最近7天的文件
        for md_file in daily_dir.glob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                # 提取URL（简单的正则匹配）
                found_urls = re.findall(r'https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+', content)
                urls.update(found_urls)
            except Exception:
                continue

        return urls

    async def fetch_interaction_data(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取互动数据（接口17）"""
        max_queries = self.cost_control.get('max_interaction_queries', 35)
        articles_to_query = articles[:max_queries]

        async with aiohttp.ClientSession() as session:
            for i, article in enumerate(articles_to_query):
                print(f"   [{i+1}/{len(articles_to_query)}] {article['title'][:30]}...")

                try:
                    stats = await self._fetch_article_stats(session, article['url'])
                    if stats:
                        article['stats'] = stats
                        article['metrics'] = self._calculate_metrics(stats)
                        print(f"       阅读 {stats['read']:,} | 互动率 {article['metrics']['interaction_rate']:.1f}‰")
                except Exception as e:
                    print(f"       获取失败: {e}")
                    article['stats'] = self._empty_stats()
                    article['metrics'] = self._calculate_metrics(article['stats'])

                await asyncio.sleep(0.3)

        # 对未查询的文章填充空数据
        for article in articles[max_queries:]:
            article['stats'] = self._empty_stats()
            article['metrics'] = self._calculate_metrics(article['stats'])

        # 按爆文潜力分排序
        articles = sorted(
            articles,
            key=lambda x: x.get('metrics', {}).get('viral_score', 0),
            reverse=True
        )

        return articles

    async def _fetch_article_stats(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> Optional[Dict[str, int]]:
        """调用接口17获取文章数据"""
        api_url = f"{self.base_url}/read_zan_pro"

        params = {
            'key': self.api_key,
            'url': url
        }

        try:
            async with session.get(api_url, params=params, timeout=30) as response:
                self.stats['api_17_calls'] += 1
                self.stats['total_cost'] += 0.06

                if response.status != 200:
                    return None

                data = await response.json()

                if data.get('code') != 0:
                    return None

                result = data.get('data', {})
                return {
                    'read': result.get('read', 0),
                    'zan': result.get('zan', 0),
                    'looking': result.get('looking', 0),
                    'share_num': result.get('share_num', 0),
                    'collect_num': result.get('collect_num', 0),
                    'comment_count': result.get('comment_count', 0)
                }

        except Exception:
            return None

    def _empty_stats(self) -> Dict[str, int]:
        """空数据"""
        return {
            'read': 0,
            'zan': 0,
            'looking': 0,
            'share_num': 0,
            'collect_num': 0,
            'comment_count': 0
        }

    def _calculate_metrics(self, stats: Dict[str, int]) -> Dict[str, float]:
        """计算核心指标"""
        read = stats.get('read', 0) or 1  # 避免除零
        zan = stats.get('zan', 0)
        looking = stats.get('looking', 0)
        share_num = stats.get('share_num', 0)
        collect_num = stats.get('collect_num', 0)
        comment_count = stats.get('comment_count', 0)

        # 互动率 = (点赞 + 在看) / 阅读量 * 1000
        interaction_rate = (zan + looking) / read * 1000

        # 传播指数 = (转发*2 + 在看) / 阅读量 * 1000
        spread_index = (share_num * 2 + looking) / read * 1000

        # 内容价值指数 = (收藏*2 + 评论) / 阅读量 * 1000
        content_value = (collect_num * 2 + comment_count) / read * 1000

        # 爆文潜力分 = 互动率*0.4 + 传播指数*0.3 + 内容价值指数*0.3
        viral_score = interaction_rate * 0.4 + spread_index * 0.3 + content_value * 0.3

        return {
            'interaction_rate': round(interaction_rate, 2),
            'spread_index': round(spread_index, 2),
            'content_value': round(content_value, 2),
            'viral_score': round(viral_score, 2)
        }

    async def fetch_wx_index(self, keywords: List[str]) -> Dict[str, Any]:
        """获取微信指数（接口38）"""
        max_queries = self.cost_control.get('max_wx_index_queries', 10)
        keywords_to_query = keywords[:max_queries]

        results = {}

        async with aiohttp.ClientSession() as session:
            for keyword in keywords_to_query:
                try:
                    index_data = await self._fetch_wx_index_by_keyword(session, keyword)
                    if index_data:
                        results[keyword] = index_data
                except Exception as e:
                    print(f"   获取微信指数失败 [{keyword}]: {e}")

                await asyncio.sleep(0.3)

        return results

    async def _fetch_wx_index_by_keyword(
        self,
        session: aiohttp.ClientSession,
        keyword: str
    ) -> Optional[Dict[str, Any]]:
        """调用接口38获取微信指数"""
        url = f"{self.base_url}/wx_index"

        params = {
            'key': self.api_key,
            'keyword': keyword
        }

        try:
            async with session.get(url, params=params, timeout=30) as response:
                self.stats['api_38_calls'] += 1
                self.stats['total_cost'] += 0.5

                if response.status != 200:
                    return None

                data = await response.json()

                if data.get('code') != 0:
                    return None

                result = data.get('data', {})
                today = result.get('today', 0)
                yesterday = result.get('yesterday', 0)

                # 计算变化率
                if yesterday > 0:
                    change_rate = (today - yesterday) / yesterday * 100
                else:
                    change_rate = 0

                # 判断趋势
                if change_rate > 50:
                    trend = '🚀 爆发式增长'
                elif change_rate > 20:
                    trend = '📈 快速上升'
                elif change_rate > 5:
                    trend = '📊 稳定增长'
                elif change_rate > -5:
                    trend = '➡️ 持平'
                else:
                    trend = '📉 下降'

                return {
                    'today': today,
                    'yesterday': yesterday,
                    'change_rate': round(change_rate, 1),
                    'trend': trend
                }

        except Exception:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats
