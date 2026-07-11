#!/usr/bin/env python3
"""evolve scan.py — deterministic plumbing inventory for /evolve Phase 0.

Walks the repo (stdlib only, no installs), flags UI-surface files, and greps
for candidate plumbing — endpoints, stores, model calls, navigation — that the
Surface Dossier must ACCOUNT FOR (covered, or dismissed with a reason). The
accounting keys it emits are the coverage contract: verify.py --check-dossier
refuses to open ideation while any key is UNCHARTED.

Usage:
  python3 scan.py <root> [--surface <path>] --json > .evolve/scan.json

--surface narrows the `surfaces` list (where ideation focuses) but NEVER the
candidate sweep — CONNECT needs the whole repo's plumbing to find wires.
"""
import argparse
import json
import os
import re
import sys

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", ".expo", ".expo-shared",
    "coverage", ".evolve", ".polish", ".ascend", ".gauntlet", "venv", ".venv",
    "__pycache__", "vendor", "target", ".turbo", "out", ".cache", "Pods",
    "DerivedData", ".gradle", ".idea", ".vscode",
}
CODE_EXT = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte",
    ".py", ".rb", ".go", ".dart", ".swift", ".kt", ".java", ".php", ".rs",
}
UI_EXT = {".tsx", ".jsx", ".vue", ".svelte"}
UI_DIR_HINT = re.compile(r"(^|/)(screens?|pages?|views?|components?|features?|layouts?|app)(/|$)", re.I)

MAX_FILE_BYTES = 1_000_000
PER_FILE_PER_CAT = 3      # matches recorded per file per category (existence is what matters)
PER_CAT_CAP = 500         # hard cap per category; overflow is announced, never silent

CATEGORIES = {
    "endpoint": [
        r"\bfetch\s*\(", r"\baxios\b", r"\bcreateApi\b", r"\buseQuery\b",
        r"\buseMutation\b", r"\buseSWR\b", r"\bgql`", r"\btrpc\b",
        r"\bsupabase\.", r"\bprisma\.", r"\bfirestore\b", r"\bknex\b",
        r"\bapp\.(get|post|put|patch|delete)\s*\(",
        r"\brouter\.(get|post|put|patch|delete)\s*\(",
        r"@(Get|Post|Put|Patch|Delete)\s*\(",
        r"\burlpatterns\b", r"\b@app\.route\b", r"\bHandleFunc\b",
    ],
    "store": [
        r"\bcreateSlice\b", r"\bconfigureStore\b", r"\bcreateStore\b",
        r"\bzustand\b", r"\bcreateContext\b", r"\bdefineStore\b",
        r"\batom\s*\(", r"\bselector\s*\(", r"\bobservable\b",
        r"\bwritable\s*\(", r"\bmakeAutoObservable\b", r"\bcreate\s*\(\s*\(\s*set\b",
    ],
    "model_call": [
        r"\banthropic\b", r"\bAnthropic\b", r"\bopenai\b", r"\bOpenAI\b",
        r"\bmessages\.create\b", r"\bchat\.completions\b",
        r"\bgenerateText\b", r"\bstreamText\b", r"\bgenerateObject\b",
        r"claude-", r"gpt-4", r"gpt-5", r"\bgemini\b", r"\bollama\b",
        r"\bbedrock\b", r"\bcompletion\s*\(",
    ],
    "navigation": [
        r"\bcreateBrowserRouter\b", r"<Route\b", r"\buseNavigate\b",
        r"\bcreateStackNavigator\b", r"\bcreateBottomTabNavigator\b",
        r"\bcreateNativeStackNavigator\b", r"<(Stack|Tabs?|Drawer)\.Screen\b",
        r"\bnavigation\.navigate\s*\(", r"\brouter\.push\s*\(", r"\buseRouter\b",
    ],
}
COMPILED = {cat: [re.compile(p) for p in pats] for cat, pats in CATEGORIES.items()}


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for fn in sorted(filenames):
            ext = os.path.splitext(fn)[1].lower()
            if ext in CODE_EXT:
                yield os.path.join(dirpath, fn)


def is_surface(rel, ext, text):
    if ext in UI_EXT:
        return True
    if UI_DIR_HINT.search(rel.replace(os.sep, "/")) and ("<" in text or "render" in text):
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--surface", default=None, help="narrow the surfaces list (never the candidate sweep)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    surfaces, skipped_large, files_scanned = [], [], 0
    candidates = {cat: [] for cat in CATEGORIES}
    truncated = {cat: False for cat in CATEGORIES}

    for path in iter_files(root):
        rel = os.path.relpath(path, root)
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                skipped_large.append(rel)
                continue
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        files_scanned += 1
        ext = os.path.splitext(path)[1].lower()
        if is_surface(rel, ext, text):
            surfaces.append(rel)
        lines = text.splitlines()
        per_cat_hits = {cat: 0 for cat in CATEGORIES}
        for lineno, line in enumerate(lines, 1):
            for cat, pats in COMPILED.items():
                if per_cat_hits[cat] >= PER_FILE_PER_CAT:
                    continue
                if any(p.search(line) for p in pats):
                    if len(candidates[cat]) >= PER_CAT_CAP:
                        truncated[cat] = True
                        continue
                    candidates[cat].append(
                        {"file": rel, "line": lineno, "snippet": line.strip()[:100]}
                    )
                    per_cat_hits[cat] += 1

    if args.surface:
        want = args.surface.rstrip("/").replace(os.sep, "/")
        surfaces = [
            s for s in surfaces
            if s.replace(os.sep, "/").startswith(want) or want in s.replace(os.sep, "/")
        ]

    accounting_keys = sorted({
        f"{cat}::{c['file']}" for cat, items in candidates.items() for c in items
    })
    out = {
        "root": root,
        "surface_filter": args.surface,
        "files_scanned": files_scanned,
        "skipped_large": skipped_large,
        "surfaces": surfaces,
        "candidates": candidates,
        "truncated": truncated,
        "accounting_keys": accounting_keys,
    }
    if args.json:
        json.dump(out, sys.stdout, indent=2)
        print()
    else:
        print(f"scanned {files_scanned} files · {len(surfaces)} surfaces")
        for cat, items in candidates.items():
            note = " (TRUNCATED — raise the cap or narrow the repo)" if truncated[cat] else ""
            print(f"  {cat}: {len(items)} candidates in {len({i['file'] for i in items})} files{note}")
        print(f"  accounting keys the dossier must cover or dismiss: {len(accounting_keys)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
