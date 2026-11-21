# Steps 11 and 12 · Gate, delivery and export

## Step 11 · Number, gates, final gate

1. **Number:** `python scripts/research.py number research/<tag>/draft.md research/<tag>/sources --out research/<tag>/report.md --refs-title "<the profile's reference heading>"`. It turns `[sNN]` into `[N]` in order of appearance and builds one bibliography, pruned to what is cited, with tiers. `draft.md` stays as it is: it is the audit trail of every citation. If the profile needs another citation style (author-date, footnotes, ABNT, APA, Vancouver), convert the numbered list as the last edit and say so.
2. **Voice gate** on `report.md`: the blacklist of the output language (companion skill `humanize-text`, light regime for internal technical documents, full regime for anything published).
3. **Status gate** (`status-check.md`): copula, agency, triads, analogies with no breaking point, erased disagreement, a level promoted relative to the source note.
4. Fix gate findings by editing **both** `report.md` and `draft.md` (they move together; if they diverge, the gate checks the wrong text).
4b. **Consistency with the user's own documents:** if the user's notes, earlier reports or published work state the same number or date, check they agree; a divergence goes into the report, and the primary source decides.
5. **Final gate:** `python scripts/research.py gate <tag>` (it includes `meta`: title, author, year and venue against Crossref, preprints, and any correction or retraction the note does not record).

**Four levels of source verification, recorded separately because they fail differently:** (1) **existence** (`doi`), (2) **metadata** (`meta`: a real reference with a displaced title or author, or one conflated from several works, passes an existence check), (3) **editorial state** (preprint, published, corrected, retracted), (4) **support** (the checker in step 9, reading the source, not the abstract). Level 4 matters most and is the only one that needs reading. It checks required sections, length (profile range ±20%), dangling citations, quotes without a source, the checker's verdict file, a bibliography with no orphan numbers, process leaks, formulas, retractions, and DOIs that exist nowhere.
6. **The gate's verdict is final.** If it fails, change the **text** until it passes; do not reinterpret the rule. Up to three rounds. On the third failure the run stays `blocked-at-gate` and the report to the user says exactly what failed: a blocked run with an honest manifest is worth more than a delivered one that lies.
   - over the length ceiling → one compression pass, cutting repetition, never caveats;
   - quote without a source → it becomes an unquoted paraphrase, or goes back to the literal note;
   - retracted → the sentence says the study was retracted, or the citation goes.

## Step 12 · Delivery

### Destination
- Copy `report.md` to the destination in `decomposition.json` with a clear name (default `research/<tag>/<Short title>.md`).
- **Never overwrite** an existing file: if the destination exists, save with a suffix and say so.

### Export (Markdown, Word, PDF)
The `.md` is the source and already is the LaTeX export (read in Obsidian, GitHub, VS Code, Typora). Word and PDF are renders:

```bash
python scripts/research.py export "<report.md>" --formats md,docx,pdf --png research/<tag>/temp/export
```

- A formula with an ERROR in the `.md` **blocks** the export.
- `.docx`: with **pandoc** installed it is used (full LaTeX math becomes native, editable Word equations; `--template ref.docx` applies your styles). Without pandoc, the built-in renderer plus the LaTeX→Word converter (needs Microsoft Office's MML2OMML.XSL, found automatically on Windows and macOS, or set `MML2OMML_XSL`). The script **counts native equations against the formulas in the `.md`** and looks for raw `$`.
- `.pdf`: Word itself on Windows (native equations render perfectly), else LibreOffice, else pandoc with a LaTeX engine. The script looks for raw LaTeX in the PDF text.
- **Visual check, mandatory:** open the pages in `temp/export/page-NN.png` that have formulas or tables and look. The count proves a formula became an equation; only the eye proves it became the right equation.
- A `.docx` newer than the `.md` (edited in Word) is not overwritten: move the edits into the `.md` first. `--force` only when there is nothing to lose.

### Report to the user (short)
1. **The answer**, in three to six lines, with a **confidence** level computed from the evidence, never felt (a model's self-reported confidence is not introspection): **high** = consensus of 3 or more independent voices, at least one tier A, no counter-evidence of comparable strength; **medium** = 2 voices, or a dispute where one side has clearly better evidence; **low** = 1 voice, only tier B or C, or our own inference (level 4).
2. What stayed **disputed** and what stayed **unanswered**.
2b. **Correction log:** every error found and fixed during the run (a figure, a reference label, a false support, an editorial state), with what it was, what it became and how it was caught. Logging your own corrections strengthens the document.
3. The run in numbers: sources read, independent voices, tiers A/B/C, languages, searches; critic findings applied, refused and structural (these with the suggestion).
4. Where each file is (Markdown, and Word and PDF if exported).
5. Blocked sites, in one list (URL and reason), for the user to open if they wish.

### Cross-check runs: keep a ledger of error patterns
When the run audits someone else's research (profile `cross-check`), append to `research/ERROR-PATTERNS.md`: tool of origin (which AI or service), topic, claims checked, and the count per category (`status promoted`, `number differs`, `source does not say this`, `source does not exist`, `wrong attribution`, `caveat lost`), with one literal example each. Update the running totals at the top. **When a pattern shows up in three cross-checks or more**, turn it into an explicit instruction in the brief you give that tool next time. That is how outside research gets better over time: the error measured here becomes a line in the prompt there.
