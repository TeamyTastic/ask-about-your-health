const esc = s => s.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

const HEADINGS = ["Is this the right question?","Short answer","What the good evidence shows","How it works","What is still uncertain","What to expect","Risks, side effects and interactions","Questions to ask your GP or pharmacist"];
function tidy(t){ // Anthropic splits text into blocks at citations and the newline after a heading can vanish there
  for (const h of HEADINGS) t = t.replace(new RegExp("\\n?#{1,3}\\s*" + h.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\s*:?\\n?", "g"), "\n## " + h + "\n");
  return t.replace(/([^\n])(#{1,3} )/g, "$1\n$2");
}
function md(src){ // ponytail: tiny renderer — headings, bold, lists, paragraphs. Enough for the fixed shape.
  const out=[]; let list=null;
  const inline = t => esc(t).replace(/\*\*(.+?)\*\*/g,"<strong>$1</strong>").replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
  for (const raw of src.split("\n")) {
    const line = raw.trim();
    const li = line.match(/^[-*•]\s+(.*)/);
    if (li) { if(!list){list=[];} list.push("<li>"+inline(li[1])+"</li>"); continue; }
    if (list) { out.push("<ul>"+list.join("")+"</ul>"); list=null; }
    if (!line) continue;
    const h = line.match(/^#{1,3}\s+(.*)/);
    out.push(h ? "<h2>"+inline(h[1])+"</h2>" : "<p>"+inline(line)+"</p>");
  }
  if (list) out.push("<ul>"+list.join("")+"</ul>");
  return out.join("");
}

function assert(c,m){ if(!c) { console.error(m); process.exit(1);} }
const out = md(tidy("## Short answerA PET scan is a test.\n\n## What the good evidence showsPET stands for positron emission tomography.\n\n## Questions to ask your GP or pharmacist\n- What will this change?"));
const h2s = [...out.matchAll(/<h2>(.*?)<\/h2>/g)].map(m=>m[1]);
assert(JSON.stringify(h2s)===JSON.stringify(["Short answer","What the good evidence shows","Questions to ask your GP or pharmacist"]), "headings wrong: "+JSON.stringify(h2s));
assert(out.includes("<p>A PET scan is a test.</p>"), "body lost");
console.log("tidy/md check ok:", h2s.length, "headings");
