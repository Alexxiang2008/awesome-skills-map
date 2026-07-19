#!/usr/bin/env bash
# aggregate.sh — 聚合 GitHub 博主技能地图
# 用法: ./aggregate.sh alchaincyf [--min-stars 10] [--topic claude-skill] [--json] [--output out.md]
# 依赖: gh (GitHub CLI), jq

set -euo pipefail

# ---------- 默认参数 ----------
MIN_STARS=10
INCLUDE_FORKS=false
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
    --topic)        TOPIC_FILTER="$2"; shift 2 ;;
    --json)         JSON_OUTPUT=true; shift ;;
    --output)       OUTPUT_PATH="$2"; shift 2 ;;
    --sort)         SORT_BY="$2"; shift 2 ;;
    --limit)        LIMIT="$2"; shift 2 ;;
    --help|-h)
      echo "用法: $0 <users...> [options]"
      echo "  --min-stars N       最小 star 数 (默认 10)"
      echo "  --include-forks     包含 fork 仓库"
      echo "  --topic TAG         限定主题"
      echo "  --json              输出 JSON 而非 Markdown"
      echo "  --output PATH       写入文件"
      echo "  --sort stars|updated|name"
      echo "  --limit N           单博主最多显示几个 (0=全部)"
      exit 0 ;;
    -*) echo "未知参数: $1"; exit 1 ;;
    *)  USERS+=("$1"); shift ;;
  esac
done

[[ ${#USERS[@]} -eq 0 ]] && { echo "❌ 至少给一个 GitHub 用户名"; exit 1; }
command -v gh >/dev/null || { echo "❌ 需要 gh CLI"; exit 1; }
command -v jq >/dev/null || { echo "❌ 需要 jq"; exit 1; }

# ---------- 分类启发式 ----------
classify() {
  local name="$1" desc="$2"
  local text="$name $desc"
  if echo "$text" | grep -qiE "skill|distill|optim|evolve|darlin|nuwa"; then
    if echo "$text" | grep -qiE "jobs|musk|芒格|karpathy|feynman|naval|trump|taleb|paul graham|张雪峰|张一鸣|孙宇晨|mrbeast|ilya|弗洛伊德|巴菲特|芒格"; then
      echo "👤 人物蒸馏"
    else
      echo "🧠 元能力 Skills"
    fi
  elif echo "$text" | grep -qiE "design|html|slide|cover|visual|image|huashu"; then
    echo "🎨 设计/视觉"
  elif echo "$text" | grep -qiE "content|editor|writing|article|publish|wechat|公众号"; then
    echo "📝 内容创作"
  elif echo "$text" | grep -qiE "claude-code|cursor|mcp|cli|vibe|tool|codex|glm|doubao|weread|fanbox"; then
    echo "🛠 开发工具"
  elif echo "$text" | grep -qiE "book|guide|orange-book|tutorial|deep.dive|orange"; then
    echo "📚 教程/电子书"
  elif echo "$text" | grep -qiE "translat|paper|论文|翻译"; then
    echo "🌐 翻译/论文"
  else
    echo "🌐 其他"
  fi
}

# ---------- 单用户拉取 ----------
fetch_user_repos() {
  local user="$1"
  gh api "users/$user/repos?per_page=100" --jq '
    .[] | {
      name: .name,
      desc: (.description // ""),
      stars: .stargazers_count,
      url: .html_url,
      topics: .topics,
      lang: (.language // ""),
      fork: .fork,
      updated: .updated_at
    }
  '
}

# ---------- 过滤 ----------
filter_repos() {
  local include_forks="$1" topic_filter="$2" min_stars="$3"
  local jq_filter
  jq_filter='select(.stars >= '"$min_stars"')'
  if [[ "$include_forks" != "true" ]]; then
    jq_filter+=' | select(.fork == false)'
  fi
  if [[ -n "$topic_filter" ]]; then
    jq_filter+=' | select(.topics | index("'"$topic_filter"'"))'
  fi
  jq -c "$jq_filter"
}

# ---------- Markdown 渲染 ----------
render_markdown() {
  local user="$1" bio="$2" total="$3" filtered="$4"
  echo "# 🎯 $user 技能地图"
  echo ""
  echo "> **$bio** · $total 公开仓库 · 过滤后 $filtered 个项目"
  echo ""
  echo "## 👤 用户画像"
  echo ""
  echo "$bio"
  echo ""
}

# ---------- 主流程 ----------
for user in "${USERS[@]}"; do
  echo "📡 拉取 $user 的仓库..." >&2
  user_info=$(gh api "users/$user" --jq '{name, bio, public_repos, followers}')
  bio=$(echo "$user_info" | jq -r '.bio // "（无简介）"')
  total_repos=$(echo "$user_info" | jq -r '.public_repos')
  followers=$(echo "$user_info" | jq -r '.followers')

  repos=$(fetch_user_repos "$user" | filter_repos "$INCLUDE_FORKS" "$TOPIC_FILTER" "$MIN_STARS")
  filtered_count=$(echo "$repos" | grep -c . || echo 0)

  if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "$repos" | jq -s --arg user "$user" '{user: $user, repos: .}'
    continue
  fi

  render_markdown "$user" "$bio" "$total_repos" "$filtered_count"

  echo "## 🏆 旗舰三件套（>=1K ⭐）"
  echo ""
  echo "| 仓库 | ⭐ | 简介 |"
  echo "|------|---|------|"
  echo "$repos" | jq -r 'select(.stars >= 1000) "| [\(.name)](\(.url)) | \(.stars) | \(.desc | gsub("\\|";"\\|") | gsub("\n";" ")) |"' | head -10

  echo ""
  echo "## 🧠 元能力 Skills / 👤 人物蒸馏"
  echo ""
  echo "$repos" | jq -r 'select((.desc + " " + .name) | test("skill|distill|darlin|nuwa|jobs|musk|芒格|karpathy|feynman|naval|trump|taleb|张雪峰"; "i")) |
    "| [\(.name)](\(.url)) | \(.stars) | \(.desc | gsub("\\|";"\\|") | gsub("\n";" ")) |"' | head -20

  # ... 更多分类（按需扩展）
  echo ""
  echo "## 📦 全部高质量仓库（>= $MIN_STARS ⭐）"
  echo ""
  echo "| 仓库 | ⭐ | 简介 |"
  echo "|------|---|------|"
  echo "$repos" | jq -r '"'| [\(.name)](\(.url)) | \(.stars) | \(.desc | gsub("\\|";"\\|") | gsub("\n";" ")) |"'
done