# DSAI5102 Group 16 — submission package

Reducing Development Indicators While Preserving Country Rankings and Income Classification.

This folder is self-contained: the data, the code, the results, the report and the slides are all here, and
the analysis can be re-run offline without downloading anything.

| Folder | Contents |
|:--|:--|
| `report/` | `DSAI5102_Group16_Report.pdf` (17 pages) — the Markdown source stays in the main repository, so `report/` here holds the PDF only |
| `archive/` | the earlier PowerPoint deck (v1, pptx + pdf) and the retired report builders |
| `slides/` | `DSAI5102_Group16_slides.pdf` (9 slides, 16:9) — the deck is made in Canva, so the PDF is the deliverable |
| `scripts/` | ten scripts: extraction, analysis, figures, tables, split-seed check, report builders |
| `data/` | frozen WDI extracts (`raw/`, `processed/`) and `PROVENANCE.md` |
| `results/` | `analysis.json` — every number quoted in the report — plus figures, tables and intermediate CSVs |
| `expected/` | the reference copy of `analysis.json` and of the split-seed check, used by `reproduce.py` |

## Reproduce everything

```bash
python -m venv .venv && . .venv/bin/activate     # Python 3.10 or newer
pip install -r requirements.txt

python reproduce.py          # analysis + numeric check against expected/   (about 2 min)
python reproduce.py --full   # also figures, tables and the ten split seeds (about 4 min)
```

`reproduce.py` re-runs `scripts/analyse.py` and compares every scalar in the new `results/analysis.json`
with `expected/analysis_reference.json` at 1e-9 relative tolerance (the zip checksum and any runtime field
are ignored). It prints `CHECK PASSED` when the numbers match. Nothing is downloaded: `data/` holds the
frozen World Bank extract, and `results/official_panel.csv` + `results/country_metadata.csv` are the
analysis inputs.

Single-threaded, no GPU, no network. About 100 s for the analysis, 50 s for the split-seed check.

## What each script does

| Script | Output |
|:--|:--|
| `scripts/extract_official.py` | builds `results/official_panel.csv` from the World Bank WDI archive (already done; needs the zip, so this step is optional) |
| `scripts/analyse.py` | `results/analysis.json` and the intermediate CSVs: coverage, PCA, sparse path, classification, clustering, windows |
| `scripts/make_figures.py` | Figures 3, 4, 6 (structure, selection, groups) |
| `scripts/add_figures.py` | Figures 1, 2, 5, 7 (missingness, workflow, confusion, rank changes) |
| `scripts/export_tables.py` | the tables used in the report |
| `scripts/repeat_splits.py` | `results/repeat_splits.csv` — the ten split seeds quoted in Section 5 |
| `scripts/schema.py` | the 28-indicator schema, paths and plotting style, imported by everything else |

## Documents

`report/DSAI5102_Group16_Report.pdf` is the submitted report. Its Markdown source and the script that
typesets it (`build_report_html.py`) live in the main repository,
https://github.com/PKLgames/dsai5102miniproject_2, where the text and its PDF are rebuilt together; this
package carries the PDF only. The deck is designed in Canva and exported to PDF, so it has no PowerPoint source
either.

## Data

World Bank World Development Indicators, CC BY 4.0, retrieved through the official API on
19 November 2026. 28 series × 198 economies × 2005–2022. `data/PROVENANCE.md` records the retrieval, and
`results/analysis.json` stores the SHA-256 of the source archive that was used.

## Note on the code history

The analysis was developed iteratively; this package contains the final version of every script and the
results it produced. Numbers in the report come from `results/analysis.json`, never from a hard-coded
constant in the text.
