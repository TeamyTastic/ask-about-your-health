#!/usr/bin/env python3
"""Playwright sense-check of the live page. Owner-run (a browser cannot launch from the agent sandbox):

    cd ~/Projects/health-search && HEALTH_PW='…' "$TMPDIR/pw/bin/python" spec/ui-check.py
    (or any python with `pip install playwright && playwright install chromium`)

Logs in through the password gate, then captures spec/screens/*.png:
  phone-light / phone-dark (390x844), tablet (1024), print emulation, a real question end-to-end,
  and the 999 red-flag banner. Also asserts: no horizontal overflow at 390px, fonts loaded,
  no console errors, Save → appears in Saved answers → Remove."""
import os, sys, time, pathlib
from playwright.sync_api import sync_playwright

SITE = "https://" + (os.environ.get("SITE_SLUG") or sys.exit("set SITE_SLUG=<your-here-now-slug>")) + ".here.now/"
OUT = pathlib.Path(__file__).with_name("screens"); OUT.mkdir(exist_ok=True)
PW = os.environ.get("HEALTH_PW") or sys.exit("set HEALTH_PW")
errors = []

def shot(pg, name, full=True): pg.screenshot(path=str(OUT / f"{name}.png"), full_page=full); print("  saved", name)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for scheme in ("light", "dark"):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme=scheme, is_mobile=True, has_touch=True)
        pg = ctx.new_page(); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "401" not in m.text else None)  # the gate itself 401s before login
        pg.goto(SITE); pg.fill("input[name=password]", PW); pg.click("button[type=submit]"); pg.wait_for_load_state()
        if pg.locator("input[name=password]").count(): sys.exit("password gate refused HEALTH_PW — replace the placeholder with the real site password")
        pg.wait_for_selector("#q", timeout=20000)
        pg.wait_for_timeout(1500)  # fonts
        w = pg.evaluate("document.documentElement.scrollWidth"); assert w <= 390, f"horizontal overflow at 390px: {w}"
        fonts = pg.evaluate("Array.from(document.fonts).filter(f=>f.status==='loaded').map(f=>f.family)")
        assert any("Atkinson" in f for f in fonts) and any("Fraunces" in f for f in fonts), f"fonts not loaded: {fonts}"
        shot(pg, f"phone-{scheme}")
        if scheme == "light":
            # real question end-to-end
            pg.fill("#q", "Does vitamin D help prevent falls?"); pg.click("#go")
            pg.wait_for_selector("#searches li", timeout=60000); shot(pg, "phone-working", full=False)
            pg.wait_for_function("document.getElementById('go').disabled === false", timeout=180000)
            assert pg.locator("#sources a").count() > 0, "no sources rendered"
            assert "## " not in pg.inner_text("#body"), "raw markdown leaked"
            shot(pg, "phone-answer")
            pg.click("#save"); pg.wait_for_function("document.getElementById('save').textContent.startsWith('Saved')", timeout=20000)
            pg.wait_for_selector("#savedwrap:not([hidden]) details", timeout=20000); shot(pg, "phone-saved")
            pg.click("#savedwrap details summary"); pg.click("#savedwrap .remove"); pg.wait_for_timeout(1500)
            pg.emulate_media(media="print"); shot(pg, "print"); pg.emulate_media(media="screen")
            # red flag → banner only
            pg.fill("#q", "crushing chest pain and my arm is numb"); pg.click("#go")
            pg.wait_for_function("document.getElementById('go').disabled === false", timeout=120000)
            assert pg.locator(".b999").count() == 1 and pg.inner_text("#body").strip() == "", "999 banner not exclusive"
            shot(pg, "phone-999", full=False)
        ctx.close()
    ctx = b.new_context(viewport={"width": 1024, "height": 900}); pg = ctx.new_page()
    pg.goto(SITE); pg.fill("input[name=password]", PW); pg.click("button[type=submit]"); pg.wait_for_selector("#q"); pg.wait_for_timeout(1200); shot(pg, "tablet")
    b.close()
assert not errors, f"console errors: {errors}"
print("UI CHECK PASSED —", len(list(OUT.glob('*.png'))), "screenshots in", OUT)
