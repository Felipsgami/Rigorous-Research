# Step 6 · Draft in the chosen profile

**You** write it (not a researcher), once, in `research/<tag>/draft.md`. Before writing, read: `query.md`, `decomposition.json`, `map.md`, `temp/prior.md`, the profile in `profiles.md`, and **the full source notes** you will cite (not just their summaries).

## Before the first word
- Load the voice bans for the output language (the companion skill `humanize-text` has them in full; at minimum: no era frames, no "it's important to note", no anonymous "studies show", no "not X but Y" without an owner, no inflated significance, no chatbot residue) and the five status questions of `status-check.md`.
- Build the skeleton with **exactly** the `required_sections`, in order. A required section the evidence does not support stays, saying what is missing.

## Citing in the draft
- Every claim that is not trivial public knowledge carries the marker of the note that supports it: `[s23]`, or `[s23, s41]` for two voices.
- **Always cited:** numbers, dates, formulas, quotations, names of laws/effects/principles, attributions of authorship, disputed claims, anything a sceptical reader would want to check.
- A claim with no note does not go in. A claim you know is true but have no note for → one more search, or mark it `> [!question] To verify`. A public fact confirmed on the web goes in with the note of the source that confirmed it.
- **Do not write the bibliography.** `number` builds it from the notes in step 11.

## Writing law
1. **The answer first.** The opening of the text (and of each section) states the finding; the route comes after.
2. **The caveat sits next to the claim**, when it applies. Never collected in a final "limitations" appendix that readers of the body never reach.
3. **The source's exact status.** If the note says `status: model`, the text says "the model of X describes", never "X is". A central analogy says where it breaks. What the source gave as disputed (level 3) does not become consensus; our own application is declared "our model" (level 4).
4. **Conflicts shown:** both sides, the strength of each, the scope; take a position only where the evidence allows, and say why.
5. **Consensus counts voices:** "three independent groups" only if `independence` said three voices.
6. **Data interpreted, not listed:** what the number means, with its denominator, period and a fair comparison (`formulas-and-numbers.md`).
7. **Perspective as a tool:** the topic's culture of origin first, a counterpoint from outside when it illuminates, never as a quota.
8. **Density without filler:** each paragraph brings information, a source or a new inference. Tables when comparing is the job; prose when arguing is the job.
9. **What is not known** has a place in the text (gaps left after step 5), written as a finding. **A negative claim carries its scope:** "there is no literature on X" only with where you looked (databases, languages, date).
9b. **The caveat governs and is never undone:** it sits in the sentence or paragraph it qualifies, and no closing line cancels it ("still, X is Y" after saying X only works as Y).
9c. **The source's level of analysis:** a finding about tasks does not become a claim about people; a population correlation does not become an individual prognosis; a trend does not become a law.
10. **Register `teach`:** start from what the reader already knows, one step at a time, the concrete example before the abstraction, a table or diagram where prose alone tangles.
11. **Formulas:** only those transcribed in a note, in LaTeX, with "where" defining every symbol and the location (author, year, equation number). Full rules in step 10.
12. **Output language:** the one in `decomposition.json`; in English, one variant (US or UK) throughout.

## When you finish
- Run `python scripts/research.py cites research/<tag>/draft.md research/<tag>/sources` once now: dangling citations and quotes without a source are fixed before the critics.
- From here on the draft is **never rewritten**: surgical edits only (steps 8 and 9).
