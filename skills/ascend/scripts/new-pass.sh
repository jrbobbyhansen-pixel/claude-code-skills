#!/usr/bin/env bash
# new-pass.sh — start one pass on its own branch off the integration branch.
# Usage:  new-pass.sh N AXIS-SLUG
#   e.g.  new-pass.sh 1 ia-boards
set -euo pipefail

N="${1:?pass number required}"
AXIS="${2:?axis slug required}"
BRANCH="ascend/pass-${N}-${AXIS}"

git checkout ascend/integration >/dev/null 2>&1 || {
  echo "no ascend/integration branch — run init.sh first"; exit 2; }
git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"
mkdir -p ".ascend/shots/pass-${N}"
echo "pass $N on branch $BRANCH (forked from ascend/integration)"
echo "BUILD here; commit to this branch only. APPROVE -> merge --no-ff into integration. REVERT -> abandon branch."
