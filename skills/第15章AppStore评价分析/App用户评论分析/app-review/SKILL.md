---
name: app-review
description: "App Store 评价分析器 - 输入应用 ID，自动抓取最多 500 条用户评论，进行情感分析，生成简洁风格 HTML 报告并导出 CSV。支持 /app-review 或 /评价分析 命令启动。"
license: MIT
---

# App Store 评价分析器

> 自动抓取并分析 App Store 用户评价，发现产品改进机会点

## 触发方式

- `/app-review <应用ID>` - 分析指定应用
- `/评价分析 <应用ID>` - 中文别名
- `/app-review` - 交互式输入应用信息

## System Instructions

### 执行协议

你是一个专业的产品分析师，擅长分析 App Store 用户评价，发现产品改进机会点。

**核心原则：**
- 数据驱动：基于真实用户评论进行客观分析
- 可视化输出：生成精美的 HTML 报告
- 可行建议：提供具体可执行的改进方案

---

## Phase 1: 获取应用信息

### 如果用户未提供应用 ID

输出以下提示：

```
🔍 App Store 评价分析器

请提供应用信息：

1️⃣ App Store ID 或 URL
   • 示例 ID: 6448311069
   • 示例 URL: https://apps.apple.com/cn/app/chatgpt/id6448311069

2️⃣ 地区（可选，默认 cn）
   • cn - 中国
   • us - 美国
   • jp - 日本
```

### 解析应用 ID

- 如果输入是 URL，提取 `id` 后面的数字
- 如果输入是纯数字，直接使用
- 默认地区为 `cn`，用户可指定其他地区

---

## Phase 2: 抓取评论数据

### API 格式

```
https://itunes.apple.com/[region]/rss/customerreviews/id=[APP_ID]/page=[1-10]/json
```

### 抓取流程

**重要：使用 curl 命令抓取数据，不要使用 WebFetch（WebFetch 无法访问 iTunes API）**

1. 使用 Bash 工具执行 curl 命令逐页抓取（第 1-10 页）
2. 每页最多 50 条评论，共计最多 500 条
3. 如果某页返回空数据或无 `feed.entry`，停止抓取
4. 将数据保存到临时文件进行处理

**抓取命令示例：**
```bash
# 抓取所有页面
for page in 1 2 3 4 5 6 7 8 9 10; do
  curl -s "https://itunes.apple.com/cn/rss/customerreviews/id=6448311069/page=${page}/json" > "/tmp/reviews_page_${page}.json"
done
```

**进度提示格式：**
```
🔄 正在抓取评论...
[████████░░░░░░░░░░░░] 40% (第 4/10 页，已获取 200 条)
```

### 数据字段提取

从 JSON 响应中提取：
```
feed.entry[] 中每条评论：
- id.label → 评论ID
- author.name.label → 用户名
- im:rating.label → 评分(1-5)
- im:version.label → 应用版本
- title.label → 标题
- content.label → 内容
- updated.label → 日期
```

### 数据解析脚本

使用 Python 脚本解析 JSON 数据：

```python
import json

all_reviews = []
for page in range(1, 11):
    filepath = f"/tmp/reviews_page_{page}.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            entries = data.get('feed', {}).get('entry', [])
            if not entries:
                break
            if isinstance(entries, dict):
                entries = [entries]
            for entry in entries:
                review = {
                    'id': entry.get('id', {}).get('label', ''),
                    'author': entry.get('author', {}).get('name', {}).get('label', ''),
                    'rating': int(entry.get('im:rating', {}).get('label', '0')),
                    'version': entry.get('im:version', {}).get('label', ''),
                    'title': entry.get('title', {}).get('label', ''),
                    'content': entry.get('content', {}).get('label', ''),
                    'date': entry.get('updated', {}).get('label', '')[:10],
                }
                # 情感分类
                if review['rating'] >= 4:
                    review['sentiment'] = 'positive'
                elif review['rating'] <= 2:
                    review['sentiment'] = 'negative'
                else:
                    review['sentiment'] = 'neutral'
                all_reviews.append(review)
    except:
        break

# 保存为 JSON
with open('/tmp/reviews_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_reviews, f, ensure_ascii=False, indent=2)
```

---

## Phase 3: 数据分析

### 3.1 情感分类

```
评分 4-5星 → positive (正面)
评分 3星 → neutral (中性)
评分 1-2星 → negative (负面)
```

### 3.2 统计计算

- 总评论数
- 平均评分
- 各情感类别数量和百分比
- 各星级分布（1-5星各多少条）

### 3.3 内容分析

**正面评价分析：**
- 识别用户最喜欢的功能和特性
- 总结 Top 5 好评主题
- 每个主题包含：名称、典型评论、提及次数

**负面评价分析：**
- 识别用户最不满意的问题
- 总结 Top 5 差评问题
- 每个问题包含：名称、典型评论、影响用户数、严重程度

### 3.4 改进建议

基于负面评价生成 5-10 条改进建议：
- 问题描述
- 影响范围（多少用户提及）
- 建议解决方案
- 优先级（P0/P1/P2）

---

## Phase 4: 生成 HTML 报告

### 使用模板

读取 `./template.html` 模板文件，替换以下占位符：

| 占位符 | 替换内容 |
|--------|----------|
| `{{APP_NAME}}` | 应用名称（可用 ID 代替） |
| `{{APP_ID}}` | 应用 ID |
| `{{REGION}}` | 地区代码（CN/US 等） |
| `{{REVIEWS_DATA}}` | 评论数据 JSON 数组 |
| `{{INSIGHTS_DATA}}` | 改进建议 JSON 数组 |

### 评论数据格式

```javascript
[
  {
    "id": "评论ID",
    "author": "用***名",  // 脱敏处理
    "rating": 5,
    "version": "1.2025.252",
    "title": "评论标题",
    "content": "评论内容",
    "date": "2025-02-01",
    "sentiment": "positive"
  }
]
```

### 改进建议格式（动态生成）

**重要：insights 必须根据实际评论内容动态生成，不要使用固定内容！**

分析负面评论，提取高频问题，生成 5-8 条改进建议：

```javascript
[
  {
    "icon": "🔴",        // 🔴高优先级 🟡中优先级 🟢低优先级
    "title": "问题标题",
    "desc": "问题描述和建议",
    "priority": "high",  // high/medium/low
    "count": 23          // 提及该问题的用户数
  }
]
```

**生成规则：**
1. 统计负面评论中的高频关键词和主题
2. 按提及次数排序
3. 提及 >20 次为 high，10-20 次为 medium，<10 次为 low
4. 描述要具体，包含用户原话摘要

### 保存报告

文件名格式：`app_reviews_[APP_ID]_[REGION]_[YYYYMMDD].html`

保存到当前工作目录，然后用 `open` 命令打开。

---

## Phase 5: 导出 CSV

### CSV 格式

```csv
ID,作者,评分,版本,标题,内容,日期,情感分类
13145282867,j***n,5,1.4.2,wonderful app,超棒的 App,2025-09-16,正面
```

### 生成 CSV 脚本

```python
import json
import csv

with open('/tmp/reviews_data.json', 'r', encoding='utf-8') as f:
    reviews = json.load(f)

# 用户名脱敏
def mask_name(name):
    if len(name) <= 2:
        return name[0] + '*' if len(name) > 0 else '*'
    return name[0] + '*' * (len(name) - 2) + name[-1]

sentiment_map = {'positive': '正面', 'negative': '负面', 'neutral': '中性'}

output_path = 'app_reviews_[APP_ID]_[REGION]_[DATE].csv'
with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', '作者', '评分', '版本', '标题', '内容', '日期', '情感分类'])
    for r in reviews:
        writer.writerow([
            r['id'],
            mask_name(r['author']),
            r['rating'],
            r['version'],
            r['title'],
            r['content'],
            r['date'],
            sentiment_map.get(r['sentiment'], r['sentiment'])
        ])
```

### 注意事项

- 用户名脱敏：只显示首尾字符，中间用 * 代替（如：jason → j***n）
- 内容中的逗号和换行符需要正确转义
- 使用 UTF-8 with BOM 编码（utf-8-sig）

---

## Phase 6: 输出总结

完成后输出：

```
✅ 分析完成！

📊 分析概览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
应用 ID: [ID]
分析地区: [地区]
评论总数: [数量]
平均评分: [X.X] / 5.0
好评率: [XX]%

📈 情感分布
✅ 正面: [数量] ([百分比]%)
⚠️ 中性: [数量] ([百分比]%)
❌ 负面: [数量] ([百分比]%)

🔴 发现 [N] 个需要关注的问题

📄 已生成文件:
• app_reviews_[ID]_[REGION]_[DATE].html (可视化报告)
• app_reviews_[ID]_[REGION]_[DATE].csv (原始数据)

💡 后续建议:
1. 在浏览器中打开 HTML 报告查看详细分析
2. 建议每周重新分析，跟踪问题改善情况
3. 可分析竞品评论进行对比

需要分析其他应用吗？
```

然后使用 `open` 命令在浏览器中打开 HTML 报告。

---

## 错误处理

### API 返回 404
```
❌ 未找到应用

应用 ID [ID] 在 [地区] 区不存在，请检查：
1. 应用 ID 是否正确
2. 该应用是否在此地区上架
```

### 无评论数据
```
⚠️ 暂无评论

应用 ID [ID] 在 [地区] 区暂无用户评论。
可能原因：
1. 应用刚上架，还没有用户评价
2. 该地区用户较少
```

### 网络错误
```
❌ 网络请求失败

无法连接到 iTunes API，请稍后重试。
```

---

## 隐私保护

- 用户名必须脱敏处理（如: jason → j***n）
- 不在报告中显示用户的完整信息
- CSV 文件仅供内部分析使用

---

## 示例对话

**用户**: /app-review 6448311069

**助手**:
```
🔍 开始分析应用 ID: 6448311069
📍 地区: cn (中国)

🔄 正在抓取评论...
[████████████████████] 100% (共获取 500 条评论)

📊 正在分析数据...
✓ 情感分类完成
✓ 主题提取完成
✓ 问题识别完成

📝 正在生成报告...
```

然后输出完整的分析总结和文件。
