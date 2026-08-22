#!/usr/bin/env bash
# Fail if README's published skill count drifts from skills/*/SKILL.md.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

# Top-level packages only — ignore nested templates such as loom/*/SKILL.md.
skill_files=()
while IFS= read -r path; do
  skill_files+=("$path")
done < <(find skills -mindepth 2 -maxdepth 2 -name SKILL.md | LC_ALL=C sort)

actual="${#skill_files[@]}"
if [[ "$actual" -eq 0 ]]; then
  echo "error: found 0 skills/*/SKILL.md" >&2
  exit 1
fi

readme="README.md"
if [[ ! -f "$readme" ]]; then
  echo "error: $readme not found" >&2
  exit 1
fi

marker="$(sed -n 's/.*<!-- skill-count: \([0-9][0-9]*\) -->.*/\1/p' "$readme" | head -n1)"
headline="$(sed -n 's/.*[Aa] collection of \([0-9][0-9]*\) battle-tested custom skills.*/\1/p' "$readme" | head -n1)"
table="$(grep -cE '^\| \[`/[^`]+`\]\(skills/[^/]+/SKILL\.md\)' "$readme" || true)"

fail=0

if [[ -z "$marker" ]]; then
  echo "error: README.md missing <!-- skill-count: N --> marker" >&2
  fail=1
elif [[ "$marker" != "$actual" ]]; then
  echo "error: README marker says $marker, disk has $actual skills/*/SKILL.md" >&2
  fail=1
fi

if [[ -z "$headline" ]]; then
  echo "error: README.md missing 'A collection of N battle-tested custom skills'" >&2
  fail=1
elif [[ "$headline" != "$actual" ]]; then
  echo "error: README headline says $headline, disk has $actual skills/*/SKILL.md" >&2
  fail=1
fi

if [[ "$table" != "$actual" ]]; then
  echo "error: README library table has $table rows, disk has $actual skills/*/SKILL.md" >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "on disk:" >&2
  printf '  %s\n' "${skill_files[@]}" >&2
  exit 1
fi

echo "ok: $actual skills (headline, marker, and table match disk)"
