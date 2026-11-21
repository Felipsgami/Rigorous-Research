# Steps 0 and 1 · Frame the question, then check what you already know

The cheapest step and the one with the most leverage: an error avoided here does not have to be hunted later. The biggest quality variance in long research is whether it answers, in shape and scope, what was actually asked.

## Step 0 · Frame

### 0.1 Pin the question
Write the user's request, character for character, to `research/<tag>/query.md`. It is never edited afterwards, and every researcher brief pastes it whole. Packaging requirements (destination, format, length, output language and variant) go to `decomposition.json`, separate from the question.

### 0.2 Question hygiene (before any search)
Rewrite for internal use (`neutral_question` in `decomposition.json`) any wording that builds in the conclusion. Test: could an honest researcher come back with "the premise is false"? If not, the question is loaded. Ask for **status and disagreement, not a verdict**; ask for the **negative analogy** when the topic revolves around an explanatory image; ask for the primary source with exact location, and for the statement "term absent from the primary work" when it does not exist in the original. (Details: `status-check.md`.)

### 0.3 Decompose into atomic items
Extract **everything** the question names, each as a separate item, even if it looks redundant (a false item is cheap to drop later; a missing one is never found):
- **sub-questions**, explicit and implicit;
- **entities** (work, author, concept, period, institution, product), each with the fields the question asks of it;
- **required formats** (table, timeline, comparison, glossary);
- **required sections** ("include X", "end with Y");
- **pinned periods**: a date, edition, version or year that has its own primary source (the 1819 edition, not "the book"; the 2025 report, not "the latest"). A pinned period researched from the wrong document is the number-one cause of wrong figures;
- **scope conditions** ("in Brazil", "in Zen, not Buddhism in general");
- **out of scope**: what the research does **not** cover.

### 0.4 Coverage matrix (mandatory self-audit)
Re-read the question phrase by phrase. For every noun phrase, proper name and technical term: does it map to an item? Does the item keep the phrase's **natural scope** (it did not narrow "Japanese music" to "anime soundtracks")? If the phrase has two plausible meanings, are both covered? Write `temp/coverage.md`:

```markdown
| Question phrase (verbatim) | Item(s) | Scope | Gap? |
|---|---|---|---|
| "Japanese aesthetics" | E1 mono no aware; E2 wabi-sabi; E3 yūgen | full | no |
| "neuroscience of nostalgia" | S2 | NARROWED: item says "grief" | **YES** |
```

A gap goes back to the decomposition. Never move on with a known gap: a gap here becomes a missing search, which becomes a missing section.

### 0.5 Profile, level and levers
- **Output profile** by the declared or likely use: `profiles.md`. The user dictated a structure → `custom` with theirs. None fits → `report` with sections derived from the sub-questions.
- **Level:**

| Level | When | Approximate cost |
|---|---|---|
| `light` | bounded question, facts to confirm, brief, short fact-check, overview with 2 to 5 sub-questions | 15 to 30 searches and reads, no or 1 to 2 helpers |
| `standard` | report, dossier, concept explainer, comparison, cross-check | 3 to 5 parallel researchers, 1 critic, 1 checker |
| `deep` | scientific-paper profiles, systematic review, contested topic, anything that will be published or decide money or health | 5 to 8 researchers, 3 critics, checker on everything |

  The user's level wins. When the question is contested or will be published, `standard` is the floor.
- **Register**, from the verb: `teach` ("explain", "how does it work"), `map` ("overview", "what are the"; no verdict), `analyze` (default: evaluate, compare, decide), `argue` ("make the case"). Leave `analyze` only on a strong signal. The citation check never changes with the register.
- **Inference depth:** `surface` (textbook consensus suffices), `standard`, `deep` (the answer lives in grey literature, hard primary sources, inference over absences). Provisional: step 4 may raise it.
- **Domain notes:** two or three sentences on where strong evidence lives for this topic, what counts as proof here, and the time window that matters. Every researcher gets them.
- **Output language and variant:** the user's language unless they ask otherwise (Portuguese; English US or UK). Search runs in several languages regardless.

### 0.6 Write `decomposition.json`
```json
{
  "neutral_question": "...",
  "profile": "paper-natural-sciences",
  "level": "deep",
  "register": "analyze",
  "inference_depth": "standard",
  "domain_notes": "...",
  "output_language": "en-GB",
  "sub_questions": ["S1 ...", "S2 ..."],
  "entities": [{"id": "E1", "name": "...", "fields": ["..."]}],
  "pinned_periods": [{"period": "1819", "primary_source": "1st edition of ..."}],
  "scope": ["..."],
  "out_of_scope": ["..."],
  "required_sections": ["## ...", "## ..."],
  "words": [3000, 6000],
  "search_languages": ["en", "pt", "ja", "de"],
  "destination": "research/<tag>/<Short title>.md",
  "formulas_expected": true
}
```
`required_sections` is never empty: it comes from the profile, the question's own enumeration, or the sub-questions. The gate checks it.

## Step 1 · What you already know

Before the web, look at what is already on hand; it is local and cheap.
1. The user's own material: notes folder, library, documents they attached, earlier runs in `research/` on the same topic (reuse their `sources/`; do not fetch twice).
2. Write `temp/prior.md`: what the existing material already states (and how reliable it is), what it does **not** cover, and which primary sources it cites (they become seeds for the sweep).
3. If the user's own published work exists on the topic, it is input, and a contradiction with it is reported, not silently resolved.

**Prior notes guide; they do not replace a source.** A personal or secondary note is not cited in the final text as evidence: climb to the primary source it cites.
