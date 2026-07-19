#!/usr/bin/env python3
"""
本地视频爆款拆解分析工具 v2
- 仅支持本地视频文件输入
- 自动压缩 + 豆包API原生视频理解
- 8维度爆款拆解 + 可复制模板输出
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import ssl
import threading
import urllib.request
import urllib.error
from pathlib import Path

# 报告生成器
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# macOS Python SSL 证书修复
SSL_CONTEXT = ssl.create_default_context()
try:
    import certifi
    SSL_CONTEXT.load_verify_locations(certifi.where())
except ImportError:
    SSL_CONTEXT.check_hostname = False
    SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# ─── 配置 ───────────────────────────────────────────────
API_ENDPOINT = os.environ.get("DOUBAO_API_ENDPOINT", "https://ark.cn-beijing.volces.com/api/v3/responses")
API_KEY = os.environ.get("DOUBAO_API_KEY", "")
MODEL = os.environ.get("DOUBAO_MODEL", "doubao-seed-2-0-pro-260215")
MAX_RETRIES = 3
TARGET_SIZE_MB = 35     # 压缩目标大小（MB），base64后约47MB，留安全余量
API_MAX_MB = 50         # API base64上传大小上限（MB），对应原始文件约37MB
WORK_DIR = "/tmp/video-local-analyze"

# 支持的视频格式
SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv", ".m4v", ".ts", ".mts"}

# ─── 分析 Prompt ────────────────────────────────────────

VIDEO_ANALYSIS_PROMPT = """你是一名顶级短视频运营专家 + AI视觉分析师。我会给你一段完整的短视频，请你从以下8个维度进行深度分析。

## 视频信息
- 文件名: {file_name}
- 总时长: {duration}秒
- 分辨率: {width}x{height}

## 请逐一分析以下8个维度，每个维度给出1-10的评分：

### 1. 开头吸引力（黄金3秒）
- 前3秒的视觉冲击力如何？
- 是否有文字Hook/问题/悬念？
- 开场公式是什么类型？（问题型/数字型/反差型/情感型/故事型）

### 2. 叙事结构
- 故事弧线属于哪种类型？（悬念型/反转型/教程型/对比型/清单型/情感型）
- 信息揭示的顺序是什么？
- 按时间段拆解每个段落的功能

### 3. 节奏感
- 画面变化频率如何？
- 节奏是快-慢-快还是匀速？
- 标记关键节奏点（第几秒发生了什么转折）

### 4. 视觉构图与效果
- 使用了哪些景别？（特写/中景/远景/俯拍等）
- 色彩风格和调色倾向是什么？
- 有哪些转场效果或特效？
- 画面构图质量如何？

### 5. 字幕与文字设计
- 画面上是否有文字叠加？位置在哪？
- 字体大小、颜色、风格如何？
- 关键词是否有高亮或动画效果？
- 文字信息密度如何？

### 6. 音乐与音效
- 背景音乐的风格和节奏如何？BPM大致多少？
- 是否有音效？在什么时间点出现？
- 音乐和画面节奏是否同步？
- 人声（如有）的语调、语速、情感如何？

### 7. 互动引导（CTA）
- 是否有引导关注/点赞/评论的元素？
- 出现在第几秒？
- 形式是什么？（文字/口播/手势/贴纸/动画）

### 8. 结尾设计
- 结尾的设计是什么？
- 是否有Loop设计（结尾衔接开头）？
- 是否有"下集预告"或系列钩子？

## 评分标准（重要！）

你必须基于视频的实际质量独立评分，不要受到示例格式中任何数字的影响。评分应有明显区分度：
- 1-3分：差，明显不足，业余水平
- 4-5分：一般，有基本功但缺乏亮点
- 6-7分：良好，有一定专业度和创意
- 8-9分：优秀，接近头部水平
- 10分：顶级，教科书级别（极少给出）

overall_score 应该是8个维度评分的加权平均（hook和narrative权重更高），不要简单给一个笼统的高分。
差的视频就应该给低分（3-5分），一般的给中间分（5-7分），只有真正优秀的才给8分以上。

## 输出要求

请严格按以下JSON格式输出（不要输出其他内容）。
注意：下面JSON中所有 `<X>` 标记的地方都是需要你根据实际分析结果填入的值，不是固定值。

```json
{{
  "overall_score": "<根据8维度加权计算，保留1位小数>",
  "summary": "一句话总结这个视频的核心亮点和风格",
  "dimensions": {{
    "hook": {{
      "score": "<1-10整数，基于实际开头质量>",
      "description": "详细描述开头表现",
      "formula": "提取的开场公式，如：反差开场+数字承诺",
      "template": "可复制的开场话术模板"
    }},
    "narrative": {{
      "score": "<1-10整数>",
      "type": "识别的叙事类型",
      "description": "叙事结构分析",
      "timeline": [
        {{"time": "0-3s", "content": "描述", "function": "Hook"}},
        {{"time": "3-10s", "content": "描述", "function": "铺垫"}}
      ],
      "template": "可复制的结构公式"
    }},
    "pacing": {{
      "score": "<1-10整数>",
      "description": "节奏分析",
      "cut_points": ["第X秒场景切换", "第X秒节奏变化"],
      "pattern": "节奏模式描述，如快-慢-快"
    }},
    "visual": {{
      "score": "<1-10整数>",
      "description": "视觉分析",
      "shots": ["特写", "中景"],
      "color_style": "色彩风格描述",
      "effects": ["使用的特效或转场"]
    }},
    "text_overlay": {{
      "score": "<1-10整数>",
      "description": "字幕文字分析",
      "has_text": true,
      "style": "字幕风格描述",
      "highlights": ["高亮关键词或技巧"]
    }},
    "audio": {{
      "score": "<1-10整数>",
      "description": "音频分析（含背景音乐、音效、人声）",
      "estimated_bpm": "推测的BPM范围",
      "sync_evidence": "音画同步证据",
      "voice_style": "人声风格描述"
    }},
    "cta": {{
      "score": "<1-10整数>",
      "description": "互动引导分析",
      "has_cta": true,
      "cta_time": "出现时间",
      "cta_type": "CTA类型"
    }},
    "ending": {{
      "score": "<1-10整数>",
      "description": "结尾设计分析",
      "is_loopable": false,
      "has_series_hook": false,
      "ending_type": "结尾类型描述"
    }}
  }},
  "replicable_template": {{
    "structure": "可复制的整体结构公式",
    "shot_list": [
      {{"shot": 1, "time": "0-3s", "type": "特写", "content": "描述", "text": "文字"}}
    ],
    "script_template": "可替换关键词的文案模板"
  }},
  "top3_strengths": ["亮点1", "亮点2", "亮点3"],
  "top3_improvements": ["改进点1", "改进点2", "改进点3"],

  "emotional_arc": {{
    "arc_type": "弧线类型（如: Man in a Hole先抑后扬 / Rags to Riches持续上升 / Icarus先扬后抑 / Cinderella起伏型 / Oedipus悲剧型 / 过山车型）",
    "arc_description": "一句话描述整体情绪走向特征",
    "curve_points": [
      {{"time": "0:00", "valence": "<-5到+5>", "arousal": "<0到10>", "label": "开场"}},
      {{"time": "M:SS", "valence": "<-5到+5>", "arousal": "<0到10>", "label": "描述"}}
    ],
    "turning_points": [
      {{"time": "M:SS", "type": "情绪锚点/高潮/反转/低谷", "description": "描述此处情绪转折及原因"}}
    ]
  }},

  "retention_prediction": {{
    "hook_rate_3s": "<0-100，基于开场实际吸引力>",
    "retention_30s": "<0-100，基于前30秒内容密度>",
    "midpoint_retention": "<0-100，基于中段节奏>",
    "completion_rate": "<0-100，基于整体完播动力>",
    "risk_segments": [
      {{"time": "开始-结束", "risk": "high/medium", "label": "段落名", "reason": "为什么观众可能划走", "fix": "具体修复建议"}}
    ]
  }},

  "viral_formulas": {{
    "script_formula": {{
      "steps": [
        {{"time": "0-3s", "name": "段落名", "desc": "这个段落做什么"}}
      ],
      "fill_template": "可填空的文案模板，用____标记可替换位置"
    }},
    "emotion_formula": {{
      "nodes": [
        {{"emotion": "情绪名", "valence": "<-5到+5>"}}
      ],
      "key_principles": ["情绪编排要点1", "情绪编排要点2"]
    }},
    "algorithm_formula": {{
      "drivers": [
        {{"type": "完播率驱动/评论率驱动/分享率驱动/收藏率驱动", "icon": "🔄", "factor": "具体驱动因素", "impact": "影响描述"}}
      ],
      "weight_tips": ["算法权重变化提示"]
    }}
  }},

  "algorithm_fitness": {{
    "metrics": {{
      "completion_rate": {{"score": "<0-100百分比>", "factors": [{{"name": "因素名", "value": "高/中/低或具体值", "positive": true}}]}},
      "interaction_rate": {{"score": "<0-20百分比>", "factors": [{{"name": "因素名", "value": "值", "positive": true}}]}},
      "share_rate": {{"score": "<0-20百分比>", "factors": [{{"name": "因素名", "value": "值", "positive": true}}]}},
      "save_rate": {{"score": "<0-20百分比>", "factors": [{{"name": "因素名", "value": "值", "positive": true}}]}}
    }},
    "platform_fit": [
      {{"platform": "B站", "icon": "📺", "score": "<0-100>", "reason": "适配原因", "recommended": "<true/false>"}},
      {{"platform": "抖音", "icon": "🎵", "score": "<0-100>", "reason": "适配原因", "recommended": "<true/false>"}},
      {{"platform": "小红书", "icon": "📕", "score": "<0-100>", "reason": "适配原因", "recommended": "<true/false>"}}
    ]
  }},

  "learning_path": [
    {{
      "rank": 1,
      "technique": "最值得学的技巧名",
      "difficulty": "easy/medium/hard",
      "why": "为什么值得学（结合视频中的具体效果说明）",
      "exercises": ["具体练习步骤1", "具体练习步骤2", "具体练习步骤3"],
      "reference": "进阶学习参考（书籍/搜索关键词/方法论名称）"
    }},
    {{
      "rank": 2,
      "technique": "第二个技巧",
      "difficulty": "easy/medium/hard",
      "why": "为什么值得学",
      "exercises": ["练习1", "练习2", "练习3"],
      "reference": "进阶参考"
    }},
    {{
      "rank": 3,
      "technique": "第三个技巧",
      "difficulty": "easy/medium/hard",
      "why": "为什么值得学",
      "exercises": ["练习1", "练习2", "练习3"],
      "reference": "进阶参考"
    }}
  ]
}}
```

## 补充说明

### emotional_arc 情绪弧线
- curve_points: 按视频时间轴等间隔采样（约每15-30秒一个点），valence范围-5(极消极)到+5(极积极)，arousal范围0(平静)到10(极兴奋)
- turning_points: 标记3-5个关键情绪转折点
- 基于你实际感受到的视频情绪变化，不要编造

### retention_prediction 留存预测
- 基于视频的内容节奏、悬念密度、视觉变化频率来预测
- hook_rate_3s: 前3秒留存率(0-100)，取决于开场吸引力
- risk_segments: 只标记medium和high风险的段落（观众可能划走的位置）

### viral_formulas 爆款公式
- script_formula.steps: 拆解视频的叙事骨架为可复用的段落公式
- emotion_formula.nodes: 按时间顺序列出情绪节点和效价值
- algorithm_formula.drivers: 分析哪些因素驱动完播/互动/分享/收藏

### algorithm_fitness 算法适配
- 各metrics的score: completion_rate用百分比(0-100)，其余用百分比(0-20)
- platform_fit: 评估视频在不同平台的适配度(0-100)，标记最适合的平台

### learning_path 学习路径
- 提取视频中最值得学习的3个技巧，按学习价值排序
- exercises: 给出3-5个具体可执行的练习步骤
- difficulty: easy(新手可学)/medium(需要一定经验)/hard(高阶技巧)"""


# ─── 工具函数 ──────────────────────────────────────────

def check_ffmpeg():
    """检查 ffmpeg 是否安装"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def validate_local_video(path):
    """校验本地视频文件是否存在且格式支持"""
    if not os.path.exists(path):
        print(f"[ERROR] 视频文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"[ERROR] 不支持的视频格式: {ext}", file=sys.stderr)
        print(f"[INFO] 支持的格式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}", file=sys.stderr)
        sys.exit(1)

    return os.path.abspath(path)


def get_video_info(video_path):
    """获取视频基本信息"""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] 无法读取视频信息: {video_path}", file=sys.stderr)
        sys.exit(1)
    info = json.loads(result.stdout)

    duration = float(info.get("format", {}).get("duration", 0))
    width, height = 0, 0
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            width = stream.get("width", 0)
            height = stream.get("height", 0)
            break

    return {
        "duration": round(duration, 1),
        "width": width,
        "height": height,
        "file_size_mb": round(os.path.getsize(video_path) / 1024 / 1024, 1),
        "file_name": os.path.basename(video_path),
        "title": "",  # 由调用方填充
    }


# ─── 视频压缩 ─────────────────────────────────────────

def compress_video(input_path, output_path=None, target_mb=None):
    """压缩视频到目标大小，确保 base64 后不超过 API_MAX_MB"""
    target_mb = target_mb or TARGET_SIZE_MB

    if output_path is None:
        base = Path(input_path)
        output_path = str(base.parent / f"{base.stem}_compressed.mp4")

    current_size_mb = os.path.getsize(input_path) / 1024 / 1024

    # base64 膨胀系数约 1.33
    base64_est_mb = current_size_mb * 4 / 3

    if current_size_mb <= target_mb and base64_est_mb <= API_MAX_MB:
        print(f"[INFO] 视频已小于{target_mb}MB ({current_size_mb:.1f}MB, base64≈{base64_est_mb:.0f}MB)，无需压缩")
        # 即使不压缩，也要确保 moov atom 在文件开头（faststart），
        # 否则浏览器通过 HTTP 无法流式播放视频
        faststart_path = output_path if not input_path.endswith(".mp4") else \
            str(Path(input_path).parent / f"{Path(input_path).stem}_fs.mp4")
        cmd = ["ffmpeg", "-i", input_path, "-c", "copy",
               "-movflags", "+faststart", "-y", faststart_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # 如果是原地处理mp4，替换原文件
            if input_path.endswith(".mp4") and faststart_path != input_path:
                os.replace(faststart_path, input_path)
                return input_path
            return faststart_path
        else:
            print(f"[WARN] faststart 重封装失败，使用原文件: {result.stderr[-200:]}")
            if input_path.endswith(".mp4"):
                return input_path
            return output_path

    # 如果文件本身不大但 base64 会超限，调低 target
    effective_target = min(target_mb, API_MAX_MB * 3 / 4 * 0.95)  # base64安全线的95%
    if current_size_mb > effective_target:
        effective_target = effective_target  # 需要压缩
    else:
        effective_target = current_size_mb  # 文件本身OK，不压缩

    # 如果真的需要压缩
    if current_size_mb > effective_target or base64_est_mb > API_MAX_MB:
        # 倒推: base64 < API_MAX_MB => 原始文件 < API_MAX_MB * 3/4
        safe_file_mb = API_MAX_MB * 3 / 4 * 0.92  # 留8%余量
        effective_target = min(target_mb, safe_file_mb)
        return _do_compress(input_path, output_path, effective_target)

    return input_path


def _do_compress(input_path, output_path, target_mb):
    """执行实际压缩"""
    current_size_mb = os.path.getsize(input_path) / 1024 / 1024

    # 获取视频信息
    info = get_video_info(input_path)
    duration = info["duration"]

    if duration <= 0:
        print("[ERROR] 无法获取视频时长", file=sys.stderr)
        sys.exit(1)

    # 计算目标码率 (kbps)
    target_total_bitrate = int(target_mb * 8 * 1024 / duration)
    audio_bitrate = 128 if target_total_bitrate > 300 else 64
    video_bitrate = max(200, target_total_bitrate - audio_bitrate)

    print(f"[INFO] 压缩视频: {current_size_mb:.1f}MB -> 目标{target_mb:.0f}MB")
    print(f"[INFO] 目标视频码率: {video_bitrate}kbps, 音频: {audio_bitrate}kbps, 时长: {duration:.0f}s")

    cmd = [
        "ffmpeg", "-i", input_path,
        "-c:v", "libx264",
        "-b:v", f"{video_bitrate}k",
        "-maxrate", f"{int(video_bitrate * 1.5)}k",
        "-bufsize", f"{video_bitrate * 2}k",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", f"{audio_bitrate}k",
        "-movflags", "+faststart",
        "-y",
        output_path
    ]

    # 如果视频高度超过720p，增加缩放
    if info["height"] > 720:
        idx = cmd.index("-c:v")
        cmd[idx:idx] = ["-vf", "scale=-2:720"]
        print(f"[INFO] 缩放: {info['width']}x{info['height']} -> 720p")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        print(f"[ERROR] 压缩失败: {result.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)

    new_size_mb = os.path.getsize(output_path) / 1024 / 1024
    new_b64_mb = new_size_mb * 4 / 3
    print(f"[OK] 压缩完成: {new_size_mb:.1f}MB (base64≈{new_b64_mb:.0f}MB, 压缩率 {current_size_mb/new_size_mb:.1f}x)")

    # 安全检查: 如果 base64 仍超限，二次压缩
    if new_b64_mb > API_MAX_MB:
        print(f"[WARN] base64 {new_b64_mb:.0f}MB 仍超过{API_MAX_MB}MB限制，二次压缩...")
        second_target = API_MAX_MB * 3 / 4 * 0.85  # 更激进的余量
        second_output = output_path.replace("_compressed.mp4", "_compressed2.mp4")
        return _do_compress(output_path, second_output, second_target)

    return output_path


# ─── API 调用 ──────────────────────────────────────────

def video_to_base64_url(video_path):
    """将视频转为base64 data URL"""
    size_mb = os.path.getsize(video_path) / 1024 / 1024
    print(f"[INFO] 正在编码视频为base64... ({size_mb:.1f}MB)")
    sys.stdout.flush()

    with open(video_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    b64_size_mb = len(b64) / 1024 / 1024
    print(f"[INFO] base64编码大小: {b64_size_mb:.1f}MB")
    sys.stdout.flush()

    return f"data:video/mp4;base64,{b64}"


def _heartbeat_printer(stop_event, label="API", interval=30):
    """在等待 API 响应时定期打印心跳，防止 stream idle timeout"""
    start = time.time()
    tick = 0
    while not stop_event.wait(interval):
        tick += 1
        elapsed = int(time.time() - start)
        print(f"[HEARTBEAT] {label} 等待中... 已 {elapsed}s", flush=True)
    elapsed = int(time.time() - start)
    if elapsed > interval:
        print(f"[HEARTBEAT] {label} 响应到达，耗时 {elapsed}s", flush=True)


def call_doubao_video_api(video_url, prompt):
    """调用豆包API进行视频分析（带心跳防 idle timeout）"""
    content = [
        {
            "type": "input_video",
            "video_url": video_url
        },
        {
            "type": "input_text",
            "text": prompt
        }
    ]

    payload = {
        "model": MODEL,
        "input": [
            {
                "role": "user",
                "content": content
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_ENDPOINT,
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    for attempt in range(MAX_RETRIES):
        # 启动心跳线程
        stop_event = threading.Event()
        heartbeat = threading.Thread(
            target=_heartbeat_printer,
            args=(stop_event, f"豆包视频分析(尝试{attempt+1})", 30),
            daemon=True,
        )

        try:
            print(f"[INFO] 调用豆包API视频分析... (尝试 {attempt + 1}/{MAX_RETRIES})")
            sys.stdout.flush()
            heartbeat.start()
            with urllib.request.urlopen(req, timeout=600, context=SSL_CONTEXT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                stop_event.set()
                heartbeat.join(timeout=2)
                return result
        except urllib.error.HTTPError as e:
            stop_event.set()
            heartbeat.join(timeout=2)
            error_body = e.read().decode("utf-8") if e.fp else ""
            print(f"[WARN] API调用失败 (HTTP {e.code}): {error_body}", file=sys.stderr)
            if attempt < MAX_RETRIES - 1:
                wait = (attempt + 1) * 5
                print(f"[INFO] {wait}秒后重试...")
                time.sleep(wait)
        except Exception as e:
            stop_event.set()
            heartbeat.join(timeout=2)
            print(f"[WARN] API调用异常: {e}", file=sys.stderr)
            if attempt < MAX_RETRIES - 1:
                wait = (attempt + 1) * 5
                print(f"[INFO] {wait}秒后重试...")
                time.sleep(wait)

    print("[ERROR] API调用失败，已达最大重试次数", file=sys.stderr)
    return None


# ─── 响应解析 ──────────────────────────────────────────

def extract_text_from_response(response):
    """从豆包API响应中提取文本内容"""
    if not response:
        return None

    output = response.get("output", {})

    # responses API 格式: output 为列表 [{reasoning}, {message}]
    if isinstance(output, list):
        texts = []
        for block in output:
            if block.get("type") == "message":
                content = block.get("content", [])
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "output_text":
                        texts.append(item.get("text", ""))
        if texts:
            return "\n".join(texts)

    # responses API 格式: output 为 dict
    if isinstance(output, dict):
        content = output.get("content", [])
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "output_text":
                    texts.append(item.get("text", ""))
            if texts:
                return "\n".join(texts)

        if "text" in output:
            return output["text"]

    # 兼容 chat completions 格式
    choices = response.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        return message.get("content", "")

    if isinstance(output, str):
        return output

    return json.dumps(response, ensure_ascii=False)


def extract_json_from_text(text):
    """从文本中提取JSON（支持 object 和 array）"""
    if not text:
        return None

    # 尝试找 ```json ... ``` 块
    json_match = re.search(r'```json\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试找 { ... } 块（匹配最外层大括号）
    brace_start = text.find('{')
    if brace_start >= 0:
        depth = 0
        end = brace_start
        for i in range(brace_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        try:
            return json.loads(text[brace_start:end])
        except json.JSONDecodeError:
            pass

    # 尝试找 [ ... ] 块（匹配最外层方括号，用于 JSON array）
    bracket_start = text.find('[')
    if bracket_start >= 0:
        depth = 0
        for i in range(bracket_start, len(text)):
            if text[i] == '[':
                depth += 1
            elif text[i] == ']':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[bracket_start:i + 1])
                    except json.JSONDecodeError:
                        pass
                    break

    return None


# ─── Scene 细拆 Prompt ────────────────────────────────

SCENE_ENRICHMENT_PROMPT = """你是一名专业视频拆解分析师。我会给你一段完整视频和它的章节分段。

## 视频信息
- 文件名: {file_name}
- 总时长: {duration}秒

## 已有章节分段
{chapters_desc}

## 你的任务

对每个章节，按 **15-25秒** 粒度拆分为具体场景（scene）。每个场景需要描述：

1. **visual**: 画面内容（构图、景别、画面元素、色彩变化、文字叠加）
2. **audio**: 音频变化（BGM变化、人声语调语速、音效）
3. **emotion**: 此刻观众的情绪状态（如好奇、兴奋、共鸣、紧张、反差、认同等）
4. **emotion_valence**: 情绪效价，范围 -5(极消极) 到 +5(极积极)，用于绘制情绪曲线
5. **emotion_arousal**: 唤醒度，范围 0(平静) 到 10(极兴奋)，用于绘制情绪曲线
6. **retention_risk**: 此段的留存风险等级: "low" / "medium" / "high"（观众是否可能划走）
7. **risk_reason**: 如果 retention_risk 为 medium 或 high，说明为什么观众可能划走（空字符串如果是 low）
8. **risk_fix**: 如果 retention_risk 为 medium 或 high，给出具体修复建议（空字符串如果是 low）
9. **quote**: 这段时间内关键台词的原文摘录（无明显台词则留空字符串）
10. **techniques**: 这个场景中使用的**爆款手法**（至少识别1个，最多3个），每个手法包含：
   - **name**: 手法名称（简短，如"反差钩子"、"开环悬念"、"数据佐证"）
   - **category**: 所属类别（Hook / 留存 / 节奏 / 情绪 / 信任 / 互动 / 视觉）
   - **why**: 为什么这个手法在此处有效（从完播率/互动/转化角度分析，1-2句话）

常见爆款手法参考（不限于此）：
- Hook类：反差开场、悬念抛出、数字承诺、痛点共鸣、模式打断
- 留存类：开环（未解决问题）、预告暗示、信息缺口、进度暗示
- 节奏类：快慢交替、静默张力、加速推进、节奏同步剪辑
- 情绪类：情绪过山车、反转落差、共鸣触发、爽感释放
- 信任类：实测展示、数据佐证、自嘲真诚、踩坑真实感
- 互动类：引导评论、系列钩子、知识缺口激发讨论
- 视觉类：色彩对比、关键词高亮、信息分层、动态文字

## 输出要求

严格按以下 JSON 格式输出（不要输出其他内容）：

```json
[
  {{
    "chapter_index": 0,
    "time": "0-13s",
    "scenes": [
      {{
        "time": "0-3s",
        "visual": "具体画面描述",
        "audio": "具体音频描述",
        "emotion": "情绪标记",
        "emotion_valence": 2,
        "emotion_arousal": 7,
        "retention_risk": "low",
        "risk_reason": "",
        "risk_fix": "",
        "quote": "台词原文或空字符串",
        "techniques": [
          {{
            "name": "手法名称",
            "category": "类别",
            "why": "为什么有效"
          }}
        ]
      }}
    ]
  }}
]
```

注意：
- 每个章节必须拆分为 2-5 个 scene
- scene 的时间段加起来应覆盖整个章节
- 描述要具体，不要笼统概括，基于你实际看到/听到的内容
- quote 字段只填关键台词原文，不要编造
- techniques 必须基于实际视频内容识别，不要生搬硬套
- emotion_valence 和 emotion_arousal 要反映观众在该时刻的真实情绪体验
- retention_risk 判断依据：画面单一超过15秒=medium，纯文字无变化超过20秒=high，抽象概念无类比=medium，节奏突然放慢=medium
- risk_fix 要给出可操作的具体建议（如"增加动画""插入实拍画面""压缩到10秒"等）"""


def enrich_scenes(analysis, video_info, video_url):
    """用第二次 API 调用获取 scene 级细拆，合并到 analysis 中

    Args:
        analysis: 第一步分析得到的干净 JSON（含 dimensions.narrative.timeline）
        video_info: 视频信息 dict
        video_url: 已编码的 base64 video data URL（复用，不重新编码）

    Returns:
        bool: 是否成功合并
    """
    timeline = analysis.get("dimensions", {}).get("narrative", {}).get("timeline", [])
    if not timeline:
        print("[WARN] 无 timeline 数据，跳过 scene 细拆", file=sys.stderr)
        return False

    # 构造章节描述
    chapters_desc = ""
    for i, ch in enumerate(timeline):
        chapters_desc += f"  章节{i+1}: {ch.get('time', '')} — [{ch.get('function', '')}] {ch.get('content', '')}\n"

    prompt = SCENE_ENRICHMENT_PROMPT.format(
        file_name=video_info.get("file_name", ""),
        duration=video_info.get("duration", 0),
        chapters_desc=chapters_desc,
    )

    print("[INFO] 调用豆包API获取逐场景细拆...")
    sys.stdout.flush()
    response = call_doubao_video_api(video_url, prompt)
    text = extract_text_from_response(response)
    if not text:
        print("[WARN] scene 细拆 API 返回为空", file=sys.stderr)
        return False

    scene_data = extract_json_from_text(text)
    if not isinstance(scene_data, list):
        print("[WARN] scene 细拆 JSON 解析失败或格式不符", file=sys.stderr)
        return False

    # 合并 scenes 到 timeline
    merged = 0
    for ch_data in scene_data:
        idx = ch_data.get("chapter_index", -1)
        scenes = ch_data.get("scenes", [])
        if 0 <= idx < len(timeline) and scenes:
            timeline[idx]["scenes"] = scenes
            merged += len(scenes)

    print(f"[OK] 逐场景细拆完成: {len(scene_data)} 章节, {merged} 个 scene")
    return merged > 0


# ─── 主分析流程 ────────────────────────────────────────

def analyze_video(video_path, output_path="/tmp/video-local-result.json", video_url=None):
    """分析视频（使用豆包原生视频理解）

    Args:
        video_path: 视频文件路径
        output_path: 结果保存路径
        video_url: 已编码的 base64 data URL（可选，传入则跳过编码）

    Returns:
        (final_result, video_url) 元组
    """
    video_info = get_video_info(video_path)

    print(f"[INFO] 视频: {video_info['file_name']}")
    print(f"[INFO] 时长: {video_info['duration']}s, 分辨率: {video_info['width']}x{video_info['height']}")
    print(f"[INFO] 大小: {video_info['file_size_mb']}MB")

    # 转为base64 data URL
    if video_url is None:
        video_url = video_to_base64_url(video_path)

    # 构造分析prompt
    prompt = VIDEO_ANALYSIS_PROMPT.format(
        file_name=video_info["file_name"],
        duration=video_info["duration"],
        width=video_info["width"],
        height=video_info["height"]
    )

    # 调用API
    response = call_doubao_video_api(video_url, prompt)
    text = extract_text_from_response(response)

    analysis = None
    if text:
        analysis = extract_json_from_text(text)
        if not analysis:
            # JSON解析失败，保存原始文本
            print("[WARN] JSON解析失败，保存原始文本")
            analysis = {"raw_text": text}
    else:
        print("[ERROR] API返回为空", file=sys.stderr)

    # 组装结果
    final_result = {
        "video_info": video_info,
        "analysis_method": "native_video",
        "analysis": analysis,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 分析完成，结果已保存到: {output_path}")
    return final_result, video_url


# ─── 命令行入口 ────────────────────────────────────────

def cmd_run(args):
    """一键运行：校验 -> 压缩 -> 分析（仅本地文件）"""
    if not API_KEY:
        print("[ERROR] 豆包 API Key 未配置！", file=sys.stderr)
        print("  请设置环境变量: export DOUBAO_API_KEY=\"your-api-key\"", file=sys.stderr)
        print("  获取地址: https://console.volcengine.com/ark", file=sys.stderr)
        sys.exit(1)
    if not check_ffmpeg():
        print("[ERROR] ffmpeg 未安装！请运行: brew install ffmpeg", file=sys.stderr)
        sys.exit(1)

    input_path = args.input
    output_path = args.output or "/tmp/video-local-result.json"
    target_mb = args.target_size

    print("=" * 55)
    print("  本地视频爆款拆解分析 v2 (豆包原生视频理解)")
    print("=" * 55)

    # Step 1: 校验本地文件
    video_path = validate_local_video(input_path)
    print(f"\n[Step 1/4] 使用本地视频: {os.path.basename(video_path)}")

    # Step 2: 压缩
    print(f"\n[Step 2/4] 视频压缩")
    compressed_path = compress_video(video_path, target_mb=target_mb)

    # Step 3: 8 维度分析
    print(f"\n[Step 3/4] AI 8维度分析")
    result, video_url = analyze_video(compressed_path, output_path)

    # 存储视频标题（优先用 --title 参数，其次从文件名推断）
    if hasattr(args, 'title') and args.title:
        result.setdefault("video_info", {})["title"] = args.title

    # Step 3.5: 逐场景细拆（复用已编码的 base64 视频）
    print(f"\n[Step 3.5/4] AI 逐场景细拆")
    try:
        from report_generator import unwrap_analysis_data
        analysis, video_info = unwrap_analysis_data(result)
        if analysis and "overall_score" in analysis:
            ok = enrich_scenes(analysis, video_info, video_url)
            if ok:
                # 回写增强后的 analysis 到 result 并保存
                result["analysis"] = analysis
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"[OK] 增强结果已保存: {output_path}")
            else:
                print("[WARN] scene 细拆未成功，报告将使用章节级数据")
        else:
            print("[WARN] 主分析数据不完整，跳过 scene 细拆")
    except Exception as e:
        print(f"[WARN] scene 细拆失败: {e}", file=sys.stderr)

    # Step 4: 生成 HTML 报告
    print(f"\n[Step 4/4] 生成 HTML 可视化报告")
    archive_dir = getattr(args, 'archive_dir', None) if args else None
    video_title = result.get("video_info", {}).get("title", "")
    try:
        from report_generator import generate_report
        report_path = generate_report(
            result_json=result,
            video_path=video_path,
            output_dir=os.path.dirname(video_path) if video_path else None,
            title=video_title,
            archive_dir=archive_dir,
        )
        if report_path:
            print(f"  报告文件: {report_path}")
    except Exception as e:
        print(f"[WARN] HTML 报告生成失败: {e}", file=sys.stderr)
        import traceback; traceback.print_exc()
        report_path = None

    print("\n" + "=" * 55)
    print("  分析完成!")
    print("=" * 55)
    print(f"  结果文件: {output_path}")
    if report_path:
        print(f"  HTML报告: {report_path}")

    return result


def cmd_compress(args):
    """压缩子命令"""
    if not check_ffmpeg():
        print("[ERROR] ffmpeg 未安装！请运行: brew install ffmpeg", file=sys.stderr)
        sys.exit(1)
    validate_local_video(args.input)
    compress_video(args.input, args.output, args.target_size)


def cmd_analyze(args):
    """直接分析本地视频（不压缩）"""
    if not API_KEY:
        print("[ERROR] 豆包 API Key 未配置！", file=sys.stderr)
        print("  请设置环境变量: export DOUBAO_API_KEY=\"your-api-key\"", file=sys.stderr)
        print("  获取地址: https://console.volcengine.com/ark", file=sys.stderr)
        sys.exit(1)
    if not check_ffmpeg():
        print("[ERROR] ffmpeg 未安装！请运行: brew install ffmpeg", file=sys.stderr)
        sys.exit(1)
    validate_local_video(args.input)
    analyze_video(args.input, args.output)


def cmd_report(args):
    """从已有 JSON 结果重新生成 HTML 报告"""
    result_path = args.result
    if not os.path.exists(result_path):
        print(f"[ERROR] 结果文件不存在: {result_path}", file=sys.stderr)
        sys.exit(1)

    video_path = args.video
    if video_path and not os.path.exists(video_path):
        print(f"[WARN] 视频文件不存在: {video_path}，将跳过截图和播放器", file=sys.stderr)
        video_path = None

    from report_generator import generate_report
    report_path = generate_report(
        result_json=result_path,
        video_path=video_path,
        output_dir=args.output_dir,
        title=getattr(args, 'title', None),
        archive_dir=getattr(args, 'archive_dir', None),
    )
    if report_path:
        print(f"\n用浏览器打开查看: file://{report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="本地视频爆款拆解分析工具 v2 (豆包原生视频理解) - 仅支持本地文件"
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # run 子命令（主入口：校验+压缩+分析）
    p_run = subparsers.add_parser("run", help="一键分析（仅支持本地文件）")
    p_run.add_argument("input", help="本地视频文件路径")
    p_run.add_argument("--output", default=None, help="分析结果输出路径")
    p_run.add_argument("--target-size", type=int, default=TARGET_SIZE_MB,
                        help=f"压缩目标大小(MB)，默认{TARGET_SIZE_MB}")
    p_run.add_argument("--title", default=None, help="视频标题（用于归档目录命名）")
    p_run.add_argument("--archive-dir", default=None,
                        help="归档根目录。指定后报告自动保存到 '日期_标题' 子目录，并生成 index.html 汇总页")
    p_run.add_argument("--video-url", default=None,
                        help="视频的公网URL（用于 report-lite.html 引用视频）")

    # compress 子命令
    p_compress = subparsers.add_parser("compress", help="仅压缩视频")
    p_compress.add_argument("input", help="视频文件路径")
    p_compress.add_argument("--target-size", type=int, default=TARGET_SIZE_MB,
                            help=f"目标大小(MB)，默认{TARGET_SIZE_MB}")
    p_compress.add_argument("--output", default=None, help="输出路径")

    # analyze 子命令（直接分析本地视频）
    p_analyze = subparsers.add_parser("analyze", help="仅分析视频（不压缩）")
    p_analyze.add_argument("input", help="视频文件路径")
    p_analyze.add_argument("--output", default="/tmp/video-local-result.json",
                           help="分析结果输出路径")

    # report 子命令（从已有 JSON 重新生成 HTML 报告）
    p_report = subparsers.add_parser("report", help="从已有分析结果生成 HTML 报告")
    p_report.add_argument("--result", required=True, help="分析结果 JSON 文件路径")
    p_report.add_argument("--video", default=None, help="原始视频路径（用于截图和播放器）")
    p_report.add_argument("--output-dir", default=None, help="报告输出目录")
    p_report.add_argument("--title", default=None, help="视频标题（用于归档目录命名）")
    p_report.add_argument("--archive-dir", default=None, help="归档根目录")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "compress":
        cmd_compress(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
