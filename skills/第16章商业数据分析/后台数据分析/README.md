# 小红书创作平台数据采集器

> 自动采集小红书创作平台的笔记数据，支持 JSON/CSV 导出和本地服务同步

## 📦 文件说明

```
xiaohongshu-scraper/
├── xiaohongshu-scraper.user.js    # Tampermonkey 脚本
├── server.js                       # 本地 API 服务
├── package.json                    # 依赖配置
└── README.md                       # 使用说明（本文件）
```

## 🚀 快速开始

### 第一步：安装 Tampermonkey

根据你的浏览器选择：

- **Chrome**: https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo
- **Edge**: https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd
- **Firefox**: https://addons.mozilla.org/firefox/addon/tampermonkey/

### 第二步：安装脚本

1. 点击浏览器工具栏中的 Tampermonkey 图标
2. 选择 **Dashboard（管理面板）**
3. 点击 **+** 号（新建脚本）
4. 删除默认内容
5. 打开 `xiaohongshu-scraper.user.js` 文件，复制全部内容
6. 粘贴到编辑器中
7. 按 **Ctrl+S** (Windows) 或 **Cmd+S** (Mac) 保存

### 第三步：启动本地服务（可选）

如果你需要自动同步数据到本地：

```bash
# 1. 安装依赖
npm install

# 2. 启动服务
npm start
```

看到以下提示表示服务启动成功：

```
🚀 小红书数据采集服务已启动

📡 服务地址: http://localhost:3000
📁 数据目录: /path/to/data
```

### 第四步：开始采集

1. 访问小红书创作平台：https://creator.xiaohongshu.com
2. 登录你的账号
3. 进入笔记列表页面
4. 右上角会出现 **小红书采集器** 控制面板
5. 点击 **▶️ 开始采集** 按钮
6. 脚本会自动翻页并采集数据
7. 采集完成后，点击 **💾 导出数据**

## 📊 采集的数据字段

| 字段名 | 说明 | 示例 |
|--------|------|------|
| id | 笔记ID | 69831f55000000002103185c |
| title | 笔记标题 | App分析Skills！ |
| type | 笔记类型 | 2=视频, 1=图文 |
| post_time | 发布时间 | 1770200917000 |
| read_count | 阅读量 | 10 |
| like_count | 点赞数 | 1 |
| fav_count | 收藏数 | 0 |
| comment_count | 评论数 | 0 |
| share_count | 分享数 | 0 |
| imp_count | 曝光量 | 1092 |
| view_time_avg | 平均观看时长（秒） | 20 |
| increase_fans_count | 涨粉数 | 0 |
| coverClickRate | 封面点击率 | 0.055 |
| cover_url | 封面图片URL | http://... |
| audit_status | 审核状态 | 1=已发布 |

## 💡 使用模式

### 自动模式（推荐）

1. 点击 **▶️ 开始采集**
2. 脚本自动翻页并采集数据
3. 包含防检测机制：
   - 随机延迟 2-5 秒
   - 15% 概率随机停顿 3-10 秒
   - 随机滚动页面
4. 采集完成后自动停止

### 手动模式

1. 不点击"开始采集"按钮
2. 手动翻页浏览笔记
3. 脚本会自动拦截并保存数据
4. 适合需要精细控制的场景

## 📥 数据导出

点击 **💾 导出数据** 后，可以选择：

### 1. JSON 格式
- 原始数据，包含所有字段
- 适合二次开发和数据处理
- 文件名：`xiaohongshu_notes_时间戳.json`

### 2. CSV 格式
- 表格格式，可用 Excel 打开
- 适合数据分析和可视化
- 文件名：`xiaohongshu_notes_时间戳.csv`

### 3. 同步到本地服务
- 自动保存 JSON 和 CSV 两种格式
- 数据保存在 `data/` 目录
- 需要先启动本地服务

## 🛡️ 防检测机制

脚本内置多种防检测措施：

- ✅ 随机翻页延迟（2-5秒）
- ✅ 随机停顿（15%概率，3-10秒）
- ✅ 随机滚动页面
- ✅ 模拟真实用户行为
- ✅ 避免短时间大量请求

## ⚙️ 配置说明

如需调整配置，编辑脚本中的 `CONFIG` 对象：

```javascript
const CONFIG = {
    API_URL: '/api/galaxy/creator/datacenter/note/analyze/list',
    LOCAL_API: 'http://localhost:3000',
    ENABLE_LOCAL_SYNC: true,
    AUTO_COLLECT: true,

    // 防检测配置
    PAGE_DELAY_MIN: 2000,        // 翻页最小延迟（毫秒）
    PAGE_DELAY_MAX: 5000,        // 翻页最大延迟（毫秒）
    PAUSE_PROBABILITY: 0.15,     // 随机停顿概率（0-1）
    PAUSE_TIME_MIN: 3000,        // 停顿最小时长（毫秒）
    PAUSE_TIME_MAX: 10000,       // 停顿最大时长（毫秒）
    ENABLE_SCROLL: true,         // 是否启用随机滚动
};
```

## 📊 数据分析建议

采集到数据后，你可以进行以下分析：

### 1. 内容表现分析
- 哪些类型的笔记表现更好？（图文 vs 视频）
- 哪些主题的笔记互动率更高？
- 发布时间对数据的影响？

### 2. 趋势分析
- 阅读量、点赞数的变化趋势
- 粉丝增长趋势
- 内容质量变化

### 3. 对比分析
- 不同时期的数据对比
- 不同类型内容的对比
- 封面点击率分析

### 4. 优化建议
- 基于数据发现内容优化方向
- 找到最佳发布时间
- 识别高价值话题

## ❓ 常见问题

### Q: 脚本没有加载？
**A:** 检查以下几点：
1. Tampermonkey 是否已启用
2. 脚本是否已保存
3. 当前页面 URL 是否匹配 `creator.xiaohongshu.com`

### Q: 数据没有被拦截？
**A:**
1. 打开浏览器控制台（F12）
2. 查看是否有 "🎯 拦截到笔记数据" 的日志
3. 如果没有，可能是 API 地址变化了，需要重新查找

### Q: 自动翻页不工作？
**A:**
1. 检查是否有下一页按钮
2. 可能已经是最后一页
3. 查看控制台是否有错误信息

### Q: 同步到本地服务失败？
**A:**
1. 确认本地服务是否已启动
2. 检查端口 3000 是否被占用
3. 查看服务控制台的错误信息

### Q: 导出的数据不完整？
**A:**
1. 确保所有页面都已采集
2. 检查控制面板显示的数据条数
3. 可以清空数据后重新采集

### Q: 被平台检测到异常？
**A:**
1. 降低采集频率（增加延迟时间）
2. 增加随机停顿概率
3. 避免在短时间内大量采集
4. 建议分多次采集

## 🔧 高级用法

### 修改本地服务端口

编辑 `server.js`：

```javascript
const PORT = 3000;  // 改为其他端口，如 8080
```

同时修改脚本中的配置：

```javascript
LOCAL_API: 'http://localhost:8080',
```

### 自定义数据处理

在 `server.js` 中添加自定义逻辑：

```javascript
app.post('/api/sync/xiaohongshu/notes', (req, res) => {
    const { notes } = req.body;

    // 自定义处理逻辑
    // 例如：过滤、转换、存储到数据库等

    res.json({ success: true });
});
```

### 增量采集

脚本已内置去重功能，重复的笔记不会被添加。

## ⚠️ 注意事项

1. **仅用于个人数据备份和分析**
2. **请遵守小红书平台服务条款**
3. **建议合理控制采集频率**
4. **避免对平台造成压力**
5. **不要用于商业用途**
6. **数据仅供个人学习研究使用**

## 📝 更新日志

### v1.0.0 (2024-02-04)
- ✨ 初始版本发布
- ✅ 支持自动翻页采集
- ✅ 支持 JSON/CSV 导出
- ✅ 支持本地服务同步
- ✅ 内置防检测机制
- ✅ 可视化控制面板

## 📄 许可证

MIT License

## 🙏 致谢

本工具由 Claude Code 生成，参考了 doulaoban.js 的设计思路。

---

**如有问题或建议，欢迎反馈！**
