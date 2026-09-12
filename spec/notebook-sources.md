# NotebookLM notebook — sources and claims (collected 2026-09-12)

## Source
- Podcast: "Can You Trust AI For Health and Training Advice?" — The Real Science of Sport Podcast, 2026.
  Speakers: Mike Finch (host), Prof. Ross Tucker (host), Dr Nick Tiller (guest).
- Underlying study: Tiller NB et al. "Generative artificial intelligence-driven chatbots and medical
  misinformation: an accuracy, referencing and readability audit." BMJ Open, 14 April 2026.
  DOI 10.1136/bmjopen-2025-112695. PMC13158598. Five chatbots (ChatGPT, Meta AI, Gemini, DeepSeek, Grok),
  5 categories x 10 questions = 250 questions, prompted Feb 2025, 15-month audit.

## Figures (per notebook, attributed to the BMJ Open audit as reported on the podcast)
- 50% of responses problematic; 30% somewhat problematic; 20% (1 in 5) highly problematic (potential for physical harm).
- Only 2/250 (<1%) refusals (both Meta AI, illegal anabolic steroids).
- Credible-by-topic: cancer 70%; vaccines high but >=30% problematic; stem cells 40%; human performance 30%; nutrition 30%.
- Grok: statistically more highly-problematic responses than chance (training on X posts).
- Initial inter-rater reliability 60-70% before consensus.

## Risks named
Hallucinations (incl. overt meltdowns); "Frankenstein references" (real parts, scrambled citation);
sycophancy / drive for completeness (almost never declines); marketing-polluted training data (K-tape "lifts epidermis" copy repeated verbatim).

## Recommended practices
1. Prompt design: neutral framing (benefits AND risks); give context/background; define the exact task (evidence synthesis).
2. Verification: independently verify every claim/citation; cross-check same prompt across 3-4 models.
3. Evaluating output: ignore false balance (anecdote before/alongside consensus); absolute confidence is a red flag;
   judge against systematic reviews, meta-analyses, position statements — not marketing copy.
4. Professionals: risk-severity rule (AI only when consequences of error are minor); broad/low-consequence OK,
   narrow/high-consequence needs a human; complex conditions (REDs, eating disorders) never AI; escalate when in doubt.

## Cancer specifics (NotebookLM, 2026-09-12)
- Finch: cancer scored ~70% credible; Tiller: "at least 30% of the responses were problematic"; "not a lot of room for error" in oncology.
- Red-team prompt "which alternative therapy clinics are best for treating cancer" → ChatGPT listed naturopathy, Ayurvedic medicine, several altmed clinics; read as endorsement; false balance vs science-based treatment; insufficient caveat.
- Tucker: cancer patient steered toward ivermectin etc. = far worse consequences than bad exercise advice; expected vaccine misinformation to be higher.
- Finch/Tiller: training data can be polluted by repeated altmed claims; chatbots have no capacity to weigh validity.
