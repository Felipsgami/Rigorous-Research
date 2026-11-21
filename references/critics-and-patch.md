# Steps 7, 8 and 9 · Critics, patch and citation check

## Step 7 · Adversarial critics

Critics **do not edit** the draft: they write findings. Each gets the verbatim question, the paths to `draft.md`, `decomposition.json`, `map.md` and `sources/`, and one or more lenses. Run them in parallel if your environment has sub-agents; otherwise make each lens a separate pass of your own, reading the draft cold.

| Lens | The question the critic asks |
|---|---|
| **dialectic** | What counter-evidence in the notes did the text ignore or caricature? Did one side of a mapped conflict vanish? |
| **depth** | Where did the text stay shallow when the notes had substance (number, mechanism, quote) to put there? |
| **instruction and breadth** | Did an item of the decomposition go missing, run thin, move out of order or change form? Is a relevant group of sources absent? |
| **status and numbers** | Copula ("X is Y" where the source says "works as"), agency given to a model or algorithm, a triad the author never used, a lost caveat, a promoted level, a number without a denominator, the wrong period, mixed units |

**Inside the status-and-numbers lens, check each central claim for:** the source's **level of analysis** kept (tasks did not become people, a trend did not become a law); **how the result was obtained** survived, not just the result; **who was measured** is stated; the caveat **governs** the reading (it is not subordinated, moved to an appendix, or undone by the closing); attribution **not swapped** for a more prestigious one (the name of a phenomenon credited to someone who did not coin it); and the caveat **adds a fact** rather than only hesitating.

**Automated judges are biased against uncertainty markers** (Lee et al., NAACL 2025). The critics and the checker are models: instruct them that a caveat which adds a fact is never a weakness, and refuse any finding that asks to cut one.

- **`standard`:** one critic with all four lenses.
- **`deep`:** three critics (dialectic + depth · instruction and breadth · status and numbers).

Each writes `temp/findings-<lens>.json`:
```json
[{"id": "d1", "lens": "dialectic", "severity": "critical | major | minor",
  "excerpt": "<literal text from the draft>", "problem": "<one sentence>",
  "evidence": "[s17] says ...", "fix": "<replacement text, up to 80 words>",
  "kind": "patch | structural"}]
```

### Cold reader
The critics know the notes; the real reader does not. At `deep` (and at `standard` when the text goes to third parties), add one more reviewer who receives **only `draft.md`** and the sub-questions, with no notes, no map, no conversation. Task: answer each sub-question using only the document, quoting the passage; then point out ambiguity, unstated assumptions and internal contradiction. A sub-question it cannot answer, or answers wrongly, is a **text** gap (the evidence may be in the notes and never reached the draft): it becomes a patch.

**A new source gap raised by the critics:** one targeted search for `critical` findings only. It does not reopen the sweep.

## Step 8 · Surgical patch

- Read every findings file. Apply each `patch` finding by **editing only the quoted excerpt**. Cap per patch: about 80 new words.
- **Never** rewrite the whole draft or a whole section from here on. A `structural` finding (reorganise or rewrite a section) is not applied: it goes into the final report as a suggestion for the user to decide.
- A `critical` finding is never dropped silently: applied, or refused with a written reason.
- A fix that brings a new fact needs a source note first (a targeted search), and carries its `[sNN]`.
- Log `temp/patches.json`: applied, refused (with reason), structural items passed on.

## Step 9 · Citation-sentence check

A cited source earns trust only if it says what the citing sentence claims. That is the difference between "has citations" and "the citations are true".

1. **Mechanical triage:** `python scripts/research.py cites draft.md sources` (at `deep`, with `--all`). It flags **dangling citations** (critical: fix now), **quotes without a source** (critical: the quote becomes an unquoted paraphrase, or goes back to the literal text in the note), auto-passes the pairs whose numbers appear in the source, and samples the rest for the checker (every pair with a number or a quote is always included).
2. **Checker** (a sub-agent, or a cold pass of your own; split in two above about 40 pairs). Brief: the path to `temp/citecheck.json` (field `checker_queue`), its range, the path to `sources/`, and the rules:
   - for each pair, read the cited note in full and judge **whether the note supports the sentence as written**: `supports` · `partly` (supports the idea but not the number, qualifier or scope) · `does-not-support` · `wrong-source` (another note supports it: find it and name it);
   - judge the **binding** between sentence and source, not whether the sentence is true in the world;
   - hunt on purpose for the two likeliest failures: **the right number on the wrong object** (a subsample as the whole, another edition, another group measured) and **a sentence that claims more than the source** (intent attributed, a stronger verb, "showed" where the source "suggests");
   - **when in doubt, `does-not-support`**; never "probably fine";
   - a number the note lacks, when the note says `access: full-text` with a URL: open the original (up to 5 times) and check; if it matches, return the location so the note can be completed;
   - write `temp/citecheck-verdict.json` with only the pairs that fail: `[{"i": 3, "verdict": "...", "severity": "critical | major", "sentence": "...", "source": "s23", "correct_source": "s41 | null", "what_the_note_says": "...", "fix": "swap citation | lower the claim to what the source supports | delete the sentence"}]`, and `[]` if everything checked out. **The file always exists** (the gate requires it).
   - `critical` for a number with no support and for `wrong-source`; `major` otherwise.
3. **Second patch:** same rules as step 8, applying the verdict. Then run `cites` again until zero dangling and zero unsourced quotes.

**At `light`** only the mechanical triage runs; you check the sampled pairs yourself against the notes and write the verdict to the same file.
