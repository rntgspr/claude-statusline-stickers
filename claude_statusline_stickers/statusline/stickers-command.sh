#!/bin/bash
# Claude Code statusLine
#   line 1: current dir (white) + git branch (blue) ... model · ctx · cost (right)
#   then:   the agent's sprite, as colour glyph text from the patched font
#
# The sprite is chosen by the AGENT — the folder right above the project dir
# (agentic-workspace/<agent>/<project>). build.py emits a manifest
# mapping each theme's agentNames to a glyph-text file; this script looks the
# agent up there and cats the matching file (plain PUA text that survives the
# statusline escape filter). Needs the ClaudeStatusLineStickers font installed and
# ligatures ON. Outside agentic-workspace, no sprite is shown.
#
# Toggle: set "hideStickers": true in any settings.json (project .claude/,
# .claude/settings.local.json, or ~/.claude/) to hide the sprite.

CACHE="$HOME/.claude/claude-statusline-stickers"
MANIFEST="$CACHE/manifest.json"

# Read JSON from stdin
input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // empty' 2>/dev/null)
[ -z "$cwd" ] && cwd="$PWD"
proj=$(echo "$input" | jq -r '.workspace.project_dir // empty' 2>/dev/null)
[ -z "$proj" ] && proj="$cwd"
dir="${cwd/#$HOME/~}"

# Model + context-window usage (graceful: any missing field just drops its segment)
model=$(echo "$input" | jq -r '.model.display_name // empty' 2>/dev/null)
model_id=$(echo "$input" | jq -r '.model.id // empty' 2>/dev/null)
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty' 2>/dev/null)
ctx_in=$(echo "$input"  | jq -r '.context_window.total_input_tokens // empty' 2>/dev/null)
ctx_max=$(echo "$input" | jq -r '.context_window.context_window_size // empty' 2>/dev/null)
session_usd=$(echo "$input" | jq -r '.cost.total_cost_usd // empty' 2>/dev/null)

# Per-MTok input price per model (USD). Used to estimate cost of current context.
case "$model_id" in
  claude-fable-5|claude-mythos-5)              in_price=10.00 ;;
  claude-opus-4-8|claude-opus-4-7|claude-opus-4-6|claude-opus-4-5) in_price=5.00 ;;
  claude-sonnet-4-6|claude-sonnet-4-5)         in_price=3.00 ;;
  claude-haiku-4-5*)                           in_price=1.00 ;;
  *)                                           in_price="" ;;
esac

# Compact token formatter: 1234567->1.2M, 84000->84k, 512->512
fmt_k() {
  local n=$1
  if   [ "$n" -ge 1000000 ]; then awk -v x="$n" 'BEGIN{printf "%.1fM", x/1000000}'
  elif [ "$n" -ge 1000 ];    then echo "$(( (n + 500) / 1000 ))k"
  else echo "$n"
  fi
}

# hideStickers toggle — first settings file that defines it wins (local > project > global)
hide=false
for f in "$proj/.claude/settings.local.json" "$proj/.claude/settings.json" "$HOME/.claude/settings.json"; do
  if [ -f "$f" ]; then
    v=$(jq -r '.hideStickers // empty' "$f" 2>/dev/null)
    [ "$v" = "true" ] && { hide=true; break; }
    [ "$v" = "false" ] && break
  fi
done

# Agent name can come from the project dir itself OR the folder right above it
# (agentic-workspace/<agent>/<project>, or a project named after the agent). The
# current dir is tried first, so on conflict it wins over the parent.
agent_cur=$(basename "$proj")
agent_parent=$(basename "$(dirname "$proj")")

# Git branch, full — read from the JSON cwd, not the process PWD
git_branch=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" branch 2>/dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')

# Resolve the agent to a sprite via the build manifest, then cat its glyph text
# (plain PUA chars the font renders). The current dir is tried first so it wins
# on conflict; then the parent dir. Unknown agents inside agentic-workspace fall
# back to the pokéball; outside agentic-workspace, no sprite.
sprite=""
if [ "$hide" != "true" ] && [ -s "$MANIFEST" ]; then
  txt=$(jq -r --arg a "$agent_cur" '.agents[$a].txt // empty' "$MANIFEST" 2>/dev/null)
  [ -z "$txt" ] && txt=$(jq -r --arg a "$agent_parent" '.agents[$a].txt // empty' "$MANIFEST" 2>/dev/null)
  if [ -z "$txt" ] && printf '%s' "$proj" | grep -q '/agentic-workspace/'; then
    txt=$(jq -r '.agents.pokeball.txt // empty' "$MANIFEST" 2>/dev/null)
  fi
  [ -n "$txt" ] && [ -s "$CACHE/$txt" ] && sprite=$(cat "$CACHE/$txt")
fi

# Terminal width — needed to right-align the cost segments on line 1
cols=${COLUMNS:-0}
[ "$cols" -le 0 ] && cols=$(tput cols 2>/dev/null || echo 80)

# Strip ANSI for visible-length measurement
visible_len() { printf '%b' "$1" | sed $'s/\x1b\\[[0-9;]*m//g' | awk '{print length}'; }

# --- Line 1 LEFT: directory (white) + branch (blue) --------------------------
left="\033[37m${dir}\033[0m"
[ -n "$git_branch" ] && left="$left  \033[34m${git_branch}\033[0m"

# --- Line 1 RIGHT: model · ctx % tokens · $ctx · Σ $session ------------------
right=""
[ -n "$model" ] && right="\033[36m${model}\033[0m"

if [ -n "$ctx_pct" ]; then
  # green < 50, yellow 50–79, red >= 80
  if   [ "$ctx_pct" -ge 80 ]; then c=31
  elif [ "$ctx_pct" -ge 50 ]; then c=33
  else c=32
  fi
  seg="\033[${c}mctx ${ctx_pct}%\033[0m"
  if [ -n "$ctx_in" ] && [ "$ctx_in" -gt 0 ] && [ -n "$ctx_max" ] && [ "$ctx_max" -gt 0 ]; then
    seg="$seg \033[90m$(fmt_k "$ctx_in")/$(fmt_k "$ctx_max")\033[0m"
  fi
  [ -n "$right" ] && right="$right \033[90m·\033[0m $seg" || right="$seg"
fi

if [ -n "$ctx_in" ] && [ "$ctx_in" -gt 0 ] && [ -n "$in_price" ]; then
  ctx_usd=$(awk -v t="$ctx_in" -v p="$in_price" 'BEGIN{printf "%.3f", t*p/1000000}')
  seg="\033[35m\$${ctx_usd}\033[0m"
  [ -n "$right" ] && right="$right \033[90m·\033[0m $seg" || right="$seg"
fi

if [ -n "$session_usd" ] && [ "$session_usd" != "0" ]; then
  sess_fmt=$(awk -v u="$session_usd" 'BEGIN{printf "%.2f", u}')
  seg="\033[36mΣ \$${sess_fmt}\033[0m"
  [ -n "$right" ] && right="$right \033[90m·\033[0m $seg" || right="$seg"
fi

# Render line 1: left, padding, then right pinned to terminal edge.
# If the right block is wider than the terminal, fall back to a newline so
# nothing is truncated by the renderer.
if [ -n "$right" ]; then
  lvis=$(visible_len "$left")
  rvis=$(visible_len "$right")
  pad=$(( cols - lvis - rvis ))
  if [ "$pad" -ge 2 ]; then
    printf '%b%*s%b' "$left" "$pad" "" "$right"
  else
    printf '%b\n%b' "$left" "$right"
  fi
else
  printf '%b' "$left"
fi

# --- Then: the agent's sprite (left-aligned, last; no trailing blank line) ----
[ -n "$sprite" ] && printf '\n%s' "$sprite"
exit 0
