"""Build single-file, print-ready (PDF) editions of the Letta visual guide.

Produces, relative to the project root:

    print-zh.html   all lessons concatenated, Chinese only
    print-en.html   all lessons concatenated, English only

Each file is fully self-contained (inlined CSS, no external assets, relative
links only) and print-optimized: open it in a browser and use
"Print -> Save as PDF" to get a bilingual pair of PDFs. This keeps the
zero-dependency ethos — no headless browser or PDF library required.

Usage:
    cd src && python build_print.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import shell  # noqa: E402
import quizzes  # noqa: E402
from registry import CONTENT  # noqa: E402

# Extra rules layered on top of shell.CSS for the concatenated print edition.
PRINT_CSS = r"""
/* ---- print edition layout ---- */
.print-cover { text-align:center; padding:3rem 1rem 2.5rem; border-bottom:1px solid var(--line); margin-bottom:1.5rem; }
.print-cover h1 { font-size:2rem; margin:.2rem 0; }
.print-cover .sub { color:var(--muted); font-size:1.05rem; }
.print-hint { max-width:760px; margin:1.2rem auto 0; padding:.8rem 1rem; border:1px dashed var(--line);
              border-radius:10px; color:var(--muted); font-size:.92rem; }
.print-toc { max-width:820px; margin:1.5rem auto; }
.print-toc ol { columns:2; column-gap:2rem; padding-left:1.2rem; }
.print-toc li { margin:.15rem 0; break-inside:avoid; }
.print-toc .pt-part { font-weight:700; color:var(--accent-ink); columns:1; margin:.8rem 0 .2rem; list-style:none; }
.print-lesson { max-width:820px; margin:0 auto; padding:1.4rem 0 1.8rem; border-top:1px solid var(--line); }
.print-lesson > h2.pl-title { font-size:1.5rem; margin:.4rem 0 1rem; }
.print-lesson > h2.pl-title .pl-num { color:var(--muted); font-weight:600; }

@media print {
  .topbar, .langtoggle, .print-hint, .nav, .footer { display:none !important; }
  body { font-size:11pt; }
  .print-lesson { break-before:page; padding-top:0; border-top:none; }
  .print-cover { break-after:page; }
  .card, .codefile, table, .cellgroup, .vflow, .cols, details, figure, .note, .cute { break-inside:avoid; }
  h2, h3, h4 { break-after:avoid; }
  a { color:inherit; text-decoration:none; }
  /* force light, ink-on-paper rendering regardless of OS dark mode */
  :root { color-scheme:light; }
}
"""


def _lesson_section(page, lang):
    fname, title_zh, title_en, part_zh, part_en = page
    num = fname.split("-", 1)[0]
    title = title_zh if lang == "zh" else title_en
    body = CONTENT[fname][lang] + quizzes.render(fname, lang)
    # In the concatenated single-file edition, cross-lesson links like
    # href="08-memory-blocks.html" (e.g. the glossary index) become intra-document
    # jumps to the section anchors below.
    body = re.sub(r'href="(\d{2})-[a-z0-9-]+\.html"', r'href="#L\1"', body)
    return (
        f'<section class="print-lesson" id="L{num}">'
        f'<h2 class="pl-title"><span class="pl-num">{num}</span> &nbsp;{shell.esc(title)}</h2>'
        f"{body}</section>"
    )


def _toc(lang):
    rows = []
    seen_part = None
    for page in shell.PAGES:
        fname, tz, te, pz, pe = page
        num = fname.split("-", 1)[0]
        part = pz if lang == "zh" else pe
        if part != seen_part:
            rows.append(f'<li class="pt-part">{shell.esc(part)}</li>')
            seen_part = part
        title = tz if lang == "zh" else te
        rows.append(f'<li><a href="#L{num}">{num} · {shell.esc(title)}</a></li>')
    return '<nav class="print-toc"><ol>' + "".join(rows) + "</ol></nav>"


def print_page(lang):
    title = "Letta 图解教程" if lang == "zh" else "Letta Visual Guide"
    sub = (
        "中英双语 · 8 个部分 · 31 课 · 打印版（用浏览器“打印 → 另存为 PDF”）"
        if lang == "zh"
        else "Bilingual guide \u00b7 8 parts \u00b7 31 lessons \u00b7 print edition (use your browser's Print \u2192 Save as PDF)"
    )
    hint = (
        "提示：这是把全部 31 课拼在一页的打印版。用浏览器的<strong>打印</strong>功能、目标选<strong>另存为 PDF</strong>即可导出整本。"
        if lang == "zh"
        else "Tip: this single page concatenates all 31 lessons. Use your browser's <strong>Print</strong> dialog and choose <strong>Save as PDF</strong> to export the whole book."
    )
    total = len(shell.PAGES)
    nparts = len({p[3] for p in shell.PAGES})
    sections = "\n".join(_lesson_section(p, lang) for p in shell.PAGES)
    head = shell.head_meta(title, sub)
    return f"""<!DOCTYPE html>
<html lang="{'zh-Hans' if lang == 'zh' else 'en'}" data-lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{shell.esc(title)}</title>
{head}
<style>{shell.CSS}{PRINT_CSS}</style>
</head><body>
<main class="wrap">
  <header class="print-cover">
    <h1>{shell.esc(title)}</h1>
    <p class="sub">{sub}</p>
    <p class="print-hint">{hint}</p>
  </header>
  <p style="text-align:center;color:var(--muted)">{total} {'课' if lang=='zh' else 'lessons'} · {nparts} {'个部分' if lang=='zh' else 'parts'}</p>
  {_toc(lang)}
  {sections}
</main>
</body></html>"""


def build():
    written = []
    for lang in ("zh", "en"):
        fname = f"print-{lang}.html"
        with open(os.path.join(ROOT, fname), "w", encoding="utf-8") as f:
            f.write(print_page(lang))
        written.append(fname)
    return written


if __name__ == "__main__":
    done = build()
    print("Wrote", len(done), "print editions under", ROOT)
    for f in done:
        print("  -", f)
