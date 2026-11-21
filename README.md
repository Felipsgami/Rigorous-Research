# rigorous-research

**PT-BR** · [English below](#english)

Uma skill de pesquisa profunda com rigor de artigo científico e saída moldada ao uso. Funciona em **português** e em **inglês (americano e britânico)**, no Claude, no Codex e, pelo `PROMPT.md`, em qualquer assistente que busque na web (ChatGPT, Gemini, DeepSeek, Kimi, Qwen, Mistral).

Duas coisas estragam pesquisa feita com IA mais do que qualquer outra: **a pergunta já contém a resposta** (o modelo defende com competência uma premissa falsa) e **a citação é enfeite** (a fonte existe, mas não diz o que a frase afirma). Esta skill foi construída contra as duas.

## O que ela faz

1. **Enquadra a pergunta:** neutraliza a premissa embutida, decompõe em itens, confere numa matriz de cobertura se nada foi estreitado, escolhe perfil de saída, nível e idioma.
2. **Busca em cinco lentes:** largura, fonte canônica, contrária, documento primário do período exato, e perspectiva em vários idiomas (literatura regional, teses e dissertações, não só os periódicos mais citados).
3. **Registra cada fonte como nota** com localização exata e **estatuto** de cada afirmação (dado, definição, modelo, analogia, hipótese).
4. **Mapeia disputas e conta vozes independentes:** cinco reprints de um release valem uma voz.
5. **Pergunta o que derrubaria a direção atual** e faz uma rodada única de busca para isso.
6. **Redige uma vez**, com cada afirmação ligada à sua nota, e depois **só remenda**.
7. **Ataca o próprio texto** com críticos (dialético, profundidade, instrução, estatuto e números) e um **leitor frio** que só tem o texto.
8. **Confere cada citação:** a fonte diz isto, como está escrito?
9. **Valida fórmulas e números:** LaTeX transcrito da fonte, conferido no desenho; armadilhas de denominador, período, unidade, média de médias.
10. **Exporta** em Markdown, Word (equação nativa e editável, tabela de verdade) e PDF, contando as equações e conferindo as páginas.

Também faz **contraprova** de pesquisa feita por outra IA: refaz às cegas as afirmações de risco, compara uma a uma e registra os padrões de erro para melhorar o próximo pedido àquela ferramenta.

## Perfis de saída

Relatório · resposta direta · checagem de fatos · comparativo · linha do tempo · guia prático · dossiê · explicação de conceito · revisão de literatura · revisão sistemática (no espírito do PRISMA) · contraprova · estrutura personalizada · e **artigo científico na forma de cada área**: IMRaD (ciências naturais, da vida e sociais), *Nature* (conferido no guia oficial), física, matemática (definição, teorema, prova), engenharia e computação (estilo IEEE/ACM) e humanidades (seções argumentativas, fonte primária, ABNT/Chicago/MLA). O guia do periódico-alvo sempre manda.

## Instalação

**Claude Code** (e agentes que leem o padrão `SKILL.md`): copie a pasta `rigorous-research` para `~/.claude/skills/` ou para `.claude/skills/` dentro de um projeto. Peça "pesquisa profunda sobre…", "faz uma revisão de literatura sobre…", "checa estes fatos".

**Claude.ai (app e web):** compacte a pasta em `.zip` e envie em *Configurações › Capacidades › Skills*.

**ChatGPT, Gemini, DeepSeek, Kimi e outros:** cole [`PROMPT.md`](PROMPT.md) nas instruções do assistente. Onde houver Python, envie também a pasta `scripts/`.

Combina com a skill irmã [`humanize-text`](../humanize-text), que tem as regras completas de voz em português e inglês.

## O motor (`scripts/research.py`)

Python 3.9+. `pip install requests python-docx lxml` (e, opcionais, `matplotlib pdfplumber pypdfium2`). Para exportar com o vocabulário completo de LaTeX, instale o [pandoc](https://pandoc.org).

```bash
python scripts/research.py init "tema" --profile report --level standard
python scripts/research.py scholar "predictive coding music" --order citations --since 2005
python scripts/research.py doi relatorio.md                # retratado? acesso aberto?
python scripts/research.py independence research/<tag>/sources
python scripts/research.py cites research/<tag>/draft.md research/<tag>/sources
python scripts/research.py number research/<tag>/draft.md research/<tag>/sources --out research/<tag>/report.md
python scripts/research.py formulas report.md --png figuras/
python scripts/research.py gate <tag>
python scripts/research.py export report.md --formats md,docx,pdf --png paginas/
python scripts/research.py resume                         # retomar a última pesquisa
```

A busca acadêmica usa o **OpenAlex** sem chave (com recuo para o Crossref). Sem chave, o OpenAlex divide um orçamento diário pequeno por IP; uma chave gratuita em `OPENALEX_API_KEY` aumenta o teto.

## Arquivos

```
rigorous-research/
├── SKILL.md                     instruções e tabela de passos
├── PROMPT.md                    o método inteiro num arquivo, para qualquer IA
├── references/
│   ├── frame.md                 passos 0-1: pergunta, decomposição, perfil, nível
│   ├── sweep.md                 passos 2-3: plano em cinco lentes, varredura
│   ├── researcher.md            instruções do pesquisador e formato da nota de fonte
│   ├── map-and-critic.md        passos 4-5: independência, disputas, crítico de corpus
│   ├── drafting.md              passo 6: redação
│   ├── critics-and-patch.md     passos 7-9: críticos, remendo, checagem de citação
│   ├── formulas-and-numbers.md  passo 10
│   ├── gate-and-delivery.md     passos 11-12: portão, entrega, exportação
│   ├── profiles.md              todos os perfis de saída, incluindo artigo por área
│   └── status-check.md          o gate de estatuto (verdade)
└── scripts/
    ├── research.py              o motor
    ├── latex_omml.py            LaTeX → equação nativa do Word
    └── md_docx.py               Markdown → Word sem pandoc
```

## Limites

- A skill organiza e confere; ela não substitui ler a fonte primária quando a decisão é sua.
- O perfil *Science* está marcado "a verificar": as instruções da revista barraram a leitura automática quando ele foi escrito.
- O conversor próprio de LaTeX para Word cobre o subconjunto comum em relatórios; para LaTeX completo, use pandoc.

Licença: [MIT](LICENSE).

---

<a name="english"></a>
## English

A deep research skill with the rigour of a scientific paper and an output shaped to its use. It works in **Portuguese** and **English (US and UK)**, in Claude, in Codex and, through `PROMPT.md`, in any assistant that can search the web (ChatGPT, Gemini, DeepSeek, Kimi, Qwen, Mistral).

Two things spoil AI research more than anything else: **the question already contains the answer** (the model competently defends a false premise) and **citations are decoration** (the source exists but does not say what the sentence claims). This skill is built against both.

### What it does
1. **Frames the question:** neutralises the built-in premise, decomposes it into items, checks a coverage matrix for narrowing, picks the output profile, level and language.
2. **Searches in five lenses:** breadth, canonical source, adversarial, the primary document of the exact period, and perspective across languages (regional literature, theses and dissertations, not only the most-cited journals).
3. **Records every source as a note** with exact location and the **status** of each claim (data, definition, model, analogy, hypothesis).
4. **Maps disputes and counts independent voices:** five reprints of one press release are one voice.
5. **Asks what would overturn the current direction** and runs one search round for it.
6. **Drafts once**, every claim tied to its note, then **only patches**.
7. **Attacks its own text** with critics (dialectic, depth, instruction, status and numbers) and a **cold reader** who has only the text.
8. **Checks every citation:** does the source say this, as written?
9. **Validates formulas and numbers:** LaTeX transcribed from the source and checked visually; traps of denominator, period, units, averages of averages.
10. **Exports** to Markdown, Word (native, editable equations; real tables) and PDF, counting equations and checking pages.

It also **cross-checks research made by another AI**: it re-researches the risky claims blind, compares them one by one and logs the error patterns to improve the next brief to that tool.

### Output profiles
Report · brief · fact-check · comparison · timeline · how-to guide · dossier · concept explainer · literature review · systematic review (PRISMA-style) · cross-check · custom structure · and a **scientific paper in each field's own form**: IMRaD (natural, life and social sciences), *Nature* (checked against the official guide), physics, mathematics (definition, theorem, proof), engineering and computing (IEEE/ACM style) and humanities (argument-driven sections, primary sources, Chicago/MLA/ABNT). The target journal's guidelines always win.

### Install
**Claude Code** (and agents that read the `SKILL.md` standard): copy the `rigorous-research` folder to `~/.claude/skills/` or to `.claude/skills/` inside a project. Ask for "deep research on…", "a literature review of…", "fact-check these claims".

**Claude.ai (app and web):** zip the folder and upload it under *Settings › Capabilities › Skills*.

**ChatGPT, Gemini, DeepSeek, Kimi and others:** paste [`PROMPT.md`](PROMPT.md) into the assistant's instructions. Where Python is available, upload the `scripts/` folder too.

Pairs with the sibling skill [`humanize-text`](../humanize-text), which holds the full voice rules for Portuguese and English.

### The engine
Python 3.9+. `pip install requests python-docx lxml` (optional: `matplotlib pdfplumber pypdfium2`). For the full LaTeX vocabulary on export, install [pandoc](https://pandoc.org). Commands as listed above. Scholarly search uses **OpenAlex** with no key (Crossref fallback); without a key OpenAlex shares a small daily budget per IP, and a free key in `OPENALEX_API_KEY` raises it.

### Limits
- The skill organises and checks; it does not replace reading the primary source when the decision is yours.
- The *Science* profile is marked "to verify": the journal's instructions blocked automated reading when it was written.
- The built-in LaTeX-to-Word converter covers the subset common in reports; for full LaTeX, use pandoc.

License: [MIT](LICENSE).
