#!/usr/bin/env python3
"""
detect.py — Project Profile detector for /ascend.

Resolves the project-specific commands every pass needs (typecheck, lint, test,
build) and how to launch the app, so VERIFY never *guesses* a command. The SKILL
is constant; this profile carries what's project-specific. Mirrors the pattern in
/ship's detect.py and /polish's scan.py. Stdlib only — no dependencies.

Usage:
    python3 detect.py [PATH] [--json]
Default PATH is the current directory.
"""
from __future__ import annotations
import json, sys
from pathlib import Path


def read_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def detect(root: Path) -> dict:
    pkg = read_json(root / "package.json")
    scripts = pkg.get("scripts", {}) or {}
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    def has(*names): return any((root / n).exists() for n in names)
    def dep(*names): return any(n in deps for n in names)
    # prefer an explicit script; else a sensible binary fallback
    def script_or(name_keys, fallback):
        for k in name_keys:
            if k in scripts:
                return f"npm run {k}"
        return fallback

    # ---- type ----
    if dep("react-native") or has("metro.config.js", "metro.config.ts", "app.json") or (root / ".expo").exists():
        ptype = "react-native"
    elif dep("next"):
        ptype = "nextjs"
    elif dep("react", "react-dom"):
        ptype = "react-web"
    elif dep("vue"):
        ptype = "vue"
    elif dep("svelte"):
        ptype = "svelte"
    elif has("Package.swift") or next(root.glob("*.xcodeproj"), None):
        ptype = "swiftui"
    elif has("pubspec.yaml"):
        ptype = "flutter"
    elif pkg:
        ptype = "node"
    else:
        ptype = "unknown"

    # ---- typecheck ----
    # honor an explicit typecheck script regardless of TS detection (monorepo/peer-dep case),
    # then fall back to npx tsc --noEmit only when TS is actually present.
    explicit_tc = next((f"npm run {k}" for k in ("typecheck", "type-check") if k in scripts), "")
    if explicit_tc:
        typecheck = explicit_tc
    elif dep("typescript") or has("tsconfig.json"):
        typecheck = "npx tsc --noEmit"
    else:
        typecheck = ""

    # ---- lint / test / build ----
    lint = script_or(["lint"], "npx eslint ." if dep("eslint") else "")
    test = script_or(["test"], "")
    build = script_or(["build"], "")

    # ---- launch adapter (how VERIFY runs/renders the app) ----
    if ptype == "react-native":
        # simulators rarely boot in a headless agent turn -> render-test fallback
        launch = "render-test" if dep("react-test-renderer", "@testing-library/react-native") else "render-test?"
        launch_cmd = script_or(["ios", "android", "start"], "npx expo start" if dep("expo") else "npx react-native start")
    elif ptype in ("nextjs", "react-web", "vue", "svelte", "node"):
        launch = "dev-server"
        launch_cmd = script_or(["dev", "start"], "npm run dev")
    elif ptype == "flutter":
        launch, launch_cmd = "device", "flutter run"
    elif ptype == "swiftui":
        launch, launch_cmd = "simulator", "xcodebuild"
    else:
        launch, launch_cmd = "unknown", ""

    return {
        "type": ptype,
        "typecheck": typecheck,
        "lint": lint,
        "test": test,
        "build": build,
        "launch_adapter": launch,      # dev-server | render-test | simulator | device | unknown
        "launch_cmd": launch_cmd,
        "has_tests": bool(test),
        "is_git": (root / ".git").exists(),
        "notes": _notes(ptype, typecheck, test),
    }


def _notes(ptype, typecheck, test):
    n = []
    if ptype == "react-native":
        n.append("RN/Metro does NOT type-check at bundle time; run the typecheck command explicitly.")
        n.append("Simulator usually unavailable headless -> use render-test tier (mount App + new surface).")
    if not test:
        n.append("No test script found -> VERIFY cannot guard regressions; say so at the review gate.")
    if not typecheck:
        n.append("No TypeScript detected -> typecheck tier unavailable.")
    return n


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]).resolve() if args else Path.cwd()
    prof = detect(root)
    if "--json" in sys.argv or True:
        print(json.dumps(prof, indent=2))


if __name__ == "__main__":
    main()
