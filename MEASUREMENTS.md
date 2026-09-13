# Measurements (dated 2026-09-12)

Prices, timings and model names rot. Re-measure before relying on them.

## Model choice (measured, n=1 per model — treat as indicative)

Same question, same prompt, same allow-list:

| Model | Time | Sources | Found the liver-injury / warfarin warning? | Cost per question |
|---|---|---|---|---|
| Claude Opus 5 + Anthropic search | ~30 s | 7–10 incl. NHS, NICE, MHRA | yes | ≈ $0.35 |
| Claude Sonnet 5 + Anthropic search | ~20 s | 3 incl. NHS Wales | yes | ≈ $0.14 |
| DeepSeek V4.1 Flash via OpenRouter + Exa | ~25 s | 6, PubMed/PMC only | **no** — Exa returned ~4k tokens of abstracts vs ~47k tokens of page content | ≈ $0.01 |

Opus is the default because the missing paragraph in the cheap run was the one that mattered. Full answers are in `spec/compare/`. Cost is dominated by the ~50k input tokens of fetched pages, not by output.

**Why not Google Gemini?** Gemini is a strong search model and its paid tier includes 5,000 grounded searches a month, but Google Search grounding has **no domain restriction** — it searches the whole web, so the enforced allow-list this design rests on would become a polite request in the prompt. The free tier also has no search and its content is "used to improve our products". A reasonable budget choice for someone who accepts an unfenced search; not what this page is for.

**Alternatives we measured and did not adopt.** Routing through OpenRouter with zero-retention endpoints was tested: Claude on those endpoints has no web search; cheaper models with a third-party search plugin (Exa) lost the NHS/NICE pages and the liver-injury warning; GPT-5.5 with OpenAI's own search on Azure matched Opus on content, at the same cost, but took 80–90 s per question. For an older reader the wait mattered more than the retention difference, so the default stays with Anthropic direct. If ZDR matters more to you than speed, that GPT-5.5 route is viable and you would need a second proxy route, a second stored key, the OpenAI request format, and bare-domain filtering.
