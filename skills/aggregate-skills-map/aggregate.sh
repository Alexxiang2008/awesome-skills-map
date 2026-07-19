#!/usr/bin/env bash
# aggregate.sh - 聚合 GitHub 博主/牛人技能地图
# 默认行为：只看 star>=500 的项目（可用 --skill-only 进一步筛 skills 关键词）
# 用法: ./aggregate.sh <users...> [options]
# 依赖: gh (GitHub CLI 已登录), jq

set -euo pipefail

# ---------- 默认参数 ----------
MIN_STARS=500          # 默认只拉星标 500 以上的项目
INCLUDE_FORKS=false
SKILL_ONLY=false        # 默认关闭；开启后只保留 name/desc 含 skill/nuwa/darwin
TOPIC_FILTER=""
JSON_OUTPUT=false
OUTPUT_PATH=""
SORT_BY="stars"
LIMIT=0
USERS=()

# ---------- 参数解析 ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --min-stars)    MIN_STARS="$2"; shift 2 ;;
    --include-forks) INCLUDE_FORKS=true; shift ;;
    --skill-only)   SKILL_ONLY=true; shift ;;
    --topic)        TOPIC_FILTER="$2"; shift 2 ;;
    --json)         JSON_OUTPUT=true; shift ;;
    --output)       OUTPUT_PATH="$2"; shift 2 ;;
    --sort)         SORT_BY="$2"; shift 2 ;;
    --limit)        LIMIT="$2"; shift 2 ;;
    --help|-h)
      cat <<'EOF'
用法: aggregate.sh <users...> [options]
  --min-stars N       最小 star 数 (默认 500)
  --include-forks     包含 fork 仓库
  --skill-only        只保留 name/desc 含 skill/nuwa/darwin 关键词
  --topic TAG         限定主题（如 claude-skill）
  --json              输出 JSON 而非 Markdown
  --output PATH       写入文件
  --sort stars|updated|name
  --limit N           单博主最多显示几个 (0=全部)

默认行为（最常用）：只看 star>=500 的项目
  ./aggregate.sh alchaincyf                       # star>=500，全部约 14 个
  ./aggregate.sh alchaincyf --skill-only          # star>=500 + 仅 skills 关键词，约 8 个
  ./aggregate.sh alchaincyf --min-stars 100       # 放宽到 100+
EOF
      exit 0 ;;
    -*) echo "❌ 未知参数: $1"; exit 1 ;;
    *)  USERS+=("$1"); shift ;;
  esac
done

# ---------- 前置检查 ----------
[[ ${#USERS[@]} -eq 0 ]] && { echo "❌ 至少给一个 GitHub 用户名"; exit 1; }
command -v gh >/dev/null || { echo "❌ 需要 gh CLI"; exit 1; }
command -v jq >/dev/null || { echo "❌ 需要 jq"; exit 1; }

# ---------- 核心函数 ----------
fetch_user_repos() {
  local user="$1"
  gh api "users/$user/repos?per_page=100" --jq \
    '.[] | {name: .name, desc: (.description // ""), stars: .stargazers_count, url: .html_url, topics: .topics, fork: .fork, updated: .updated_at}'
}

filter_repos() {
  local include_forks="$1" topic_filter="$2" min_stars="$3" skill_only="$4"
  local f="select(.stars >= $min_stars)"
  [[ "$include_forks" != "true" ]] && f+=" | select(.fork == false)"
  if [[ -n "$topic_filter" ]]; then
    f+=" | select(.topics | index(\"$topic_filter\"))"
  fi
  if [[ "$skill_only" == "true" ]]; then
    f+=" | select((.name + \" \" + .desc) | test(\"skill|nuwa|darwin\"; \"i\"))"
  fi
  jq -c "$f"
}

# ---------- 输出辅助 ----------
write_out() {
  if [[ -n "$OUTPUT_PATH" ]]; then
    cat > "$OUTPUT_PATH"
  else
    cat
  fi
}

# ---------- 主流程 ----------
for user in "${USERS[@]}"; do
  echo "📡 拉取 $user 的仓库..." >&2

  user_info=$(gh api "users/$user" --jq '{name, bio, public_repos, followers, html_url}')
  bio=$(echo "$user_info" | jq -r '.bio // "（无简介）"')
  total_repos=$(echo "$user_info" | jq -r '.public_repos')
  followers=$(echo "$user_info" | jq -r '.followers')
  html_url=$(echo "$user_info" | jq -r '.html_url')

  repos=$(fetch_user_repos "$user" | filter_repos "$INCLUDE_FORKS" "$TOPIC_FILTER" "$MIN_STARS" "$SKILL_ONLY")
  filtered_count=$(echo "$repos" | grep -c . || true)

  # JSON 输出
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$repos" | jq -s --arg user "$user" --arg bio "$bio" \
      '{user: $user, bio: $bio, total_repos: '"$total_repos"', filtered_count: '"$filtered_count"', repos: .}' \
      | write_out
    continue
  fi

  # Markdown 输出
  {
    echo "# 🎯 $user 技能地图"
    echo ""
    echo "> **$bio**"
    echo ">"
    echo "> [$total_repos 公开仓库]($html_url) · $followers followers · 过滤后 **$filtered_count** 个项目"
    echo ""
    echo "**筛选条件**：star >= $MIN_STARS$([ "$INCLUDE_FORKS" == "true" ] && echo " · 含 fork")$([[ "$SKILL_ONLY" == "true" ]] && echo " · 仅 skills 关键词")$([[ -n "$TOPIC_FILTER" ]] && echo " · topic=$TOPIC_FILTER")"
    echo ""

    if [[ "$filtered_count" -eq 0 ]]; then
      echo "⚠️ 没有匹配的仓库。可放宽过滤（--min-stars 100 / 去掉 --skill-only）"
      echo ""
      continue
    fi

    # 全部匹配仓库按 stars 降序
    echo "## 📦 全部高质量仓库"
    echo ""
    echo "| ⭐ | 仓库 | 简介 |"
    echo "|----|------|------|"
    echo "$repos" | jq -r '"\(.stars)\t\(.name)\t\(.desc)\t\(.url)"' \
      | sort -t$'\t' -k1,1 -rn \
      | awk -F'\t' '{
          gsub(/\|/, "\\|", $3)  # escape pipe in description for Markdown table
          printf "| %s | [%s](%s) | %s |\n", $1, $2, $4, $3
        }'

    # 分类小计
    echo ""
    echo "## 📊 分类小计"
    echo ""
    echo "$repos" | jq -r '"\(.name)|\(.desc)"' | while IFS='|' read -r name desc; do
      text="$name $desc"
      if echo "$text" | grep -qiE "skill|distill|nuwa|darwin"; then
        if echo "$text" | grep -qiE "jobs|musk|芒格|karpathy|feynman|naval|trump|taleb|张雪峰|张一鸣|孙宇晨|mrbeast|ilya|弗洛伊德|巴菲特|paul graham"; then
          echo "👤 人物蒸馏"
        else
          echo "🧠 元能力 Skills"
        fi
      elif echo "$text" | grep -qiE "design|html|slide|cover|visual|image"; then
        echo "🎨 设计/视觉"
      elif echo "$text" | grep -qiE "book|guide|orange-book|tutorial|deep.dive|orange"; then
        echo "📚 教程/电子书"
      elif echo "$text" | grep -qiE "tool|cli|mcp|editor|fanbox|weread|cursor|claude-code|codex"; then
        echo "🛠 开发工具"
      else
        echo "📦 其他"
      fi
    done | sort | uniq -c | sort -rn | awk '{printf "- **%s**：%s 个仓库\n", $2, $1}'
    echo ""
  } | write_out
done

echo "✅ 完成（输出：${OUTPUT_PATH:-stdout}）" >&2