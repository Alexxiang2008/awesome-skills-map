"""2026前沿风格HTML模板 - 白色背景 + Bento Grid + 柔和渐变"""

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公众号爆文监控 - {date}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --border-light: #e2e8f0;
            --border-medium: #cbd5e1;
            --accent-1: #6366f1;
            --accent-2: #8b5cf6;
            --accent-3: #ec4899;
            --accent-4: #06b6d4;
            --accent-5: #10b981;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-tertiary: #94a3b8;
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        /* 顶部渐变装饰条 */
        .top-gradient {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-1), var(--accent-2), var(--accent-3), var(--accent-4));
            z-index: 100;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 24px;
        }}

        /* Header */
        .header {{
            background: var(--bg-primary);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.08), transparent 70%);
            pointer-events: none;
        }}

        .header-content {{
            position: relative;
            z-index: 1;
        }}

        .header h1 {{
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--text-primary);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .header .subtitle {{
            font-size: 15px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .header .tag {{
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            padding: 6px 16px;
            border-radius: 100px;
            font-size: 13px;
            font-weight: 500;
            color: white;
        }}

        /* Bento Grid 统计卡片 */
        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}

        .bento-card {{
            background: var(--bg-primary);
            border-radius: 16px;
            padding: 24px;
            box-shadow: var(--shadow-md);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid var(--border-light);
        }}

        .bento-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-xl);
        }}

        .bento-card .icon {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-bottom: 16px;
        }}

        .bento-card:nth-child(1) .icon {{ background: linear-gradient(135deg, #eef2ff, #e0e7ff); }}
        .bento-card:nth-child(2) .icon {{ background: linear-gradient(135deg, #ecfeff, #cffafe); }}
        .bento-card:nth-child(3) .icon {{ background: linear-gradient(135deg, #fefce8, #fef08a); }}
        .bento-card:nth-child(4) .icon {{ background: linear-gradient(135deg, #fdf2f8, #fce7f3); }}

        .bento-card .value {{
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}

        .bento-card .label {{
            font-size: 13px;
            color: var(--text-tertiary);
            font-weight: 500;
        }}

        /* Section */
        .section {{
            background: var(--bg-primary);
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-light);
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-light);
        }}

        .section-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white;
        }}

        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
        }}

        /* 文章卡片 */
        .article-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.25s ease;
        }}

        .article-card:hover {{
            border-color: var(--accent-1);
            box-shadow: var(--shadow-md);
            background: var(--bg-primary);
        }}

        .article-header {{
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }}

        .article-rank {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white;
            flex-shrink: 0;
        }}

        .article-info {{
            flex: 1;
            min-width: 0;
        }}

        .article-title {{
            font-size: 16px;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 8px;
        }}

        .article-title a {{
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.2s;
        }}

        .article-title a:hover {{
            color: var(--accent-1);
        }}

        .article-meta {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13px;
            color: var(--text-secondary);
        }}

        .article-meta .account {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .article-meta .type-badge {{
            background: var(--bg-tertiary);
            color: var(--accent-1);
            padding: 3px 10px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 500;
        }}

        .article-stats {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            padding: 16px;
            background: var(--bg-primary);
            border-radius: 12px;
            margin-bottom: 16px;
            border: 1px solid var(--border-light);
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-item .value {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 2px;
        }}

        .stat-item .label {{
            font-size: 11px;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .article-metrics {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 14px;
        }}

        .metric-pill {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: var(--bg-primary);
            border: 1px solid var(--border-light);
            border-radius: 100px;
            font-size: 13px;
        }}

        .metric-pill .label {{
            color: var(--text-tertiary);
        }}

        .metric-pill .value {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .metric-pill.highlight {{
            background: linear-gradient(135deg, #eef2ff, #e0e7ff);
            border-color: rgba(99, 102, 241, 0.3);
        }}

        .metric-pill.highlight .value {{
            color: var(--accent-1);
        }}

        .article-analysis {{
            padding-top: 14px;
            border-top: 1px solid var(--border-light);
        }}

        .formula-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 13px;
        }}

        .formula-row .label {{
            color: var(--text-tertiary);
        }}

        .formula-row code {{
            background: #fdf2f8;
            color: var(--accent-3);
            padding: 5px 12px;
            border-radius: 6px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 12px;
        }}

        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .tag {{
            background: linear-gradient(135deg, #eef2ff, #e0e7ff);
            border: 1px solid rgba(99, 102, 241, 0.2);
            color: var(--accent-1);
            padding: 5px 12px;
            border-radius: 100px;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s;
        }}

        .tag:hover {{
            background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
            transform: scale(1.02);
        }}

        /* 趋势分析 */
        .trend-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .trend-item {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            transition: all 0.25s ease;
        }}

        .trend-item:hover {{
            background: var(--bg-primary);
            border-color: var(--accent-1);
            box-shadow: var(--shadow-sm);
        }}

        .trend-rank {{
            font-size: 24px;
        }}

        .trend-keyword {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            min-width: 100px;
        }}

        .trend-count {{
            background: #ecfeff;
            color: var(--accent-4);
            padding: 4px 12px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 600;
        }}

        .trend-heat {{
            font-size: 13px;
            color: var(--text-secondary);
        }}

        .trend-interaction {{
            margin-left: auto;
            font-size: 14px;
            font-weight: 600;
            color: var(--accent-1);
        }}

        /* 选题建议 */
        .suggestion-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
        }}

        .suggestion-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }}

        .suggestion-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-1), var(--accent-2), var(--accent-3));
        }}

        .suggestion-card:hover {{
            background: var(--bg-primary);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }}

        .suggestion-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 14px;
            line-height: 1.5;
        }}

        .suggestion-meta {{
            display: flex;
            gap: 10px;
            margin-bottom: 14px;
        }}

        .suggestion-type {{
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white;
            padding: 4px 12px;
            border-radius: 100px;
            font-size: 11px;
            font-weight: 600;
        }}

        .suggestion-rate {{
            color: var(--text-secondary);
            font-size: 12px;
            display: flex;
            align-items: center;
        }}

        .suggestion-ref {{
            font-size: 12px;
            color: var(--text-tertiary);
            margin-bottom: 6px;
            padding: 10px;
            background: var(--bg-primary);
            border-radius: 8px;
            border: 1px solid var(--border-light);
        }}

        .suggestion-structure {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 32px;
            color: var(--text-tertiary);
            font-size: 13px;
        }}

        /* 响应式 */
        @media (max-width: 1024px) {{
            .bento-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px 16px;
            }}

            .header {{
                padding: 28px 20px;
            }}

            .header h1 {{
                font-size: 24px;
            }}

            .bento-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }}

            .bento-card {{
                padding: 18px;
            }}

            .bento-card .value {{
                font-size: 22px;
            }}

            .article-stats {{
                grid-template-columns: repeat(3, 1fr);
            }}

            .article-header {{
                flex-direction: column;
            }}

            .suggestion-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* 打印优化 */
        @media print {{
            body {{
                background: white;
            }}
            .top-gradient {{
                display: none;
            }}
            .section, .bento-card, .header {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}
    </style>
</head>
<body>
    <div class="top-gradient"></div>

    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-content">
                <h1>📊 公众号爆文监控</h1>
                <div class="subtitle">
                    <span>{date}</span>
                    <span class="tag">{keywords}</span>
                </div>
            </div>
        </div>

        <!-- Bento Grid Stats -->
        <div class="bento-grid">
            <div class="bento-card">
                <div class="icon">📄</div>
                <div class="value">{total}</div>
                <div class="label">新增爆文</div>
            </div>
            <div class="bento-card">
                <div class="icon">👁</div>
                <div class="value">{avg_read}</div>
                <div class="label">平均阅读</div>
            </div>
            <div class="bento-card">
                <div class="icon">💬</div>
                <div class="value">{avg_interaction}‰</div>
                <div class="label">平均互动率</div>
            </div>
            <div class="bento-card">
                <div class="icon">🚀</div>
                <div class="value">{avg_spread}‰</div>
                <div class="label">平均传播指数</div>
            </div>
        </div>

        <!-- 爆文榜单 -->
        <div class="section">
            <div class="section-header">
                <div class="section-icon">🔥</div>
                <h2 class="section-title">今日爆文榜</h2>
            </div>
            {article_cards}
        </div>

        <!-- 选题趋势 -->
        <div class="section">
            <div class="section-header">
                <div class="section-icon">💡</div>
                <h2 class="section-title">选题方向分析</h2>
            </div>
            <div class="trend-list">
                {trends_html}
            </div>
        </div>

        <!-- 选题建议 -->
        <div class="section">
            <div class="section-header">
                <div class="section-icon">🎯</div>
                <h2 class="section-title">选题建议</h2>
            </div>
            <div class="suggestion-grid">
                {suggestions_html}
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            报告生成时间: {generated_at}
        </div>
    </div>
</body>
</html>'''

ARTICLE_CARD_TEMPLATE = '''
<div class="article-card">
    <div class="article-header">
        <div class="article-rank">{rank}</div>
        <div class="article-info">
            <h3 class="article-title">
                <a href="{url}" target="_blank">{title}</a>
            </h3>
            <div class="article-meta">
                <span class="account">📝 {account}</span>
                <span class="type-badge">{topic_type}</span>
            </div>
        </div>
    </div>
    <div class="article-stats">
        <div class="stat-item">
            <div class="value">{read}</div>
            <div class="label">阅读</div>
        </div>
        <div class="stat-item">
            <div class="value">{zan}</div>
            <div class="label">点赞</div>
        </div>
        <div class="stat-item">
            <div class="value">{looking}</div>
            <div class="label">在看</div>
        </div>
        <div class="stat-item">
            <div class="value">{share}</div>
            <div class="label">转发</div>
        </div>
        <div class="stat-item">
            <div class="value">{collect}</div>
            <div class="label">收藏</div>
        </div>
    </div>
    <div class="article-metrics">
        <div class="metric-pill">
            <span class="label">互动率</span>
            <span class="value">{interaction_rate}‰</span>
        </div>
        <div class="metric-pill">
            <span class="label">传播指数</span>
            <span class="value">{spread_index}‰</span>
        </div>
        <div class="metric-pill highlight">
            <span class="label">爆文潜力分</span>
            <span class="value">{viral_score}</span>
        </div>
    </div>
    <div class="article-analysis">
        <div class="formula-row">
            <span class="label">标题公式</span>
            <code>{title_formula}</code>
        </div>
        <div class="tags">
            {tags}
        </div>
    </div>
</div>
'''

TREND_ITEM_TEMPLATE = '''
<div class="trend-item">
    <span class="trend-rank">{rank_icon}</span>
    <span class="trend-keyword">{keyword}</span>
    <span class="trend-count">{count}篇</span>
    <span class="trend-heat">{heat_level}</span>
    <span class="trend-interaction">互动率 {interaction_rate}‰</span>
</div>
'''

SUGGESTION_CARD_TEMPLATE = '''
<div class="suggestion-card">
    <div class="suggestion-title">{title}</div>
    <div class="suggestion-meta">
        <span class="suggestion-type">{type}</span>
        <span class="suggestion-rate">预计互动率 {rate}</span>
    </div>
    <div class="suggestion-ref">📎 参考: {reference}</div>
    <div class="suggestion-structure">📐 结构: {structure}</div>
</div>
'''
