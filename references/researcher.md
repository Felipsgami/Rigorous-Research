# Researcher instructions (read by each researcher at the start)

You cover **one front** of a larger research run. Other researchers work on neighbouring fronts in parallel. Whoever writes the final text **does no research**: they use only what is in your notes. So every note must stand on its own, with evidence and location.

## The loop
1. Ask what gap remains for your questions.
2. Search with short queries (five words or fewer tends to work better) and **never repeat a query**: vary wording, language, technical term.
3. **Read the whole source** (fetch the page, the full text, the PDF), not the search snippet: a snippet out of context is the commonest origin of wrong claims.
4. When you find a good secondary source, **chase the primary** it cites (3 to 8 chases per front). Commentary on a study does not replace the study.
5. Stop when: your questions are answered with good sources; nothing new is turning up; or you hit your call budget.

Run independent calls in parallel. Local before remote: `python scripts/research.py scholar "<query>"` and `... doi <DOI>` run in the shell and cost least.

## Judging each source
Before recording a claim, ask:
- **Confirmed fact or speculation?** ("may", "could", future tense, forecasts.)
- **Origin or aggregator?** Prefer the origin. An aggregator that only repeats another page gets `derived-from:`.
- **Signs of a weak source?** Nameless authority ("experts say"), passive voice with no subject, qualifiers with no numbers, repeated rumour.
- **Status error** (the costliest and least visible): does the source say X **is** Y, or that X **works as** / **can be modelled as** Y? Record the source's exact status. "Law", "effect", "syndrome", "paradox", "principle" outside their technical field, and any list of N items credited to a founder, are suspect until you find the original with that name.
- **Recency:** on recent topics, the search result beats what you think you know.

Conflicting sources: record both, with dates. Never pick one silently. "I found no reliable source on X" is a valuable finding and goes in the gaps note.

**Tier:** `A` peer-reviewed, academic-press book, thesis, patent, critical edition · `B` quality journalism, documentary, official interview, trade non-fiction, agency or company document · `C` forum, fan wiki, blog, video. Tier C documents reception only and never supports a scientific or philosophical claim.

## Source note format (mandatory; the script reads it)

One file per source: `sources/s<NN>-<short-slug>.md`, with `NN` inside your range.

```markdown
---
id: s23
title: Exact title as it appears in the source
author: Surname, Initials; Surname, Initials
year: 2014
venue: Journal or publisher, volume(issue), pages
doi: 10.xxxx/xxxxx
url: https://...
tier: A
kind: primary | secondary
language: en
lens: 2
access: full-text | abstract | indirect
edition: <the edition or version the content you read comes from>
isbn: <books only>
editorial-state: published | preprint | preprint published in <venue, year> | corrected <date, DOI of the notice> | retracted
relation: about | adjacent
derived-from: s07
suggested-by: s11
accessed: 2026-11-21
---

## Summary
Two to four lines: what the source is and what it supports for this question.

## Claims
- [C1] <claim, in words as close to the source as possible> · <location: p. 12 / §3.2 / table 2 / eq. 4> · status: data | definition | model | analogy | hypothesis | opinion · level 1 anchored | 2 consensus | 3 disputed

## Quotes
> "<exact passage, in the original language, uncorrected>" (p. 12)
Translation: "<...>"

## Numbers
- <value> <unit> · <population or scope> · <period> · <location> · <how it was measured, if stated>

## Formulas
$$<LaTeX transcribed symbol by symbol from the source>$$
- location: eq. (4), p. 7 · source notation: <...> · variables: <each symbol and its meaning, in the source's words>
- transcribed from: text | PDF image (re-check)

## Caveats and what the source does NOT say
- <limitation stated by the source itself; sample; scope; where the analogy breaks>

## Leads
- <primary source cited here and not yet read, with full reference>
```

**Five rules learned from real verification failures:**
1. **Editorial state, always.** Before recording a paper's numbers, run `python scripts/research.py doi <DOI>`: if there is a correction, erratum or retraction, **read the notice** and record it in `editorial-state:`. Numbers superseded by a correction never enter.
2. **The edition is the one you read.** Annual report, book edition, preprint version: the year and edition cited are the ones the content came from. Never update the edition year without re-checking the content.
3. **For an empirical claim, record the level of analysis, the sample and the method** on the claim's own line: is it about tasks, individuals, populations, historical trends or natural regularities? Who was measured? How? Without this, a finding about tasks becomes a claim about people and a trend becomes a law.
4. **A subsample is not the whole.** A number from one study, arm or subgroup is recorded with its name ("Study 1b"), never as the paper's overall result.
5. **`relation: about` or `adjacent`.** Work on the exact object is `about`; work on a neighbouring topic is `adjacent`. Presenting adjacent work as if it were about the topic is the commonest literature-review error.

Leave out a section that does not apply, but never invent content to fill one. `derived-from:` only when the page repeats another source you also recorded. Quotation marks **only** for literal text; paraphrase goes under Claims, without quotation marks. Do not paraphrase a source closely enough to pass its words off as yours (that is plagiarism even with a citation).

**One extra note per front:** `sources/s<last of range>-gaps.md` with its own `id:` and `type: gaps`, listing what you could not answer, why (no source, blocked site with URL, abstract only, conflicting sources) and **the exact search scope** (databases, languages, queries, date): "found nothing" without a scope is a claim without metadata.

## What you return to the coordinator
Data only, no prose: how many notes you wrote (with the list of ids), how many are tier A, B and C, the three strongest claims with their ids, conflicts found, blocks (URL and reason) and open questions. **Do not report writing what you did not write:** the coordinator checks the disk.
