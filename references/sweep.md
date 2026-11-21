# Steps 2 and 3 · Search plan and sweep

## Step 2 · A search plan in five lenses

Improvised searching finds forty sources on the same three sub-topics. A plan spreads the search over every item of the decomposition and over angles a single searcher misses. For **each atomic item**, plan searches in five lenses:

| Lens | What it looks for | Examples |
|---|---|---|
| **1 · Breadth** | the item's factual content, the current state (last two or three years), every entity and sub-concept | `"mono no aware" Motoori Norinaga`; `predictive coding music 2024` |
| **2 · Depth and citation chain** | the canonical source, the founding paper, the reference edition, the original that commentary derives from | `research.py scholar "..." --order citations`; "original study", critical edition |
| **3 · Adversarial** | criticism, limitations, negative results, failed replications, rival schools, who says it is wrong | `"criticism of" X`; `replication failure` X |
| **4 · Pinned primary** | for each pinned period: the document of that exact period (edition, report, filing, score, original interview), not commentary on it | `Die Welt als Wille und Vorstellung 1819 Erstausgabe` |
| **5 · Perspectival and multilingual** | the topic's culture of origin first, then the same cultural block, then a counterpoint from outside it; terms in the original language | `もののあはれ 本居宣長`; `Sehnsucht Romantik Begriffsgeschichte` |

**Search for the name you do not know yet.** When the topic is a phenomenon (not a work or a person), one search describes the phenomenon **without naming it** and asks which technical terms exist for it across fields (philosophy of science, rhetoric, corpus linguistics, psychology, education, bibliometrics, science communication) and languages (English, German, French, Spanish, Portuguese at least). If the phenomenon already has a name, using it is mandatory; coining a term for something already named is an error. The same search separates work **about** the object from **adjacent** work.

**Minimums:** lens 3 has at least one search per central thesis (at `deep`, at least eight in total); lens 5 runs in at least three languages unless the topic is local; lens 4 is mandatory for every pinned period. Write `temp/plan.md`:

```markdown
| Item | Query | Tool | Lens | Language | Researcher |
|---|---|---|---|---|---|
| S1 | "Hansen Pearce 2014 information content" | scholar | 2 | en | R1 |
```

**Check the plan against the coverage matrix:** every row of `temp/coverage.md` has at least one query? Any topic, entity or region of the question with zero rows? Add it now.

### A literature search is a reconstruction of conversations
Good bibliographic research follows the dialogue, not just the famous names:
- start from **regional and national literature in the topic's own language** (SciELO for Latin America and Iberia, CiNii and J-STAGE for Japan, CNKI for China, KCI for Korea, national repositories), not only from the big journals of the Global North;
- **theses and dissertations** hold much of the detailed work on a topic and save you from redoing what was done (national catalogues, ProQuest Dissertations, DART-Europe, university repositories);
- relevant articles lead to **relevant journals** (read their recent issues) and to **researchers** (follow their profiles: ORCID, Google Scholar, national CV platforms such as Lattes in Brazil).

### Where evidence lives, by field
Always the most primary that exists. **Local before remote:** the script before a web search, a web search before reading a dozen pages.

| Field | First | Then |
|---|---|---|
| science in general | `research.py scholar` (OpenAlex, Crossref fallback; no key) | web search and fetch; arXiv through OpenAlex |
| life sciences, medicine, psychology | PubMed (and PubMed Central full text), bioRxiv/medRxiv (preprint: mark as not peer-reviewed), Consensus or Semantic Scholar if your environment has them | `research.py doi` for retractions and open access |
| philosophy | Stanford Encyclopedia of Philosophy, Internet Encyclopedia of Philosophy, PhilPapers, critical editions online | `scholar --type book` |
| religion and classical texts | SuttaCentral, CBETA, GRETIL, Perseus, the critical edition | peer-reviewed secondary literature |
| history | digitised primary sources (national libraries, newspaper archives, Gallica, Internet Archive) | peer-reviewed historiography |
| mathematics, physics, CS | arXiv, zbMATH, MathSciNet, the conference proceedings (ACM, IEEE) | textbooks for notation only |
| engineering and technology | standards bodies, IEEE Xplore, manufacturer datasheets (marked as manufacturer claims), patents | trade press quoting the document |
| music | IMSLP (scores), RILM through OpenAlex, liner notes as the source of the recording | |
| culture, games, film, anime | interviews with the author in the original language, official art books and booklets | fan wikis only as a map, checked against the work |
| data, markets, platforms | the agency or company document, with date and period | quality press quoting the document |

**Encyclopedias (Wikipedia included)** are reliable for identification and public facts. For a weighty scientific or philosophical claim, use the entry as a **map** and climb to the source it cites.

**Paywalled papers:** before relying on an abstract, look for a legal open copy (`research.py doi` returns the open-access link; PubMed Central; the author's repository; the preprint); then the user's institutional access (university library, national consortia such as Brazil's CAPES Periódicos via CAFe), with the user signing in themselves; then ask the user or the author for the PDF. Shadow libraries are not used: they distribute without a licence, and this method lives on clean provenance. A claim supported only by the abstract is marked `access: abstract` in the note and never supports a number the abstract does not state.

**Blocked sites** (login, bot check, 403): never bypass them. Note the URL in the gaps note and move on; at the end, one consolidated list goes to the user.

## Step 3 · Sweep

### Level `light`
You research alone, following `researcher.md` as if you were the researcher, and write the notes to `sources/`.

### Levels `standard` and `deep`
Split the plan into **non-overlapping fronts** (by sub-question, lens or tradition; never two fronts with the same query). If your environment supports parallel sub-agents, launch **all researchers at once**; if not, run the fronts yourself one after another, writing each front's notes before starting the next. Use a capable but economical model for researchers. Give each a **numbering range** so files never collide: R1 `s01`-`s19`, R2 `s20`-`s39`, R3 `s40`-`s59`, and so on.

**Brief (every field, in this order):**
```
QUESTION (verbatim, it is law):
> <paste query.md in full>

POSITION: you are researcher R<n> in step 3 of a rigorous research run.
Others cover neighbouring fronts in parallel; stay on yours. Afterwards the coordinator
measures coverage and independence, maps disputes and drafts ONLY from your notes.

YOUR FRONT: <short name>
GOAL: <what the front must deliver>
NEUTRAL QUESTIONS (none builds in the answer):
- <...>
PLANNED QUERIES: <rows of plan.md for this front>
PRIORITY SOURCES: <from the field table>
LANGUAGES: <...> · PINNED PERIODS: <...> · SCOPE / OUT OF SCOPE: <...>
DOMAIN NOTES: <...> · FORMULAS EXPECTED: <yes/no>

WRITE notes to: <absolute path>/sources/ , ids s<start> to s<end>.
BUDGET: 12 to 20 search and read calls (deep: up to 30).

FIRST STEP: read references/researcher.md in full and follow its source-note format exactly.
```

**One repair round:** a researcher that returns no notes, or notes in the wrong format, gets one replacement for the same front. Save results to disk before moving on.

**Check the disk, not the report:** count the files per range. A report that says "wrote 12 notes" without 12 files is a false report.
