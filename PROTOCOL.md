# Analysis Protocol

**Registered:** 2026-11-18, before any confirmatory analysis was run.
**Study:** Retention of event-based vs. organic newcomers in open source projects (MCEQ 12576, PUC-Campinas).
**Design:** Observational, matched-pair. Unit of analysis = pair (event-based newcomer, matched organic newcomer from the same project). Expected n = 2001 pairs across 330 repositories.

Any deviation from this protocol must be documented in a dated entry in the "Amendments" section at the end of this file.

## 1. Variables

- **Independent variable (grouping):** entry mechanism — event-based (GSoC, LFX Mentorship, Hacktoberfest, 24 Pull Requests) vs. organic.
- **Dependent variable:** activity duration = months between a newcomer's first and last contribution to the project (`raw_dims[4]` in `activity_profiles.json`; integer, 1–272).
- **Paired difference:** D = duration(event) − duration(matched organic).

## 2. Hypotheses

- **H0:** μ_D = 0
- **H1:** μ_D ≠ 0 (two-sided)
- **Significance level:** α = 0.05

## 3. Main test

1. Test normality of D with the Shapiro–Wilk test (α = 0.05).
2. If normality is **not** rejected: **paired t-test** on D.
3. If normality **is** rejected: **Wilcoxon signed-rank test** on D.

## 4. Effect size

- Paired t-test → **Cohen's d_z** (mean of D / SD of D).
- Wilcoxon signed-rank → **matched-pairs rank-biserial correlation**.
- **95% confidence interval** for the effect size by **bootstrap** (resampling pairs), **10,000 resamples**, fixed seed `numpy.random.default_rng(2026)`.

## 5. Exploratory analysis

*Labelled as exploratory; not part of the confirmatory test.*

The same analysis (Section 3–4) run separately for:

- events **with mentorship**: gsoc, lfx;
- events **without mentorship**: hacktoberfest, 24pr.

## 6. Changes from the original Hypothesis Sheet

The original Hypothesis Sheet studied *API documentation format × onboarding time*. The independent and dependent variables were changed because no public dataset with onboarding time in companies exists. The underlying problem — **onboarding of newcomers** — was kept.

## 7. Initial threats to validity

- **Conclusion validity:** with a large n, even negligible differences may be statistically significant; interpretation will focus on the effect size and its CI.
- **Conclusion validity (independence):** the unit is a contributor *in a project*, so the same person can appear in several pairs (2001 event entries come from 1548 distinct people). Pairs are therefore not fully independent, which the paired tests assume.
- **Internal validity:** self-selection — newcomers choose whether to join through an event, so groups may differ in unobserved ways (motivation, experience) beyond the entry mechanism.
- **Construct validity:** activity duration does not distinguish continuous from sparse activity (two contributions years apart count the same as steady activity); it also depends on the data collection date (right-censoring for recent newcomers).
- **External validity:** only GitHub projects that participate in these events are included; results may not generalize to other projects or platforms.

## Amendments

### Amendment 1 — 2026-11-18, before any confirmatory analysis was run

**Finding.** While checking the data, we found 65 pairs in which the organic member is the same GitHub account as the event member (same `username` in `activity_profiles.json`, compared case-insensitively). In 54 of them, the organic member's commit email in `organic_contributors.csv` is the event member's GitHub no-reply address, which confirms it. These pairs compare a contributor with themselves (47 of the 65 have D = 0) and are not valid event-vs-organic comparisons. The most likely cause is that the original study identified event contributors by GitHub username and organic contributors by commit email, without merging the two identities.

Pairs by event type: hacktoberfest 31, gsoc 13, lfx 12, 24pr 9.

**Changes.**

1. **Primary analysis:** run on the pairs that are not self-matched (n = 1936). Sections 2–4 apply unchanged.
2. **Sensitivity analysis:** the same procedure (Sections 3–4: normality check, test choice, effect size, bootstrap CI) run on all 2001 pairs, to show whether the exclusion changes the conclusion.
3. **Exploratory analysis (Section 5):** run on the primary set.

Self-matched pairs are flagged in `data/processed/pairs.csv` (column `self_matched`) by `src/prepare_data.py`; no raw data is changed.
