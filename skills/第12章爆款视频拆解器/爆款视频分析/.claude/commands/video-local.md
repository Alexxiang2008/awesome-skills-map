---
description: 本地视频爆款拆解与优化分析，输出8维度评分 + 5大进阶模块 + HTML可视化报告
argument-hint: <本地视频路径> [--target-size <MB>] [--title <标题>]
allowed-tools: Bash(python:*), Bash(ffmpeg:*), Bash(which:*), Bash(cd:*), Bash(python3:*), Bash(echo:*), Bash(brew:*), Bash(pip3:*), Read, Write, Edit, Glob, Grep
---

# 本地视频爆款拆解与优化专家 v3

> 输入本地视频文件路径 → 自动压缩 → AI 原生视频理解 → 8维度深度分析 + 5大进阶模块 → HTML可视化报告

**注意：仅支持本地视频文件，不支持在线链接。** 支持格式：mp4、mkv、webm、avi、mov、flv、wmv、m4v、ts、mts

---

## 首次使用引导（每次执行前必须检查）

**在做任何分析之前**，你必须按顺序执行以下检查。如果所有检查都通过，直接跳到"执行"部分。如果有任何一项未通过，停下来引导用户完成配置。

### 检查 1：Python 3

```bash
which python3 && python3 --version
```

如果未安装，告诉用户：
- `brew install python3`（需要 Homebrew）
- 或从 https://www.python.org/downloads/ 下载

### 检查 2：ffmpeg

```bash
which ffmpeg
```

如果未安装，告诉用户运行 `brew install ffmpeg`。如果用户没有 Homebrew，先引导安装 Homebrew。

### 检查 3：豆包 API Key（最关键）

```bash
echo "${DOUBAO_API_KEY:-NOT_SET}"
```

如果输出 `NOT_SET` 或为空，说明用户还没配置 API Key。**停止分析**，进入以下引导流程：

1. 告诉用户：
   > 首次使用需要配置豆包 API Key。这是调用 AI 视频理解能力的凭证。
   >
   > **获取方式**：
   > 1. 访问 [火山引擎 Ark 控制台](https://console.volcengine.com/ark)
   > 2. 注册/登录后，创建 API Key
   > 3. 复制 API Key

2. 等用户提供 API Key 后，帮用户写入 shell 配置文件：

```bash
# 检测用户的 shell 类型
echo $SHELL
```

根据结果写入对应文件（zsh → `~/.zshrc`，bash → `~/.bashrc`）：

```bash
# 写入配置（幂等：先删旧的再写新的）
sed -i.bak '/# >>> 爆款视频分析配置 >>>/,/# <<< 爆款视频分析配置 <<</d' ~/.zshrc 2>/dev/null; rm -f ~/.zshrc.bak
cat >> ~/.zshrc << 'ENVEOF'

# >>> 爆款视频分析配置 >>>
export DOUBAO_API_KEY="用户提供的key"
# <<< 爆款视频分析配置 <<<
ENVEOF
```

3. 写入后，在当前 session 立即生效：

```bash
export DOUBAO_API_KEY="用户提供的key"
```

4. 验证配置成功：

```bash
echo "API Key 已配置: ${DOUBAO_API_KEY:0:8}..."
```

5. 配置完成后，提示用户重新输入 `/video-local <视频路径>` 开始分析。

### 检查 4：certifi（可选）

```bash
python3 -c "import certifi; print('OK')" 2>/dev/null || echo "NOT_INSTALLED"
```

如果未安装，简单提醒用户：如果后续遇到 SSL 错误，可以运行 `pip3 install certifi`。不阻塞流程。

---

## 执行

**只有当上述所有必要检查（1-3）都通过后**，才进入这个阶段。

解析用户输入的参数：`$ARGUMENTS`

- 如果用户只提供了视频路径，自动用文件名作为标题
- 如果用户提供了 `--target-size`，透传给脚本
- 如果用户提供了 `--title`，透传给脚本；否则自动从文件名生成标题

### 一键分析（推荐）

```bash
python3 ./scripts/video_analyzer.py run \
  <视频路径> \
  --title "<视频标题>" \
  --archive-dir ./outputs/reports
```

### 仅重新生成报告（从已有 JSON 结果）

如果用户输入以 `report` 开头：

```bash
python3 ./scripts/video_analyzer.py report \
  --result <JSON路径> \
  --video <视频路径> \
  --title "<视频标题>" \
  --archive-dir ./outputs/reports
```

## 执行协议

1. 收到本地视频文件路径后，先跑完所有检查项，通过后直接开始分析，不要反复确认
2. 先显示"正在压缩..."进度
3. 再显示"正在8维度分析..."进度
4. 再显示"正在逐场景细拆..."进度
5. 自动生成 HTML 可视化报告（启用归档模式，保存到 outputs/reports/）
6. 报告生成后，读取分析结果 JSON，输出完整的 Markdown 拆解报告
7. 不要反复确认，直接干
