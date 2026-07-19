#!/usr/bin/env python3
"""
爆款视频拆解 — HTML 可视化报告生成器 v3
- 从分析结果 JSON 生成自包含 HTML 报告
- 包含截图时间线、雷达图、视频同步解读面板
- v3: 情绪弧线、留存风险、爆款公式、算法适配、学习路径
- 纯标准库，无额外 pip 依赖
"""

import argparse
import base64
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from string import Template

# ─── 归档 & 汇总页 ───────────────────────────────────

def make_archive_subdir(archive_dir, title, date_str=None):
    """在 archive_dir 下创建 '日期_标题' 子目录，返回子目录路径。
    目录名仅使用 ASCII 字符，避免 URL 编码问题。"""
    import time, hashlib
    if date_str is None:
        date_str = time.strftime("%Y-%m-%d")
    raw_title = (title or "untitled").strip()
    # 转为 ASCII 安全的 slug：保留字母数字，其余替换为 -
    slug = re.sub(r'[^a-zA-Z0-9]', '-', raw_title)
    slug = re.sub(r'-+', '-', slug).strip('-')[:40]
    if not slug:
        # 纯中文标题会得到空slug，用标题hash代替
        slug = hashlib.md5(raw_title.encode()).hexdigest()[:12]
    dir_name = f"{date_str}_{slug}"
    sub_dir = os.path.join(archive_dir, dir_name)
    os.makedirs(sub_dir, exist_ok=True)
    return sub_dir


def generate_index_html(archive_dir):
    """扫描 archive_dir 下所有子目录中的 report.html，生成汇总 index.html"""
    entries = []
    for item in sorted(os.listdir(archive_dir), reverse=True):
        sub = os.path.join(archive_dir, item)
        report_file = os.path.join(sub, "report.html")
        meta_file = os.path.join(sub, "meta.json")
        if not os.path.isdir(sub) or not os.path.exists(report_file):
            continue
        # 读取 meta.json（如果有）
        meta = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                pass
        title = meta.get("title", item)
        score = meta.get("overall_score", "?")
        duration = meta.get("duration", "?")
        resolution = meta.get("resolution", "?")
        date_str = meta.get("date", item[:10] if len(item) >= 10 else "?")
        summary = meta.get("summary", "")[:80]
        # 读取截图缩略图（如果 meta 里有 thumbnail base64）
        thumb = meta.get("thumbnail", "")
        entries.append({
            "dir_name": item,
            "title": title,
            "score": score,
            "duration": duration,
            "resolution": resolution,
            "date": date_str,
            "summary": summary,
            "thumbnail": thumb,
        })

    # 生成 HTML
    cards_html = ""
    abs_archive = os.path.abspath(archive_dir)
    for e in entries:
        score_val = _safe_num(e["score"], 0)
        score_color = _score_color(score_val)
        thumb_html = ""
        if e["thumbnail"]:
            thumb_html = f'<img src="{e["thumbnail"]}" class="card-thumb">'
        else:
            thumb_html = '<div class="card-thumb-placeholder">&#x1f3ac;</div>'
        # 使用绝对 file:// 路径，避免在应用内预览时相对路径被路由器拦截导致 404
        abs_report = os.path.join(abs_archive, e["dir_name"], "report.html")
        report_url = f"file://{abs_report}"
        cards_html += f'''
        <a href="{report_url}" class="report-card">
            <div class="card-thumb-wrap">{thumb_html}
                <div class="card-score" style="background:{score_color}">{e["score"]}</div>
            </div>
            <div class="card-body">
                <div class="card-title">{e["title"]}</div>
                <div class="card-meta">{e["date"]} &middot; {e["duration"]}s &middot; {e["resolution"]}</div>
                <div class="card-summary">{e["summary"]}</div>
            </div>
        </a>'''

    index_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>爆款视频拆解 — 报告汇总</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
background:#0d1117;color:#c9d1d9;min-height:100vh;padding:30px 20px}}
h1{{text-align:center;font-size:28px;color:#e6edf3;margin-bottom:8px}}
.subtitle{{text-align:center;color:#8b949e;font-size:14px;margin-bottom:30px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px;
max-width:1200px;margin:0 auto}}
.report-card{{display:block;text-decoration:none;color:inherit;
background:#161b22;border:1px solid #30363d;border-radius:12px;
overflow:hidden;transition:all .2s ease}}
.report-card:hover{{border-color:#58a6ff;transform:translateY(-2px);
box-shadow:0 8px 24px rgba(0,0,0,.4)}}
.card-thumb-wrap{{position:relative;width:100%;aspect-ratio:16/9;background:#21262d;overflow:hidden}}
.card-thumb{{width:100%;height:100%;object-fit:cover}}
.card-thumb-placeholder{{width:100%;height:100%;display:flex;align-items:center;
justify-content:center;font-size:48px;color:#30363d}}
.card-score{{position:absolute;top:10px;right:10px;
padding:4px 10px;border-radius:6px;font-size:16px;font-weight:700;color:#fff}}
.card-body{{padding:14px 16px}}
.card-title{{font-size:16px;font-weight:600;color:#e6edf3;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.card-meta{{font-size:12px;color:#8b949e;margin-top:4px}}
.card-summary{{font-size:13px;color:#8b949e;margin-top:6px;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.empty{{text-align:center;color:#8b949e;padding:60px 0;font-size:16px}}
</style>
</head>
<body>
<h1>爆款视频拆解报告</h1>
<div class="subtitle">共 {len(entries)} 份分析报告</div>
<div class="grid">
{cards_html if cards_html else '<div class="empty">暂无报告，运行 /video-optimize 分析视频后自动归档到此处</div>'}
</div>
</body>
</html>'''

    index_path = os.path.join(archive_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    return index_path


# ─── 数据解析 ─────────────────────────────────────────

def unwrap_analysis_data(result):
    """从 result JSON 中提取干净的分析数据（处理 API 响应嵌套格式）"""
    if not result:
        return None, {}

    video_info = result.get("video_info", {})
    analysis = result.get("analysis", {})

    # 如果 analysis 已经包含 overall_score，说明已是干净数据
    if "overall_score" in analysis:
        return analysis, video_info

    # 嵌套格式：analysis 是 API 原始响应，需要从 output 中提取
    output = analysis.get("output", [])
    if isinstance(output, list):
        for block in output:
            if block.get("type") == "message":
                content = block.get("content", [])
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "output_text":
                        text = item.get("text", "")
                        parsed = _extract_json_from_text(text)
                        if parsed and "overall_score" in parsed:
                            return parsed, video_info

    # 兼容 dict output
    if isinstance(output, dict):
        content = output.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "output_text":
                    text = item.get("text", "")
                    parsed = _extract_json_from_text(text)
                    if parsed and "overall_score" in parsed:
                        return parsed, video_info

    return analysis, video_info


def _extract_json_from_text(text):
    """从文本中提取 JSON（支持 ```json 代码块）"""
    if not text:
        return None
    m = re.search(r'```json\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    start = text.find('{')
    if start >= 0:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        pass
                    break
    return None


def parse_time_range(s):
    """解析时间描述 → (start_sec, end_sec)
    支持: '0-13s', '524-541秒', '第110秒...', '0:14-1:29'
    """
    if not s:
        return (0, 0)
    s = str(s).strip()

    # '0:14-1:29' 格式
    mm_ss = re.findall(r'(\d+):(\d+)', s)
    if len(mm_ss) >= 2:
        start = int(mm_ss[0][0]) * 60 + int(mm_ss[0][1])
        end = int(mm_ss[1][0]) * 60 + int(mm_ss[1][1])
        return (start, end)

    # '0-13s' / '524-541秒' / '14-89s'
    m = re.match(r'(\d+)\s*[-–~]\s*(\d+)', s)
    if m:
        return (int(m.group(1)), int(m.group(2)))

    # '第110秒' / '110秒'
    m = re.search(r'第?(\d+)\s*秒?', s)
    if m:
        t = int(m.group(1))
        return (t, t + 5)

    # 纯数字
    m = re.match(r'(\d+)', s)
    if m:
        t = int(m.group(1))
        return (t, t)

    return (0, 0)


def extract_screenshot_timestamps(analysis, duration):
    """从分析数据中提取截图时间点，返回 (sorted_timestamps, reasons_dict)
    reasons_dict: {timestamp: reason_string}
    """
    # {timestamp: reason} — 同一时间戳只保留第一个 reason
    ts_reasons = {}

    def _add(t, reason):
        t = int(t)
        if 0 < t < duration and t not in ts_reasons:
            ts_reasons[t] = reason

    dims = analysis.get("dimensions", {})

    # 从 narrative.timeline 提取（含 scenes 子层）
    timeline = dims.get("narrative", {}).get("timeline", [])
    for entry in timeline:
        start, end = parse_time_range(entry.get("time", ""))
        func = entry.get("function", "")
        if start > 0:
            _add(start, f"{func} - 章节起始")
        mid = (start + end) // 2
        if mid > 0 and mid != start:
            _add(mid, f"{func} - 中段")
        # 从 scenes 子层提取
        for scene in entry.get("scenes", []):
            s, e = parse_time_range(scene.get("time", ""))
            if s > 0:
                emotion = scene.get("emotion", "")
                visual = scene.get("visual", "")
                reason = emotion
                if visual:
                    reason += f" - {visual[:25]}"
                _add(s, reason or func)

    # 从 pacing.cut_points 提取
    for cp in dims.get("pacing", {}).get("cut_points", []):
        m = re.search(r'第?(\d+)\s*秒?', str(cp))
        if m:
            _add(int(m.group(1)), "节奏切换点")

    # 从 cta_time 提取
    cta_time = dims.get("cta", {}).get("cta_time", "")
    start, _ = parse_time_range(cta_time)
    if start > 0:
        _add(start, "CTA互动引导出现")

    # v3: 从情绪弧线 turning_points 提取
    emotional_arc = analysis.get("emotional_arc", {})
    for tp in emotional_arc.get("turning_points", []):
        tp_time = tp.get("time", "")
        m = re.match(r'(\d+):(\d+)', tp_time)
        if m:
            sec = int(m.group(1)) * 60 + int(m.group(2))
            desc = tp.get("description", "")[:30]
            _add(sec, f"{tp.get('type', '转折')} - {desc}")

    # v3: 从留存风险 high risk segments 提取
    retention = analysis.get("retention_prediction", {})
    for seg in retention.get("risk_segments", []):
        if seg.get("risk") == "high":
            seg_start, _ = parse_time_range(seg.get("time", ""))
            if seg_start > 0:
                label = seg.get("label", "")[:20]
                _add(seg_start, f"高风险留存 - {label}")

    # 确保有开头和接近结尾
    _add(1, "视频起始")
    if duration > 10:
        _add(max(1, int(duration) - 5), "视频尾声")

    # 过滤有效范围并排序
    valid = sorted(ts_reasons.keys())

    # 限制数量（最多 12 张截图）
    if len(valid) > 12:
        step = len(valid) / 12
        valid = [valid[int(i * step)] for i in range(12)]

    reasons = {t: ts_reasons[t] for t in valid}
    return valid, reasons


def extract_screenshots(video_path, timestamps):
    """从视频中提取截图，返回 {timestamp: base64_data_url}"""
    screenshots = {}
    if not video_path or not os.path.exists(video_path):
        return screenshots

    for t in timestamps:
        try:
            cmd = [
                "ffmpeg", "-ss", str(t), "-i", video_path,
                "-frames:v", "1", "-vf", "scale=640:-1",
                "-q:v", "3", "-f", "image2pipe",
                "-vcodec", "mjpeg", "pipe:1"
            ]
            result = subprocess.run(
                cmd, capture_output=True, timeout=10
            )
            if result.returncode == 0 and result.stdout:
                b64 = base64.b64encode(result.stdout).decode("utf-8")
                screenshots[t] = f"data:image/jpeg;base64,{b64}"
        except Exception:
            pass

    return screenshots


def extract_dimension_scores(analysis):
    """提取 8 维度评分为有序列表 [(key, label, score, description)]"""
    dims = analysis.get("dimensions", {})
    order = [
        ("hook", "开头吸引力"),
        ("narrative", "叙事结构"),
        ("pacing", "节奏感"),
        ("visual", "视觉效果"),
        ("text_overlay", "字幕设计"),
        ("audio", "音乐音效"),
        ("cta", "互动引导"),
        ("ending", "结尾设计"),
    ]
    result = []
    for key, label in order:
        d = dims.get(key, {})
        score = _safe_num(d.get("score", 0))
        desc = d.get("description", "")
        result.append((key, label, score, desc))
    return result


# ─── WebVTT 生成 ──────────────────────────────────────

def _seconds_to_vtt_time(sec):
    """秒数 → VTT 时间格式 HH:MM:SS.mmm"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def generate_webvtt(analysis):
    """生成 WebVTT metadata track 内容（优先按 scene 粒度，回退到 chapter 粒度）"""
    timeline = analysis.get("dimensions", {}).get("narrative", {}).get("timeline", [])
    if not timeline:
        return ""

    lines = ["WEBVTT", ""]
    cue_idx = 0

    for i, entry in enumerate(timeline):
        scenes = entry.get("scenes", [])
        if scenes:
            for j, scene in enumerate(scenes):
                start, end = parse_time_range(scene.get("time", ""))
                payload = json.dumps({
                    "chapter_index": i,
                    "scene_index": j,
                    "visual": scene.get("visual", ""),
                    "audio": scene.get("audio", ""),
                    "emotion": scene.get("emotion", ""),
                    "quote": scene.get("quote", ""),
                }, ensure_ascii=False)
                cue_idx += 1
                lines.append(f"cue-{cue_idx}")
                lines.append(f"{_seconds_to_vtt_time(start)} --> {_seconds_to_vtt_time(end)}")
                lines.append(payload)
                lines.append("")
        else:
            start, end = parse_time_range(entry.get("time", ""))
            func = entry.get("function", "")
            content = entry.get("content", "")
            payload = json.dumps(
                {"chapter_index": i, "scene_index": -1,
                 "function": func, "content": content},
                ensure_ascii=False
            )
            cue_idx += 1
            lines.append(f"cue-{cue_idx}")
            lines.append(f"{_seconds_to_vtt_time(start)} --> {_seconds_to_vtt_time(end)}")
            lines.append(payload)
            lines.append("")

    vtt_text = "\n".join(lines)
    b64 = base64.b64encode(vtt_text.encode("utf-8")).decode("utf-8")
    return f"data:text/vtt;base64,{b64}"


# ─── HTML 片段构建 ─────────────────────────────────────

def _fmt_time(sec):
    """秒数 → 人类可读时间 M:SS"""
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m}:{s:02d}"


def _safe_num(val, default=0):
    """安全地将值转换为数字（处理模型返回字符串类型的评分）"""
    if isinstance(val, (int, float)):
        return val
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _score_color(val, max_val=10):
    """分数 → 颜色"""
    val = _safe_num(val)
    ratio = val / max_val if max_val > 0 else 0
    if ratio >= 0.8:
        return "#4caf50"
    elif ratio >= 0.6:
        return "#ff9800"
    return "#f44336"


def build_timeline_markers(analysis, screenshots, duration, reasons=None):
    """生成截图时间线 HTML（每张截图带 reason 说明）"""
    if reasons is None:
        reasons = {}
    if not screenshots:
        return ""

    # 按时间戳排序所有截图
    sorted_ts = sorted(screenshots.keys())
    total = len(sorted_ts)
    if total == 0:
        return ""

    # 为每个截图匹配最近的 timeline 章节 function
    timeline = analysis.get("dimensions", {}).get("narrative", {}).get("timeline", [])
    chapter_ranges = []
    for entry in timeline:
        start, end = parse_time_range(entry.get("time", ""))
        chapter_ranges.append((start, end, entry.get("function", "")))

    def _find_chapter_func(t):
        for cs, ce, cf in chapter_ranges:
            if cs <= t <= ce:
                return cf
        return ""

    items = []

    for idx, t in enumerate(sorted_ts):
        func = _find_chapter_func(t)
        reason = reasons.get(t, "")
        img_html = f'<img src="{screenshots[t]}" alt="{func}" loading="lazy">'

        reason_html = ""
        if reason:
            reason_html = f'<div class="tl-reason">{reason}</div>'

        items.append(f'''
        <div class="tl-item" style="flex:1;min-width:120px"
             onclick="seekTo({t})" title="{_fmt_time(t)} {func}\n{reason}">
            {img_html}
            <div class="tl-label">{_fmt_time(t)} {func}</div>
            {reason_html}
        </div>''')

    return "\n".join(items)


def _technique_category_class(category):
    """爆款手法类别 → CSS class"""
    mapping = {
        "Hook": "tech-hook",
        "hook": "tech-hook",
        "留存": "tech-retain",
        "节奏": "tech-pace",
        "情绪": "tech-emo",
        "信任": "tech-trust",
        "互动": "tech-interact",
        "视觉": "tech-vis",
    }
    return mapping.get(category, "tech-default")


def build_commentary_entries(analysis):
    """生成解读面板条目 HTML（支持 chapter + scenes 两级）"""
    timeline = analysis.get("dimensions", {}).get("narrative", {}).get("timeline", [])
    if not timeline:
        return "<p>暂无时间线数据</p>"

    items = []
    scene_global_idx = 0

    for i, entry in enumerate(timeline):
        start, end = parse_time_range(entry.get("time", ""))
        func = entry.get("function", "")
        content = entry.get("content", "")
        scenes = entry.get("scenes", [])

        if scenes:
            scene_html_parts = []
            for j, scene in enumerate(scenes):
                s_start, s_end = parse_time_range(scene.get("time", ""))
                visual = scene.get("visual", "")
                audio = scene.get("audio", "")
                emotion = scene.get("emotion", "")
                quote = scene.get("quote", "")

                quote_html = ""
                if quote:
                    quote_html = f'<div class="sc-row"><span class="sc-tag sc-quote">台词</span><span class="sc-val sc-quote-text">{quote}</span></div>'

                techniques = scene.get("techniques", [])
                tech_html = ""
                if techniques:
                    tags = []
                    tips = []
                    for tech in techniques:
                        name = tech.get("name", "")
                        cat = tech.get("category", "")
                        why = tech.get("why", "")
                        cat_cls = _technique_category_class(cat)
                        tags.append(f'<span class="tech-tag {cat_cls}">{name}<span class="tech-cat">{cat}</span></span>')
                        if why:
                            tips.append(f'<div class="tech-why">{why}</div>')
                    tech_html = f'<div class="sc-techniques">{"".join(tags)}</div>'
                    if tips:
                        tech_html += f'<div class="sc-tech-tips">{"".join(tips)}</div>'

                # Retention risk indicator
                risk = scene.get("retention_risk", "")
                risk_html = ""
                if risk in ("medium", "high"):
                    risk_cls = "risk-high" if risk == "high" else "risk-med"
                    risk_label = "高风险" if risk == "high" else "中风险"
                    risk_html = f'<span class="sc-risk {risk_cls}">{risk_label}</span>'

                scene_html_parts.append(f'''
                <div class="cmt-scene" id="scene-{i}-{j}" data-start="{s_start}" data-end="{s_end}"
                     onclick="event.stopPropagation();seekTo({s_start})">
                    <div class="sc-time">{_fmt_time(s_start)}-{_fmt_time(s_end)} {risk_html}</div>
                    <div class="sc-row"><span class="sc-tag sc-visual">画面</span><span class="sc-val">{visual}</span></div>
                    <div class="sc-row"><span class="sc-tag sc-audio">音频</span><span class="sc-val">{audio}</span></div>
                    <div class="sc-row"><span class="sc-tag sc-emotion">情绪</span><span class="sc-val">{emotion}</span></div>
                    {quote_html}
                    {tech_html}
                </div>''')
                scene_global_idx += 1

            scenes_joined = "\n".join(scene_html_parts)
            items.append(f'''
            <div class="cmt-chapter" id="cmt-ch-{i}" data-start="{start}" data-end="{end}">
                <div class="cmt-ch-header" onclick="toggleChapter(this.parentElement);seekTo({start})">
                    <span class="cmt-toggle">&#9660;</span>
                    <span class="cmt-time">{_fmt_time(start)}-{_fmt_time(end)}</span>
                    <span class="cmt-func">[{func}]</span>
                </div>
                <div class="cmt-ch-summary">{content}</div>
                <div class="cmt-scenes">{scenes_joined}</div>
            </div>''')
        else:
            items.append(f'''
            <div class="cmt-entry" id="cmt-{i}" data-start="{start}" data-end="{end}"
                 onclick="seekTo({start})">
                <div class="cmt-time">{_fmt_time(start)}-{_fmt_time(end)}</div>
                <div class="cmt-func">[{func}]</div>
                <div class="cmt-text">{content}</div>
            </div>''')

    return "\n".join(items)


def build_dimension_cards(analysis, screenshots):
    """生成 8 维度详细分析卡片 HTML"""
    scores = extract_dimension_scores(analysis)
    dims = analysis.get("dimensions", {})
    cards = []

    extra_fields = {
        "hook": lambda d: f'<p><b>开场公式：</b>{d.get("formula", "")}</p><p><b>话术模板：</b>{d.get("template", "")}</p>',
        "narrative": lambda d: f'<p><b>叙事类型：</b>{d.get("type", "")}</p><p><b>结构公式：</b>{d.get("template", "")}</p>',
        "pacing": lambda d: f'<p><b>节奏模式：</b>{d.get("pattern", "")}</p>',
        "visual": lambda d: f'<p><b>色彩风格：</b>{d.get("color_style", "")}</p>',
        "text_overlay": lambda d: f'<p><b>字幕风格：</b>{d.get("style", "")}</p>',
        "audio": lambda d: f'<p><b>BPM：</b>{d.get("estimated_bpm", "")}</p><p><b>人声风格：</b>{d.get("voice_style", "")}</p>',
        "cta": lambda d: f'<p><b>CTA时间：</b>{d.get("cta_time", "")}</p><p><b>CTA类型：</b>{d.get("cta_type", "")}</p>',
        "ending": lambda d: f'<p><b>结尾类型：</b>{d.get("ending_type", "")}</p><p><b>可循环：</b>{"是" if d.get("is_loopable") else "否"}</p>',
    }

    for key, label, score, desc in scores:
        d = dims.get(key, {})
        extra = extra_fields.get(key, lambda _: "")(d)
        color = _score_color(score)

        cards.append(f'''
        <div class="dim-card">
            <div class="dim-header">
                <span class="dim-label">{label}</span>
                <span class="dim-score" style="color:{color}">{score}/10</span>
            </div>
            <div class="dim-bar-bg"><div class="dim-bar" style="width:{score * 10}%;background:{color}"></div></div>
            <p class="dim-desc">{desc}</p>
            {extra}
        </div>''')

    return "\n".join(cards)


def build_template_section(analysis):
    """生成可复制模板 HTML"""
    tpl = analysis.get("replicable_template", {})
    if not tpl:
        return ""

    structure = tpl.get("structure", "")
    script = tpl.get("script_template", "")
    shot_list = tpl.get("shot_list", [])

    shot_rows = ""
    for s in shot_list:
        shot_rows += f'''<tr>
            <td>{s.get("shot", "")}</td>
            <td>{s.get("time", "")}</td>
            <td>{s.get("type", "")}</td>
            <td>{s.get("content", "")}</td>
            <td>{s.get("text", "")}</td>
        </tr>'''

    return f'''
    <div class="section">
        <h2>可复制模板</h2>
        <div class="tpl-box">
            <h3>结构公式</h3>
            <div class="tpl-formula">{structure}</div>
        </div>
        <div class="tpl-box">
            <h3>拍摄清单</h3>
            <table class="shot-table">
                <thead><tr><th>镜号</th><th>时间</th><th>景别</th><th>内容</th><th>文字</th></tr></thead>
                <tbody>{shot_rows}</tbody>
            </table>
        </div>
        <div class="tpl-box">
            <h3>文案模板</h3>
            <div class="tpl-script">{script}</div>
        </div>
    </div>'''


def build_suggestions(analysis):
    """生成 TOP 3 亮点 + TOP 3 改进 HTML"""
    strengths = analysis.get("top3_strengths", [])
    improvements = analysis.get("top3_improvements", [])

    s_items = "".join(f'<li class="strength-item">{s}</li>' for s in strengths)
    i_items = "".join(f'<li class="improve-item">{s}</li>' for s in improvements)

    return f'''
    <div class="section suggestions">
        <div class="sug-col">
            <h3>TOP 3 亮点</h3>
            <ol>{s_items}</ol>
        </div>
        <div class="sug-col">
            <h3>TOP 3 改进建议</h3>
            <ol>{i_items}</ol>
        </div>
    </div>'''



# ─── v3 新模块: 情绪弧线数据 ──────────────────────────

def build_emotion_arc_data(analysis):
    """提取情绪弧线数据（优先用 emotional_arc，回退从 scenes 合成）"""
    arc = analysis.get("emotional_arc", {})
    if arc and arc.get("curve_points"):
        return arc

    # 从 scenes 的 emotion_valence/emotion_arousal 合成
    timeline = analysis.get("dimensions", {}).get("narrative", {}).get("timeline", [])
    curve_points = []
    for entry in timeline:
        for scene in entry.get("scenes", []):
            valence = scene.get("emotion_valence")
            arousal = scene.get("emotion_arousal")
            if valence is not None and arousal is not None:
                s, _ = parse_time_range(scene.get("time", ""))
                curve_points.append({
                    "time": _fmt_time(s),
                    "valence": _safe_num(valence),
                    "arousal": _safe_num(arousal),
                    "label": scene.get("emotion", ""),
                })
    if not curve_points:
        return {}

    return {
        "arc_type": arc.get("arc_type", ""),
        "arc_description": arc.get("arc_description", ""),
        "curve_points": curve_points,
        "turning_points": arc.get("turning_points", []),
    }


# ─── v3 新模块: 留存风险数据 ──────────────────────────

def build_retention_data(analysis, duration):
    """提取留存风险数据（优先用 retention_prediction，回退从 scenes 合成）"""
    ret = analysis.get("retention_prediction", {})

    # 基础统计
    stats = {
        "hook_rate_3s": _safe_num(ret.get("hook_rate_3s", 0)),
        "retention_30s": _safe_num(ret.get("retention_30s", 0)),
        "midpoint_retention": _safe_num(ret.get("midpoint_retention", 0)),
        "completion_rate": _safe_num(ret.get("completion_rate", 0)),
    }
    risk_segments = ret.get("risk_segments", [])

    # 从 scenes 合成 heatbar segments
    heatbar = []
    timeline = analysis.get("dimensions", {}).get("narrative", {}).get("timeline", [])
    for entry in timeline:
        scenes = entry.get("scenes", [])
        if scenes:
            for scene in scenes:
                s, e = parse_time_range(scene.get("time", ""))
                risk = scene.get("retention_risk", "low")
                heatbar.append({
                    "start": s, "end": e,
                    "risk": risk,
                    "reason": scene.get("risk_reason", ""),
                    "fix": scene.get("risk_fix", ""),
                })
        else:
            s, e = parse_time_range(entry.get("time", ""))
            heatbar.append({
                "start": s, "end": e,
                "risk": "low",
                "reason": "",
                "fix": "",
            })

    # 构建风险详情 HTML
    risk_cards_html = ""
    # 优先用 retention_prediction.risk_segments，没有的话从 heatbar 中提取
    details = risk_segments if risk_segments else [
        seg for seg in heatbar if seg.get("risk") in ("medium", "high")
    ]
    for seg in details:
        if isinstance(seg, dict):
            t = seg.get("time", "")
            if not t and "start" in seg:
                t = f"{_fmt_time(seg['start'])}-{_fmt_time(seg['end'])}"
            risk = seg.get("risk", "medium")
            border_color = "#f44336" if risk == "high" else "#ff9800"
            risk_label = "高风险" if risk == "high" else "中风险"
            risk_bg = "rgba(244,67,54,0.2)" if risk == "high" else "rgba(255,152,0,0.2)"
            risk_color = "#f44336" if risk == "high" else "#ff9800"
            reason = seg.get("reason", "")
            fix = seg.get("fix", "")
            fix_html = f'<div class="risk-fix">{fix}</div>' if fix else ""
            label = seg.get("label", "")
            risk_cards_html += f'''
            <div class="risk-card" style="border-color:{border_color}">
                <div>
                    <div class="risk-time">{t}</div>
                    <span class="risk-level" style="background:{risk_bg};color:{risk_color}">{risk_label}</span>
                </div>
                <div>
                    <div class="risk-reason">{reason}</div>
                    {fix_html}
                </div>
            </div>'''

    return {
        "stats": stats,
        "heatbar": heatbar,
        "risk_cards_html": risk_cards_html,
        "has_data": bool(stats.get("hook_rate_3s") or heatbar),
    }


# ─── v3 新模块: 爆款公式 ──────────────────────────────

def build_formula_section(analysis):
    """生成爆款公式提取 HTML"""
    vf = analysis.get("viral_formulas", {})
    if not vf:
        return ""

    parts = []

    # 脚本公式
    sf = vf.get("script_formula", {})
    if sf and sf.get("steps"):
        steps_html = ""
        for i, step in enumerate(sf["steps"]):
            arrow = '<div class="flow-arrow">&rarr;</div>' if i < len(sf["steps"]) - 1 else ""
            steps_html += f'''
            <div class="flow-step">
                <div class="step-time">{step.get("time", "")}</div>
                <div class="step-name">{step.get("name", "")}</div>
                <div class="step-desc">{step.get("desc", "")}</div>
            </div>{arrow}'''

        fill_tpl = sf.get("fill_template", "")
        # 把 ____ 转为高亮 span
        fill_tpl_html = re.sub(r'_{3,}([^_]*?)_{0,3}', r'<span class="blank">\1</span>', fill_tpl)
        fill_tpl_html = fill_tpl_html.replace("\n", "<br>")

        fill_section = ""
        if fill_tpl:
            fill_section = f'''
            <div class="fill-template">
                <div class="tpl-title">一键填空模板</div>
                <div class="tpl-line">{fill_tpl_html}</div>
            </div>'''

        parts.append(f'''
        <div class="formula-card">
            <div class="formula-card-header">
                <div class="formula-icon" style="background:linear-gradient(135deg,#5c6bc0,#3949ab)">&#x1f4dd;</div>
                <div><h3>脚本公式</h3><div class="formula-desc">视频的叙事骨架，可直接套用到同类选题</div></div>
            </div>
            <div class="formula-card-body">
                <div class="script-flow">{steps_html}</div>
                {fill_section}
            </div>
        </div>''')

    # 情绪公式
    ef = vf.get("emotion_formula", {})
    if ef and ef.get("nodes"):
        nodes_html = ""
        for i, node in enumerate(ef["nodes"]):
            v = _safe_num(node.get("valence", 0))
            if v >= 2:
                bg, fg = "rgba(76,175,80,0.2)", "#4caf50"
            elif v >= 0:
                bg, fg = "rgba(100,181,246,0.2)", "#64b5f6"
            elif v >= -2:
                bg, fg = "rgba(255,152,0,0.2)", "#ff9800"
            else:
                bg, fg = "rgba(244,67,54,0.2)", "#f44336"
            arrow = '<span class="emo-arrow">&rarr;</span>' if i < len(ef["nodes"]) - 1 else ""
            nodes_html += f'<div class="emotion-node" style="background:{bg};color:{fg}">{node.get("emotion", "")} <span class="emo-val">{int(v):+d}</span></div>{arrow}'

        principles = ef.get("key_principles", [])
        principles_html = ""
        if principles:
            lines = "<br>".join(f"<b style='color:#ccc'>{p.split('：')[0]}：</b>{p.split('：', 1)[1] if '：' in p else p}" if '：' in p else p for p in principles)
            principles_html = f'''
            <div class="fill-template" style="background:rgba(239,83,80,0.06)">
                <div class="tpl-title" style="color:#ef5350">情绪编排要点</div>
                <div class="tpl-line" style="font-size:12px;color:#bbb">{lines}</div>
            </div>'''

        parts.append(f'''
        <div class="formula-card">
            <div class="formula-card-header">
                <div class="formula-icon" style="background:linear-gradient(135deg,#ef5350,#c62828)">&#x1f3ad;</div>
                <div><h3>情绪公式</h3><div class="formula-desc">观众情绪编排路径，驱动完播和互动的核心引擎</div></div>
            </div>
            <div class="formula-card-body">
                <div class="emotion-flow">{nodes_html}</div>
                {principles_html}
            </div>
        </div>''')

    # 算法公式
    af = vf.get("algorithm_formula", {})
    if af and af.get("drivers"):
        pills_html = ""
        for d in af["drivers"]:
            icon = d.get("icon", "")
            pills_html += f'''
            <div class="algo-pill">
                <div class="algo-pill-icon">{icon}</div>
                <div>
                    <div class="algo-pill-label">{d.get("type", "")}</div>
                    <div class="algo-pill-text">{d.get("factor", "")} = {d.get("impact", "")}</div>
                </div>
            </div>'''

        tips = af.get("weight_tips", [])
        tips_html = ""
        if tips:
            lines = "<br>".join(tips)
            tips_html = f'''
            <div class="fill-template" style="background:rgba(38,166,154,0.08)">
                <div class="tpl-title" style="color:#26a69a">2026算法权重提示</div>
                <div class="tpl-line" style="font-size:12px;color:#bbb">{lines}</div>
            </div>'''

        parts.append(f'''
        <div class="formula-card">
            <div class="formula-card-header">
                <div class="formula-icon" style="background:linear-gradient(135deg,#26a69a,#00897b)">&#x1f916;</div>
                <div><h3>算法公式</h3><div class="formula-desc">平台推荐机制的核心驱动因素拆解</div></div>
            </div>
            <div class="formula-card-body">
                <div class="algo-pills">{pills_html}</div>
                {tips_html}
            </div>
        </div>''')

    if not parts:
        return ""

    return f'''
    <div class="section">
        <h2>爆款公式提取 <span class="new-badge">NEW</span></h2>
        <div class="formula-cards">{"".join(parts)}</div>
    </div>'''


# ─── v3 新模块: 算法适配度 ────────────────────────────

def build_algo_fitness_section(analysis):
    """生成算法适配度评估 HTML"""
    af = analysis.get("algorithm_fitness", {})
    if not af:
        return ""

    metrics = af.get("metrics", {})
    platform_fit = af.get("platform_fit", [])

    metric_cards = ""
    metric_config = [
        ("completion_rate", "完播率预测", "%", 100),
        ("interaction_rate", "互动率预测", "%", 20),
        ("share_rate", "分享率预测", "%", 20),
        ("save_rate", "收藏率预测", "%", 20),
    ]
    icons = {"completion_rate": "&#x1f504;", "interaction_rate": "&#x1f4ac;",
             "share_rate": "&#x1f4e4;", "save_rate": "&#x2b50;"}

    for key, label, unit, max_val in metric_config:
        m = metrics.get(key, {})
        if not m:
            continue
        score = _safe_num(m.get("score", 0))
        color = _score_color(score, max_val)
        bar_pct = min(100, score / max_val * 100) if max_val > 0 else 0

        factors_html = ""
        for f in m.get("factors", []):
            f_color = "#4caf50" if f.get("positive", True) else "#f44336"
            factors_html += f'''
            <div class="algo-factor">
                <span class="algo-factor-name">{f.get("name", "")}</span>
                <span class="algo-factor-val" style="color:{f_color}">{f.get("value", "")}</span>
            </div>'''

        metric_cards += f'''
        <div class="algo-metric-card">
            <div class="algo-metric-header">
                <span class="algo-metric-label">{icons.get(key, "")} {label}</span>
                <span class="algo-metric-score" style="color:{color}">{score}{unit}</span>
            </div>
            <div class="algo-meter"><div class="algo-meter-fill" style="width:{bar_pct:.0f}%;background:{color}"></div></div>
            <div class="algo-factors">{factors_html}</div>
        </div>'''

    platform_html = ""
    if platform_fit:
        items = ""
        for p in platform_fit:
            rec_cls = " recommended" if p.get("recommended") else ""
            score = _safe_num(p.get("score", 0))
            color = _score_color(score, 100)
            items += f'''
            <div class="platform-item{rec_cls}">
                <div class="pf-icon">{p.get("icon", "")}</div>
                <div class="pf-name">{p.get("platform", "")}</div>
                <div class="pf-score" style="color:{color}">{score}分</div>
                <div class="pf-reason">{p.get("reason", "")}</div>
            </div>'''

        platform_html = f'''
        <div class="platform-rec">
            <h3>平台适配建议</h3>
            <div class="platform-list">{items}</div>
        </div>'''

    if not metric_cards and not platform_html:
        return ""

    return f'''
    <div class="section">
        <h2>算法适配度评估 <span class="new-badge">NEW</span></h2>
        <div class="algo-fitness-grid">{metric_cards}</div>
        {platform_html}
    </div>'''


# ─── v3 新模块: 学习路径 ──────────────────────────────

def build_learning_section(analysis):
    """生成学习路径 HTML"""
    path = analysis.get("learning_path", [])
    if not path:
        return ""

    diff_cls = {"easy": "diff-easy", "medium": "diff-medium", "hard": "diff-hard"}
    diff_label = {"easy": "难度：易", "medium": "难度：中", "hard": "难度：难"}
    rank_colors = ["linear-gradient(135deg,#4caf50,#2e7d32)",
                   "linear-gradient(135deg,#ff9800,#e65100)",
                   "linear-gradient(135deg,#f44336,#c62828)"]

    cards = ""
    for i, item in enumerate(path[:3]):
        rank = item.get("rank", i + 1)
        technique = item.get("technique", "")
        difficulty = item.get("difficulty", "medium")
        why = item.get("why", "")
        exercises = item.get("exercises", [])
        reference = item.get("reference", "")

        ex_html = ""
        if exercises:
            items = "".join(f"<li>{e}</li>" for e in exercises)
            ex_html = f'''
            <div class="learn-exercise">
                <h4>练习方法</h4>
                <ol>{items}</ol>
            </div>'''

        ref_html = ""
        if reference:
            ref_html = f'<div class="learn-reference"><b>进阶参考：</b>{reference}</div>'

        bg = rank_colors[i] if i < len(rank_colors) else rank_colors[-1]
        d_cls = diff_cls.get(difficulty, "diff-medium")
        d_label = diff_label.get(difficulty, "难度：中")

        cards += f'''
        <div class="learn-card">
            <div class="learn-card-header">
                <div class="learn-rank" style="background:{bg}">{rank}</div>
                <div>
                    <h3>{technique}</h3>
                    <span class="learn-diff {d_cls}">{d_label}</span>
                </div>
            </div>
            <div class="learn-card-body">
                <div class="learn-why"><b>为什么值得学：</b>{why}</div>
                {ex_html}
                {ref_html}
            </div>
        </div>'''

    return f'''
    <div class="section">
        <h2>学习路径 <span class="new-badge">NEW</span></h2>
        <div class="learning-cards">{cards}</div>
    </div>'''


# ─── HTML 模板渲染 ────────────────────────────────────

def render_html_template(
    video_info, analysis, video_rel_path,
    screenshots, webvtt_data_url,
    timeline_markers_html, commentary_html,
    dimension_cards_html, template_section_html,
    suggestions_html,
    radar_labels_json, radar_scores_json,
    # v3 新模块
    emotion_arc_json, retention_heatbar_json,
    retention_stats_json, retention_risk_cards_html,
    formula_section_html, algo_fitness_html,
    learning_html,
):
    """用 string.Template 渲染完整 HTML（$var 语法避免 CSS/JS {} 冲突）"""

    overall_score = _safe_num(analysis.get("overall_score", 0))
    summary = analysis.get("summary", "")
    file_name = video_info.get("file_name", "未知视频")
    duration = video_info.get("duration", 0)
    width = video_info.get("width", 0)
    height = video_info.get("height", 0)
    duration_fmt = _fmt_time(duration)

    score_color = _score_color(overall_score)

    # 检查 v3 模块是否有数据
    has_emotion_arc = emotion_arc_json != "null" and emotion_arc_json != "{}"
    has_retention = retention_heatbar_json != "[]"

    html_template = Template(r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>爆款视频拆解报告 — $file_name</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#0f1117;color:#e0e0e0;line-height:1.6}
a{color:#64b5f6;text-decoration:none}

/* Header */
.header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:32px 40px;border-bottom:2px solid #333}
.header h1{font-size:22px;font-weight:600;margin-bottom:8px;color:#fff}
.header .meta{display:flex;gap:20px;flex-wrap:wrap;font-size:14px;color:#aaa;margin-bottom:12px}
.header .meta span{display:flex;align-items:center;gap:4px}
.score-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.08);border-radius:12px;padding:6px 16px;font-size:28px;font-weight:700}
.header .summary{margin-top:12px;font-size:15px;color:#bbb;max-width:800px}

/* Main layout */
.container{max-width:1280px;margin:0 auto;padding:24px}
.section{margin-bottom:32px}
.section h2{font-size:18px;font-weight:600;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #333;color:#fff}
.new-badge{display:inline-block;background:linear-gradient(135deg,#ff6b35,#f7931a);color:#fff;padding:1px 8px;border-radius:8px;font-size:11px;font-weight:700;vertical-align:middle}

/* Radar + score table row */
.overview-row{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:32px}
@media(max-width:768px){.overview-row{grid-template-columns:1fr}}
.radar-box{background:#1a1a2e;border-radius:12px;padding:24px;display:flex;align-items:center;justify-content:center}
.radar-box canvas{max-width:360px;max-height:360px}
.score-table{background:#1a1a2e;border-radius:12px;padding:24px}
.score-table table{width:100%;border-collapse:collapse}
.score-table th,.score-table td{padding:8px 12px;text-align:left;border-bottom:1px solid #2a2a3e}
.score-table th{color:#888;font-weight:500;font-size:13px}
.score-table td:nth-child(2){font-weight:600;font-size:15px}

/* Video + commentary panel */
.player-row{display:grid;grid-template-columns:3fr 2fr;gap:0;margin-bottom:32px;border-radius:12px;overflow:hidden;background:#1a1a2e}
@media(max-width:900px){.player-row{grid-template-columns:1fr}}
.player-col{position:relative}
.player-col video{width:100%;display:block;background:#000}
.commentary-col{height:480px;overflow-y:auto;padding:16px;border-left:1px solid #333}
.commentary-col h3{font-size:14px;color:#888;margin-bottom:12px}

/* Commentary entries */
.cmt-entry{padding:10px 12px;border-radius:8px;margin-bottom:8px;cursor:pointer;transition:background 0.2s,border-left 0.2s;border-left:3px solid transparent}
.cmt-entry:hover{background:rgba(255,255,255,0.05)}
.cmt-entry.active{background:rgba(100,181,246,0.12);border-left-color:#64b5f6}
.cmt-time{font-size:12px;color:#64b5f6;font-weight:600}
.cmt-func{font-size:13px;color:#ff9800;margin:2px 0}
.cmt-text{font-size:13px;color:#bbb}

/* Chapter + Scene two-level */
.cmt-chapter{margin-bottom:6px;border-radius:8px;border-left:3px solid transparent;transition:border-left 0.2s}
.cmt-chapter.active{border-left-color:#64b5f6}
.cmt-ch-header{display:flex;align-items:center;gap:6px;padding:8px 10px;cursor:pointer;border-radius:8px 8px 0 0;transition:background 0.2s}
.cmt-ch-header:hover{background:rgba(255,255,255,0.05)}
.cmt-toggle{font-size:10px;color:#666;transition:transform 0.2s;display:inline-block;width:14px}
.cmt-chapter.collapsed .cmt-toggle{transform:rotate(-90deg)}
.cmt-chapter.collapsed .cmt-scenes{display:none}
.cmt-chapter.collapsed .cmt-ch-summary{display:none}
.cmt-ch-summary{font-size:12px;color:#888;padding:0 10px 6px 30px;line-height:1.4}
.cmt-scenes{padding:0 6px 6px 14px}
.cmt-scene{padding:8px 10px;margin-bottom:4px;border-radius:6px;cursor:pointer;transition:background 0.2s;border-left:2px solid transparent}
.cmt-scene:hover{background:rgba(255,255,255,0.04)}
.cmt-scene.active{background:rgba(100,181,246,0.10);border-left-color:#64b5f6}
.sc-time{font-size:11px;color:#64b5f6;font-weight:600;margin-bottom:4px}
.sc-row{display:flex;align-items:flex-start;gap:6px;margin-bottom:3px;font-size:12px;line-height:1.5}
.sc-tag{flex-shrink:0;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600;color:#fff}
.sc-visual{background:#5c6bc0}
.sc-audio{background:#26a69a}
.sc-emotion{background:#ef5350}
.sc-quote{background:#7e57c2}
.sc-val{color:#bbb}
.sc-quote-text{color:#ce93d8;font-style:italic}
.sc-risk{font-size:10px;padding:1px 6px;border-radius:3px;color:#fff;margin-left:6px}
.risk-high{background:#f44336}
.risk-med{background:#ff9800}

/* Technique tags */
.sc-techniques{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.tech-tag{display:inline-flex;align-items:center;gap:3px;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;color:#fff;cursor:default}
.tech-cat{font-size:9px;opacity:0.7;margin-left:2px}
.tech-hook{background:#e65100}
.tech-retain{background:#1565c0}
.tech-pace{background:#00838f}
.tech-emo{background:#c62828}
.tech-trust{background:#2e7d32}
.tech-interact{background:#6a1b9a}
.tech-vis{background:#4527a0}
.tech-default{background:#546e7a}
.sc-tech-tips{margin-top:4px;padding-left:4px}
.tech-why{font-size:11px;color:#999;line-height:1.4;margin-bottom:2px;padding-left:8px;border-left:2px solid #333}

/* Timeline */
.timeline-track{display:flex;flex-wrap:nowrap;background:#1a1a2e;border-radius:12px;margin-bottom:32px;overflow-x:auto;overflow-y:hidden;padding:12px 4px;gap:2px}
.timeline-inner{position:relative;height:100%;min-width:100%}
.tl-item{position:relative;display:inline-block;vertical-align:top;cursor:pointer;text-align:center;padding:4px 2px;box-sizing:border-box}
.tl-item img{width:100%;max-width:140px;height:78px;object-fit:cover;border-radius:6px;border:1px solid #333;display:block;margin:0 auto 4px;transition:border-color 0.2s}
.tl-item:hover img{border-color:#ff9800}
.tl-label{font-size:11px;color:#ccc;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px;margin:0 auto}
.tl-reason{font-size:10px;color:#888;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px;margin:2px auto 0;line-height:1.3}

/* Screenshot grid */

/* Dimension cards */
.dim-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
.dim-card{background:#1a1a2e;border-radius:12px;padding:20px}
.dim-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.dim-label{font-size:15px;font-weight:600;color:#fff}
.dim-score{font-size:20px;font-weight:700}
.dim-bar-bg{height:4px;background:#2a2a3e;border-radius:2px;margin-bottom:12px}
.dim-bar{height:100%;border-radius:2px;transition:width 0.6s}
.dim-desc{font-size:13px;color:#bbb;margin-bottom:8px}
.dim-card p{font-size:13px;color:#999;margin-bottom:4px}
.dim-card p b{color:#ccc}

/* Template section */
.tpl-box{background:#1a1a2e;border-radius:12px;padding:20px;margin-bottom:16px}
.tpl-box h3{font-size:15px;margin-bottom:10px;color:#64b5f6}
.tpl-formula{font-size:14px;color:#ff9800;padding:12px;background:rgba(255,152,0,0.08);border-radius:8px;word-break:break-all}
.tpl-script{font-size:14px;color:#bbb;padding:12px;background:rgba(255,255,255,0.04);border-radius:8px;white-space:pre-wrap}
.shot-table{width:100%;border-collapse:collapse;font-size:13px}
.shot-table th,.shot-table td{padding:8px 10px;text-align:left;border-bottom:1px solid #2a2a3e}
.shot-table th{color:#888;font-weight:500}

/* Suggestions */
.suggestions{display:grid;grid-template-columns:1fr 1fr;gap:24px}
@media(max-width:768px){.suggestions{grid-template-columns:1fr}}
.sug-col{background:#1a1a2e;border-radius:12px;padding:20px}
.sug-col h3{font-size:15px;margin-bottom:12px}
.sug-col ol{padding-left:20px}
.sug-col li{margin-bottom:8px;font-size:13px;color:#bbb}
.strength-item::marker{color:#4caf50}
.improve-item::marker{color:#ff9800}

/* ═══ v3: Emotion Arc ═══ */
.emotion-arc-box{background:#1a1a2e;border-radius:12px;padding:24px}
.emotion-arc-box .subtitle{font-size:12px;color:#888;margin-bottom:16px}
.arc-chart-container{position:relative;height:280px}
.arc-legend{display:flex;gap:16px;margin-top:12px;flex-wrap:wrap}
.arc-legend-item{display:flex;align-items:center;gap:6px;font-size:12px;color:#aaa}
.arc-legend-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.arc-type-badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:600;margin-top:12px;background:rgba(76,175,80,0.15);color:#4caf50;border:1px solid #4caf50}
.arc-annotations{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-top:16px}
.arc-note{background:rgba(255,255,255,0.04);border-radius:8px;padding:12px;border-left:3px solid}
.arc-note .note-time{font-size:12px;font-weight:600;margin-bottom:4px}
.arc-note .note-desc{font-size:12px;color:#bbb}

/* ═══ v3: Retention Risk ═══ */
.retention-box{background:#1a1a2e;border-radius:12px;padding:24px}
.retention-box .subtitle{font-size:12px;color:#888;margin-bottom:16px}
.retention-bar{position:relative;height:40px;border-radius:8px;overflow:hidden;background:#1e1e2e;cursor:pointer}
.retention-segment{position:absolute;top:0;height:100%;transition:opacity 0.2s}
.retention-segment:hover{opacity:0.8}
.retention-segment .seg-tooltip{display:none;position:absolute;bottom:48px;left:50%;transform:translateX(-50%);background:#222;border:1px solid #444;border-radius:8px;padding:10px 14px;font-size:12px;white-space:nowrap;z-index:10;min-width:200px;box-shadow:0 4px 12px rgba(0,0,0,0.5)}
.retention-segment:hover .seg-tooltip{display:block}
.retention-time-axis{display:flex;justify-content:space-between;margin-top:6px;font-size:11px;color:#666}
.retention-legend{display:flex;gap:16px;margin-top:12px}
.retention-legend-item{display:flex;align-items:center;gap:6px;font-size:12px;color:#aaa}
.retention-legend-dot{width:14px;height:14px;border-radius:3px;flex-shrink:0}
.retention-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}
@media(max-width:768px){.retention-stats{grid-template-columns:repeat(2,1fr)}}
.ret-stat{text-align:center;background:rgba(255,255,255,0.04);border-radius:8px;padding:12px}
.ret-stat .stat-val{font-size:22px;font-weight:700}
.ret-stat .stat-label{font-size:11px;color:#888;margin-top:2px}
.risk-details{margin-top:16px}
.risk-card{background:rgba(255,255,255,0.04);border-radius:8px;padding:14px;margin-bottom:8px;border-left:3px solid;display:grid;grid-template-columns:100px 1fr;gap:12px;align-items:start}
.risk-card .risk-time{font-size:13px;font-weight:600;color:#64b5f6}
.risk-card .risk-level{font-size:11px;padding:2px 8px;border-radius:4px;display:inline-block;margin-top:2px}
.risk-card .risk-reason{font-size:12px;color:#bbb;margin-bottom:4px}
.risk-card .risk-fix{font-size:12px;color:#4caf50;font-style:italic}

/* ═══ v3: Viral Formula ═══ */
.formula-cards{display:grid;grid-template-columns:1fr;gap:16px}
.formula-card{background:#1a1a2e;border-radius:12px;overflow:hidden}
.formula-card-header{padding:16px 20px;display:flex;align-items:center;gap:12px}
.formula-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.formula-card-header h3{font-size:15px;color:#fff}
.formula-card-header .formula-desc{font-size:12px;color:#888;margin-top:2px}
.formula-card-body{padding:0 20px 20px}
.script-flow{display:flex;align-items:stretch;gap:0;margin-bottom:16px;overflow-x:auto;padding-bottom:8px}
.flow-step{display:flex;flex-direction:column;align-items:center;min-width:110px;padding:10px 8px;background:rgba(255,255,255,0.04);border-radius:8px;text-align:center}
.flow-step .step-time{font-size:11px;color:#64b5f6;font-weight:600;margin-bottom:4px}
.flow-step .step-name{font-size:13px;color:#fff;font-weight:600;margin-bottom:4px}
.flow-step .step-desc{font-size:11px;color:#999}
.flow-arrow{display:flex;align-items:center;padding:0 4px;color:#555;font-size:16px;flex-shrink:0}
.fill-template{background:rgba(255,152,0,0.08);border-radius:8px;padding:16px;margin-top:12px}
.fill-template .tpl-title{font-size:12px;color:#ff9800;font-weight:600;margin-bottom:8px}
.fill-template .tpl-line{font-size:13px;color:#ccc;line-height:1.8}
.fill-template .blank{display:inline-block;border-bottom:2px dashed #ff9800;min-width:60px;color:#ff9800;padding:0 4px;margin:0 2px}
.emotion-flow{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
.emotion-node{padding:6px 12px;border-radius:20px;font-size:13px;font-weight:600;display:inline-flex;align-items:center;gap:6px}
.emotion-node .emo-val{font-size:11px;opacity:0.8}
.emo-arrow{color:#555;font-size:14px}
.algo-pills{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.algo-pill{display:flex;align-items:center;gap:10px;background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 14px}
.algo-pill-icon{font-size:18px;flex-shrink:0}
.algo-pill-text{font-size:12px;color:#bbb}
.algo-pill-label{font-size:13px;color:#fff;font-weight:600}

/* ═══ v3: Algorithm Fitness ═══ */
.algo-fitness-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
@media(max-width:768px){.algo-fitness-grid{grid-template-columns:1fr}}
.algo-metric-card{background:#1a1a2e;border-radius:12px;padding:20px}
.algo-metric-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.algo-metric-label{font-size:15px;font-weight:600;color:#fff;display:flex;align-items:center;gap:8px}
.algo-metric-score{font-size:24px;font-weight:700}
.algo-meter{height:6px;background:#2a2a3e;border-radius:3px;margin-bottom:12px;overflow:hidden}
.algo-meter-fill{height:100%;border-radius:3px;transition:width 0.6s}
.algo-factors{padding:0}
.algo-factor{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #222;font-size:13px}
.algo-factor:last-child{border-bottom:none}
.algo-factor-name{color:#bbb}
.algo-factor-val{font-weight:600}
.platform-rec{background:#1a1a2e;border-radius:12px;padding:20px;margin-top:16px}
.platform-rec h3{font-size:15px;color:#fff;margin-bottom:12px}
.platform-list{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
@media(max-width:768px){.platform-list{grid-template-columns:1fr}}
.platform-item{background:rgba(255,255,255,0.04);border-radius:10px;padding:14px;text-align:center}
.platform-item .pf-icon{font-size:28px;margin-bottom:6px}
.platform-item .pf-name{font-size:14px;font-weight:600;color:#fff;margin-bottom:4px}
.platform-item .pf-score{font-size:20px;font-weight:700;margin-bottom:4px}
.platform-item .pf-reason{font-size:11px;color:#999}
.platform-item.recommended{border:2px solid #4caf50;background:rgba(76,175,80,0.08)}

/* ═══ v3: Learning Path ═══ */
.learning-cards{display:grid;grid-template-columns:1fr;gap:16px}
.learn-card{background:#1a1a2e;border-radius:12px;overflow:hidden}
.learn-card-header{display:flex;align-items:center;gap:14px;padding:16px 20px}
.learn-rank{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;color:#fff;flex-shrink:0}
.learn-card-header h3{font-size:15px;color:#fff}
.learn-diff{font-size:11px;padding:2px 8px;border-radius:4px;margin-left:8px}
.diff-easy{background:rgba(76,175,80,0.2);color:#4caf50}
.diff-medium{background:rgba(255,152,0,0.2);color:#ff9800}
.diff-hard{background:rgba(244,67,54,0.2);color:#f44336}
.learn-card-body{padding:0 20px 20px}
.learn-why{font-size:13px;color:#bbb;margin-bottom:12px;padding:10px;background:rgba(255,255,255,0.04);border-radius:8px}
.learn-exercise{margin-bottom:12px}
.learn-exercise h4{font-size:13px;color:#64b5f6;margin-bottom:6px}
.learn-exercise ol{padding-left:20px}
.learn-exercise li{font-size:12px;color:#bbb;margin-bottom:4px;line-height:1.5}
.learn-reference{font-size:12px;color:#888;padding:8px 10px;background:rgba(255,255,255,0.03);border-radius:6px}
.learn-reference b{color:#aaa}

/* Footer */
.footer{text-align:center;padding:24px;color:#555;font-size:12px;border-top:1px solid #222}
</style>
</head>
<body>

<!-- ─── Header ─── -->
<div class="header">
    <h1>爆款视频拆解报告</h1>
    <div class="meta">
        <span>$file_name</span>
        <span>$duration_fmt</span>
        <span>${width}x${height}</span>
        <span>豆包原生视频理解</span>
    </div>
    <div class="score-badge" style="color:$score_color">
        爆款指数 $overall_score/10
    </div>
    <p class="summary">$summary</p>
</div>

<div class="container">

<!-- ─── Radar + Score Table ─── -->
<div class="overview-row">
    <div class="radar-box">
        <canvas id="radarChart"></canvas>
    </div>
    <div class="score-table">
        <h2>评分汇总</h2>
        <table>
            <thead><tr><th>维度</th><th>评分</th><th>简评</th></tr></thead>
            <tbody id="scoreTbody"></tbody>
        </table>
    </div>
</div>

<!-- ─── v3: Emotion Arc ─── -->
<div class="section" id="secEmotionArc" style="display:none">
    <h2>情绪弧线分析 <span class="new-badge">NEW</span></h2>
    <div class="emotion-arc-box">
        <p class="subtitle">蓝线=情绪效价(积极/消极)，橙线=唤醒度(紧张/平静)</p>
        <div class="arc-chart-container">
            <canvas id="emotionChart"></canvas>
        </div>
        <div class="arc-legend">
            <div class="arc-legend-item"><div class="arc-legend-dot" style="background:#64b5f6"></div>情绪效价 (-5消极 ~ +5积极)</div>
            <div class="arc-legend-item"><div class="arc-legend-dot" style="background:#ff9800"></div>唤醒度 (0平静 ~ 10兴奋)</div>
        </div>
        <div id="arcType"></div>
        <div id="arcAnnotations" class="arc-annotations"></div>
    </div>
</div>

<!-- ─── v3: Retention Risk ─── -->
<div class="section" id="secRetention" style="display:none">
    <h2>留存风险分析 <span class="new-badge">NEW</span></h2>
    <div class="retention-box">
        <p class="subtitle">绿色=安全 | 黄色=有风险 | 红色=高风险。hover查看原因和修复建议</p>
        <div class="retention-bar" id="retentionBar"></div>
        <div class="retention-time-axis" id="retTimeAxis"></div>
        <div class="retention-legend">
            <div class="retention-legend-item"><div class="retention-legend-dot" style="background:#4caf50"></div>安全</div>
            <div class="retention-legend-item"><div class="retention-legend-dot" style="background:#ff9800"></div>有风险</div>
            <div class="retention-legend-item"><div class="retention-legend-dot" style="background:#f44336"></div>高风险</div>
        </div>
        <div class="retention-stats" id="retStats"></div>
        <div class="risk-details" id="riskDetails">$retention_risk_cards_html</div>
    </div>
</div>

<!-- ─── Video + Commentary ─── -->
<div class="section">
    <h2>视频播放 &amp; 同步解读</h2>
    <div class="player-row">
        <div class="player-col">
            <video id="mainVideo" controls preload="metadata">
                <source src="$video_rel_path" type="video/mp4">
                <track id="metaTrack" kind="metadata" src="$webvtt_data_url" default>
                您的浏览器不支持视频播放
            </video>
        </div>
        <div class="commentary-col" id="commentaryPanel">
            <h3>时间线解读</h3>
            $commentary_html
        </div>
    </div>
</div>

<!-- ─── Timeline ─── -->
<div class="section">
    <h2>截图时间线</h2>
    <div class="timeline-track">
        <div class="timeline-inner">
            $timeline_markers_html
        </div>
    </div>
</div>

<!-- ─── Dimension Cards ─── -->
<div class="section">
    <h2>8 维度详细分析</h2>
    <div class="dim-grid">
        $dimension_cards_html
    </div>
</div>

<!-- ─── v3: Formula ─── -->
$formula_section_html

<!-- ─── v3: Algorithm Fitness ─── -->
$algo_fitness_html

<!-- ─── Template ─── -->
$template_section_html

<!-- ─── v3: Learning Path ─── -->
$learning_html

<!-- ─── Suggestions ─── -->
<div class="section">
    <h2>亮点与改进</h2>
    $suggestions_html
</div>

</div><!-- /container -->

<div class="footer">
    由 爆款视频拆解工具 v3 自动生成 | 豆包原生视频理解
</div>

<script>
// ─── Data ───
var RADAR_LABELS = $radar_labels_json;
var RADAR_SCORES = $radar_scores_json;
var DURATION = $duration;
var EMOTION_ARC = $emotion_arc_json;
var RETENTION_HEATBAR = $retention_heatbar_json;
var RETENTION_STATS = $retention_stats_json;

// ─── Radar Chart ───
(function() {
    var ctx = document.getElementById('radarChart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: RADAR_LABELS,
            datasets: [{
                label: '评分',
                data: RADAR_SCORES,
                backgroundColor: 'rgba(100,181,246,0.18)',
                borderColor: '#64b5f6',
                pointBackgroundColor: '#64b5f6',
                pointBorderColor: '#fff',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    min: 0, max: 10,
                    ticks: { stepSize: 2, color: '#666', backdropColor: 'transparent' },
                    grid: { color: '#2a2a3e' },
                    angleLines: { color: '#2a2a3e' },
                    pointLabels: { color: '#ccc', font: { size: 13 } }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
})();

// ─── Score Table ───
(function() {
    var tbody = document.getElementById('scoreTbody');
    var dims = $dimensions_json;
    dims.forEach(function(d) {
        var color = d[2] >= 8 ? '#4caf50' : (d[2] >= 6 ? '#ff9800' : '#f44336');
        var tr = document.createElement('tr');
        tr.innerHTML = '<td>' + d[1] + '</td><td style="color:' + color + '">' + d[2] + '/10</td><td style="font-size:13px;color:#999">' + d[3].substring(0, 40) + (d[3].length > 40 ? '...' : '') + '</td>';
        tbody.appendChild(tr);
    });
})();

// ─── v3: Emotion Arc Chart ───
(function() {
    if (!EMOTION_ARC || !EMOTION_ARC.curve_points || EMOTION_ARC.curve_points.length === 0) return;
    document.getElementById('secEmotionArc').style.display = '';

    var pts = EMOTION_ARC.curve_points;
    var labels = pts.map(function(p) { return p.time; });
    var valence = pts.map(function(p) { return p.valence; });
    var arousal = pts.map(function(p) { return p.arousal; });

    var ctx = document.getElementById('emotionChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '情绪效价',
                    data: valence,
                    borderColor: '#64b5f6',
                    backgroundColor: 'rgba(100,181,246,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                },
                {
                    label: '唤醒度',
                    data: arousal,
                    borderColor: '#ff9800',
                    backgroundColor: 'rgba(255,152,0,0.05)',
                    fill: false,
                    tension: 0.4,
                    pointRadius: 2,
                    borderDash: [5, 3],
                    pointHoverRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            scales: {
                x: {
                    ticks: { color: '#666', maxRotation: 45, font: { size: 10 } },
                    grid: { color: '#1e1e2e' }
                },
                y: {
                    min: -5, max: 10,
                    ticks: { color: '#666', stepSize: 2.5 },
                    grid: { color: '#1e1e2e' }
                }
            },
            plugins: { legend: { display: false } }
        }
    });

    // Arc type badge
    if (EMOTION_ARC.arc_type) {
        var desc = EMOTION_ARC.arc_description || '';
        document.getElementById('arcType').innerHTML = '<div class="arc-type-badge">' + EMOTION_ARC.arc_type + (desc ? ' — ' + desc : '') + '</div>';
    }

    // Turning points
    var tps = EMOTION_ARC.turning_points || [];
    if (tps.length > 0) {
        var html = '';
        var colors = ['#ef5350', '#ff9800', '#4caf50', '#64b5f6', '#7e57c2'];
        tps.forEach(function(tp, i) {
            var c = colors[i % colors.length];
            html += '<div class="arc-note" style="border-color:' + c + '">' +
                '<div class="note-time" style="color:' + c + '">' + (tp.time || '') + ' ' + (tp.type || '') + '</div>' +
                '<div class="note-desc">' + (tp.description || '') + '</div></div>';
        });
        document.getElementById('arcAnnotations').innerHTML = html;
    }
})();

// ─── v3: Retention Heatbar ───
(function() {
    if (!RETENTION_HEATBAR || RETENTION_HEATBAR.length === 0) return;
    if (!RETENTION_STATS.hook_rate_3s && RETENTION_HEATBAR.every(function(s) { return s.risk === 'low'; })) return;
    document.getElementById('secRetention').style.display = '';

    var bar = document.getElementById('retentionBar');
    var riskColors = { low: '#4caf50', medium: '#ff9800', high: '#f44336' };
    var riskOpacity = { low: '0.4', medium: '0.6', high: '0.9' };
    var riskLabels = { low: '安全', medium: '中风险', high: '高风险' };

    RETENTION_HEATBAR.forEach(function(seg) {
        var el = document.createElement('div');
        el.className = 'retention-segment';
        el.style.left = (seg.start / DURATION * 100) + '%';
        el.style.width = ((seg.end - seg.start) / DURATION * 100) + '%';
        el.style.background = riskColors[seg.risk] || riskColors.low;
        el.style.opacity = riskOpacity[seg.risk] || '0.4';
        el.onclick = function() { seekTo(seg.start); };

        if (seg.risk !== 'low' && seg.reason) {
            var fixHtml = seg.fix ? '<div style="color:#4caf50;margin-top:4px">' + seg.fix + '</div>' : '';
            el.innerHTML = '<div class="seg-tooltip">' +
                '<div style="font-weight:600;color:#fff">' + fmtTime(seg.start) + '-' + fmtTime(seg.end) + ' ' + (riskLabels[seg.risk] || '') + '</div>' +
                '<div style="color:#bbb;margin-top:4px">' + seg.reason + '</div>' +
                fixHtml + '</div>';
        }
        bar.appendChild(el);
    });

    // Time axis
    var axisEl = document.getElementById('retTimeAxis');
    var step = Math.ceil(DURATION / 8);
    var html = '';
    for (var t = 0; t <= DURATION; t += step) {
        html += '<span>' + fmtTime(t) + '</span>';
    }
    axisEl.innerHTML = html;

    // Stats
    var statsEl = document.getElementById('retStats');
    var statsData = [
        { val: RETENTION_STATS.hook_rate_3s, label: '3秒留存预测' },
        { val: RETENTION_STATS.retention_30s, label: '30秒留存预测' },
        { val: RETENTION_STATS.midpoint_retention, label: '中点留存预测' },
        { val: RETENTION_STATS.completion_rate, label: '完播率预测' }
    ];
    var shtml = '';
    statsData.forEach(function(s) {
        if (!s.val) return;
        var c = s.val >= 60 ? '#4caf50' : (s.val >= 35 ? '#ff9800' : '#f44336');
        shtml += '<div class="ret-stat"><div class="stat-val" style="color:' + c + '">' + s.val + '%</div><div class="stat-label">' + s.label + '</div></div>';
    });
    statsEl.innerHTML = shtml;

    function fmtTime(s) {
        var m = Math.floor(s / 60);
        var sec = Math.floor(s % 60);
        return m + ':' + (sec < 10 ? '0' : '') + sec;
    }
})();

// ─── Video Sync ───
(function() {
    var video = document.getElementById('mainVideo');
    var panel = document.getElementById('commentaryPanel');
    var entries = document.querySelectorAll('.cmt-entry');
    var chapters = document.querySelectorAll('.cmt-chapter');
    var scenes = document.querySelectorAll('.cmt-scene');
    var track = document.getElementById('metaTrack');
    var fallbackTimer = null;
    var cueChangeWorking = false;

    function highlightEntry(currentTime) {
        var found = null;
        entries.forEach(function(el) {
            var s = parseFloat(el.dataset.start);
            var e = parseFloat(el.dataset.end);
            if (currentTime >= s && currentTime < e) {
                el.classList.add('active');
                found = el;
            } else {
                el.classList.remove('active');
            }
        });

        var activeScene = null;
        chapters.forEach(function(ch) {
            var cs = parseFloat(ch.dataset.start);
            var ce = parseFloat(ch.dataset.end);
            if (currentTime >= cs && currentTime < ce) {
                ch.classList.add('active');
                ch.classList.remove('collapsed');
            } else {
                ch.classList.remove('active');
            }
        });
        scenes.forEach(function(sc) {
            var ss = parseFloat(sc.dataset.start);
            var se = parseFloat(sc.dataset.end);
            if (currentTime >= ss && currentTime < se) {
                sc.classList.add('active');
                activeScene = sc;
            } else {
                sc.classList.remove('active');
            }
        });

        var target = activeScene || found;
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    if (track && track.track) {
        track.track.mode = 'hidden';
        track.track.oncuechange = function() {
            cueChangeWorking = true;
            highlightEntry(video.currentTime);
        };
    }

    video.addEventListener('play', function() {
        if (fallbackTimer) clearTimeout(fallbackTimer);
        fallbackTimer = setTimeout(function() {
            if (!cueChangeWorking) {
                video.addEventListener('timeupdate', function() {
                    highlightEntry(video.currentTime);
                });
            }
        }, 3000);
    });

    video.addEventListener('seeked', function() {
        highlightEntry(video.currentTime);
    });
})();

// ─── Helpers ───
function toggleChapter(chapterEl) {
    chapterEl.classList.toggle('collapsed');
}
function seekTo(sec) {
    var video = document.getElementById('mainVideo');
    video.currentTime = sec;
    video.play();
}
</script>
</body>
</html>''')

    return html_template.safe_substitute(
        file_name=file_name,
        duration_fmt=duration_fmt,
        width=width,
        height=height,
        score_color=score_color,
        overall_score=overall_score,
        summary=summary,
        video_rel_path=video_rel_path,
        webvtt_data_url=webvtt_data_url,
        commentary_html=commentary_html,
        timeline_markers_html=timeline_markers_html,
        dimension_cards_html=dimension_cards_html,
        template_section_html=template_section_html,
        suggestions_html=suggestions_html,
        radar_labels_json=radar_labels_json,
        radar_scores_json=radar_scores_json,
        duration=duration,
        dimensions_json=json.dumps(
            extract_dimension_scores(analysis), ensure_ascii=False
        ),
        # v3 新模块
        emotion_arc_json=emotion_arc_json,
        retention_heatbar_json=retention_heatbar_json,
        retention_stats_json=retention_stats_json,
        retention_risk_cards_html=retention_risk_cards_html,
        formula_section_html=formula_section_html,
        algo_fitness_html=algo_fitness_html,
        learning_html=learning_html,
    )


# ─── 主入口 ───────────────────────────────────────────

def generate_report(result_json, video_path=None, output_dir=None,
                     title=None, archive_dir=None, video_url=None):
    """主入口：解析 → 截图 → WebVTT → 渲染 → 写文件

    Args:
        result_json: 分析结果（dict 或 JSON 文件路径）
        video_path: 原始视频路径（用于截图和播放器）
        output_dir: 报告输出目录（默认与视频同目录）
        title: 视频标题（用于归档子目录命名和 meta.json）
        archive_dir: 归档根目录。若指定，则在此目录下创建 '日期_标题' 子目录保存报告，
                     并自动更新 index.html 汇总页。会覆盖 output_dir。
        video_url: 视频的公网 URL（用于 report-lite.html 的视频引用，解决静态预览
                   无法加载相对路径 video.mp4 的问题）。若不提供则使用相对路径 'video.mp4'。

    Returns:
        生成的 HTML 文件路径
    """
    # 1. 加载数据
    if isinstance(result_json, str):
        with open(result_json, "r", encoding="utf-8") as f:
            result_json = json.load(f)

    analysis, video_info = unwrap_analysis_data(result_json)
    if not analysis or "overall_score" not in analysis:
        print("[ERROR] 无法从结果中提取分析数据", file=sys.stderr)
        return None

    duration = video_info.get("duration", 0)

    # 2. 确定输出目录（归档模式下创建子目录）
    if archive_dir:
        # 自动推断标题：优先用传入的 title，其次从 video_info 取，最后从 analysis.summary 截取
        if not title:
            title = video_info.get("title") or ""
        if not title:
            title = (analysis.get("summary") or "")[:30]
        if not title:
            title = video_info.get("file_name", "未命名视频")
        output_dir = make_archive_subdir(archive_dir, title)
        print(f"[INFO] 归档目录: {output_dir}")
    elif output_dir is None:
        if video_path:
            output_dir = os.path.dirname(os.path.abspath(video_path))
        else:
            output_dir = "/tmp/video-optimize"
    os.makedirs(output_dir, exist_ok=True)

    # 3. 截图
    print("[INFO] 正在提取关键帧截图...")
    timestamps, reasons = extract_screenshot_timestamps(analysis, duration)
    screenshots = {}
    if video_path and os.path.exists(video_path):
        screenshots = extract_screenshots(video_path, timestamps)
        print(f"[OK] 提取了 {len(screenshots)} 张截图")
    else:
        print("[WARN] 视频文件不可用，跳过截图提取")

    # 4. WebVTT
    webvtt_data_url = generate_webvtt(analysis)

    # 5. 视频：内嵌为 base64 data URL，确保 HTML 完全自包含、任何环境都能播放
    video_rel_path = ""
    if video_path and os.path.exists(video_path):
        import shutil
        video_abs = os.path.abspath(video_path)
        output_abs = os.path.abspath(output_dir)
        file_size_mb = os.path.getsize(video_abs) / (1024 * 1024)
        print(f"[INFO] 正在内嵌视频 ({file_size_mb:.1f}MB) 为 base64 data URL...")
        with open(video_abs, "rb") as vf:
            video_b64 = base64.b64encode(vf.read()).decode("ascii")
        video_rel_path = f"data:video/mp4;base64,{video_b64}"
        print(f"[OK] 视频已内嵌为 data URL ({len(video_b64) / 1024 / 1024:.1f}MB base64)")
        # 同时复制一份 video.mp4 到 output_dir 备用
        safe_dest = os.path.join(output_abs, "video.mp4")
        if video_abs != safe_dest:
            shutil.copy2(video_abs, safe_dest)

    # 6. 构建 HTML 片段（原有模块）
    radar_labels = [s[1] for s in extract_dimension_scores(analysis)]
    radar_scores = [s[2] for s in extract_dimension_scores(analysis)]

    timeline_markers_html = build_timeline_markers(analysis, screenshots, duration, reasons)
    commentary_html = build_commentary_entries(analysis)
    dimension_cards_html = build_dimension_cards(analysis, screenshots)
    template_section_html = build_template_section(analysis)
    suggestions_html = build_suggestions(analysis)

    # 7. 构建 v3 新模块
    emotion_arc_data = build_emotion_arc_data(analysis)
    retention_data = build_retention_data(analysis, duration)
    formula_section_html = build_formula_section(analysis)
    algo_fitness_html = build_algo_fitness_section(analysis)
    learning_html = build_learning_section(analysis)

    # 8. 渲染
    print("[INFO] 正在渲染 HTML 报告...")
    html = render_html_template(
        video_info=video_info,
        analysis=analysis,
        video_rel_path=video_rel_path,
        screenshots=screenshots,
        webvtt_data_url=webvtt_data_url,
        timeline_markers_html=timeline_markers_html,
        commentary_html=commentary_html,
        dimension_cards_html=dimension_cards_html,
        template_section_html=template_section_html,
        suggestions_html=suggestions_html,
        radar_labels_json=json.dumps(radar_labels, ensure_ascii=False),
        radar_scores_json=json.dumps(radar_scores),
        # v3 新模块
        emotion_arc_json=json.dumps(emotion_arc_data, ensure_ascii=False) if emotion_arc_data else "null",
        retention_heatbar_json=json.dumps(retention_data.get("heatbar", []), ensure_ascii=False),
        retention_stats_json=json.dumps(retention_data.get("stats", {}), ensure_ascii=False),
        retention_risk_cards_html=retention_data.get("risk_cards_html", ""),
        formula_section_html=formula_section_html,
        algo_fitness_html=algo_fitness_html,
        learning_html=learning_html,
    )

    # 9. 写文件
    output_path = os.path.join(output_dir, "report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] HTML 报告已生成: {output_path}")

    # 9.1 生成轻量版 report-lite.html（视频用外部引用，HTML 体积从 ~45MB 降至 ~500KB）
    #     若提供 video_url（公网URL），使用绝对地址，确保静态预览也能播放视频
    #     否则使用相对路径 'video.mp4'，需通过 HTTP 服务器访问
    import re as _re
    video_src = video_url if video_url else 'video.mp4'
    lite_html = _re.sub(r'data:video/mp4;base64,[A-Za-z0-9+/=]+', video_src, html)
    lite_path = os.path.join(output_dir, "report-lite.html")
    with open(lite_path, "w", encoding="utf-8") as f:
        f.write(lite_html)
    lite_size_kb = os.path.getsize(lite_path) / 1024
    print(f"[OK] 轻量版报告已生成: {lite_path} ({lite_size_kb:.0f}KB)")

    # 10. 归档模式：保存 meta.json + 更新 index.html
    if archive_dir:
        import time as _time
        # 提取第一张截图作为缩略图
        thumb_b64 = ""
        if screenshots:
            first_ts = sorted(screenshots.keys())[0] if screenshots else None
            if first_ts and screenshots[first_ts]:
                # screenshots[t] 已包含完整 data URI 前缀，直接使用
                thumb_b64 = screenshots[first_ts]
        meta = {
            "title": title or video_info.get("file_name", ""),
            "overall_score": str(_safe_num(analysis.get("overall_score", 0))),
            "duration": str(round(duration)),
            "resolution": f"{video_info.get('width', '?')}x{video_info.get('height', '?')}",
            "date": _time.strftime("%Y-%m-%d"),
            "summary": (analysis.get("summary") or "")[:100],
            "thumbnail": thumb_b64,
        }
        meta_path = os.path.join(output_dir, "meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        # 更新汇总页
        idx_path = generate_index_html(archive_dir)
        print(f"[OK] 汇总页已更新: {idx_path}")

    return output_path


# ─── CLI ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="从视频分析结果生成 HTML 可视化报告")
    parser.add_argument("--result", required=True, help="分析结果 JSON 文件路径")
    parser.add_argument("--video", default=None, help="原始视频文件路径（用于截图和播放器）")
    parser.add_argument("--output-dir", default=None, help="报告输出目录")
    parser.add_argument("--title", default=None, help="视频标题（用于归档目录命名）")
    parser.add_argument("--archive-dir", default=None, help="归档根目录（启用归档模式）")
    args = parser.parse_args()

    if not os.path.exists(args.result):
        print(f"[ERROR] 结果文件不存在: {args.result}", file=sys.stderr)
        sys.exit(1)

    path = generate_report(args.result, args.video, args.output_dir,
                           title=args.title, archive_dir=args.archive_dir)
    if path:
        print(f"\n用浏览器打开查看: file://{path}")


if __name__ == "__main__":
    main()
