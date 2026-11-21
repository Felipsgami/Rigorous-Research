# Step 10 · Formulas and numbers

Formulas and numbers are where AI research errs most and where errors cost most: one model invents a formula, another breaks its notation, and the conversion to Word silently drops it. This step closes all three doors.

## Formulas

### Where they come from
1. **Only formulas transcribed in a source note**, with location (author, year, equation number, page). No formula "from memory".
2. **Symbol-by-symbol transcription**, in the source's notation. If you change the notation (for clarity, or to unify two sources), say so in the text: "in X's notation, setting *K* = 1 and using base 2".
3. **Every display formula** is followed by "where" defining each symbol, and by its location. Applying a formula to a case the source does not treat is declared "our model" (level 4).
4. **Never fabricate a formalisation.** Stating that the literature offers no formal model is stronger than inventing one.
5. Transcribed from a PDF image (`transcribed from: image` in the note): check it against the image again, symbol by symbol.

### How to write them (the subset that converts to Word without loss)
- `$...$` inline, `$$...$$` for display, **one equation per block** (no `align`, `cases`, `matrix` unless you export with pandoc).
- Commands, never Unicode characters: `\leq` not ≤, `\times` not ×, `\alpha` not α, `x_i` not xᵢ, `\log_2` not log₂. A formula typed in Unicode inside running text never becomes an equation and nobody checks it: the validator flags it.
- Multi-letter names in `\mathrm{KL}`; words in `\text{...}`.
- Supported by the built-in Word converter: `_{}` `^{}`, `\frac`, `\sqrt`, `\sum` `\prod` `\int` with limits, `\log` `\ln` `\exp` `\sin` `\cos` `\max` `\min` `\lim`, `\cdot` `\times` `\leq` `\geq` `\neq` `\approx` `\infty` `\to` `\partial` `\pm` `\propto` `\sim` `\in`, `\|` `\mid`, `\left` `\right`, Greek letters, `\,` `\;` `\quad`. With pandoc installed, the full LaTeX math vocabulary works.
- A currency sign next to a number is read as a formula: write "US$ 10" with a space, or "10 dollars".

### Check (mandatory)
1. `python scripts/research.py formulas draft.md --png research/<tag>/temp/formulas`: zero ERROR; warnings fixed or justified.
2. **Open every PNG** and compare it with the note's transcription and, when in doubt, with the source: sign, subscript, logarithm base, summation limits, what is in the numerator.
3. The final check in Word and PDF belongs to `export` (step 12).

## Numbers

### Every number carries five things
value · unit · scope or population · period or date · source with location. Missing one, it is not ready for the text.

### Traps
- **Shifting denominator:** a percentage of what? "36% of replications" of 97 studies whose original result was significant, not of 100.
- **Average of averages**, percentages of percentages: recompute from the totals.
- **Simpson's paradox:** the aggregate trend can reverse inside the groups.
- **Cherry-picked window:** does the same data tell a different story in another window? State the window and why it is right.
- **Unfair comparison:** different periods, populations or measurement methods are not compared without saying so.
- **Mixed units and scales:** million vs billion (and the old British billion), power dB vs amplitude dB, exchange rate of which date.
- **Manufacturer, press-release or self-promotional figures** are marked as such.
- **Median vs mean** in skewed distributions (income, views, citations): say which.
- **Correlation described as cause:** the verb must match the study design (observational does not "cause").
- **Silent rounding:** "about 40%" where the source says 36% is an error, not style.
- **Subsample as the whole:** a number from one study or arm ("Study 1b") presented as the paper's overall result.
- **Superseded by a correction:** the paper received a corrigendum and the values changed (`research.py doi` shows it).
- **Wrong edition:** the figure comes from another edition of the report or book.
- **False precision:** 36.17% of a sample of 97 is noise; use the precision the sample supports.
- **Locale formats:** 1.234,5 (Portuguese) and 1,234.5 (English) are the same number; write it in the output language's convention and never mix.

### Change over time
When the text explains why a number changed, decompose the change into its components (volume, price, mix, or whatever the domain's drivers are) and show the bridge in a table, from the start value to the end value, with the parts summing exactly. A component that does not close the sum means missing data.

### Arithmetic runs in code, never in your head
Every derived number (sum, ratio, conversion, percentage change, weighted mean) is computed with a one-line script, and the command goes to `temp/calculations.md` next to the result, so anyone can redo it.

### Data from a dataset
If the research uses a table or dataset (CSV, spreadsheet, official statistics), profile it in `temp/data-profile.md` before quoting any number: rows, columns, period covered, missing-value rate per column (warn above 5%, alert above 20%), impossible values, duplicates, and the official definition of every metric used.
