# Getting it running — three levels of effort

Pick the level that matches you. Each one is complete on its own.

---

## Level 1 — Five minutes, no code: just use the prompt

You don't need to deploy anything to get most of the benefit.

1. Open [`PROMPT.md`](PROMPT.md) and copy the first box.
2. Paste it into the AI you already use, as a saved instruction so you only do it once:
   - **ChatGPT:** *Projects* → new project → paste into *Instructions*
   - **Claude:** *Projects* → new project → paste into *Project instructions*
   - **Gemini:** *Gems* → new Gem → paste into *Instructions*
3. Ask your question in plain words.

**Two honest limits.** A chatbot can't be *forced* to stick to the listed websites — it's a strong request, so check the references it gives you are real pages on those sites. And **use the best model you have for anything that matters**: the fast/free models read well and miss things. Levels 2 and 3 fix the first problem; only you can fix the second.

---

## Level 2 — An hour, no coding: let an AI agent deploy it for you

The page is designed to be deployed by an AI coding agent. If you use **Claude Code**, **Cursor**, **Codex** or similar, paste this into it:

```text
Deploy the open-source project https://github.com/TeamyTastic/ask-about-your-health for me.
Follow its DEPLOY.md "Level 3" steps exactly. I will provide:
  - a here.now account (help me create one if I don't have it — it needs the paid plan for proxy routes),
  - an Anthropic API key from a dedicated workspace with a monthly spend limit (walk me through creating it; I'll paste the key myself, never show it back to me),
  - the email address to show under the feedback box, and the site password I want.
When it's live, run spec/live-test.py so we both see the turmeric question and the chest-pain check pass, then tell me
how to add the page to an iPhone home screen.
```

The agent does the steps below; you supply the three things only you can (account, key, password).

---

## Level 3 — Step by step, for a person or an agent

You need: a [here.now](https://here.now) account on a paid plan (proxy routes and analytics), and an [Anthropic Console](https://platform.claude.com) account.

**1. Make a dedicated Anthropic key with a spending limit.**
Console → workspace switcher → *Create workspace* (call it `health-page`) → *Settings → Limits* → set a monthly limit (£10 is plenty for a family) → *API keys → Create key*. Copy it; it's shown once.

**2. Store the key at here.now, pinned so it can only ever be sent to Anthropic.**
```bash
curl -sS -o /dev/null -w '%{http_code}\n' -X PUT https://here.now/api/v1/me/variables/ANTHROPIC_API_KEY \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)" -H 'content-type: application/json' \
  -d '{"value":"PASTE-KEY-HERE","allowedUpstreams":["api.anthropic.com"]}'
```
Expect `200`. Then clear that line from your shell history (`history -d $(history 1 | awk '{print $1}')`).

**3. Configure the page.** In `site/index.html`, near the top of the `<script>`, set `CONTACT_EMAIL` (or `""` to hide it), optionally `RESEARCH_NOTEBOOK_URL`, and check `ALLOWED_DOMAINS` — the list is UK-specific by design; change it for your country's health service.

**4. Publish.**
```bash
npx skills add heredotnow/skill --skill here-now -g     # once
~/.claude/skills/here-now/scripts/publish.sh ./site      # prints the live URL
```
Check the finalize output has no `warnings` — an invalid `.herenow/` manifest silently disables the proxy route.

**5. Password-protect it** (replace the slug and choose a password):
```bash
curl -sS -o /dev/null -w '%{http_code}\n' -X PATCH https://here.now/api/v1/publish/YOUR-SLUG/metadata \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)" -H 'content-type: application/json' \
  -d '{"password":"CHOOSE-A-WORD"}'
```
The password also gates the API route, so the paid key can't be used without it.

**6. Make it permanent** (a fresh publish defaults to a temporary site):
```bash
curl -sS -o /dev/null -w '%{http_code}\n' -X PATCH https://here.now/api/v1/publish/YOUR-SLUG/metadata \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)" -H 'content-type: application/json' -d '{"ttlSeconds":null}'
```
Re-run this after **every** republish — publishing with a `--ttl` resets it.

**7. Prove it works.**
```bash
SITE_SLUG=YOUR-SLUG HEALTH_PW='your-password' python3 spec/live-test.py
```
It asks a real question (every citation must be on the allow-list) and a chest-pain question (must return only the 999 line). Costs about 30p.

**8. Put it on their phone.** Send them the link. In Safari: enter the password once (let Safari save it) → Share → *Add to Home Screen* → name it "Health". It opens inside Safari on purpose — standalone web apps lose their saved login after a while and would quietly lock an older person out.

**9. (Optional) Weekly feedback and usage alerts.** `bin/check-feedback.sh` with `SITE_SLUG`, `EXPECTED_COUNTRIES` and a `NOTIFY_CMD` of your choice; `deploy/` has a macOS LaunchAgent example. It never sees questions or answers — only the feedback box and country-level analytics.

---

## Which level should I pick?

| If… | Level |
|---|---|
| You just want better answers from the chatbot you already have | **1** |
| You want a relative to have a one-tap page that cannot read the wrong sites | **2** (agent) or **3** (yourself) |
| The person you're helping would struggle with a password prompt | 3, then switch the site to *restricted* access with their email — one API call, described in the here.now docs |
