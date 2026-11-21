#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
research.py · local engine of the rigorous-research skill

Everything in a deep research run that is mechanical, done on disk without a model:
run manifest, scholarly search, retraction check, source independence, citation-sentence
check, quote integrity, bibliography numbering, formula validation, final gate, export.

Workspace: ./research/<tag>/ (override with --dir or RESEARCH_DIR). Python 3.9+.
Needs `requests` for the network commands; `python-docx` + `lxml` for Word export;
`matplotlib` (optional) to draw formulas; `pdfplumber` / `pypdfium2` (optional) to check PDFs.

COMMANDS
  init <slug> [--profile P] [--level light|standard|deep]   create the run folder
  step <tag> <id> --status running|done|skipped [--note ..] record a step (resume memory)
  resume [tag]                                              what is done, what is next
  scholar "<query>" [--n 10] [--since YEAR] [--lang xx] [--type article|book] [--order relevance|citations]
                                                            OpenAlex (no key), Crossref fallback
  doi <file-or-DOIs...>                                     retracted?, citations, open access
  independence <sources-dir>                                sources that are one voice
  meta <sources-dir>                                        title, author, year, venue vs Crossref;
                                                            preprints; corrections/retractions; ISBN
  cites <draft.md> <sources-dir> [--all]                    citation-sentence triage + quote check
  number <draft.md> <sources-dir> --out <file.md> [--refs-title "References"]
                                                            [sNN] → [N] + one pruned bibliography
  formulas <file.md> [--png DIR]                            validate LaTeX; draw each formula
  gate <tag> [--file report.md]                             final gate
  export <file.md> [--formats md,docx,pdf] [--template ref.docx] [--png DIR] [--force]
                                                            md → docx (native equations) → pdf
Aliases in Portuguese: iniciar, passo, retomar, academico, independencia, citacoes, numerar,
formulas, portao, exportar.
"""
import argparse, datetime, hashlib, json, os, re, secrets, shutil, subprocess, sys, time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
UA = {"User-Agent": "rigorous-research/1.0 (academic search; local script)"}

STEPS = {
    "0": ("Frame: question, decomposition, coverage, profile", "frame.md"),
    "1": ("Prior knowledge first (your notes, your library)", "frame.md"),
    "2": ("Search plan in five lenses", "sweep.md"),
    "3": ("Sweep: researchers in parallel → sources/", "sweep.md"),
    "4": ("Coverage, independence and dispute map", "map-and-critic.md"),
    "5": ("Corpus critic and one gap round", "map-and-critic.md"),
    "6": ("Draft in the chosen profile (draft.md with [sNN])", "drafting.md"),
    "7": ("Adversarial critics", "critics-and-patch.md"),
    "8": ("Surgical patch (never regenerate)", "critics-and-patch.md"),
    "9": ("Citation-sentence check and second patch", "critics-and-patch.md"),
    "10": ("Formulas and numbers", "formulas-and-numbers.md"),
    "11": ("Number, voice and status gates, final gate", "gate-and-delivery.md"),
    "12": ("Delivery and export", "gate-and-delivery.md"),
}
SEQ = {"light": ["0", "1", "2", "3", "6", "10", "11", "12"],
       "standard": [str(i) for i in range(13)], "deep": [str(i) for i in range(13)]}


def root():
    return Path(os.environ.get("RESEARCH_DIR") or ARGS_DIR or "research").resolve()


ARGS_DIR = None


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def write(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read(path):
    return Path(path).read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")


def front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    d = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if mm:
            k, v = mm.group(1).strip(), mm.group(2).strip()
            d[k] = [x.strip().strip("\"'") for x in v[1:-1].split(",") if x.strip()] if v.startswith("[") and v.endswith("]") else v.strip("\"'")
    return d, text[m.end():]


def run_dir(tag):
    base = root()
    if tag:
        p = base / tag
        if not p.exists():
            c = sorted(base.glob(tag + "*"))
            p = c[0] if len(c) == 1 else p
        if not (p / "run.json").exists():
            sys.exit(f"ERROR: run '{tag}' not found in {base}")
        return p
    runs = sorted(base.glob("*/run.json"), key=lambda x: x.stat().st_mtime)
    if not runs:
        sys.exit(f"ERROR: no runs in {base}")
    return runs[-1].parent


def load_run(p):
    return json.loads(read(p / "run.json"))


def save_run(p, d):
    write(p / "run.json", json.dumps(d, ensure_ascii=False, indent=2) + "\n")


def http_json(url, params=None, timeout=25):
    import requests
    params = dict(params or {})
    key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if "openalex.org" in url and key:
        params["api_key"] = key
    last = "failed"
    for wait in (0, 2, 6):
        if wait:
            time.sleep(wait)
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            if r.status_code == 404:
                return None, 404
            if r.status_code in (429, 500, 502, 503, 504):
                last = f"HTTP {r.status_code}"
                if r.status_code == 429 and r.headers.get("X-RateLimit-Remaining-USD") in ("0", "0.0"):
                    return None, "OpenAlex daily budget used up (without a key it is shared per IP)"
                continue
            r.raise_for_status()
            left = r.headers.get("X-RateLimit-Remaining-USD")
            if left and "openalex" in url and float(left) < 0.02:
                print(f"note: OpenAlex daily budget almost used (US$ {left}); a free key in OPENALEX_API_KEY raises it",
                      file=sys.stderr)
            return r.json(), r.status_code
        except Exception as e:
            last = str(e)[:120]
    return None, last


DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>\)\]\},;]+)", re.I)


def clean_doi(d):
    return d.rstrip(".").rstrip(")").lower()


# ─────────────── manifest ───────────────
def cmd_init(a):
    slug = re.sub(r"[^a-z0-9]+", "-", a.slug.lower()).strip("-")[:40] or "research"
    root().mkdir(parents=True, exist_ok=True)
    while True:
        tag = f"{slug}-{secrets.token_hex(3)}"
        if not (root() / tag).exists():
            break
    p = root() / tag
    (p / "sources").mkdir(parents=True)
    (p / "temp").mkdir()
    save_run(p, {"tag": tag, "created": now(), "profile": a.profile, "level": a.level, "state": "running", "steps": {}})
    print(f"tag: {tag}\nfolder: {p}\nlevel: {a.level} · steps: {' → '.join(SEQ[a.level])}")


def cmd_step(a):
    p = run_dir(a.tag)
    d = load_run(p)
    if a.id not in STEPS:
        sys.exit("ERROR: step must be 0 to 12")
    d["steps"][a.id] = {"status": a.status, "at": now(), **({"note": a.note} if a.note else {})}
    save_run(p, d)
    print(f"{d['tag']} · step {a.id} ({STEPS[a.id][0]}): {a.status}")


def cmd_resume(a):
    p = run_dir(a.tag)
    d = load_run(p)
    print(f"run: {d['tag']} · profile {d.get('profile')} · level {d['level']} · state {d['state']}\nfolder: {p}")
    nxt = None
    for s in SEQ[d["level"]]:
        st = d["steps"].get(s, {}).get("status", "pending")
        print(f"  [{st:>8}] {s:>2} · {STEPS[s][0]}")
        if nxt is None and st not in ("done", "skipped"):
            nxt = s
    print("ALL STEPS DONE." if nxt is None else f"NEXT: step {nxt} · read references/{STEPS[nxt][1]}")
    print(f"sources: {len(list((p / 'sources').glob('*.md')))}")


# ─────────────── scholarly ───────────────
def cmd_scholar(a):
    filters = []
    if a.since:
        filters.append(f"from_publication_date:{a.since}-01-01")
    if a.lang:
        filters.append(f"language:{a.lang}")
    if a.type:
        filters.append(f"type:{a.type}")
    params = {"per_page": a.n, "select": "doi,display_name,publication_year,cited_by_count,is_retracted,"
                                          "open_access,primary_location,type,authorships"}
    if a.order == "citations":  # loose search sorted by citations returns the world's most cited paper
        filters.append("title_and_abstract.search:" + a.query.replace(",", " "))
        params["sort"] = "cited_by_count:desc"
    else:
        params["search"] = a.query
    if filters:
        params["filter"] = ",".join(filters)
    d, st = http_json("https://api.openalex.org/works", params)
    if d and d.get("results") is not None:
        print(f"OpenAlex · {d.get('meta', {}).get('count', '?')} results · showing {len(d['results'])}")
        for w in d["results"]:
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            au = [x.get("author", {}).get("display_name", "") for x in (w.get("authorships") or [])[:2]]
            au += ["et al."] if len(w.get("authorships") or []) > 2 else []
            src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            oa = (w.get("open_access") or {}).get("oa_url") or ""
            print(f"{w.get('publication_year') or '?':>4} | cit {w.get('cited_by_count', 0):>6} | {(w.get('type') or '?')[:9]:<9} | {doi or 'no DOI'}\n"
                  f"       {w.get('display_name')} · {', '.join(x for x in au if x)}{' · ' + src if src else ''}"
                  f"{' · OA: ' + oa if oa else ''}{'  ‼ RETRACTED' if w.get('is_retracted') else ''}")
        return
    print(f"OpenAlex failed ({st}); falling back to Crossref")
    cp = {"query.bibliographic": a.query, "rows": a.n * 2,
          "select": "DOI,title,issued,container-title,author,is-referenced-by-count,type",
          "filter": "type:journal-article,type:book,type:book-chapter,type:proceedings-article,type:posted-content"
                    + (f",from-pub-date:{a.since}" if a.since else "")}
    if a.order == "citations":
        cp.update(sort="is-referenced-by-count", order="desc")
    d, st = http_json("https://api.crossref.org/works", cp)
    if not d:
        sys.exit(f"ERROR: Crossref failed too ({st}). Use web search.")
    for it in [x for x in d["message"]["items"] if not re.search(r"\.supp|\.s\d+$", x.get("DOI", ""), re.I)][:a.n]:
        year = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        au = ", ".join(x.get("family", "") for x in (it.get("author") or [])[:2])
        print(f"{year or '?':>4} | cit {it.get('is-referenced-by-count', 0):>6} | {it.get('type', '?')[:9]:<9} | {it.get('DOI')}\n"
              f"       {(it.get('title') or ['?'])[0]} · {au} · {(it.get('container-title') or [''])[0]}")


def crossref(doi):
    d, _ = http_json(f"https://api.crossref.org/works/{doi}")
    return (d or {}).get("message")


def editorial_state(w):
    """Notices Crossref links to the record (updated-by): correction, erratum, retraction,
    expression of concern. Catches the correction that never circulated."""
    out = []
    for u in (w or {}).get("updated-by", []) or []:
        dp = ((u.get("updated") or {}).get("date-parts") or [[None]])[0]
        out.append((u.get("type", "?"), u.get("DOI", "?"), "-".join(str(x) for x in dp if x)))
    return out


def fold(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c)).lower()


def isbn_ok(s):
    d = re.sub(r"[^0-9Xx]", "", s or "")
    if len(d) == 10:
        return sum((10 - i) * (10 if c in "Xx" else int(c)) for i, c in enumerate(d)) % 11 == 0
    if len(d) == 13 and d.isdigit():
        return sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(d)) % 10 == 0
    return False


def cmd_meta(a):
    """Level 2 of verification (existence → METADATA → support): for every note with a DOI,
    compare title, first author, year and venue with Crossref; flag preprints (and their
    published version when linked); list corrections, errata and retractions, and require the
    note to record them in `editorial-state:`; validate ISBN check digits. Catches a real
    reference with a displaced label and a reference conflated from several works, which an
    existence check alone lets through."""
    src = load_sources(a.folder)
    findings, n = [], 0
    for sid, s in sorted(src.items()):
        fm, probs = s["fm"], []
        if fm.get("isbn") and not isbn_ok(fm["isbn"]):
            probs.append(("MISMATCH", f"ISBN {fm['isbn']} fails its check digit"))
        doi = clean_doi(fm.get("doi", "")) if fm.get("doi") else ""
        if doi:
            n += 1
            w = crossref(doi)
            if not w:
                probs.append(("MISMATCH", "DOI not found in Crossref (check DataCite and the publisher)"))
            else:
                title = " ".join((w.get("title") or []) + (w.get("subtitle") or []))
                A, B = shingles(title, 1), shingles(fm.get("title", ""), 1)
                if A and B and len(A & B) / max(1, min(len(A), len(B))) < 0.5:
                    probs.append(("MISMATCH", f"title: note says «{fm.get('title', '')[:70]}», the DOI is «{title[:70]}»"))
                first = (w.get("author") or [{}])[0]
                fam = fold(first.get("family", "") or first.get("name", ""))
                au = fm.get("author") or ""
                au = au[0] if isinstance(au, list) else au
                if fam and au and fam.split()[-1] not in fold(au):
                    probs.append(("MISMATCH", f"first author: note says «{au[:40]}», record says «{fam}»"))
                years = {((w.get(k) or {}).get("date-parts") or [[None]])[0][0] for k in ("issued", "published-print", "published-online")}
                years.discard(None)
                y = str(fm.get("year", ""))[:4]
                if y.isdigit() and years and min(abs(int(y) - x) for x in years) > 1:
                    probs.append(("MISMATCH", f"year: note says {y}, record says {sorted(years)}"))
                cont = fold(" ".join(w.get("container-title") or []))
                if cont and fm.get("venue") and not any(t in fold(fm["venue"]) for t in cont.split()[:3]):
                    probs.append(("WARN", f"venue: note says «{fm['venue'][:50]}», record says «{cont[:50]}»"))
                if w.get("type") == "posted-content":
                    pub = [r.get("id") for r in (w.get("relation") or {}).get("is-preprint-of", [])]
                    probs.append(("WARN", "preprint" + (f", published as {pub[0]}: cite the published version" if pub else
                                                         ": check whether it was published; never cite it as peer-reviewed")))
                rec = fold(str(fm.get("editorial-state", "")))
                for kind, ndoi, date in editorial_state(w):
                    lvl = "MISMATCH" if not rec or ("retract" in kind and "retract" not in rec) else "ok"
                    probs.append((lvl, f"{kind} published {date} ({ndoi})" + ("" if lvl == "ok" else
                                 ": the note does not record it in editorial-state: (read the notice; figures may be superseded)")))
                time.sleep(0.1)
        findings += [{"source": sid, "level": l, "msg": m} for l, m in probs if l != "ok"]
        mark = "MISMAT" if any(l == "MISMATCH" for l, _ in probs) else "warn  " if any(l == "WARN" for l, _ in probs) else "ok    "
        print(f"{mark} {sid} {s['file'][:50]}")
        for l, m in probs:
            print(f"        {l}: {m}")
    bad = sum(f["level"] == "MISMATCH" for f in findings)
    out = Path(a.folder).parent / "temp" / "metadata.json"
    write(out, json.dumps(findings, ensure_ascii=False, indent=2))
    print(f"--- {len(src)} notes · {n} with DOI · {bad} MISMATCH · {len(findings) - bad} warning(s) · written: {out}")
    sys.exit(1 if bad else 0)


def cmd_doi(a):
    dois = []
    for x in a.inputs:
        dois += [clean_doi(m) for m in DOI_RE.findall(read(x) if os.path.exists(x) else x)]
    dois = list(dict.fromkeys(dois))
    retracted = 0
    for doi in dois:
        d, st = http_json(f"https://api.openalex.org/works/https://doi.org/{doi}",
                          {"select": "display_name,publication_year,cited_by_count,is_retracted,type,open_access"})
        if not d:
            c, cst = http_json(f"https://api.crossref.org/works/{doi}")
            print(f"{'exists' if c else 'NOT FOUND':<11} {doi} · not in OpenAlex ({st}); Crossref: {'found' if c else cst}")
            continue
        ee = editorial_state(crossref(doi))
        ret = d.get("is_retracted") or any("retract" in k for k, _, _ in ee)
        retracted += bool(ret)
        oa = (d.get("open_access") or {}).get("oa_url") or ""
        print(f"{'‼ RETRACTED' if ret else '‼ CORRECTED' if ee else 'ok':<11} {doi} · {d.get('publication_year')} · cit {d.get('cited_by_count')} · "
              f"{d.get('type')} · {(d.get('display_name') or '')[:90]}{' · OA: ' + oa if oa else ''}")
        for kind, ndoi, date in ee:
            print(f"            {kind} {date}: {ndoi} (read the notice: figures and conclusions may have changed)")
        time.sleep(0.12)
    print(f"--- {len(dois)} DOIs · {retracted} retracted")
    sys.exit(1 if retracted else 0)


# ─────────────── sources ───────────────
def load_sources(folder):
    out = {}
    for f in sorted(Path(folder).glob("*.md")):
        fm, body = front_matter(read(f))
        m = re.match(r"^(s\d+)", f.stem, re.I)
        sid = fm.get("id") or (m.group(1) if m else None)
        if not sid or fm.get("type") == "gaps":
            continue
        out[sid.lower()] = {"file": f.name, "fm": fm, "body": body}
    return out


def canon_url(u):
    from urllib.parse import urlparse, parse_qsl, urlencode
    if not u:
        return ""
    p = urlparse(u.strip().lower())
    q = urlencode(sorted((k, v) for k, v in parse_qsl(p.query) if not re.match(r"^(utm_|fbclid|gclid|ref$|source$)", k)))
    return f"{p.netloc.removeprefix('www.')}{p.path.rstrip('/')}{'?' + q if q else ''}"


def section(body, name):
    m = re.search(rf"^##\s+{name}.*?$(.*?)(?=^##\s|\Z)", body, re.M | re.S | re.I)
    return m.group(1) if m else ""


def norm(t):
    t = t.lower().replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def shingles(t, n=6):
    w = norm(t).split()
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def cmd_independence(a):
    src = load_sources(a.folder)
    ids = list(src)
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x

    why = {}

    def union(x, y, reason):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx
        why.setdefault(find(x), set()).add(reason)

    seen = {}
    for i in ids:
        fm = src[i]["fm"]
        for key, val in (("url", canon_url(fm.get("url", ""))), ("doi", clean_doi(fm.get("doi", "")) if fm.get("doi") else "")):
            if val:
                if (key, val) in seen:
                    union(seen[(key, val)], i, key)
                else:
                    seen[(key, val)] = i
        der = fm.get("derived-from")
        for d in (der if isinstance(der, list) else [der] if der else []):
            if d.lower() in src:
                union(d.lower(), i, "derived-from")
    sh = {i: shingles(section(src[i]["body"], "Quot")) for i in ids}
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            A, B = sh[ids[x]], sh[ids[y]]
            if len(A) >= 4 and len(B) >= 4 and find(ids[x]) != find(ids[y]) and len(A & B) / min(len(A), len(B)) >= 0.5:
                union(ids[x], ids[y], "shared-verbatim-quote")
    groups = {}
    for i in ids:
        groups.setdefault(find(i), []).append(i)
    multi = [g for g in groups.values() if len(g) > 1]
    print(f"{len(ids)} sources · {len(groups)} independent voices · {len(multi)} group(s) of one voice")
    for g in multi:
        print(f"  one voice ({'+'.join(sorted(why.get(find(g[0]), {'?'})))}): {', '.join(sorted(g))}")
    out = Path(a.folder).parent / "temp" / "independence.json"
    write(out, json.dumps({"sources": len(ids), "voices": len(groups), "groups": [sorted(g) for g in multi]}, indent=2))
    print(f"written: {out}")


# ─────────────── citations ───────────────
MARK = re.compile(r"\[(s\d+(?:\s*[,;]\s*s\d+)*)\]", re.I)
QUOTE = re.compile(r"[“\"]([^”\"\n]{12,}?)[”\"]")


def sentences_with_marks(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = [s] if s.startswith("|") else re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÀÇ“\"(\[])", s)
        out += [p for p in parts if p.strip()]
    return out


def numbers(t):
    return {re.sub(r"\D", "", x) for x in re.findall(r"\d[\d.,]*\d", t) if len(re.sub(r"\D", "", x)) >= 2}


def check_cites(draft, folder, everything=False):
    src = load_sources(folder)
    pairs, dangling, pending, bad_quotes, cited = [], [], [], [], set()
    for sent in sentences_with_marks(read(draft)):
        ids = [x.strip().lower() for m in MARK.findall(sent) for x in re.split(r"[,;]", m)]
        if not ids:
            continue
        clean = MARK.sub("", sent).strip()
        nums, has_q = numbers(clean), bool(QUOTE.search(clean))
        for sid in ids:
            cited.add(sid)
            if sid not in src:
                dangling.append({"sentence": clean[:300], "source": sid}); continue
            if nums and nums <= numbers(src[sid]["body"]) and not has_q:
                state = "auto-passed"
            else:
                h = int(hashlib.md5((clean + sid).encode()).hexdigest(), 16)
                picked = everything or bool(nums) or has_q or (len(ids) == 1 and h % 2 == 0) or h % 3 == 0
                state = "checker" if picked else "not-sampled"
                if picked:
                    pending.append({"i": len(pending) + 1, "sentence": clean[:400], "source": sid, "file": src[sid]["file"],
                                    "why": "number" if nums else "quote" if has_q else "sample"})
            pairs.append(state)
        for q in QUOTE.findall(clean):
            if len(q.split()) >= 5:
                pool = [src[s]["body"] for s in ids if s in src] or [v["body"] for v in src.values()]
                if not any(norm(q) in norm(b) for b in pool):
                    bad_quotes.append({"quote": q[:200], "sources": ids})
    return {"pairs": len(pairs), "auto_passed": pairs.count("auto-passed"), "for_checker": len(pending),
            "not_sampled": pairs.count("not-sampled"), "dangling": dangling, "quotes_without_source": bad_quotes,
            "uncited_sources": sorted(set(src) - cited), "checker_queue": pending}


def cmd_cites(a):
    r = check_cites(a.draft, a.folder, a.all)
    out = Path(a.folder).parent / "temp" / "citecheck.json"
    write(out, json.dumps(r, ensure_ascii=False, indent=2))
    print(f"pairs {r['pairs']} · auto-passed {r['auto_passed']} · for the checker {r['for_checker']} · not sampled {r['not_sampled']}")
    print(f"DANGLING (critical): {len(r['dangling'])} · QUOTES WITHOUT SOURCE: {len(r['quotes_without_source'])} · "
          f"uncited sources: {len(r['uncited_sources'])}")
    for d in r["dangling"]:
        print(f"  ✗ [{d['source']}] {d['sentence'][:120]}")
    for q in r["quotes_without_source"]:
        print(f"  ✗ quote not found in {q['sources']}: “{q['quote'][:110]}”")
    print(f"written: {out}")
    sys.exit(1 if r["dangling"] or r["quotes_without_source"] else 0)


def reference(fm):
    au = fm.get("author") or fm.get("authors") or ""
    au = "; ".join(au) if isinstance(au, list) else au
    title = fm.get("title") or "?"
    loc = f"https://doi.org/{fm['doi']}" if fm.get("doi") else fm.get("url", "")
    parts = [f"{au} ({fm.get('year') or 'n.d.'})." if au else f"({fm.get('year') or 'n.d.'}).",
             f"*{title}*" + ("" if title[-1:] in "?!." else ".")]
    if fm.get("venue"):
        parts.append(f"{fm['venue']}.")
    if loc:
        parts.append(loc)
    if fm.get("tier"):
        parts.append(f"[{fm['tier'].upper()}]")
    return " ".join(parts)


def cmd_number(a):
    src = load_sources(a.folder)
    text = read(a.draft)
    order = []
    for m in MARK.finditer(text):
        for x in re.split(r"[,;]", m.group(1)):
            x = x.strip().lower()
            if x not in order:
                order.append(x)
    missing = [x for x in order if x not in src]
    if missing:
        sys.exit(f"ERROR: citation without a source note: {', '.join(missing)}. Run `cites` first.")
    num = {s: i + 1 for i, s in enumerate(order)}
    body = MARK.sub(lambda m: "[" + ", ".join(map(str, sorted({num[x.strip().lower()] for x in re.split(r"[,;]", m.group(1))}))) + "]",
                    text).rstrip()
    refs = "\n".join(f"{num[s]}. {reference(src[s]['fm'])}" for s in order)
    write(a.out, f"{body}\n\n## {a.refs_title}\n\n{refs}\n")
    print(f"{len(order)} cited sources → numbered bibliography · written: {a.out}")


# ─────────────── formulas ───────────────
UNI_MATH = set("≤≥≠≈×·−±∞→∑∏∫∂αβγδεζηθλμνξπρστφχψωΓΔΘΛΣΦΨΩ√∈∉⊂⊆∪∩∀∃′″")
INLINE = r"(?<![\\$\w])\$(?!\s)([^$\n]+?)(?<!\s)\$(?![\w$])"


def find_formulas(text):
    t = re.sub(r"```.*?```", lambda m: " " * len(m.group(0)), text, flags=re.S)
    t = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), t)
    out = [("block", m.group(1), text.count("\n", 0, m.start()) + 1) for m in re.finditer(r"\$\$(.+?)\$\$", t, re.S)]
    rest = re.sub(r"\$\$.+?\$\$", lambda m: " " * len(m.group(0)), t, flags=re.S)
    out += [("inline", m.group(1), text.count("\n", 0, m.start()) + 1) for m in re.finditer(INLINE, rest)
            if not re.fullmatch(r"[\d.,\s]+", m.group(1))]
    loose = len(re.findall(r"(?<!\\)\$", re.sub(INLINE, " ", rest)))
    return sorted(out, key=lambda x: x[2]), loose


def cmd_formulas(a):
    text = read(a.file)
    forms, loose = find_formulas(text)
    try:
        import latex_omml as lo
    except Exception:
        lo = None
    try:
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib.mathtext import MathTextParser, math_to_image
        mt = MathTextParser("path")
    except Exception:
        mt = None
        print("note: matplotlib not installed; no drawing check")
    if a.png:
        Path(a.png).mkdir(parents=True, exist_ok=True)
    errors = warns = 0
    lines = text.splitlines()
    for n, (kind, tex, ln) in enumerate(forms, 1):
        probs = []
        if tex.count("{") - tex.count("\\{") != tex.count("}") - tex.count("\\}"):
            probs.append(("ERROR", "unbalanced braces"))
        if len(re.findall(r"\\left\b", tex)) != len(re.findall(r"\\right\b", tex)):
            probs.append(("ERROR", "\\left without \\right"))
        uni = sorted({c for c in tex if c in UNI_MATH})
        if uni:
            probs.append(("WARN", f"Unicode instead of a LaTeX command: {''.join(uni)}"))
        if re.search(r"\\begin\{", tex):
            probs.append(("WARN", "environment (align, cases, matrix): fine for pandoc, not for the built-in Word converter"))
        if lo:
            try:
                lo.latex_to_mathml(tex)
            except Exception as e:
                probs.append(("WARN", f"built-in Word converter cannot take it ({e}); export with pandoc"))
        if mt:
            try:
                mt.parse(f"${tex.strip()}$")
                if a.png:
                    math_to_image(f"${tex.strip()}$", str(Path(a.png) / f"formula-{n:02d}-L{ln}.png"), dpi=170)
            except Exception as e:
                msg = str(e).strip().splitlines()
                probs.append(("WARN", f"matplotlib cannot draw it: {msg[-1][:90] if msg else e}"))
        if kind == "block":
            near = "\n".join(lines[max(0, ln - 3): ln + tex.count("\n") + 4]).lower()
            if not re.search(r"\b(where|onde|em que|with|sendo)\b", near):
                probs.append(("WARN", "display formula with no 'where' defining its symbols nearby"))
            if not re.search(r"eq\.|equation\s*\(?\d|equa[çc][ãa]o\s*\(?\d|\(\d+\.?\d*\)|\b(1[5-9]|20)\d\d\b|our model|modelagem nossa", near):
                probs.append(("WARN", "display formula with no source location (author, year, eq. no.) nor 'our model'"))
        errors += sum(p[0] == "ERROR" for p in probs)
        warns += sum(p[0] == "WARN" for p in probs)
        print(f"{'ERROR' if any(p[0] == 'ERROR' for p in probs) else 'warn ' if probs else 'ok   '} #{n:02d} L{ln:<5} {kind:<6} {tex.strip()[:80]}")
        for lvl, msg in probs:
            print(f"        {lvl}: {msg}")
    if loose:
        errors += 1
        print(f"ERROR {loose} unpaired $ delimiter(s)")
    outside = re.sub(r"\$\$.+?\$\$|\$[^$\n]+\$|```.*?```|`[^`\n]*`", " ", text, flags=re.S)
    for ln, line in enumerate(outside.splitlines(), 1):
        hits = re.findall(r"\S*[ᵢⱼₖₙₓ₀-₉⁰-⁹⁻]\S*|[A-Za-z]\s*\([^)]{1,15}\)\s*=\s*[−\-]?\s*\S+", line)
        hits = [h for h in hits if re.search(r"[ᵢⱼₖₙₓ₀-₉⁰-⁹⁻−=]", h)]
        if hits and not line.lstrip().startswith(("|", "#")):
            warns += 1
            print(f"warn  L{ln:<5} formula outside LaTeX (Unicode or plain text): {', '.join(dict.fromkeys(hits))[:110]}")
    print(f"--- {len(forms)} formulas · {errors} ERROR · {warns} warning(s)" + (f" · PNGs in {a.png} (open and compare with the source)" if a.png and forms else ""))
    sys.exit(1 if errors else 0)


# ─────────────── gate ───────────────
LEAK = re.compile(r"\[s\d+|\bTODO\b|\bTBD\b|draft\.md|findings\.json|decomposition\.json|self-critique|prolixity control", re.I)


def cmd_gate(a):
    p = run_dir(a.tag)
    d = load_run(p)
    rep = Path(a.file) if a.file else p / "report.md"
    checks = []

    def ok(name, passed, detail=""):
        checks.append({"check": name, "passed": passed, "detail": detail})

    if not rep.exists():
        ok("report-exists", False, str(rep))
        return close_gate(p, d, checks)
    text = read(rep)
    ok("report-exists", True, str(rep))
    dec = json.loads(read(p / "decomposition.json")) if (p / "decomposition.json").exists() else {}
    heads = [norm(x) for x in re.findall(r"^#{1,3}\s+(.+)$", text, re.M)]
    missing = [s for s in dec.get("required_sections", []) if not any(norm(re.sub(r"^#+\s*", "", s)) in h for h in heads)]
    ok("required-sections", not missing, "missing: " + "; ".join(missing) if missing else f"{len(dec.get('required_sections', []))} present")
    body = re.split(r"^##\s+.*(?:refer|bibliograph|sources|works cited).*$", text, flags=re.M | re.I)[0]
    words = len(re.findall(r"\w+", re.sub(r"\$\$.*?\$\$", " ", body, flags=re.S)))
    rng = dec.get("words")
    ok("length", (rng[0] * 0.8 <= words <= rng[1] * 1.2) if rng else True,
       f"{words} words" + (f" (range {rng[0]}-{rng[1]}, ±20%)" if rng else ""))
    draft = p / "draft.md"
    if draft.exists():
        r = check_cites(draft, p / "sources")
        ok("no-dangling-citations", not r["dangling"], f"{len(r['dangling'])} dangling")
        ok("quotes-have-sources", not r["quotes_without_source"], f"{len(r['quotes_without_source'])} without source")
        need = r["for_checker"] > 0 and d.get("level") != "light"
        ok("checker-ran", (not need) or (p / "temp" / "citecheck-verdict.json").exists(),
           f"{r['for_checker']} sampled pair(s)")
    else:
        ok("no-dangling-citations", False, "draft.md missing: the check runs on the draft with [sNN]")
    used = {int(x) for m in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", body) for x in m.split(",")}
    defined = {int(x) for x in re.findall(r"^(\d+)\.\s", text[len(body):], re.M)}
    ok("bibliography", used == defined, f"cited without entry: {sorted(used - defined)} · entries never cited: {sorted(defined - used)}")
    leaks = sorted(set(m.group(0) for m in LEAK.finditer(text)))
    ok("no-process-leaks", not leaks, ", ".join(leaks))
    r = subprocess.run([sys.executable, str(Path(__file__)), "formulas", str(rep)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    ok("formulas", r.returncode == 0, (r.stdout.strip().splitlines() or ["?"])[-1])
    r = subprocess.run([sys.executable, str(Path(__file__)), "doi", str(rep)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    retr = [l for l in r.stdout.splitlines() if "RETRACTED" in l]
    missing_dois = [l for l in r.stdout.splitlines() if l.startswith("NOT FOUND")]
    ok("retractions", bool(not retr or re.search(r"retract", body, re.I)), f"{len(retr)} retracted source(s) cited")
    ok("dois-exist", not missing_dois, f"{len(missing_dois)} DOI(s) found nowhere")
    if (p / "sources").exists():
        r = subprocess.run([sys.executable, str(Path(__file__)), "meta", str(p / "sources")], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=900)
        ok("metadata-and-corrections", r.returncode == 0, (r.stdout.strip().splitlines() or ["?"])[-1][:150])
    close_gate(p, d, checks)


def close_gate(p, d, checks):
    passed = all(c["passed"] for c in checks)
    for c in checks:
        print(f"{'OK  ' if c['passed'] else 'FAIL'} {c['check']:<24} {c['detail']}")
    print(f"=== GATE: {'PASSED' if passed else 'FAILED'}")
    write(p / "temp" / "gate.json", json.dumps({"at": now(), "passed": passed, "checks": checks}, indent=2))
    d["state"] = "gate-passed" if passed else "blocked-at-gate"
    save_run(p, d)
    sys.exit(0 if passed else 1)


# ─────────────── export ───────────────
PS_PDF = r"""
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
try { $d = $w.Documents.Open($env:EXP_DOCX, $false, $true); $d.SaveAs2([ref]$env:EXP_PDF, [ref]17); $d.Close([ref]0) }
finally { $w.Quit() }
"""


def cmd_export(a):
    md = Path(a.file).resolve()
    fmts = {f.strip().lower() for f in a.formats.split(",")}
    base = md.with_suffix("")
    text = read(md)
    forms, _ = find_formulas(text)
    fails = []
    r = subprocess.run([sys.executable, str(Path(__file__)), "formulas", str(md)] + (["--png", a.png] if a.png else []),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("[md]   " + (r.stdout.strip().splitlines() or ["?"])[-1])
    if r.returncode:
        print(r.stdout)
        sys.exit("ERROR: a formula has an ERROR in the .md; fix it before exporting.")
    docx_p, pdf_p = base.with_suffix(".docx"), base.with_suffix(".pdf")
    pandoc = shutil.which("pandoc")
    if fmts & {"docx", "pdf"}:
        if docx_p.exists() and docx_p.stat().st_mtime > md.stat().st_mtime and not a.force:
            sys.exit(f"ERROR: {docx_p.name} is newer than the .md (edited in Word?). Move the edits to the .md, or use --force.")
        if pandoc:
            cmd = [pandoc, str(md), "-o", str(docx_p), "--from", "markdown+tex_math_dollars+pipe_tables"]
            if a.template:
                cmd += ["--reference-doc", a.template]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode:
                sys.exit(f"ERROR in pandoc: {r.stderr[-500:]}")
            how = "pandoc"
        else:
            import md_docx, latex_omml
            md_docx.render(str(md), str(docx_p), a.template)
            try:
                latex_omml.convert(str(docx_p))
            except FileNotFoundError as e:
                fails.append(f"docx: {e}")
            how = "built-in renderer"
        import docx as _docx
        from docx.oxml.ns import qn
        d = _docx.Document(str(docx_p))
        n_eq = sum(1 for _ in d.element.body.iter(qn("m:oMath")))
        texts = [p.text for p in d.paragraphs] + [p.text for t in d.tables for row in t.rows for c in row.cells for p in c.paragraphs]
        raw = [t for t in texts if re.search(r"(?<!\\)\$[^$\s][^$]*\$", t)]
        if n_eq < len(forms):
            fails.append(f"docx: {n_eq} native equations for {len(forms)} formulas in the .md")
        if raw:
            fails.append(f"docx: {len(raw)} paragraph(s) with raw LaTeX: {raw[0][:80]}")
        print(f"[docx] {docx_p} · {how} · {n_eq} native Word equation(s) for {len(forms)} formula(s)")
    if "pdf" in fmts:
        made = False
        if os.name == "nt":
            env = dict(os.environ, EXP_DOCX=str(docx_p), EXP_PDF=str(pdf_p))
            r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", PS_PDF], env=env,
                               capture_output=True, text=True, timeout=300)
            made = r.returncode == 0 and pdf_p.exists()
        if not made and shutil.which("soffice"):
            r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(pdf_p.parent), str(docx_p)],
                               capture_output=True, text=True, timeout=300)
            made = pdf_p.exists()
        if not made and pandoc and (shutil.which("xelatex") or shutil.which("lualatex")):
            eng = "xelatex" if shutil.which("xelatex") else "lualatex"
            r = subprocess.run([pandoc, str(md), "-o", str(pdf_p), f"--pdf-engine={eng}"], capture_output=True, text=True)
            made = pdf_p.exists()
        if not made:
            fails.append("pdf: no converter found (Word on Windows, LibreOffice, or pandoc with a LaTeX engine); "
                         "open the .docx and save as PDF")
        else:
            info = ""
            try:
                import pdfplumber
                with pdfplumber.open(str(pdf_p)) as pdf:
                    txt = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
                    info = f" · {len(pdf.pages)} page(s)"
                if re.search(r"\$\$|\\(frac|sum|mathrm|log)\b", txt):
                    fails.append("pdf: raw LaTeX left in the PDF text")
            except ImportError:
                pass
            print(f"[pdf]  {pdf_p}{info}")
            if a.png:
                try:
                    import pypdfium2 as pdfium
                    doc = pdfium.PdfDocument(str(pdf_p))
                    Path(a.png).mkdir(parents=True, exist_ok=True)
                    for i in range(len(doc)):
                        doc[i].render(scale=1.4).to_pil().save(str(Path(a.png) / f"page-{i + 1:02d}.png"))
                    print(f"[pdf]  pages drawn in {a.png}: open the ones with formulas and tables")
                except ImportError:
                    print("[pdf]  install pypdfium2 to draw pages for the visual check")
    for f in fails:
        print(f"FAIL {f}")
    print("=== EXPORT: " + ("FAILED" if fails else "OK"))
    sys.exit(1 if fails else 0)


def main():
    global ARGS_DIR
    ap = argparse.ArgumentParser(description="local engine of the rigorous-research skill")
    ap.add_argument("--dir", help="workspace folder (default ./research or RESEARCH_DIR)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("init", aliases=["iniciar"]); x.add_argument("slug"); x.add_argument("--profile", default="report")
    x.add_argument("--level", choices=list(SEQ), default="standard"); x.set_defaults(f=cmd_init)
    x = sp.add_parser("step", aliases=["passo"]); x.add_argument("tag"); x.add_argument("id")
    x.add_argument("--status", required=True, choices=["running", "done", "skipped"]); x.add_argument("--note"); x.set_defaults(f=cmd_step)
    x = sp.add_parser("resume", aliases=["retomar"]); x.add_argument("tag", nargs="?"); x.set_defaults(f=cmd_resume)
    x = sp.add_parser("scholar", aliases=["academico"]); x.add_argument("query"); x.add_argument("--n", type=int, default=10)
    x.add_argument("--since", type=int); x.add_argument("--lang"); x.add_argument("--type")
    x.add_argument("--order", choices=["relevance", "citations"], default="relevance"); x.set_defaults(f=cmd_scholar)
    x = sp.add_parser("doi"); x.add_argument("inputs", nargs="+"); x.set_defaults(f=cmd_doi)
    x = sp.add_parser("independence", aliases=["independencia"]); x.add_argument("folder"); x.set_defaults(f=cmd_independence)
    x = sp.add_parser("meta", aliases=["metadados"]); x.add_argument("folder"); x.set_defaults(f=cmd_meta)
    x = sp.add_parser("cites", aliases=["citacoes"]); x.add_argument("draft"); x.add_argument("folder")
    x.add_argument("--all", action="store_true"); x.set_defaults(f=cmd_cites)
    x = sp.add_parser("number", aliases=["numerar"]); x.add_argument("draft"); x.add_argument("folder"); x.add_argument("--out", required=True)
    x.add_argument("--refs-title", default="References"); x.set_defaults(f=cmd_number)
    x = sp.add_parser("formulas"); x.add_argument("file"); x.add_argument("--png"); x.set_defaults(f=cmd_formulas)
    x = sp.add_parser("gate", aliases=["portao"]); x.add_argument("tag"); x.add_argument("--file"); x.set_defaults(f=cmd_gate)
    x = sp.add_parser("export", aliases=["exportar"]); x.add_argument("file")
    x.add_argument("--formats", default="md,docx,pdf"); x.add_argument("--template"); x.add_argument("--png")
    x.add_argument("--force", action="store_true"); x.set_defaults(f=cmd_export)
    a = ap.parse_args()
    ARGS_DIR = a.dir
    a.f(a)


if __name__ == "__main__":
    main()
