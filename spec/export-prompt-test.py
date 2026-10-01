#!/usr/bin/env python3
"""Offline checks for bin/export-prompt.py: PROMPT.md has not drifted from site/index.html (#34),
and a changed declaration gives a clear message, not AttributeError (#35)."""
import pathlib, shutil, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
def run(root, *args): return subprocess.run([sys.executable, str(root / "bin/export-prompt.py"), *args], capture_output=True, text=True)

# 34: committed PROMPT.md == what the script would write
r = run(ROOT, "--check")
assert r.returncode == 0, f"PROMPT.md drifted from site/index.html (run bin/export-prompt.py): {r.stdout}{r.stderr}"

# 35: broken declarations -> clean one-line exit naming the missing thing
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t); (t / "bin").mkdir(); (t / "site").mkdir()
    shutil.copy(ROOT / "bin/export-prompt.py", t / "bin"); shutil.copy(ROOT / "PROMPT.md", t / "PROMPT.md")
    (t / "site/index.html").write_text("<html>no declarations here</html>")
    r = run(t)
    assert r.returncode != 0 and "AttributeError" not in r.stderr and "SYSTEM" in r.stderr, f"unclear failure: {r.stderr[-300:]}"
    # drift is detected: tampered PROMPT.md fails --check
    shutil.copy(ROOT / "site/index.html", t / "site/index.html"); (t / "PROMPT.md").write_text("stale")
    assert run(t, "--check").returncode != 0, "--check missed a stale PROMPT.md"
print("export-prompt checks ok")
