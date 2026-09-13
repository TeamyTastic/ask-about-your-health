#!/usr/bin/env python3
"""Regenerate PROMPT.md from the system prompt inside site/index.html, so the copyable prompt never drifts from the live one."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
html = (root / "site/index.html").read_text()
system = re.search(r"const SYSTEM = `(.*?)`;", html, re.S).group(1).strip()
domains = re.findall(r'"([a-z0-9.\-]+\.[a-z]+(?:/[^"]*)?)"', re.search(r"const ALLOWED_DOMAINS = \[(.*?)\];", html, re.S).group(1))
SEARCH_SENTENCE = "You have web search restricted to trusted UK and academic medical sites. Use it on every question. Never answer from memory."
SEARCH_REPLACEMENT = "Use web search on every question and read ONLY these sites: " + ", ".join(domains) + ". If a result is from any other site, ignore it. Never answer from memory."
SOURCES_SENTENCE = "Do not write a sources or references section and do not paste URLs; the page builds the sources list from your citations."
SOURCES_REPLACEMENT = "At the end, list the pages you actually read, with their full web addresses. If you did not read any page from the sites above, say so and stop."
chatbot_version = system.replace(SEARCH_SENTENCE, SEARCH_REPLACEMENT).replace(SOURCES_SENTENCE, SOURCES_REPLACEMENT)
out = f"""# The prompt

This is the exact instruction the page gives the AI on every question. Two ways to use it.

## 1. Paste it into the AI you already use

Copy everything in the box below into ChatGPT, Claude, Gemini or whichever you use — ideally as a saved
"project", "custom instructions" or "Gem" so you only do it once — then ask your question in plain words.

> **Please read first.** A chatbot cannot be *forced* to read only the listed sites the way the deployed page
> can (the page uses an API feature that blocks every other site). Pasted as text, this is a strong request, not a
> guarantee — so **check that every reference it gives you is a real page on one of the listed sites** before you
> trust it. **And match the model to the stakes:** for anything that matters — a symptom, a medicine, a decision —
> use the most capable model you have access to, not the fast or free one. In our testing the cheaper models
> gave answers that read well but missed the warning that mattered.

```text
{chatbot_version}
```

## What the page's own version changes

The page uses this same prompt, except for two sentences:

- Site restriction is enforced by the API (`allowed_domains` on the web search tool), not requested in words. The page's prompt says: "{SEARCH_SENTENCE}"
- The page builds its own sources list from citations, so it tells the model not to write one, rather than asking it to list pages read. The page's prompt says: "{SOURCES_SENTENCE}"

Allowed sites (enforced with `allowed_domains` on Anthropic's web search tool): `{"`, `".join(domains)}`

---
*Generated from `site/index.html` by `bin/export-prompt.py` — edit the prompt there, then re-run it.*
"""
(root / "PROMPT.md").write_text(out)
print("PROMPT.md written:", len(out.split()), "words")
