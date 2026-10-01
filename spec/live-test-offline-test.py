#!/usr/bin/env python3
"""Offline checks for spec/live-test.py with the network faked: bad declarations fail clearly (#35),
Q2 citations are checked against the allowlist (#36), imports are tidy (#64). Touches only a temp copy."""
import ast, json, os, pathlib, shutil, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = (ROOT / "spec/live-test.py").read_text()

# 64: no duplicate imports; urllib.parse imported before first use
imports = [(n.lineno, a.name) for n in ast.parse(SRC).body if isinstance(n, ast.Import) for a in n.names]
names = [n for _, n in imports]
assert len(names) == len(set(names)), f"duplicate imports: {sorted(n for n in names if names.count(n) > 1)}"
imp = min((l for l, n in imports if n == "urllib.parse"), default=None)
use = next((i for i, l in enumerate(SRC.splitlines(), 1) if "urllib.parse." in l), None)
assert imp and imp <= use, "urllib.parse not imported before first use"

HARNESS = r'''
import json, sys, runpy, urllib.request, urllib.error
BAD = sys.argv[1] == "bad"
class R:
    status = 200
    def __init__(s, d=b"{}"): s.d = d
    def read(s, *a): return s.d
    def __enter__(s): return s
    def __exit__(s, *a): pass
n = {"ask": 0}
def fake(req, timeout=None):
    url = req.full_url if hasattr(req, "full_url") else req
    if url.endswith("/api/ask"):
        n["ask"] += 1
        if n["ask"] == 1:
            c = [{"type": "text", "text": "## Short answer\nIt may help.", "citations": [{"url": "https://www.nhs.uk/x"}]}]
        else:
            c = [{"type": "text", "text": "URGENT-999", "citations": [{"url": "https://evil.example/x" if BAD else "https://www.nhs.uk/y"}]}]
        return R(json.dumps({"content": c, "stop_reason": "end_turn", "usage": {}}).encode())
    return R()
urllib.request.urlopen = fake
runpy.run_path("spec/live-test.py", run_name="__main__")
'''
def run(mode, html=None):
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t); (t / "spec/compare").mkdir(parents=True); (t / "site").mkdir()
        shutil.copy(ROOT / "spec/live-test.py", t / "spec"); shutil.copy(ROOT / "site/index.html", t / "site")
        if html is not None: (t / "site/index.html").write_text(html)
        (t / "h.py").write_text(HARNESS)
        env = {**os.environ, "SITE_SLUG": "x", "HEALTH_PW": "x"}
        return subprocess.run([sys.executable, "h.py", mode], cwd=t, env=env, capture_output=True, text=True)

r = run("good"); assert r.returncode == 0 and "ALL ASSERTIONS PASSED" in r.stdout, "control run failed:\n" + r.stdout[-400:] + r.stderr[-400:]
r = run("bad"); assert r.returncode != 0 and "AssertionError" in r.stderr, "off-allowlist Q2 citation was not caught"
r = run("good", html="<html></html>")
assert r.returncode != 0 and "AttributeError" not in r.stderr and "SYSTEM" in r.stderr, f"unclear failure: {r.stderr[-300:]}"
print("live-test offline checks ok")
