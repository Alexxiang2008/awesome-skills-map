#!/usr/bin/env python3
"""
公众号爆文监控 - 主程序
用法:
    python viral_monitor.py              # 采集今日爆文
    python viral_monitor.py --setup      # 配置向导
    python viral_monitor.py --weekly     # 生成周报
    python viral_monitor.py --keyword "AI工具"  # 指定关键词
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.config import ConfigManager
from modules.collector import ArticleCollector
from modules.analyzer import ArticleAnalyzer
from modules.reporter import ReportGenerator


async def run_setup():
    """配置向导"""
    print("\n🔧 公众号爆文监控 - 配置向导\n")
    print("-" * 40)

    config_manager = ConfigManager()

    # 检查是否已有配置
    if config_manager.config_exists():
        confirm = input("⚠️  已存在配置文件，是否覆盖? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return

    # 获取API密钥
    print("\n📌 步骤 1/3: API配置")
    api_key = input("请输入大家啦API密钥: ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return

    # 获取关键词
    print("\n📌 步骤 2/3: 监控关键词")
    print("预设领域:")
    print("  1. AI应用 (AI, Claude, ChatGPT, Midjourney)")
    print("  2. 工作流 (n8n, 自动化, 效率工具)")
    print("  3. 内容创作 (公众号, 小红书, 短视频)")
    print("  4. AI编程 (Cursor, Copilot, 代码生成)")
    print("  5. 全部预设")
    print("  6. 自定义")

    choice = input("\n请选择 [1-6，可多选，如 1,2,3]: ").strip()

    keywords = []
    preset_keywords = {
        '1': ['AI', 'Claude', 'ChatGPT', 'Midjourney', 'GPT'],
        '2': ['n8n', '自动化', '效率工具', '工作流', 'Zapier'],
        '3': ['公众号', '小红书', '短视频', '内容创作', '爆款'],
        '4': ['Cursor', 'Copilot', 'AI编程', '代码生成', 'Windsurf'],
    }

    if '5' in choice:
        for kws in preset_keywords.values():
            keywords.extend(kws)
    else:
        for c in choice.split(','):
            c = c.strip()
            if c in preset_keywords:
                keywords.extend(preset_keywords[c])
            elif c == '6':
                custom = input("请输入自定义关键词（逗号分隔）: ").strip()
                keywords.extend([k.strip() for k in custom.split(',') if k.strip()])

    # 去重
    keywords = list(dict.fromkeys(keywords))

    if not keywords:
        print("❌ 至少需要一个关键词")
        return

    print(f"\n已选择关键词: {', '.join(keywords)}")

    # 筛选条件
    print("\n📌 步骤 3/3: 筛选条件")
    print("最低阅读量:")
    print("  1. 5000 (推荐，覆盖更多文章)")
    print("  2. 10000 (中等)")
    print("  3. 20000 (只看大爆文)")

    min_read_choice = input("请选择 [1-3，默认1]: ").strip() or '1'
    min_read_map = {'1': 5000, '2': 10000, '3': 20000}
    min_read = min_read_map.get(min_read_choice, 5000)

    # 保存配置
    config = {
        'api': {
            'key': api_key,
            'base_url': 'https://dajiala.com/fbmain/monitor/v3'
        },
        'keywords': keywords,
        'filters': {
            'min_read': min_read,
            'time_range': 'today',
            'sort_by': 'interaction'
        },
        'cost_control': {
            'max_articles_per_day': 50,
            'max_interaction_queries': 35,
            'max_wx_index_queries': 10,
            'daily_budget': 10.0
        },
        'output': {
            'daily_dir': 'daily',
            'analysis_dir': 'analysis'
        }
    }

    config_manager.save_config(config)

    print("\n" + "=" * 40)
    print("✅ 配置完成！")
    print(f"   关键词: {len(keywords)}个")
    print(f"   最低阅读量: {min_read}")
    print(f"   预计每日成本: 5-8元")
    print("\n运行 python viral_monitor.py 开始采集")
    print("=" * 40)


async def run_collect(keyword: str = None):
    """采集爆文"""
    print("\n📊 公众号爆文监控 - 开始采集\n")
    print("-" * 40)

    # 加载配置
    config_manager = ConfigManager()
    if not config_manager.config_exists():
        print("❌ 未找到配置文件")
        print("   请先运行: python viral_monitor.py --setup")
        return

    config = config_manager.load_config()

    # 确定关键词
    keywords = [keyword] if keyword else config['keywords']

    # 显示任务计划
    print("📋 采集计划")
    print(f"   关键词: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''} ({len(keywords)}个)")
    print(f"   最低阅读量: {config['filters']['min_read']}")
    print(f"   预计成本: ~{len(keywords) * 0.5:.1f}元")
    print()

    # 初始化模块
    collector = ArticleCollector(config)
    analyzer = ArticleAnalyzer(config)
    reporter = ReportGenerator(config)

    # 1. 采集爆文
    print("🔍 步骤 1/4: 采集爆文...")
    articles = await collector.collect_viral_articles(keywords)

    if not articles:
        print("❌ 未找到符合条件的文章")
        return

    print(f"   找到 {len(articles)} 篇文章")

    # 2. 去重
    print("\n🔄 步骤 2/4: 去重处理...")
    articles = await collector.deduplicate(articles)
    print(f"   去重后剩余 {len(articles)} 篇新文章")

    if not articles:
        print("✅ 今日无新文章")
        return

    # 3. 获取互动数据
    print("\n📈 步骤 3/4: 获取互动数据...")
    articles = await collector.fetch_interaction_data(articles)

    # 4. AI分析
    print("\n🤖 步骤 4/4: AI分析爆文特征...")
    analysis = await analyzer.analyze_articles(articles)

    # 5. 生成报告
    print("\n📝 生成报告...")
    report_path = reporter.generate_daily_report(articles, analysis)

    # 更新索引
    reporter.update_index()

    # 获取HTML报告路径并自动打开
    html_report_path = report_path.replace('.md', '.html')

    # 完成
    print("\n" + "=" * 40)
    print("✅ 采集完成！")
    print()
    print("📊 今日数据")
    print(f"   新增爆文: {len(articles)}篇")
    if articles:
        avg_read = sum(a.get('stats', {}).get('read', 0) for a in articles) / len(articles)
        print(f"   平均阅读: {avg_read:,.0f}")
    print()
    print(f"📄 报告已生成: {report_path}")
    print(f"📄 HTML报告: {html_report_path}")
    print("=" * 40)

    # 自动打开HTML报告
    import subprocess
    import platform
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', html_report_path], check=True)
        elif platform.system() == 'Windows':
            subprocess.run(['start', '', html_report_path], shell=True, check=True)
        else:  # Linux
            subprocess.run(['xdg-open', html_report_path], check=True)
        print("\n🌐 已自动打开HTML报告")
    except Exception as e:
        print(f"\n⚠️ 无法自动打开报告: {e}")


async def run_weekly():
    """生成周报"""
    print("\n📊 公众号爆文监控 - 生成周报\n")

    config_manager = ConfigManager()
    if not config_manager.config_exists():
        print("❌ 未找到配置文件")
        return

    config = config_manager.load_config()
    reporter = ReportGenerator(config)

    report_path = reporter.generate_weekly_report()

    if report_path:
        print(f"✅ 周报已生成: {report_path}")
    else:
        print("❌ 生成周报失败，可能没有足够的数据")


def main():
    parser = argparse.ArgumentParser(description='公众号爆文监控')
    parser.add_argument('--setup', action='store_true', help='配置向导')
    parser.add_argument('--weekly', action='store_true', help='生成周报')
    parser.add_argument('--monthly', action='store_true', help='生成月报')
    parser.add_argument('--keyword', type=str, help='指定关键词')
    parser.add_argument('--trends', action='store_true', help='查看趋势')

    args = parser.parse_args()

    if args.setup:
        asyncio.run(run_setup())
    elif args.weekly:
        asyncio.run(run_weekly())
    elif args.monthly:
        print("月报功能开发中...")
    elif args.trends:
        print("趋势分析功能开发中...")
    else:
        asyncio.run(run_collect(args.keyword))


if __name__ == '__main__':
    main()
