#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
latex_omml.py · LaTeX ($...$, $$...$$) → native, editable Word equations (OMML)

No external converter: a small LaTeX → MathML parser for the subset research reports use,
then Microsoft's own MML2OMML.XSL (ships with Office) turns MathML into OMML.
Where Office is not installed, use pandoc instead (research.py export does it for you).

Supported: letters and digits, = + - ( ) [ ] , . / < > ! ' : |, _{...} and ^{...}, \\sum
\\prod \\int with limits, \\log \\ln \\exp \\sin \\cos \\tan \\max \\min \\lim \\arg, \\mathrm{}
\\text{} \\operatorname{}, \\frac{}{}, \\sqrt{}, \\, \\; \\quad, \\| \\mid \\cdot \\times \\leq
\\geq \\neq \\approx \\infty \\to \\partial \\pm \\propto, \\left \\right, Greek letters.
Anything else raises Unsupported, and the formula stays as text with a warning.

USAGE
    python latex_omml.py report.docx            # converts in place
    python latex_omml.py report.docx --check    # lists and tests, writes nothing
    MML2OMML_XSL=/path/to/MML2OMML.XSL python latex_omml.py report.docx
"""
import argparse, copy, glob, os, re, sys

GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε",
         "zeta": "ζ", "eta": "η", "theta": "θ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ",
         "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "phi": "φ", "varphi": "φ", "chi": "χ",
         "psi": "ψ", "omega": "ω", "kappa": "κ", "iota": "ι", "upsilon": "υ",
         "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Sigma": "Σ", "Phi": "Φ",
         "Psi": "Ψ", "Omega": "Ω", "Pi": "Π", "Xi": "Ξ"}
OPS = {"|": "‖", "mid": "∣", "cdot": "·", "times": "×", "leq": "≤", "geq": "≥", "neq": "≠",
       "approx": "≈", "infty": "∞", "to": "→", "partial": "∂", "pm": "±", "propto": "∝",
       "le": "≤", "ge": "≥", "ne": "≠", "sim": "∼", "equiv": "≡", "in": "∈", "rightarrow": "→",
       "leftarrow": "←", "Rightarrow": "⇒", "nabla": "∇", "ldots": "…", "cdots": "⋯"}
BIG = {"sum": "∑", "prod": "∏", "int": "∫", "oint": "∮"}
FUNCS = {"log", "ln", "exp", "sin", "cos", "tan", "max", "min", "lim", "arg", "det", "dim", "sup", "inf"}
SPACES = {",": "0.17em", ";": "0.28em", "quad": "1em", " ": "0.25em", "qquad": "2em"}

XSL_CANDIDATES = [os.environ.get("MML2OMML_XSL", ""),
                  r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL",
                  r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL",
                  r"C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL",
                  "/Applications/Microsoft Word.app/Contents/Resources/mathml2omml.xsl"]


class Unsupported(Exception):
    pass


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Parser:
    def __init__(self, s):
        self.s, self.i = s, 0

    def end(self):
        return self.i >= len(self.s)

    def skip(self):
        while not self.end() and self.s[self.i] == " ":
            self.i += 1

    def group(self):
        self.skip()
        if self.end():
            raise Unsupported("empty group")
        if self.s[self.i] == "{":
            self.i += 1
            items = self.items("}")
            self.i += 1
            return "<mrow>" + "".join(items) + "</mrow>"
        return self.atom()

    def command(self):
        m = re.match(r"\\([A-Za-z]+|.)", self.s[self.i:])
        self.i += len(m.group(0))
        return m.group(1)

    def braced_text(self):
        self.skip()
        if self.s[self.i] != "{":
            raise Unsupported("expected {")
        j = self.s.index("}", self.i)
        t = self.s[self.i + 1:j]
        self.i = j + 1
        return t

    def atom(self):
        c = self.s[self.i]
        if c == "\\":
            name = self.command()
            if name in BIG:
                return ("BIG", BIG[name])
            if name in FUNCS:
                return f'<mi mathvariant="normal">{name}</mi>'
            if name in ("mathrm", "text", "operatorname", "textrm"):
                return f'<mi mathvariant="normal">{esc(self.braced_text())}</mi>'
            if name == "frac":
                a = self.group(); b = self.group()
                return f"<mfrac>{a}{b}</mfrac>"
            if name == "sqrt":
                return f"<msqrt>{self.group()}</msqrt>"
            if name in GREEK:
                return f"<mi>{GREEK[name]}</mi>"
            if name in OPS:
                return f"<mo>{OPS[name]}</mo>"
            if name in SPACES:
                return f'<mspace width="{SPACES[name]}"/>'
            if name in ("left", "right"):
                return self.atom()
            if name in ("{", "}"):
                return f"<mo>{name}</mo>"
            raise Unsupported("\\" + name)
        self.i += 1
        if c.isalpha():
            return f"<mi>{esc(c)}</mi>"
        if c.isdigit():
            n = c
            while not self.end() and (self.s[self.i].isdigit() or self.s[self.i] == "."):
                n += self.s[self.i]; self.i += 1
            return f"<mn>{n}</mn>"
        if c in "=+-()[],./<>!':|*":
            return f"<mo>{esc({'-': '−', '*': '∗'}.get(c, c))}</mo>"
        raise Unsupported(c)

    def items(self, close=None):
        out, big = [], None
        while not self.end() and (close is None or self.s[self.i] != close):
            if self.s[self.i] == " ":
                self.i += 1; continue
            base = self.atom()
            sub = sup = None
            while True:
                self.skip()
                if not self.end() and self.s[self.i] == "_":
                    self.i += 1; sub = self.group()
                elif not self.end() and self.s[self.i] == "^":
                    self.i += 1; sup = self.group()
                else:
                    break
            if isinstance(base, tuple):
                op = f'<mo largeop="true">{base[1]}</mo>'
                base = (f"<munderover>{op}{sub}{sup}</munderover>" if sub and sup else
                        f"<munder>{op}{sub}</munder>" if sub else f"<mover>{op}{sup}</mover>" if sup else op)
                big = len(out)
            elif sub and sup:
                base = f"<msubsup>{base}{sub}{sup}</msubsup>"
            elif sub:
                base = f"<msub>{base}{sub}</msub>"
            elif sup:
                base = f"<msup>{base}{sup}</msup>"
            out.append(base)
        if close is not None and self.end():
            raise Unsupported("unclosed brace")
        # Word only puts the summand inside the sum (m:e) if it is grouped
        if big is not None and big + 1 < len(out):
            out = out[:big + 1] + ["<mrow>" + "".join(out[big + 1:]) + "</mrow>"]
        return out


def latex_to_mathml(tex):
    return '<math xmlns="http://www.w3.org/1998/Math/MathML">' + "".join(Parser(tex.strip()).items()) + "</math>"


_XSLT = None


def xslt():
    global _XSLT
    if _XSLT is None:
        from lxml import etree
        cands = [c for c in XSL_CANDIDATES if c] + glob.glob(r"C:\Program Files*\Microsoft Office\**\MML2OMML.XSL", recursive=True)
        for c in cands:
            if os.path.exists(c):
                _XSLT = etree.XSLT(etree.parse(c))
                break
        else:
            raise FileNotFoundError("MML2OMML.XSL not found (it ships with Microsoft Office; or set MML2OMML_XSL, or use pandoc)")
    return _XSLT


def omml(tex):
    from lxml import etree
    return xslt()(etree.fromstring(latex_to_mathml(tex).encode("utf-8"))).getroot()


PATTERN = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$")


def convert_paragraph(p, warnings):
    from lxml import etree
    from docx.oxml.ns import qn
    text = p.text
    if "$" not in text:
        return 0
    m = re.fullmatch(r"\s*\$\$(.+?)\$\$\s*", text)
    if m:
        try:
            eq = omml(m.group(1))
        except Exception as e:
            warnings.append(f"{m.group(1)[:50]} -> {e}"); return 0
        for r in list(p.runs):
            r._r.getparent().remove(r._r)
        etree.SubElement(p._p, qn("m:oMathPara")).append(eq)
        return 1
    n = 0
    for r in list(p.runs):
        t = r.text
        if "$" not in t:
            continue
        pieces, pos = [], 0
        for mm in PATTERN.finditer(t):
            pieces += [("t", t[pos:mm.start()]), ("f", mm.group(1) or mm.group(2))]
            pos = mm.end()
        pieces.append(("t", t[pos:]))
        new = []
        for kind, content in pieces:
            if kind == "f":
                try:
                    new.append(omml(content)); n += 1
                    continue
                except Exception as e:
                    warnings.append(f"{content[:50]} -> {e}")
                    content = "$" + content + "$"
            if content:
                nr = copy.deepcopy(r._r)
                for wt in nr.findall(qn("w:t")):
                    nr.remove(wt)
                wt = etree.SubElement(nr, qn("w:t")); wt.text = content
                wt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                new.append(nr)
        for el in new:
            r._r.addprevious(el)
        r._r.getparent().remove(r._r)
    return n


def convert(path, check=False):
    import docx
    d = docx.Document(path)
    blocks = list(d.paragraphs) + [p for t in d.tables for row in t.rows for c in row.cells for p in c.paragraphs]
    if check:
        for p in blocks:
            for m in PATTERN.finditer(p.text):
                try:
                    latex_to_mathml(m.group().strip("$")); print("   ok    ", m.group())
                except Exception as e:
                    print("   FAIL  ", m.group(), "->", e)
        return 0
    warnings, total = [], 0
    for p in blocks:
        total += convert_paragraph(p, warnings)
    if total:
        d.save(path)
    print(f"{os.path.basename(path)}: {total} formula(s) converted to Word equations")
    for w in warnings:
        print("   WARNING (left as text):", w)
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", nargs="+")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    for f in a.docx:
        convert(f, a.check)
