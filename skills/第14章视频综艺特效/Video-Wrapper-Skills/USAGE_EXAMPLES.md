# 📖 使用示例

## 🎯 三种使用方式

### 方式一：YouTube 视频链接（最简单）

```bash
/video-wrapper https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**流程：**
1. 🎬 自动检测 YouTube 视频
2. ⬇️ 下载视频（最佳质量）
3. ⬇️ 下载字幕（优先中文，其次英文）
4. 📊 分析字幕内容
5. 💡 生成特效建议
6. ✅ 用户审批后渲染

**优点：**
- 无需手动下载
- 自动获取字幕
- 一条命令搞定

---

### 方式二：Bilibili 视频链接

```bash
/video-wrapper https://www.bilibili.com/video/BV1xx411c7mD
```

**流程：**
1. 🎬 自动检测 Bilibili 视频
2. ⬇️ 下载视频
3. ⬇️ 下载字幕（如果有）
4. 📊 分析字幕内容
5. 💡 生成特效建议
6. ✅ 用户审批后渲染

**支持的 B站链接格式：**
- `https://www.bilibili.com/video/BVxxxxx`
- `https://b23.tv/xxxxx`（短链接）

---

### 方式三：本地文件

```bash
/video-wrapper my-video.mp4 my-subtitles.srt
```

**适用场景：**
- 已经下载好的视频
- 自己制作的视频
- 使用其他工具生成的字幕

---

## 🎨 完整示例

### 示例 1：处理 YouTube 访谈视频

```bash
/video-wrapper https://www.youtube.com/watch?v=xxxxx
```

**Claude 的响应：**

```
🎬 检测到 YouTube 视频
📊 获取视频信息...
📹 视频标题: Anthropic CEO Interview - The Future of AI

⬇️  开始下载视频...
✅ 视频下载完成: ./downloads/Anthropic_CEO_Interview_The_Future_of_AI.mp4

⬇️  开始下载字幕...
✅ 字幕下载完成: ./downloads/Anthropic_CEO_Interview_The_Future_of_AI.srt

📊 正在分析字幕内容...

## 🎨 视觉特效建议

**推荐主题**: notion（温暖知识风格）

### 1. 人物条 (Lower Third)
- **姓名**: Dario Amodei
- **职位**: CEO
- **公司**: Anthropic
- **出现时间**: 1000ms
- **持续时长**: 5000ms

### 2. 章节标题 (Chapter Title)
- **编号**: Part 1
- **标题**: AI 的发展历程
- **副标题**: The History of AI Development
- **出现时间**: 0ms
- **持续时长**: 4000ms

### 3. 花字高亮 (Fancy Text)
1. **"AI发展是平滑的指数曲线"** (emphasis)
   - 时间: 2630ms - 5500ms
   - 原因: 核心观点首次提及

### 4. 名词卡片 (Term Card)
- **中文**: 摩尔定律
- **英文**: Moore's Law
- **解释**: 集成电路晶体管数量每18-24个月翻一番
- **首次出现**: 37550ms
- **显示时长**: 6 秒

### 5. 金句卡片 (Quote)
- **内容**: "AI 的发展是一个非常平滑的指数曲线"
- **作者**: — Dario Amodei
- **出现时间**: 30000ms
- **持续时长**: 5000ms

---

请审核以上建议，你可以：
1. ✅ 确认全部 - 直接使用所有建议
2. ✏️ 修改部分 - 告诉我需要调整的地方
3. ❌ 删除某些 - 告诉我不需要哪些组件
4. ➕ 添加新的 - 告诉我还需要添加什么

你想如何处理？
```

**用户回复：**
```
确认全部，使用 cyberpunk 主题
```

**Claude 继续：**
```
✅ 已确认，使用 cyberpunk 主题

📝 正在生成配置文件...
✅ 配置文件已生成: config.json

🎬 开始渲染视频...
🎨 渲染人物条... [完成]
📖 渲染章节标题... [完成]
🏷️ 渲染花字高亮... [完成]
📝 渲染名词卡片... [完成]
💬 渲染金句卡片... [完成]
🎬 合成最终视频...

✅ 完成！
📹 输出文件: Anthropic_CEO_Interview_The_Future_of_AI_wrapped.mp4
```

---

### 示例 2：处理 Bilibili 视频

```bash
/video-wrapper https://www.bilibili.com/video/BV1xx411c7mD
```

**流程相同，自动下载并处理**

---

### 示例 3：自定义修改建议

**用户：**
```
/video-wrapper https://www.youtube.com/watch?v=xxxxx
```

**Claude 给出建议后，用户回复：**
```
修改以下内容：
1. 删除社交媒体条
2. 把人物条的出现时间改到 5 秒
3. 添加一个金句："未来已来，只是分布不均" 在 1 分钟处
4. 使用 apple 主题
```

**Claude 会：**
1. 更新配置文件
2. 展示修改后的配置供确认
3. 确认后开始渲染

---

## 🎨 主题选择指南

### Notion 主题 🟡
**风格：** 温暖知识风，柔和渐变
**适合：** 教育、知识分享、课程、讲座
**色系：** 暖黄 + 蓝色

**示例场景：**
- 在线课程
- 知识分享视频
- 教育讲座
- 技能教学

---

### Cyberpunk 主题 💜
**风格：** 霓虹未来感，高对比
**适合：** 科技、前沿话题、科幻内容
**色系：** 霓虹紫 + 青色

**示例场景：**
- 科技产品发布
- AI/区块链话题
- 未来趋势讨论
- 游戏/电竞内容

---

### Apple 主题 ⚪
**风格：** 极简优雅，专业感
**适合：** 商务、企业、正式访谈
**色系：** 黑白灰

**示例场景：**
- 企业访谈
- 商务会议
- 专业论坛
- 正式发布会

---

### Aurora 主题 🌈
**风格：** 渐变流光，艺术感
**适合：** 创意、设计、艺术内容
**色系：** 渐变彩虹

**示例场景：**
- 设计分享
- 艺术创作
- 创意工作坊
- 音乐/表演

---

## 💡 高级技巧

### 技巧 1：指定视频质量

```bash
/video-wrapper https://www.youtube.com/watch?v=xxxxx --quality 720p
```

可选质量：
- `best` - 最佳质量（默认）
- `1080p` - 1080p
- `720p` - 720p
- `480p` - 480p

---

### 技巧 2：只下载不渲染

```bash
/video-wrapper https://www.youtube.com/watch?v=xxxxx --download-only
```

用于：
- 先下载视频和字幕
- 手动编辑字幕
- 稍后再处理

---

### 技巧 3：使用已有配置

如果你已经有配置文件：

```bash
/video-wrapper video.mp4 subtitles.srt config.json output.mp4
```

---

### 技巧 4：批量处理

创建一个视频列表文件 `videos.txt`：
```
https://www.youtube.com/watch?v=xxxxx1
https://www.youtube.com/watch?v=xxxxx2
https://www.bilibili.com/video/BVxxxxx
```

然后：
```bash
/video-wrapper --batch videos.txt
```

---

## ⚠️ 常见问题

### Q: 视频没有字幕怎么办？

**A:** 如果视频没有字幕，你可以：
1. 使用语音识别工具生成字幕（如 Whisper）
2. 手动创建 SRT 字幕文件
3. 使用在线字幕生成服务

---

### Q: 下载速度很慢？

**A:** 可能的原因：
1. 网络连接问题
2. YouTube/Bilibili 限速
3. 视频文件很大

**解决方案：**
- 使用代理
- 降低视频质量
- 分段下载

---

### Q: 支持其他视频平台吗？

**A:** 目前支持：
- ✅ YouTube
- ✅ Bilibili

计划支持：
- 🔜 抖音
- 🔜 小红书
- 🔜 Twitter/X

---

### Q: 可以处理多长的视频？

**A:** 理论上没有限制，但建议：
- 短视频（< 5 分钟）：最佳
- 中等视频（5-30 分钟）：推荐
- 长视频（> 30 分钟）：可能需要较长处理时间

---

## 📞 获取帮助

如果遇到问题：
1. 查看 [README.md](./README.md)
2. 查看 [ARCHITECTURE.md](./ARCHITECTURE.md)
3. 提交 Issue: https://github.com/op7418/Video-Wrapper-Skills/issues

---

## 🎉 开始使用

现在你已经了解了所有使用方式，试试处理你的第一个视频吧！

```bash
/video-wrapper <你的视频链接或文件>
```
