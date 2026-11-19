# Replication Package

**Same Project, Different Start: How Contribution Events Shape Activity and Retention in Open Source**

EASE 2026 -- The 30th International Conference on Evaluation and Assessment in Software Engineering (OSS4SG Track), Glasgow, United Kingdom, June 9--12, 2026.

---

## Citation

```bibtex
@inproceedings{ashraf2026sameproject,
  title     = {Same Project, Different Start: How Contribution Events Shape
               Activity and Retention in Open Source},
  author    = {Ashraf, Mohamad and [co-authors]},
  booktitle = {Proceedings of the 30th International Conference on Evaluation
               and Assessment in Software Engineering (EASE '26)},
  year      = {2026},
  address   = {Glasgow, United Kingdom},
  publisher = {ACM},
  note      = {OSS4SG Track}
}
```

---

## 1. Study Overview

We conduct a matched-cohort study comparing **2,001 event-based** and **2,001 organic** contributors across **330 open source projects**, investigating whether the entry mechanism -- how a contributor first joins a project -- shapes systematically different behavioral patterns and long-term retention outcomes.

### Research Questions

| RQ | Question |
|----|----------|
| **RQ1** | How do the contribution patterns of event-based and organic contributors differ? |
| **RQ2** | How do these patterns relate to long-term retention and core contributor transitions? |

### Contributor Groups

| Group | Events | n |
|-------|--------|---|
| Mentorship | Google Summer of Code (739) + LFX Mentorship (170) | 909 |
| Non-Mentorship | 24 Pull Requests (576) + Hacktoberfest (516) | 1,092 |
| Organic (matched 1:1) | Same project, no event, commit count [0.5x, 1.5x] | 2,001 |
| **Total** | | **4,002** |

---

## 2. Repository Structure

```
replication_package/
│
├── README.md                 <-- You are here
├── requirements.txt          <-- Python dependencies
├── run_all.py                <-- Runs all 6 scripts in order
├── run_all.sh                <-- Shell wrapper
│
├── data/                     <-- Input data (CSV + JSON)
│   ├── event_contributors.csv
│   ├── organic_contributors.csv
│   ├── per_contributor_core_status.csv
│   ├── per_contributor_retention.csv
│   ├── activity_profiles.json
│   ├── contribution_index_timeseries.json
│   ├── descriptive_core_stats.csv
│   ├── first_3months_weekly_results.json
│   ├── statistical_test_results.json
│   ├── survival_retention_results.json
│   ├── survival_core_results.json
│   └── scott_knott_results.json
│
├── scripts/                  <-- One script per paper section
│   ├── 00_dataset_validation.py
│   ├── 01_activity_profiles.py
│   ├── 02_early_engagement_patterns.py
│   ├── 03_core_rate_and_ttc.py
│   ├── 04_survival_analysis.py
│   └── 05_pattern_outcome_ranking.py
│
└── figures/                  <-- Generated figures (after running)
    ├── spider_plot.png       <-- Figure 1
    ├── weekly_patterns.png   <-- Figure 2
    └── survival_curves.png   <-- Figure 3
```

---

## 3. Script-to-Paper Mapping

Each script is self-contained and maps directly to a section of the paper. Every script prints the paper section it corresponds to, the expected results from the paper, and the actual computed results.

| Script | Paper Section | What It Does | Output |
|--------|--------------|--------------|--------|
| `00_dataset_validation.py` | Sec. 3.1--3.3, Table 1 | Validates matched-cohort design; reproduces Table 1 (dataset breakdown); Mann-Whitney test confirming event/organic comparability (p=0.21, d=-0.02) | Terminal output |
| `01_activity_profiles.py` | Sec. 3.5 (RQ1), Sec. 4.1.1, **Fig. 1** | Computes 6 activity dimensions per contributor (percentile-rank normalized); generates spider/radar plot showing Mentorship=community-engaged, Non-Ment.=code-focused, Organic=balanced | `figures/spider_plot.png` |
| `02_early_engagement_patterns.py` | Sec. 3.5 (RQ1), Sec. 4.1.2, **Fig. 2** | Builds 12-week CI series; K-means K=2..6 (selects K=3 by silhouette); labels Front-Loading/Intermittent/Steady; chi-squared on distribution | `figures/weekly_patterns.png` |
| `03_core_rate_and_ttc.py` | Sec. 3.5 (RQ2), Sec. 4.2.1, **Table 2** (top) | Chi-squared + OR for core rate (Event vs Organic, Ment. vs Non-Ment.); Mann-Whitney + Cliff's delta for time-to-core | Terminal output |
| `04_survival_analysis.py` | Sec. 3.5 (RQ2), Sec. 4.2.2, **Fig. 3** | Kaplan-Meier curves, log-rank tests, Cox PH for retention and core achievement; tests the mentorship paradox | `figures/survival_curves.png` |
| `05_pattern_outcome_ranking.py` | Sec. 3.5 (RQ2), Sec. 4.2.3, **Table 2** (bottom) | Scott-Knott ESD partitioning patterns into ranks by retention and core rate; cross-group validation | Terminal output |

---

## 4. Data Description

### 4.1 Contributor Data

**`data/event_contributors.csv`** (2,001 rows) -- One row per event contributor.

| Column | Description |
|--------|-------------|
| `username` | GitHub username |
| `repo` | GitHub repository (owner/name) |
| `event` | Event program: gsoc, lfx, hacktoberfest, 24pr |
| `commit_count` | Number of commits in this project |
| `contribution_id` | Unique identifier |

**`data/organic_contributors.csv`** (2,001 rows) -- One row per matched organic contributor.

| Column | Description |
|--------|-------------|
| `email` | Contributor email (for commit matching) |
| `name` | Contributor name |
| `repo` | Same project as matched event contributor |
| `matched_event_type` | Event type of matched counterpart |
| `commit_count` | Number of commits |
| `event_commits` | Commit count of the matched event contributor |
| `matched_event_contribution_id` | Links to the matched event contributor |

### 4.2 Core Status (RQ2)

**`data/per_contributor_core_status.csv`** (4,002 rows) -- Core contributor status for every contributor.

| Column | Description |
|--------|-------------|
| `contributor_id` | Unique identifier |
| `contributor_type` | `event` or `organic` |
| `event_type` | gsoc, lfx, hacktoberfest, 24pr |
| `ever_core` | `True` / `False` -- did contributor reach core status |
| `time_to_core_months` | Months from first commit to first core appearance |
| `is_mentorship` | `True` if gsoc or lfx |

Core definition: Pareto 80/20 (smallest set with 80% of cumulative commits), computed monthly, skipping first 12 months (founder-dominated period).

### 4.3 Retention / Survival (RQ2)

**`data/per_contributor_retention.csv`** (~3,288 rows) -- Survival data for Kaplan-Meier analysis.

| Column | Description |
|--------|-------------|
| `contributor_type` | `event` or `organic` |
| `event_type` | Event program |
| `is_mentorship` | `True` / `False` |
| `survival_months` | Months from first commit to leaving (or censoring) |
| `event_observed` | `1` = left the project; `0` = right-censored (still active) |
| `is_event` | `1` = event contributor; `0` = organic |

"Left the project" = no recorded activity for >= 5 consecutive months (Calefato et al. 2022).

### 4.4 Activity Profiles (RQ1)

**`data/activity_profiles.json`** (4,002 entries) -- Six activity dimensions per contributor.

Each entry contains:
- `percentile_dims`: [commit_freq, pr_success, issue_activity, discussion_depth, activity_duration, contribution_breadth] -- all normalized to [0,1] via percentile rank
- `raw_dims`: raw values before normalization
- `raw_counts`: {commits, prs, merged_prs, issues, issue_comments}
- `contributor_type`, `event_type`, `repo`

### 4.5 Contribution Index Time Series (RQ1)

**`data/contribution_index_timeseries.json`** -- Monthly CI per contributor.

Structure: `{"event": [...], "organic": [...]}` where each entry has:
- `months`: list of "YYYY-MM" strings
- `ci`: monthly CI values (0.35*commits + 0.25*PRs + 0.20*merged + 0.20*issues)
- `ci_normalized`: min-max normalized CI
- `username`/`email`, `repo`, `event_type`

---

## 5. How to Run

### Requirements

```bash
pip install -r requirements.txt
```

Python >= 3.8. Dependencies: pandas, numpy, scipy, scikit-learn, matplotlib, lifelines.

### Run Everything

```bash
python replication_package/run_all.py
```

### Run Individual Scripts

```bash
# Just dataset validation
python replication_package/scripts/00_dataset_validation.py

# Just the survival analysis
python replication_package/scripts/04_survival_analysis.py

# Only RQ2 scripts (03, 04, 05)
python replication_package/run_all.py 03 04 05
```

### Expected Runtime

| Script | Approximate time |
|--------|-----------------|
| 00 | < 5 seconds |
| 01 | < 10 seconds |
| 02 | ~30 seconds (K-means fitting) |
| 03 | < 5 seconds |
| 04 | ~15 seconds (survival fitting) |
| 05 | ~10 seconds (depends on Script 02 output) |
| **Total** | **~1 minute** |

---

## 6. Key Definitions

| Term | Definition | Source |
|------|-----------|--------|
| **Newcomer** | First recorded contribution to the project | Pinto et al. 2016 |
| **Core contributor** | Smallest set with 80% of cumulative commits (monthly, skip 12 months) | Mockus et al. 2002; Yamashita et al. 2015 |
| **Time-to-core** | Months from first commit to first core appearance | -- |
| **Left the project** | >= 5 consecutive months with no activity | Calefato et al. 2022 |
| **Weekly CI** | 0.35 * commits + 0.25 * PRs + 0.20 * merged + 0.20 * issues | Cheng & Guo 2019 |
| **Percentile rank** | Rank-based normalization to [0, 1] | Anderson et al. 2025 |
| **Scott-Knott ESD** | Hierarchical clustering into statistically distinct ranks | Tantithamthavorn et al. 2017 |
| **Cliff's delta** | Non-parametric effect size (negligible < 0.147 < small < 0.33 < medium < 0.474 < large) | -- |

---

## 7. Ethical Considerations

All data was collected from publicly available GitHub repositories and public event registries. Contributor identities (usernames, emails) are included solely to enable replication. We request that replicators do not use this data to contact or identify individual contributors beyond the scope of this study.

---

## License

MIT License. Dataset provided for research purposes only.
