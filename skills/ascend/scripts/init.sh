#!/usr/bin/env bash
# init.sh — set up the /ascend working area safely, ONCE, before the loop.
# Order matters: stash the dirty tree FIRST, then branch, then COMMIT the
# .gitignore entry on the integration branch — so .ascend/ is really ignored,
# is committed (not floating in the working tree), and survives the stash.
#
# Usage:  init.sh [BASE_BRANCH]      (BASE defaults to the current branch)
# After this, call:  state.py init --scope ... --loops N --stack ...
set -euo pipefail

BASE="${1:-}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "NOT-A-GIT-REPO: /ascend needs version control for safe, revertible passes."
  echo "  -> run 'git init && git add -A && git commit -m baseline' first, OR"
  echo "  -> ask the user to confirm copy-based snapshots instead. Do NOT auto-apply without revert."
  exit 2
fi

if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "NO-COMMITS-YET: make an initial commit so passes are revertible."
  echo "  -> git add -A && git commit -m baseline"
  exit 2
fi

# capture the base branch BEFORE we move off it
[ -z "$BASE" ] && BASE="$(git rev-parse --abbrev-ref HEAD)"

# 1) quarantine a dirty tree FIRST so each pass diff contains ONLY ascend's changes
STASHED="no"
if [ -n "$(git status --porcelain)" ]; then
  git stash push -u -m "ascend: pre-loop stash $(git rev-parse --short HEAD)" >/dev/null
  STASHED="yes"
  echo "dirty tree stashed (git stash) — restore with 'git stash pop' after the loop"
fi

# 2) integration branch off BASE (accepted passes merge here; main untouched until SYNTH)
git checkout -b ascend/integration "$BASE" 2>/dev/null || git checkout ascend/integration

# 3) gitignore .ascend/ and COMMIT it on the integration branch (real + survives the stash)
if [ ! -f .gitignore ] || ! grep -qxF ".ascend/" .gitignore 2>/dev/null; then
  printf '\n# /ascend working artifacts\n.ascend/\n' >> .gitignore
  git add .gitignore
  git commit -m "ascend: ignore working artifacts (.ascend/)" >/dev/null
  echo "committed .ascend/ to .gitignore on ascend/integration"
fi

mkdir -p .ascend/shots
echo "integration branch: ascend/integration (base=$BASE, stashed=$STASHED)"
echo "NOTE: /ascend works on shared-tree BRANCHES (not isolated worktrees) — that is why a dirty tree is stashed."
