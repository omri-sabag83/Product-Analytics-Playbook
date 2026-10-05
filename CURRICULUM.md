# Product Analytics Playbook — Learning Program

**Goal:** one consolidated reference for the standard product-analytics topic
landscape, from how events are logged to how a metric drop is diagnosed. A
reader can go through it start to finish.

**Starting point:** a Product Analyst background (B2C marketplace, B2B
security). Several topics here were already worked through in two earlier
public repos, the
[A/B Testing Playbook](https://github.com/omri-sabag83/A-B-Testing-Playbook)
and the
[Product Analytics Case Study](https://github.com/omri-sabag83/Product-Analytics-Case-Study).
Those topics get **recap modules**: short, with a pointer to where the full
treatment lives. Topics no earlier repo covers get **full modules**.

**Scope boundary:** experimentation (A/B tests) is covered in the A/B Testing
Playbook and is not repeated here. Predictive modelling is covered in the
[Scikit-Learn Playbook](https://github.com/omri-sabag83/Scikit-Learn-Playbook);
only k-means clustering (Module 9) is new.

---

## Progress

`🟩🟩⬜⬜⬜⬜⬜⬜⬜⬜` **20% complete (2/10 modules)**

⬜ Not started · 🟨 In progress · 🟩 Completed

| # | Module | Depth | Status | Completed On |
|---|--------|-------|--------|---------------|
| 1 | Event Instrumentation & the Semantic Layer | Full | 🟩 Completed | 2026-10-04 |
| 2 | Metrics Frameworks: North Star, HEART, AARRR, OKRs | Full | 🟩 Completed | 2026-10-05 |
| 3 | Funnel Analysis | Recap | ⬜ Not started | |
| 4 | Activation: Definition & Measurement | Recap | ⬜ Not started | |
| 5 | Retention & Cohorts | Recap | ⬜ Not started | |
| 6 | Engagement: DAU/MAU Stickiness | Recap | ⬜ Not started | |
| 7 | Feature Adoption | Recap | ⬜ Not started | |
| 8 | Monetization Metrics | Full | ⬜ Not started | |
| 9 | Segmentation: The Methodology Landscape | Full | ⬜ Not started | |
| 10 | Metric-Movement Diagnosis | Full | ⬜ Not started | |

---

## How this program works

**Two module depths.**
- **Full module:** Concepts, Why it matters, Worked example(s), Resources,
  Exercise type, Interview angle. These cover ground no earlier repo covers.
- **Recap module:** a short concept summary, the earlier repo's *printed*
  numbers with a link to the exact notebook and section, one compact
  recomputation on this playbook's dataset, and key takeaways. Recaps are
  deliberately shorter. The full treatment lives at the link.

**Order.** Module 1 comes first because every later module computes its
metrics through Module 1's semantic layer: one written definition per metric,
reused everywhere. Module 10 comes last because diagnosing a metric movement
uses everything before it.

**Running dataset.** "eCommerce Events History in Cosmetics Shop" (Michael
Kechinov, REES46 Marketing Platform, on
[Kaggle](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop)).
It holds 20.7 million real events (view, cart, remove_from_cart, purchase) from
a mid-size online cosmetics store, October 2019 to February 2020, with user,
session, product, brand and price. The licence is "Data files © Original
Authors", which is not an open licence, so the data is **not** in this repo.
`data/get_data.py` verifies the files a reader downloads and builds a fixed 10%
sample of users (2,026,833 events, 164,270 users). The notebooks show
aggregates only.

**Standards applied in every notebook:**
- Findings are tagged **Observation** (what the data shows), **Hypothesis** (a
  proposed explanation, not yet tested) or **Conclusion** (what the evidence
  supports).
- Correlation vs. causation is stated explicitly.
- Data-quality issues come first, not last.
- Every printed number gets a plain-English sentence.
- Every chosen number (a threshold, a window) is labelled as chosen, with the
  reason.
- Simulated data is used only where a known ground truth is the point, and is
  always labelled as simulated.

---

## <u>Module 1 — Event Instrumentation & the Semantic Layer</u>

**Concepts**
- Events, properties and entities: what a product event log actually records,
  and what it doesn't (here: no order id, no quantity, no signup event)
- The tracking plan: one written set of rules per event (name, required
  properties, types, allowed values), naming conventions (Object + Action), and
  validating real events against it with JSON Schema (a standard format for
  data rules that a program can check)
- Instrumentation failure modes: duplicate firing, missing properties,
  impossible values, events whose meaning is unclear
- The semantic layer: metric definitions written once (entity, filter,
  aggregation, time grain) and reused, so "revenue" or "active user" means the
  same thing in every chart. Time grain = the period a metric is counted over
  (day, month)
- Why definitions change answers: the same question computed under two
  reasonable definitions

**Why it matters**
Every metric in Modules 2–10 is only as good as the events beneath it and the
definition on top. Two dashboards that disagree can be showing two definitions,
not two realities. Defining the semantic layer for product event data is core
analyst work: it decides what every downstream number means.

**Worked example**
An audit of the raw log, with every issue counted:
- About 5% of rows are extra copies of another row, concentrated in
  `remove_from_cart` (24.82% of those events in the sample) and `cart` (1.96%), against 0.06% for
  purchases.
- `category_code` is about 98% empty and `brand` about 42% empty.
- There is no order id. An order is reconstructed as all purchase lines sharing
  a user, session and timestamp.

Then a tracking plan for the four events, the raw events validated against it,
and a semantic layer (metric definitions plus SQLite views) built on the
cleaned events. Finally, "how many orders / how much cart activity?" answered
under raw vs. defined counting, showing the gap in numbers.

**Resources**
- [Data Collection Best Practices](https://www.twilio.com/docs/segment/protocols/tracking-plan/best-practices)
  (Twilio Segment docs, ~15 min, verified): naming conventions, Object + Action,
  why fewer events with richer properties.
- [About MetricFlow](https://docs.getdbt.com/docs/build/about-metricflow)
  (dbt docs, ~15 min, verified): how an industry semantic layer structures
  semantic models and metrics. This module builds the same idea from scratch in
  SQLite.

**Exercise type:** design drills, fully worked: write the tracking-plan entry
for a new event; diagnose which definition two disagreeing dashboards used.

**Interview angle:** "How would you instrument feature X?" / "Two teams report
different DAU (Daily Active Users) numbers. What do you do?"

---

## <u>Module 2 — Metrics Frameworks: North Star, HEART, AARRR, OKRs</u>

**Concepts**
- North Star Metric: one metric for the value customers get, plus 3–5 input
  metrics teams can move
- HEART (Happiness, Engagement, Adoption, Retention, Task success) with
  Goals → Signals → Metrics (Google's user-centred framework)
- AARRR, the "pirate metrics" (Acquisition, Activation, Retention, Referral,
  Revenue): a lifecycle funnel of metrics
- OKRs (Objectives and Key Results): how a framework's metrics become
  quarterly targets
- Primary metric plus guardrails: the experiment-time view (the OEC, Overall
  Evaluation Criterion, in the A/B Testing Playbook)
- What each framework is for, what each misses, and when to pick which

**Why it matters**
"What metrics would you track for X?" is a standard product-analyst
interview question. Frameworks give a structured answer and expose blind
spots. Without one, teams pick metrics with blind spots they don't notice, and
optimise the wrong thing.

**Worked example**
Each framework applied to the cosmetics-store event log with real numbers: a North Star
candidate and its input tree; HEART with "no data" cells
(no Happiness data exists); AARRR stages computed where the log supports them
(no Acquisition source, no Referral event). Recapped as one example: the
Product Analytics Case Study's applied primary metric (Week-2 Activation Rate,
61.7%) plus three guardrails
([`05_Metrics_Framework_and_Synthesis.ipynb`](https://github.com/omri-sabag83/Product-Analytics-Case-Study/blob/main/05_Metrics_Framework_and_Synthesis.ipynb),
section "Framework summary").

**Resources**
- [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://research.google.com/pubs/archive/36299.pdf)
  (Rodden, Hutchinson & Fu, CHI 2010, ~25 min, verified): the original HEART
  paper.
- [North Star Playbook: About the North Star Framework](https://amplitude.com/books/north-star/about-north-star-framework)
  (Amplitude, ~20 min, verified).
- [Startup Metrics for Pirates](https://www.slideshare.net/slideshow/startup-metrics-for-pirates-presentation/629833)
  (Dave McClure, 2007 slides, ~10 min, verified): the original AARRR deck.

**Exercise type:** framework selection, fully worked: given three product
scenarios, choose and fill a framework, and name what it can't see.

**Interview angle:** "What would be the North Star for product X?" / "What
metrics would you track for this feature launch?"

---

## <u>Module 3 — Funnel Analysis</u> *(recap)*

**Covered in:**
- A/B Testing Playbook,
  [`02_b2c_product_metrics.ipynb`](https://github.com/omri-sabag83/A-B-Testing-Playbook/blob/main/02_b2c_product_metrics.ipynb),
  "Part 1 — Funnel decomposition (the worked example, simulated at user level)"
- Product Analytics Case Study,
  [`03_Engagement_and_Retention.ipynb`](https://github.com/omri-sabag83/Product-Analytics-Case-Study/blob/main/03_Engagement_and_Retention.ipynb),
  "The funnel"

**Recap:** step conversion vs. overall conversion; decomposing a top-line rate
into steps, so a step that moves the wrong way isn't hidden.

**Compact recompute:** view → cart → purchase on the running dataset,
user-level vs. session-level (19% of purchasing sessions contain no cart
event, so the two disagree).

---

## <u>Module 4 — Activation: Definition & Measurement</u> *(recap)*

**Covered in:** Product Analytics Case Study,
[`02_Activation.ipynb`](https://github.com/omri-sabag83/Product-Analytics-Case-Study/blob/main/02_Activation.ipynb):
3 signals × 3 windows, dose-response, confound and specificity checks.

**Recap:** an activation definition is chosen, not discovered: candidate
signal × window, a check for a natural break, then confound checks.

**Compact recompute:** one first-week signal vs. later return on the running
dataset.

---

## <u>Module 5 — Retention & Cohorts</u> *(recap)*

**Covered in:**
- A/B Testing Playbook,
  [`02_b2c_product_metrics.ipynb`](https://github.com/omri-sabag83/A-B-Testing-Playbook/blob/main/02_b2c_product_metrics.ipynb),
  "Part 2 — Retention curves & cohort analysis" (simulated)
- Product Analytics Case Study,
  [`03_Engagement_and_Retention.ipynb`](https://github.com/omri-sabag83/Product-Analytics-Case-Study/blob/main/03_Engagement_and_Retention.ipynb),
  "Retention over time" and "When do withdrawals actually happen?"

**Recap:** curve shapes (declining, flattening, smile), cohort comparison,
censoring (young cohorts haven't had time).

**Compact recompute:** a monthly cohort triangle on the running dataset.

---

## <u>Module 6 — Engagement: DAU/MAU Stickiness</u> *(recap)*

**Covered in:** A/B Testing Playbook,
[`02_b2c_product_metrics.ipynb`](https://github.com/omri-sabag83/A-B-Testing-Playbook/blob/main/02_b2c_product_metrics.ipynb),
"Part 3 — DAU/MAU stickiness" (simulated).

**Recap:** DAU (Daily Active Users) / MAU (Monthly Active Users) as "how many
days a month the average monthly user shows up"; "active" depends on the
definition (Module 1).

**Compact recompute:** real DAU/MAU over five months, under two definitions of
"active".

---

## <u>Module 7 — Feature Adoption</u> *(recap)*

**Covered in:** Product Analytics Case Study,
[`04_Feature_Adoption_and_Segmentation.ipynb`](https://github.com/omri-sabag83/Product-Analytics-Case-Study/blob/main/04_Feature_Adoption_and_Segmentation.ipynb),
"Adoption" and "Does the mix of features used relate to outcome, independent
of volume?"

**Recap:** adoption (share of users who ever use it) vs. usage share (share of
activity), and mix vs. volume.

**Compact recompute:** adoption vs. usage share on the running dataset's
nearest "feature" dimension.

---

## <u>Module 8 — Monetization Metrics</u>

**Upgraded from recap to full:** the A/B Testing Playbook defines ARPU and LTV
in one paragraph
([`02_b2c_product_metrics.ipynb`](https://github.com/omri-sabag83/A-B-Testing-Playbook/blob/main/02_b2c_product_metrics.ipynb),
Lesson, "Revenue/monetization metrics") but builds no worked example, so there
was nothing with numbers to recap.

**Concepts**
- ARPU (Average Revenue Per User), ARPPU (Average Revenue Per Paying User),
  payer conversion, AOV (Average Order Value), purchase frequency
- The identity revenue = active users × payer rate × orders per payer × AOV,
  and why it locates a revenue change
- Cohort LTV (Lifetime Value): cumulative revenue per user of a starting cohort,
  and why short windows understate it
- Revenue concentration: what share of revenue the top payers bring

**Why it matters**
Revenue is the lagging metric every business tracks. A revenue change without
its decomposition can't be acted on: more buyers, bigger baskets and higher
prices call for different responses.

**Worked example**
The identity computed month by month on the running dataset, with each month's
change split into its four factors; cohort LTV curves; a concentration curve.

**Resources:** to be verified when the module is built.

**Exercise type:** fully worked: "revenue rose X% this month; which factor
drove it?"

**Interview angle:** "Revenue is up but ARPU is down. How is that possible?"

---

## <u>Module 9 — Segmentation: The Methodology Landscape</u>

**Concepts**
- Rule-based slicing by existing fields (what the Case Study did), and its
  limit: it only finds the differences someone thought to slice by
- RFM (Recency, Frequency, Monetary): scoring buyers on three behavioural axes
- Behavioural clustering: k-means on scaled features, choosing k, checking
  stability across random seeds, and validating on planted (simulated) groups
  first
- From clusters to personas: describing, naming, sizing, and the limit
  (clusters describe, they don't explain)

**Why it matters**
"Who are our users?" is answered either by fields someone already logged or
by behaviour. The second can find groups nobody named, but it can also find
groups that aren't there. Knowing the methods and their failure modes is the
skill.

**Worked example**
Rule-based slice recapped from the Product Analytics Case Study
([`04_Feature_Adoption_and_Segmentation.ipynb`](https://github.com/omri-sabag83/Product-Analytics-Case-Study/blob/main/04_Feature_Adoption_and_Segmentation.ipynb),
"Segmentation — does feature mix or outcome vary by student background?"),
then RFM scores and k-means on the running dataset's buyers, with a seed
stability check.

**Resources**
- [RFM and CLV: Using Iso-Value Curves for Customer Base Analysis](https://brucehardie.com/abstracts/abstract-fhl_rfm_clv_2005-02.html)
  (Fader, Hardie & Lee, *Journal of Marketing Research* 42(4), 2005; abstract
  page, verified).
- k-means: verified when the module is built.

**Exercise type:** fully worked: turn a cluster table into named personas, and
say which ones a seed change breaks.

**Interview angle:** "How would you segment our users?"

---

## <u>Module 10 — Metric-Movement Diagnosis</u>

**Added beyond the original scope:** it is a top product-analyst interview
question, it uses Modules 1–9 together, and no earlier repo covers it.

**Concepts**
- A fixed order of checks: is it real (instrumentation, Module 1), is it the
  calendar, is it mix or rate, where is it (segment, funnel step)
- Rate-vs-mix decomposition: splitting a change into "groups changed size"
  and "groups changed behaviour"
- When a movement can't be explained by this data, saying so

**Why it matters**
"Metric X dropped 8% yesterday, why?" is asked in nearly every product-analyst
loop and in real jobs every week. A structured answer that checks the logging
first saves days of chasing a bug as if it were user behaviour.

**Worked example**
A real movement in the running dataset, worked through the checklist (first
case: the February 2020 surge in zero-price cart events found in Module 1),
plus a simulated case with a planted logging bug as known ground truth.

**Resources:** to be verified when the module is built.

**Exercise type:** fully worked diagnosis memos.

**Interview angle:** "DAU dropped 8% last Tuesday. Walk me through it."
