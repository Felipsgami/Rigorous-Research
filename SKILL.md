---
name: rigorous-research
description: >
  Deep research with the rigour of a scientific paper and an output shaped to its use: report,
  brief, fact-check, comparison, timeline, how-to guide, dossier, concept explainer, literature
  review, systematic review, papers in the style of each field (natural sciences, Nature,
  physics, mathematics, engineering, humanities, social sciences), or a structure the user
  dictates. Decomposes the question, searches in five lenses and several languages, runs
  researchers in parallel, maps disputes, counts independent voices, drafts with every claim
  tied to a source note, attacks the draft with critics, patches surgically, checks that each
  citation says what its sentence claims, validates formulas and numbers, and exports to
  Markdown, Word (native equations) and PDF. Also cross-checks research produced by another AI.
  Works in Portuguese and English (US/UK). Use when asked for "deep research", "a thorough
  report on", "literature review", "fact-check this", "check this AI research", "pesquisa
  profunda", "pesquisar sobre", "levantamento completo", "checar estes fatos".
---

# Rigorous research

Two things make AI research go wrong more than anything else: the question already contains the answer, and the citations are decoration (the source exists, but it does not say what the sentence claims). This skill is built against both. Everything mechanical runs locally in `scripts/research.py`; the model judges, the script counts.

## Rules that always hold
1. **The question is law.** The user's literal request goes to `query.md` once; every step and every helper receives it pasted, never paraphrased. Packaging (destination, format, length, output language) lives in `decomposition.json`.
2. **Question hygiene before any search:** no query, brief or sub-question builds in the conclusion. Ask for status and disagreement, not a verdict (`references/status-check.md`).
3. **Nothing without evidence.** Every claim in the final text points to a source note in `sources/` with an exact location. What is uncertain becomes `> [!question] To verify` and is not asserted. Verify before cutting.
4. **Patch, never regenerate.** Once the draft exists, every change is a surgical edit of a quoted excerpt. Anything that needs a section rewritten is structural and goes to the report as a suggestion.
5. **Consensus counts voices, not links** (`research.py independence`).
6. **Script before model:** scholarly search, retractions, independence, citation and quote checks, formula validation, numbering, the gate and the export are mechanical.
7. **The manifest is memory.** Each step starts with `research.py step <tag> <N> --status running` and ends with `--status done`. Save every helper's result to disk before starting the next. A run that is interrupted resumes with `research.py resume`.

## Start
1. **Resuming?** `python scripts/research.py resume [tag]` and continue from the step it names.
2. **Frame** with `references/frame.md` (steps 0 and 1): profile, level, output language and destination are decided there. If the question is ambiguous in a way that changes the research, ask one short question; otherwise take the most likely reading and say which.
3. `python scripts/research.py init "<slug>" --profile <profile> --level light|standard|deep` creates `research/<tag>/` with `sources/`, `temp/` and `run.json`.

## Steps, and where each procedure lives
**Read each step's file when you reach that step**, in full, even if you read it earlier: it keeps a long run from dropping steps as context fills up.

| # | Step | Procedure | light | standard | deep |
|---|---|---|---|---|---|
| 0 | Frame: question, decomposition, coverage matrix, profile, level | `frame.md` | yes | yes | yes |
| 1 | What you already know | `frame.md` | yes | yes | yes |
| 2 | Search plan in five lenses | `sweep.md` | short | yes | yes |
| 3 | Sweep → `sources/` | `sweep.md` + `researcher.md` | yourself | 3 to 5 researchers | 5 to 8 |
| 4 | Coverage, independence, dispute map | `map-and-critic.md` | no | yes | yes |
| 5 | Corpus critic and **one** gap round | `map-and-critic.md` | no | yes | yes |
| 6 | Draft in the profile → `draft.md` with `[sNN]` | `drafting.md` + `profiles.md` | yes | yes | yes |
| 7 | Adversarial critics (+ cold reader) | `critics-and-patch.md` | no | 1 combined | 3 + cold reader |
| 8 | Surgical patch | `critics-and-patch.md` | no | yes | yes |
| 9 | Citation-sentence check, second patch | `critics-and-patch.md` | script only | yes | yes, `--all` |
| 10 | Formulas and numbers | `formulas-and-numbers.md` | yes | yes | yes |
| 11 | Number, voice and status gates, final gate | `gate-and-delivery.md` | yes | yes | yes |
| 12 | Delivery and export (md, docx, pdf) | `gate-and-delivery.md` | yes | yes | yes |

**Respect the level.** Do not add steps "to be safe" or drop steps "to save time": the level is the cost contract. When unsure between two levels, go one up.

**No sub-agents in your environment?** Run every "parallel" item as a sequential pass of your own, writing its output to disk before the next. Critics and the cold reader then read the draft as if for the first time, without the notes in view.

## Export
The `.md` is the source and already carries LaTeX (`$...$`, `$$...$$`). Word and PDF: `python scripts/research.py export "<file.md>" --formats md,docx,pdf --png <folder>`. Word gets native, editable equations and real tables; the PDF comes from Word, LibreOffice or pandoc. The script blocks the export on a formula error, counts native equations against the formulas in the `.md`, looks for raw LaTeX in both files, and draws the pages for the visual check, which is mandatory.

## Files
- `references/` · one file per step, plus `profiles.md` (all output shapes, including papers by field) and `status-check.md` (the truth gate)
- `scripts/research.py` · the engine (Python 3.9+; `requests`; `python-docx` and `lxml` for Word; optional `matplotlib`, `pdfplumber`, `pypdfium2`)
- `scripts/latex_omml.py`, `scripts/md_docx.py` · Word export without pandoc
- `PROMPT.md` · the whole method in one file, for assistants that do not load skills

Companion skill: `humanize-text` holds the full voice rules for Portuguese and English used in steps 6 and 11.
