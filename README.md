# Ask About Your Health

A one-page web app that lets a non-technical person — built for elderly parents — type a health question in their own words and get a cautious, plain-English answer written **only from trusted UK medical sources**, with every reference being a page that was actually read, and ending with questions to take to their GP or pharmacist.

No app store, no account, no chat history. A password-protected link on the home screen.

**Just want the prompt?** → [`PROMPT.md`](PROMPT.md) — paste it into ChatGPT, Claude or Gemini and you have most of the benefit in five minutes.
**Want the page for someone?** → [`DEPLOY.md`](DEPLOY.md) — three levels, from "no code" to "an AI agent does it for you".

**Live example (private):** the author runs one for their family. This repo is the template.

---

## The job to be done

> When an older relative has a health worry, they want to understand it well enough to have a good conversation with their doctor — without being frightened by a search engine, sold to by a supplement site, or confidently misled by a chatbot.

Concretely, it replaces three worse habits:

| Instead of… | Which fails because… | This page… |
|---|---|---|
| Googling the symptom | first results are ads, forums and US content | reads only NHS, NICE, Cochrane, PubMed and the official UK medicine leaflets |
| Asking ChatGPT | fluent, confident, ~50% problematic on health questions (see below), invents references | searches every time, can only cite pages it opened, is told to say "unclear" |
| Not asking anyone | the worry festers until the appointment | produces a printable one-page sheet with three questions to ask |

It is explicitly **not** a diagnosis tool and never gives doses. Its output is a better GP appointment.

## Why it is built this way — the evidence

In 2026 Tiller et al. put 250 health questions to five popular chatbots and had experts grade the answers (*Generative AI-driven chatbots and medical misinformation: an accuracy, referencing and readability audit*, **BMJ Open**, [PMC13158598](https://pmc.ncbi.nlm.nih.gov/articles/PMC13158598/); discussed on [The Real Science of Sport Podcast](https://shows.acast.com/realscienceofsport/episodes/can-you-trust-ai-for-health-and-training-advice), May 2026):

- **50%** of answers were problematic; **1 in 5** could have caused physical harm
- **30%** credible on nutrition questions; even on the best subjects (cancer, vaccines) about 3 in 10 were problematic
- **<1%** of questions were declined (2 of 250) — chatbots would rather answer than admit ignorance
- **No chatbot produced a fully accurate reference list for any question**; the median list was 40% complete
- Answers read at university level

The four failure modes the audit names, and the structural answer to each:

| Failure | Structural fix (not a prompt request) |
|---|---|
| Hallucination — answering from memory | The model must search on every question and the API only lets it read allow-listed domains (`allowed_domains` on Anthropic's server-side web search) |
| "Frankenstein references" — real authors and journals stitched into papers that don't exist | The page builds the sources list from the API's citation objects, i.e. pages actually fetched. The model is told not to write a references section |
| Sycophancy / completeness bias | Prompt permits empty sections and zero questions; "the evidence here is unclear" is a complete answer; harms must appear alongside benefits |
| Marketing-polluted training data | Supplement sellers and blogs are simply not on the domain list |

Plus what the podcast's own recommendations map to: neutral framing (benefits *and* risks), stated reader context (older adult, UK), checkable references, confidence matched to evidence, and the **risk-severity rule** — narrow high-consequence decisions go to a clinician. The one recommendation deliberately *not* adopted is "run it through three or four chatbots": models reading the same NHS pages agree whether or not they are right, so checkable pages replace that safeguard.

## How it works

```
 you type a question
        │
        ▼
 static page (index.html) ── fetch('./api/ask') ──▶ here.now proxy route
                                                        │ injects ANTHROPIC_API_KEY server-side
                                                        ▼
                                              api.anthropic.com/v1/messages
                                              + web_search tool, allowed_domains = [nhs.uk, nice.org.uk, …]
                                                        │ searches run on Anthropic's side, citations returned
                                                        ▼
 answer streams back ◀──────────────────────────────────┘
 page renders sections, builds "Pages it read" from the citations
 Print · Copy · Share · Save (saved answers stay in the browser's own storage)
```

**There is no backend.** [here.now](https://here.now) hosts static files and provides two server features this uses: *proxy routes* (an upstream API call with a secret injected from an encrypted account variable, behind the site password) and *Site Data* (a small record store, used only for the optional feedback box). The site password also gates the proxy route, so the paid key is unreachable without it.

**Safety behaviour in the prompt** (`site/index.html`, `SYSTEM`):

- Three-tier triage: emergencies (chest pain, stroke signs even if resolved, sepsis, head injury, heavy bleeding, severe headache…) return *only* "Phone 999"; same-day concerns (black stools, new lump, unexplained weight loss…) get a "phone 111 / your GP today" banner above the answer
- Anything taken, mixed or stopped — prescription, over-the-counter, supplement, herbal — may be explained but never concluded "safe"; routed to a pharmacist, who can check the real medicine list for free
- Never a dose, never "stop a medicine", never a diagnosis; "Is this the right question?" may reframe (e.g. new memory change at 80 needs assessing before "which vitamin helps memory")
- Fixed six-section shape so deviation is visible; explain-type questions get "How it works / What to expect"

**Privacy model:** the question goes to Anthropic and to the searched sites, nowhere else. Nothing is stored unless the reader presses *Save*, and saved answers live in that browser's `localStorage` only. The site owner can read the feedback box and see here.now's content-blind analytics (countries, approximate visitors — raw IPs are not exposed); the owner cannot see questions or answers.

## What an independent review changed

Before real use, the design was steel-manned and attacked by a separate reviewer. Changes that came out of it, in priority order:

1. Binary "999 or nothing" triage → three tiers, plus the missing red flags (resolved TIA, sepsis, black stools, sudden severe headache) — fixes both missed emergencies and alarm fatigue
2. Ingestible guard → pharmacist; `medicines.org.uk` (the official UK leaflets, i.e. the interaction source) added; a US site (Mayo Clinic — wrong drug names, wrong OTC rules) removed
3. Spend cap on a dedicated API key; nothing logged by default
4. A visible "Looking up: …" state during the 30–60 s search, because an elderly user who sees nothing taps again
5. Print output: one side of A4, question verbatim at the top, max three questions, an honest "AI-written, not clinically checked" line

Rejected: a medication list in the prompt (client-side it would publish the prescriptions to anyone with the URL) and multi-model consensus (see above).

## Model choice (measured, n=1 per model — treat as indicative)

Same question, same prompt, same allow-list:

| Model | Time | Sources | Found the liver-injury / warfarin warning? | Cost per question |
|---|---|---|---|---|
| Claude Opus 5 + Anthropic search | ~30 s | 7–10 incl. NHS, NICE, MHRA | yes | ≈ $0.35 |
| Claude Sonnet 5 + Anthropic search | ~20 s | 3 incl. NHS Wales | yes | ≈ $0.14 |
| DeepSeek V4.1 Flash via OpenRouter + Exa | ~25 s | 6, PubMed/PMC only | **no** — Exa returned ~4k tokens of abstracts vs ~47k tokens of page content | ≈ $0.01 |
| GPT-5.5 via OpenRouter ZDR + OpenAI search | ~80 s | 5 incl. NICE, Cochrane, NHS | yes | ≈ $0.33 |

Opus is the default because the missing paragraph in the cheap run was the one that mattered. Full answers are in `spec/compare/`. Cost is dominated by the ~50k input tokens of fetched pages, not by output.

### Zero data retention (ZDR) — the privacy-first alternative

*ZDR* means the provider deletes your prompt and the answer as soon as it has replied — nothing logged, nothing kept to train on. The default route (Anthropic direct) is **not** ZDR: Anthropic keeps API traffic for ~30 days (not used for training). Through [OpenRouter](https://openrouter.ai) you can force ZDR routing (`"provider": {"zdr": true}`), and the page supports that as a second provider: set `PROVIDER = "openrouter"`, store an `OPENROUTER_API_KEY` variable at here.now, and the `/api/ask-or` route is already in `proxy.json`. What we measured:

| Route | ZDR | Retrieval | Found the liver / blood-thinner warnings | Time | Cost |
|---|---|---|---|---|---|
| Opus 5, Anthropic direct (default) | no | Anthropic search: NHS, NICE, MHRA | yes | ~30 s | ≈ $0.35 |
| Opus 5 via OpenRouter ZDR | — | not possible: its ZDR endpoints (Bedrock, Vertex) have no native search | — | — | — |
| DeepSeek V4.1 Flash via OpenRouter ZDR + Exa search | model only — Exa is a third party | PubMed abstracts only (~4k tokens) | **no** | ~25 s | ≈ $0.01 |
| **GPT-5.5 via OpenRouter ZDR (Azure), OpenAI's own search** | **yes, including the search** | NICE, Cochrane, NHS | yes | ~80–90 s | ≈ $0.33 |
| same, reasoning effort "low" | yes | 4 sources | thinner | ~40 s | ≈ $0.14 |

The honest trade is **privacy versus waiting time**: GPT-5.5 on a ZDR endpoint matched Opus on the content that matters, at the same cost, but takes roughly three times as long — and for an older user, 80 seconds looking at "Looking up…" is a real cost. Two practical notes if you choose it: OpenAI's domain filter takes bare domains only (the path-scoped MHRA and legacy-PMC entries are dropped automatically), and an OpenRouter account with ZDR enforced in its privacy settings refuses any non-ZDR route — which is a feature.

**Rule of thumb: match the model to the stakes.** The more the answer matters — a symptom, a medicine, a decision about treatment — the more capable the model should be. Saving 25p on a question about a blood thinner is the wrong trade. This applies doubly if you use the prompt in an ordinary chatbot (`PROMPT.md`), where nothing enforces the source list.

## Deploy your own

You need a [here.now](https://here.now) account (analytics and proxy routes need a paid plan) and an [Anthropic API key](https://platform.claude.com).

1. **Create a dedicated Anthropic workspace** for this, set a **monthly spend limit** (£10 is plenty for a family), create a key.
2. **Store the key at here.now**, pinned so it can only be sent to Anthropic:
   ```bash
   curl -sS -o /dev/null -w '%{http_code}\n' -X PUT https://here.now/api/v1/me/variables/ANTHROPIC_API_KEY \
     -H "Authorization: Bearer $(cat ~/.herenow/credentials)" -H 'content-type: application/json' \
     -d '{"value":"sk-ant-…","allowedUpstreams":["api.anthropic.com"]}'
   ```
   (then remove that line from your shell history)
3. **Edit the config block** at the top of the `<script>` in `site/index.html`: `CONTACT_EMAIL`, optional `RESEARCH_NOTEBOOK_URL`, `MODEL`. Adjust `ALLOWED_DOMAINS` for your country — the list is UK-specific by design.
4. **Publish** with the here.now skill or API: `publish.sh ./site`. Check the finalize response has no `warnings` (an invalid manifest silently disables the proxy route — every call then 404s).
5. **Set a site password:** `PATCH /api/v1/publish/<slug>/metadata {"password":"…"}`. A shared password is the right weight for a family; switch to *restricted* (email allow-list) if the link ever spreads.
6. **Make it permanent:** `PATCH …/metadata {"ttlSeconds":null}`. Note: republishing with `--ttl` resets this — re-patch after every publish.
7. **Test it:** `SITE_SLUG=<slug> HEALTH_PW=<password> python3 spec/live-test.py` — asks a real question, asserts every citation is on the allow-list, asserts a chest-pain question returns only the 999 line. `spec/ui-check.py` (Playwright) screenshots phone/tablet/print/dark and checks overflow, fonts, the save flow and the 999 banner.
8. **Feedback alerts (optional):** `bin/check-feedback.sh` lists new feedback records and a weekly content-blind usage line (views, approximate visitors, countries — flags any country outside `EXPECTED_COUNTRIES`) and hands them to whatever `NOTIFY_CMD` you point it at. `deploy/` has an example macOS LaunchAgent.
9. **On the phone:** open the link in Safari, enter the password once, Share → *Add to Home Screen*. It deliberately opens inside Safari rather than as a standalone web app, because standalone mode loses its saved login after a while and would silently lock an elderly user out.

## Things to know

- **`here.now` proxy routes strip custom headers** — `anthropic-version` must be declared in `proxy.json`, not sent from the browser.
- **Anthropic's citations can split text blocks at a citation boundary and drop the newline after a heading** — `tidy()` in the page forces known headings onto their own lines (`spec/tidy-test.js` reproduces it).
- **PubMed Central appears under two hosts** (`pmc.ncbi.nlm.nih.gov` and legacy `www.ncbi.nlm.nih.gov/pmc/`); both are on the list.
- **Safari may clear a site's local storage after ~7 days without a visit**, so saved answers are a convenience; Print/Copy/Share are the durable paths.
- **The system prompt is visible in view-source.** It is not a secret; the API key is, and it never leaves here.now.
- This is a template for a personal, family-scale deployment. It has been used by a handful of people. It is not a medical device and is not clinically validated.

## Licence

MIT. If you deploy this for someone you love, consider telling them the one honest thing it tells them at the end of every answer: *a computer wrote it from the pages listed; it can still be wrong; check it with your GP.*
