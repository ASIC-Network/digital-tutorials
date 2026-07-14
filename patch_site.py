#!/usr/bin/env python3
"""injects a Documentation section into the ASIC Network index.html.

usage: python3 patch_site.py [path/to/index.html]     (default: ./index.html)

what it does:
  - adds a "Docs" link to the nav
  - inserts a new section 03 (Library / Documentation) between Network and People
  - renumbers People/Sponsors/Register to 04/05/06 and re-alternates backgrounds
  - adds the doc-card CSS and a DOCS array + render snippet to the script

a backup is written to index.html.bak first. safe to rerun: exits if already patched.
edit the DOCS array (placeholder urls) in the patched file afterwards.
"""
import sys
import shutil
from pathlib import Path

CSS_BLOCK = r"""/* ---------- documentation ---------- */
.doc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;margin-top:34px}
.doc-card{position:relative;display:flex;flex-direction:column;gap:10px;background:#fff;border:1px solid var(--line);border-radius:13px;padding:22px 20px;text-decoration:none;overflow:hidden;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}
.doc-card::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:var(--navy);transform:scaleX(0);transform-origin:left;transition:transform .25s ease}
.doc-card:hover{transform:translateY(-3px);border-color:#cdd9ef;box-shadow:0 18px 40px -26px rgba(3,65,138,.45)}
.doc-card:hover::before{transform:scaleX(1)}
.doc-card .tag{font-family:var(--mono);font-size:.6rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--navy);background:var(--soft);border:1px solid var(--trace);border-radius:5px;padding:3px 8px;align-self:flex-start}
.doc-card h3{font-size:.98rem;font-weight:700;color:var(--ink);display:flex;align-items:center;gap:8px}
.doc-card h3 .arr{margin-left:auto;color:var(--navy);transition:transform .18s ease}
.doc-card:hover h3 .arr{transform:translateX(4px)}
.doc-card p{font-size:.87rem;color:var(--muted);line-height:1.6}
.doc-card .url{font-family:var(--mono);font-size:.62rem;letter-spacing:.08em;color:var(--muted);margin-top:auto;padding-top:8px;border-top:1px dashed var(--line);word-break:break-all}

"""

HTML_BLOCK = r"""  <!-- DOCUMENTATION -->
  <section id="docs" class="module alt reveal">
    <div class="wrap">
      <div class="marker"><span class="num">03</span><span class="txt">Library</span><span class="rule"></span></div>
      <h2>Documentation</h2>
      <p class="lede">Everything the network learns gets written down. Each track below is its own site, <b>rendered straight from markdown</b> in a public repo: fork it, write a page, open a pull request.</p>
      <p class="lede">More tracks get added as clubs contribute. If your club wants to own one, say so in the Discord.</p>
      <div class="doc-grid" id="doc-grid"></div>
    </div>
  </section>

"""

JS_BLOCK = r"""
/* ---------- documentation links (EDIT: placeholders for now) ---------- */
const DOCS = [
  { tag: "Analog",  title: "Analog Tutorials",
    desc: "Transistor-level design in the open PDKs: biasing, amplifiers, oscillators, sims in xschem + ngspice.",
    url: "https://asic-network.github.io/analog-tutorials/" },
  { tag: "Digital", title: "Digital Tutorials",
    desc: "RTL to GDSII: Verilog, verification, synthesis, place and route, and the full tape-out flow.",
    url: "https://asic-network.github.io/digital-tutorials/" },
  /* add more docs sites here:
  { tag: "Tooling", title: "Toolchain Setup", desc: "...", url: "https://..." },
  */
];
(function(){
  const grid = document.getElementById("doc-grid");
  if (!grid) return;
  grid.innerHTML = DOCS.map(d =>
    '<a class="doc-card" href="' + d.url + '" target="_blank" rel="noopener">'
    + '<span class="tag">' + d.tag + '</span>'
    + '<h3>' + d.title + '<span class="arr">&rarr;</span></h3>'
    + '<p>' + d.desc + '</p>'
    + '<span class="url">' + d.url.replace(/^https?:\/\//, "") + '</span>'
    + '</a>'
  ).join("");
})();
"""

DISCORD_LINE = "document.querySelectorAll('[data-link=\"discord\"]').forEach(a => a.href = CONFIG.discord);"

EDITS = [
    ("nav docs link",
     '<a href="#network">Network</a>',
     '<a href="#network">Network</a>\n      <a href="#docs">Docs</a>'),
    ("doc-card css",
     "/* ---------- map controls ---------- */",
     CSS_BLOCK + "/* ---------- map controls ---------- */"),
    ("docs section",
     "  <!-- PEOPLE -->",
     HTML_BLOCK + "  <!-- PEOPLE -->"),
    ("people bg flip",
     '<section id="people" class="module alt reveal">',
     '<section id="people" class="module reveal">'),
    ("sponsors bg flip",
     '<section id="sponsors" class="module reveal">',
     '<section id="sponsors" class="module alt reveal">'),
    ("join bg flip",
     '<section id="join" class="module alt reveal">',
     '<section id="join" class="module reveal">'),
    ("renumber people",
     '<span class="num">03</span><span class="txt">Roster</span>',
     '<span class="num">04</span><span class="txt">Roster</span>'),
    ("renumber sponsors",
     '<span class="num">04</span><span class="txt">Sponsors</span>',
     '<span class="num">05</span><span class="txt">Sponsors</span>'),
    ("renumber register",
     '<span class="num">05</span><span class="txt">Register</span>',
     '<span class="num">06</span><span class="txt">Register</span>'),
    ("docs render js",
     DISCORD_LINE,
     DISCORD_LINE + "\n" + JS_BLOCK),
]


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
    if not path.exists():
        sys.exit(f"abort: {path} not found")
    src = path.read_text(encoding="utf-8")

    if 'id="docs"' in src:
        sys.exit('already patched (found id="docs"), nothing to do')

    # validate every anchor appears exactly once before touching anything
    bad = False
    for name, anchor, _ in EDITS:
        n = src.count(anchor)
        if n != 1:
            print(f"abort: anchor for '{name}' found {n} times (expected 1)")
            bad = True
    if bad:
        sys.exit("file differs from the expected index.html, no changes made")

    backup = path.with_name(path.name + ".bak")
    shutil.copy2(path, backup)

    for name, anchor, repl in EDITS:
        src = src.replace(anchor, repl)
        print(f"applied: {name}")

    path.write_text(src, encoding="utf-8")
    print(f"done: {path} patched, backup at {backup}")
    print("next: edit the DOCS array in the file to point at the real docs urls")


if __name__ == "__main__":
    main()
