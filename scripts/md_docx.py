#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_docx.py · minimal Markdown → Word renderer (python-docx), used when pandoc is absent

Understands: front matter (skipped), # ## ### headings, paragraphs, **bold**, *italic*,
`code`, [links](url), - and 1. lists, > quotes, tables, $$...$$ display formulas (own
centred paragraph), inline $...$ (kept for latex_omml.py), --- rules.
Styling comes from Word's built-in styles, or from --template (a .docx whose styles you like).

USAGE
    python md_docx.py report.md report.docx [--template house-style.docx]
"""
import argparse, re, sys


def inline(par, text):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    pos = 0
    pat = re.compile(r"(\*\*.+?\*\*|(?<![\*\w])\*[^*\n]+?\*(?!\*)|`[^`]+`|\[[^\]]+\]\([^)]+\)|\$[^$\n]+\$)")
    for m in pat.finditer(text):
        if m.start() > pos:
            par.add_run(text[pos:m.start()])
        tok = m.group(0)
        if tok.startswith("**"):
            par.add_run(tok[2:-2]).bold = True
        elif tok.startswith("`"):
            r = par.add_run(tok[1:-1]); r.font.name = "Consolas"
        elif tok.startswith("["):
            label, url = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok).groups()
            rid = par.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                                     is_external=True)
            h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
            r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr"); u = OxmlElement("w:u"); u.set(qn("w:val"), "single")
            rpr.append(u); r.append(rpr); t = OxmlElement("w:t"); t.text = label
            t.set(qn("xml:space"), "preserve"); r.append(t); h.append(r); par._p.append(h)
        elif tok.startswith("$"):
            par.add_run(tok)  # latex_omml.py converts it afterwards
        else:
            par.add_run(tok[1:-1]).italic = True
        pos = m.end()
    if pos < len(text):
        par.add_run(text[pos:])


def style(doc, name, fallback="Normal"):
    try:
        doc.styles[name]
        return name
    except KeyError:
        return fallback


def render(md_path, out_path, template=None):
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    text = open(md_path, encoding="utf-8").read().lstrip("﻿")
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    doc = docx.Document(template) if template else docx.Document()
    lines = text.split("\n")
    i, para = 0, []

    def flush():
        nonlocal para
        if para:
            inline(doc.add_paragraph(style=style(doc, "Normal")), " ".join(para))
            para = []

    while i < len(lines):
        s = lines[i].strip()
        if not s:
            flush(); i += 1; continue
        if s.startswith("$$"):
            flush()
            block = s
            while not (block.endswith("$$") and len(block) > 2) and i + 1 < len(lines):
                i += 1; block += " " + lines[i].strip()
            p = doc.add_paragraph(block.strip()); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush()
            lvl = len(m.group(1))
            inline(doc.add_paragraph(style=style(doc, "Title" if lvl == 1 else f"Heading {min(lvl - 1, 3)}")),
                   m.group(2).strip())
            i += 1; continue
        if s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = lines[i].strip()
                if not set(row) <= set("|-: "):
                    row = row[1:] if row.startswith("|") else row
                    row = row[:-1] if row.endswith("|") and not row.endswith("\\|") else row
                    rows.append([c.strip() for c in re.split(r"(?<!\\)\|", row)])
                i += 1
            if rows:
                ncol = max(len(r) for r in rows)
                tab = doc.add_table(rows=len(rows), cols=ncol)
                tab.style = style(doc, "Table Grid", None) if style(doc, "Table Grid", None) else tab.style
                for r_i, r in enumerate(rows):
                    for c_i in range(ncol):
                        cell_p = tab.rows[r_i].cells[c_i].paragraphs[0]
                        inline(cell_p, (f"**{r[c_i]}**" if r_i == 0 and c_i < len(r) and r[c_i] else (r[c_i] if c_i < len(r) else "")))
                doc.add_paragraph()
            continue
        if s.startswith(">"):
            flush()
            inline(doc.add_paragraph(style=style(doc, "Quote")), s.lstrip("> ").strip())
            i += 1; continue
        if re.match(r"^[-*+]\s+", s):
            flush()
            inline(doc.add_paragraph(style=style(doc, "List Bullet")), re.sub(r"^[-*+]\s+", "", s))
            i += 1; continue
        if re.match(r"^\d+[.)]\s+", s):
            flush()
            inline(doc.add_paragraph(style=style(doc, "List Number")), re.sub(r"^\d+[.)]\s+", "", s))
            i += 1; continue
        if re.match(r"^[-*_]{3,}$", s):
            flush(); i += 1; continue
        para.append(s); i += 1
    flush()
    doc.save(out_path)
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md"); ap.add_argument("docx"); ap.add_argument("--template")
    a = ap.parse_args()
    print(render(a.md, a.docx, a.template))
