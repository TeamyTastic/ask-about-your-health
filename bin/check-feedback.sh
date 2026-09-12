#!/usr/bin/env bash
# Weekly, content-blind check for a deployed Ask About Your Health site:
#   1. new feedback records (the only thing the owner can read) → one notification each
#   2. a usage line from here.now analytics: views, approximate visitors, countries — raw IPs are never exposed —
#      flagging any country outside EXPECTED_COUNTRIES so a link that spreads shows up without anyone's questions being read
#
# Env:  SITE_SLUG (required)   EXPECTED_COUNTRIES (default GB, comma-separated)
#       NOTIFY_CMD  — a command taking two args, title and body (e.g. a script that posts to ntfy, Pushover, or `mail`).
#                     If unset, notifications are printed to stdout.
# Needs ~/.herenow/credentials (the here.now API key) and python3.
set -euo pipefail
SLUG="${SITE_SLUG:?set SITE_SLUG to your here.now slug}"
SITE_URL="https://${SLUG}.here.now/"
STATE="$(cd "$(dirname "$0")/.." && pwd)/.state/feedback-seen-ids"
LOG="$HOME/Library/Logs/health-page-feedback.log"
EXPECTED="${EXPECTED_COUNTRIES:-GB}"
mkdir -p "$(dirname "$STATE")" "$(dirname "$LOG")"; touch "$STATE"

notify() {  # title, body
  if [ -n "${NOTIFY_CMD:-}" ]; then "$NOTIFY_CMD" "$1" "$2"; else printf '%s\n%s\n\n' "$1" "$2"; fi
}

# Feedback records → id<US>message lines. Python holds the key; nothing is echoed.
if ! rows="$(python3 - "$SLUG" <<'PY'
import json, sys, urllib.request, pathlib
slug = sys.argv[1]
key = pathlib.Path.home().joinpath(".herenow/credentials").read_text().strip()
req = urllib.request.Request(f"https://here.now/api/v1/publishes/{slug}/data/feedback?limit=100", headers={"Authorization": "Bearer " + key})
for r in json.load(urllib.request.urlopen(req, timeout=30)).get("records", []):
    d = r.get("data", r); m = (d.get("message") or "").replace("\x1f", " ").replace("\n", " ")[:600]
    print(r["id"], m, sep="\x1f")   # unit separator: a tab is IFS whitespace, so empty fields would collapse
PY
)"; then
  echo "$(date -u +%FT%TZ) ERROR: here.now feedback list failed" >> "$LOG"
  notify "Health page: feedback check FAILED" "Could not list feedback records from here.now — see $LOG"
  exit 1
fi

new=0
while IFS=$'\x1f' read -r id msg; do
  [ -n "$id" ] || continue
  if grep -qxF "$id" "$STATE"; then continue; fi
  notify "New feedback on the health page" "$msg"
  echo "$id" >> "$STATE"; new=$((new+1))
  echo "$(date -u +%FT%TZ) notified $id: ${msg:0:80}" >> "$LOG"
done <<< "$rows"
echo "$(date -u +%FT%TZ) ok — $new new" >> "$LOG"

summary="$(python3 - "$SLUG" "$EXPECTED" <<'PY'
import json, sys, urllib.request, pathlib
slug, expected = sys.argv[1], set(sys.argv[2].split(","))
key = pathlib.Path.home().joinpath(".herenow/credentials").read_text().strip()
d = json.load(urllib.request.urlopen(urllib.request.Request(f"https://here.now/api/v1/publishes/{slug}/analytics?range=7d", headers={"Authorization": "Bearer " + key}), timeout=30))
t = d.get("totals", {}); cs = d.get("topCountries", [])
line = f"Last 7 days: {t.get('rangeViews',0)} views, ~{t.get('rangeVisitors',0)} visitors. " + ", ".join(f"{c['country']} {c['views']}" for c in cs)
odd = [c["country"] for c in cs if c["country"] not in expected]
print(("⚠ unexpected country: " + ", ".join(odd) + ". " if odd else "") + line)
PY
)" || summary="Usage summary unavailable — analytics call failed (see $LOG)"
notify "Health page — weekly usage" "$summary"
echo "$(date -u +%FT%TZ) usage: $summary" >> "$LOG"
