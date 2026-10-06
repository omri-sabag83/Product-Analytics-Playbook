# Product Analytics Playbook

A module-by-module reference for the standard product-analytics topics, from
how events are logged to how a metric movement is diagnosed. Ten numbered
notebooks. Topics already covered in depth elsewhere get short **recap**
modules that point to the full treatment; topics not covered elsewhere get
**full** modules.

The program, progress table and per-module detail are in
[CURRICULUM.md](CURRICULUM.md).

| # | Notebook | Topic | Depth |
|---|----------|-------|-------|
| 1 | `01_instrumentation_semantic_layer.ipynb` | Event-log audit, tracking plan, semantic layer | Full |
| 2 | `02_metrics_frameworks.ipynb` | Metrics frameworks: North Star, HEART, AARRR, OKRs | Full |
| 3 | `03_funnel_analysis.ipynb` | Funnel analysis | Recap |
| 4 | `04_activation.ipynb` | Activation | Recap |
| 5 | `05_retention_cohorts.ipynb` | Retention & cohorts | Recap |
| 6 | `06_engagement_dau_mau.ipynb` | Engagement: DAU/MAU stickiness | Recap |
| 7 | — | Feature adoption | Recap |
| 8 | — | Monetization metrics | Full |
| 9 | — | Segmentation: rule-based, RFM, clustering | Full |
| 10 | — | Metric-movement diagnosis | Full |

Related repos: [A/B Testing Playbook](https://github.com/omri-sabag83/A-B-Testing-Playbook),
[Product Analytics Case Study](https://github.com/omri-sabag83/Product-Analytics-Case-Study),
[Scikit-Learn Playbook](https://github.com/omri-sabag83/Scikit-Learn-Playbook).

## Dataset

"eCommerce Events History in Cosmetics Shop" by Michael Kechinov (REES46
Marketing Platform), published on
[Kaggle](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop):
20.7 million events from a mid-size online cosmetics store, October 2019 to
February 2020.

Its licence is "Data files © Original Authors", which does not allow
redistribution, so **the data is not in this repo** and the notebooks show
aggregates only.

## Reproduce

```bash
conda activate base                 # tested env: Python 3.13.5, versions in requirements.txt
# 1. download the five monthly CSVs from the Kaggle page above (free account) into data/raw/
python data/get_data.py             # checks SHA-256 checksums, writes a fixed 10% user sample
                                    # and data/processed/playbook.sqlite for the queries in SQL/
jupyter nbconvert --to notebook --execute --inplace 0*.ipynb
```

The sample is chosen by a fixed hash of `user_id`, so it is identical on every
machine. `common.py` loads it into SQLite and builds the semantic layer
(`semantic_layer/`: tracking plan, SQL views, metric definitions) that every
notebook computes through.

## Process

A self-directed learning program: I set the objectives, scope and review
standard; an AI assistant served as curriculum designer and pair-programmer,
building each module for my review. Claims that an earlier repo already covers a topic
were checked against that repo's notebooks, not its README. Every module went
through a structured rigor checklist, and each full module's headline result
was checked by an independent verifier that saw only the claim and the data.
