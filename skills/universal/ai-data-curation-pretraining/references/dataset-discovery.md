# Dataset Discovery

Where to find existing high-quality datasets before building your own. The rest of this skill covers building a corpus from raw crawl; this reference covers the cheaper first question — does a usable dataset already exist? Repository list adapted from Chip Huyen, *AI Engineering* (O'Reilly, 2025), ch. on dataset engineering, extended with pretraining-specific sources.

## Search order

1. **Check the open-recipe corpora first** (pretraining): FineWeb / FineWeb-2, Dolma, DCLM-Baseline, Common Pile, Common Corpus, RedPajama, SlimPajama — see the Frontier Recipes table in SKILL.md. For most pretraining tasks the answer is "start from one of these and re-filter," not "crawl from scratch."
2. **Search the general repositories** (below) for task/domain data.
3. **Only then build** — and run the licensing and contamination gates before mixing anything in.

## General repositories

| Source | Scale (order of magnitude; check the site for counts) | Best for |
| --- | --- | --- |
| [Hugging Face Datasets](https://huggingface.co/datasets) | Hundreds of thousands of datasets | Default first stop for ML; filter by task, language, license, size |
| [Kaggle Datasets](https://www.kaggle.com/datasets) | Hundreds of thousands | Tabular, competition-grade, documented data |
| [Google Dataset Search](https://datasetsearch.research.google.com/) | Meta-search across the open web | Finding datasets that live outside the ML ecosystem — underrated |
| [Data.gov](https://data.gov) / [data.gov.in](https://data.gov.in) | Hundreds of thousands / tens of thousands | Government open data (US / India); other governments run equivalents |
| [ICPSR](https://www.icpsr.umich.edu/) (U. Michigan ISR) | Tens of thousands of social studies | Social-science and survey data |
| [UCI ML Repository](https://archive.ics.uci.edu/) / [OpenML](https://www.openml.org/) | Several thousand each | Classic ML benchmarks; older but well-documented |
| [Open Data Network](https://www.opendatanetwork.com/) | Tens of thousands | Cross-portal search over civic/government open data |
| [AWS Open Data](https://registry.opendata.aws/) | Curated collection | Large cloud-hosted datasets (genomics, satellite, CommonCrawl itself) |
| Framework built-ins (e.g. TensorFlow Datasets, torchvision) | Small pre-built sets | Quick prototyping and pipeline smoke tests |
| [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) (EleutherAI) | 400+ benchmark datasets, avg 2,000+ examples each (book's figure) | Eval sets large enough to double as PEFT fine-tuning data — but see the contamination warning below |
| [SNAP — Stanford Large Network Dataset Collection](https://snap.stanford.edu/data/) | Graph datasets | Network/graph learning |

## Gates before you use what you found

- **License** — repository presence is not a license. Check the dataset card's license field and the upstream source's terms; for anything feeding a released model, prefer explicitly open licenses (see Known Traps #5 and the EU AI Act transparency trap #7 — log the source category either way).
- **Contamination cuts both ways** — fine-tuning on benchmark datasets (the lm-evaluation-harness shortcut above) permanently disqualifies those benchmarks for evaluating that model. Record which eval sets entered training and exclude them from reporting.
- **Provenance and freshness** — a popular HF dataset may be a years-old scrape or an undocumented filter of another dataset. Read the dataset card and datasheet; if there is neither, treat quality claims as unverified.
- **Pulling a dataset is not curation** — the anti-pattern in SKILL.md applies: document your filtering decisions and write a datasheet even when you started from someone else's data.

## Fine-tuning-specific discovery

For instruction/preference data specifically: filter HF Datasets by task (`text-generation`, `question-answering`) and by license; check the dataset card's construction method (human-written vs distilled from a commercial model, which triggers the distillation-licensing trap). When no dataset fits, the synthetic-data reference covers verifier-gated generation and rule-based structured records. Faker/Chance outputs are synthetic stand-ins, not proof that source PII was removed.
