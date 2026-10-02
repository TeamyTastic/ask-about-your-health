// Offline check of site/index.html: run() keeps question/answer paired (#12) and citation hrefs are scheme-checked (#82).
// Pulls the real code out of the page, so reverting the fix in index.html turns this red.
const fs = require("fs"), vm = require("vm"), path = require("path");
const html = fs.readFileSync(path.join(__dirname, "../site/index.html"), "utf8");
function assert(c, m) { if (!c) { console.error("FAIL:", m); process.exit(1); } }
const grab = re => { const m = html.match(re); assert(m, "not found in index.html: " + re); return m[0]; };
const esc = grab(/^const esc = .*$/m) + "\n" + grab(/^const safeHref = .*$/m);

// --- #82: javascript: / data: URLs must never reach an href ---
const srcs = grab(/^function renderSources[\s\S]*?^}/m);
const mkEl = () => ({ innerHTML: "", textContent: "", disabled: false, style: {}, value: "", scrollIntoView() {}, focus() {} });
function sandbox(extra) {
  const els = {}; const $ = id => els[id] || (els[id] = mkEl());
  return { els, ctx: vm.createContext({ $, window: { scrollTo() {} }, ...extra }) };
}
{
  const { els, ctx } = sandbox({});
  vm.runInContext(esc + "\n" + srcs + "\nrenderSources(new Map([['javascript:alert(1)','bad'],['https://www.nhs.uk/x','good']]));", ctx);
  const h = els.sources.innerHTML;
  assert(!/href="javascript:/i.test(h), "javascript: URL linked: " + h);
  assert(h.includes('href="https://www.nhs.uk/x"'), "https URL lost: " + h);
}
// saved-answers list reads URLs from localStorage: same guard
assert(!/href="\$\{esc\(u\)\}"/.test(html), "saved list still links unchecked esc(u)");

// --- #12: failed / in-flight second run must not pair new question with old answer ---
const run = grab(/^async function run\(\)\{[\s\S]*?^}/m);
{
  let behave = "ok", release;
  const { els, ctx } = sandbox({
    ask: q => behave === "ok" ? Promise.resolve({ text: "ANSWER-" + q, citations: new Map() })
                              : new Promise((_, rej) => { release = () => rej(new Error("boom")); }),
    renderSources() {},
    window: { scrollTo() {} },
  });
  vm.runInContext(esc + "\nlet lastText='', lastQuestion='';\n" + run + "\nthis.state=()=>({lastText,lastQuestion});this.run=run;", ctx);
  els.q = Object.assign(mkEl(), { value: "first" });
  (async () => {
    await ctx.run();
    assert(ctx.state().lastQuestion === "first" && ctx.state().lastText === "ANSWER-first", "first run state");
    behave = "fail"; els.q.value = "second";
    const p = ctx.run();
    assert(els.save.disabled === true, "save must be disabled while a run is in flight");
    release(); await p;
    const s = ctx.state();
    assert(!(s.lastQuestion === "second" && s.lastText === "ANSWER-first"), "new question paired with previous answer");
    assert(els.save.disabled === true, "save must stay disabled after a failed run");
    console.log("save-share check ok");
  })().catch(e => { console.error("FAIL:", e); process.exit(1); });
}
