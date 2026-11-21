# Steps 4 and 5 · Dispute map and corpus critic

## Step 4 · Coverage, independence and map

1. **Independence:** `python scripts/research.py independence research/<tag>/sources`. Groups that are one voice (same canonical URL, same DOI, `derived-from`, shared verbatim quotation) count as **one** voice in everything that follows. Five reprints of one press release are one source.
2. **Coverage per atomic item**, counting independent voices: **well covered** (3 or more) · **adequate** (2) · **thin** (1) · **uncovered** (0). An uncovered item goes to step 5 as a critical gap.
3. **Disputes:** gather opposing claims from the notes (same target with opposite positions, same entities with opposite conclusions, same scope with different numbers) into **conflicts**:

```markdown
### C1 · <one sentence: what is disputed>
- side A: <position> · [s03, s17] · evidence type: experimental | observational | theoretical | anecdotal
- side B: <position> · [s22]
- strength gap: <which side has better evidence, and why>
- scope: <real disagreement, or different scopes where both are right?>
- relevance to the question: high | medium | low
```

4. **Consensus:** claims with 3 or more independent voices agreeing and no counter-evidence of comparable strength. This is ground the text can state without hedging (at the status the sources give, never above it).
5. **Expert tensions** nobody resolves become a section or paragraph of their own in the text, never a footnote.
6. **Inference depth:** if the corpus shows the answer lives in grey literature or hard primary sources, raise `inference_depth` in `decomposition.json` and say why.

Write all of it to `map.md`. At `deep` with more than 40 notes, hand the map to a sub-agent (if available) that reads the notes and writes only `map.md`, keeping your context free for drafting.

## Step 5 · Corpus critic and the single gap round

The highest-leverage point of the run: a correction made before drafting costs nothing; after it, it costs patching.

### 5.1 Mechanical pre-flight
- For every **pinned period**: is there a note with the primary source **for that exact period**? The 1844 edition does not stand in for 1819; the 2024 report does not answer for 2025. Missing → critical gap.
- **Perspective:** if the question involves cultures or traditions, is there at least one voice from outside the topic's own cultural block, with a source? Missing → critical gap.
- A formula the profile needs with no note transcribing it from a source → critical gap.

### 5.2 Critic (one sub-agent, or yourself in a fresh pass)
Give it the verbatim question, `map.md`, `decomposition.json`, the path to `sources/`, and the task:
- **"What source, if it existed, would overturn the current direction?"** For each thesis the map supports: the evidence that would invalidate it and the query that would find it.
- **Problem inversion:** what if the question's premise is wrong? What would we see in the world if it were?
- **Strengthening gaps:** a thesis with one voice, a number with no primary source, a second-hand quotation.
- **Missing reception and context:** who disagrees, from which school, in which language.
- **Refute novelty and absence.** Every conclusion like "this is new", "understudied", "there is no literature on", "it has no name" becomes a target: search for the phenomenon described without its name, in other fields and languages, and for work from the last two years. Narrowing your own gap before drafting is the best possible result.
- **Editorial state of the sources behind each thesis:** run `research.py meta sources` before drafting; an unread correction is a superseded number waiting to enter the text.

Output `temp/gaps.json`: `[{"id": "g1", "type": "overturn | strengthen | independent-check | period | perspective", "priority": "critical | high", "target": "...", "queries": ["..."], "source_type": "..."}]`, pre-flight gaps first.

### 5.3 One search round
Send 1 to 3 researchers (same brief as step 3, with the gaps in place of the planned queries, and new numbering ranges). **Only one round.** Then draft with what you have, even if something is missing: a remaining gap becomes a "what is not known" paragraph in the text and a line in the open-questions list. More rounds burn time, context and quota without changing the answer in proportion.

### 5.4 Update the map
- Overturning source found → the position weakens in `map.md`, with how much.
- Adversarial search found nothing → record it: "a search for counter-evidence to <thesis> found no substantive challenge" (this **is** evidence and goes in the text).
- Strengthening found → note it; the text may state it more firmly, never above the source's status.
