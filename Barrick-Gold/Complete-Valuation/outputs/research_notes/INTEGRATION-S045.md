# Integration S045: S044 revision merged into the 24 October reports

Date: 17 November 2026. Branch `integrato/barrick-s045` of this repository.

This note records how the externally prepared S044 revision of the unified
report (28 of 75 audit interventions applied to an earlier draft) was
combined with the 24 October corrections already published here, and what
was changed afterwards in both report editions. Earlier states remain
recoverable from Git: commit `25b4bca` is the 24 October version; the S044
baseline corresponds, chapter by chapter, to the repository state of commit
`98fd945`.

## 1. Merge of the S044 interventions

Method: three-way merge per chapter, with base = S044 baseline (`baseline/s030`),
theirs = S044 head (`revision/s044-group14`, commit `4c82416`), ours = the
24 October chapter. Rules: mathematical and statistical corrections from S044
prevail; dated numerical results, carry, valuation clock and the removal of
per-share values from 24 October prevail.

| Chapter | S044 interventions | Result |
| --- | --- | --- |
| 00 discoveries | INT-004 (date of the USD 44.13 reference) | Superseded: the per-share figure and market reference were removed on 24 October. 24 October text kept. |
| 03 company perimeter | INT-031 | Merged cleanly (units of the production identity, troy-ounce constant). |
| 04 probability and pricing | INT-005, 006, 007, 008, 010 | Merged cleanly. |
| 05 econometrics | INT-011, 012, 013, 014 | Merged cleanly. |
| 06 Monte Carlo | INT-016, 017, 018, 019, 021, 022, 023, 024 | Merged; two conflicts resolved in favour of S044 (QMC point sets are not i.i.d.; payoff dispersion of one QMC set is not a standard error). The S044 phrase "no such results are supplied here" was replaced by a pointer to the Article 3 code, which does compute a replication-based error from independent scrambled Sobol' sets. Sobol' citation restored. |
| 07 gold econometrics | INT-043, 044, 045 | Conflicts resolved in favour of 24 October: the corrected code no longer clips the GPH estimate, so the S044 description of post-estimation clipping (0.452/0.490, m = 37) describes superseded code. INT-044 (constrained GARCH estimator) merged and checked against `src/barrick_unified/empirical_figures.py`. INT-045 merged; its AR(1) note was later updated to the Newey-West errors of the corrected Article 7 code. |
| 08 volatility, jumps, affine | INT-020, 025, 026, 027, 028 | Eight conflicts resolved in favour of S044 (conditional Gaussian mixtures, Gil-Pelaez with initial spot and improper integral, correlated-driver caveat, cumulants of compound jumps). Citations and the label `eq:SV_kurtosis` restored. |
| 09 option calibration | INT-030 | Conflicts resolved in favour of S044 (Hawkes empty-history initialization; the alpha = 0 limit is an inhomogeneous Poisson law, constant intensity also needs lambda_0 = lambda_bar). Hawkes citation restored. |
| 10 operations and EBITDA | INT-031 | Conflict resolved in favour of S044 (grams to troy ounces, not tonnes; kappa separate from the conversion). Label `eq:production` restored. |

S044 used two suppressive macros, `\sourceref` (printed "source item") and
`\sourcecitation` (printed "[source audit]"), which this report does not
define. They were replaced by real `\eqref` cross-references; the
uncited repository mark was dropped (INT-056).

## 2. Status of all 75 interventions

The 47 interventions not applied by S044 were checked against the merged text.
"Not applied" interventions would have re-inserted material omitted from the
source articles (Greeks, copulas, affine matrices, portfolio wealth); for a
shorter publication the source articles are cited instead (decision SC-10).

| INT | Status |
| --- | --- |
| INT-001 | applied |
| INT-002 | applied in part |
| INT-003 | applied |
| INT-004 | applied in S044, merged (superseded: per-share reference removed on 24 October) |
| INT-005 | applied in S044, merged |
| INT-006 | applied in S044, merged |
| INT-007 | applied in S044, merged |
| INT-008 | applied in S044, merged |
| INT-009 | applied |
| INT-010 | applied in S044, merged |
| INT-011 | applied in S044, merged |
| INT-012 | applied in S044, merged |
| INT-013 | applied in S044, merged |
| INT-014 | applied in S044, merged |
| INT-015 | applied |
| INT-016 | applied in S044, merged |
| INT-017 | applied in S044, merged |
| INT-018 | applied in S044, merged |
| INT-019 | applied in S044, merged |
| INT-020 | applied in S044, merged |
| INT-021 | applied in S044, merged |
| INT-022 | applied in S044, merged |
| INT-023 | applied in S044, merged |
| INT-024 | applied in S044, merged |
| INT-025 | applied in S044, merged |
| INT-026 | applied in S044, merged |
| INT-027 | applied in S044, merged |
| INT-028 | applied in S044, merged |
| INT-029 | applied in part |
| INT-030 | applied in S044, merged |
| INT-031 | applied in S044, merged |
| INT-032 | applied in part |
| INT-033 | open decision, conservative wording |
| INT-034 | applied |
| INT-035 | open decision, conservative wording |
| INT-036 | applied in part |
| INT-037 | open decision, conservative wording |
| INT-038 | open decision, conservative wording |
| INT-039 | already resolved on 24 October |
| INT-040 | open decision, conservative wording |
| INT-041 | applied in part |
| INT-042 | applied in part |
| INT-043 | applied in S044, merged (superseded: GPH clipping text replaced by the corrected unclipped estimates) |
| INT-044 | applied in S044, merged |
| INT-045 | applied in S044, merged |
| INT-046 | applied in part |
| INT-047 | applied in part |
| INT-048 | applied |
| INT-049 | applied in part |
| INT-050 | applied in part |
| INT-051 | applied in part |
| INT-052 | applied in part |
| INT-053 | applied |
| INT-054 | not applied (adds content; source article cited) |
| INT-055 | already resolved on 24 October |
| INT-056 | already resolved on 24 October |
| INT-057 | applied in part |
| INT-058 | not applied (adds content; source article cited) |
| INT-059 | applied in part |
| INT-060 | applied in part |
| INT-061 | not applied (adds content; source article cited) |
| INT-062 | applied in part |
| INT-063 | applied in part |
| INT-064 | not applied (adds content; source article cited) |
| INT-065 | applied in part |
| INT-066 | applied in part |
| INT-067 | not applied (adds content; source article cited) |
| INT-068 | applied in part |
| INT-069 | applied |
| INT-070 | applied |
| INT-071 | applied in part |
| INT-072 | not applicable (process card) |
| INT-073 | applied in part |
| INT-074 | not applied (adds content; source article cited) |
| INT-075 | not applied (adds content; source article cited) |

## 3. Scientific decisions SC-01 to SC-12

| SC | Outcome |
| --- | --- |
| SC-01 claim and role of P/Q and copper | Conservative choice in the text: a conditional four-engine operating-margin proxy; copper as a paired increment. |
| SC-02 single operating perimeter | Resolved for the valued flows by the dated clock (actuals excluded). |
| SC-03 cost-model authority | Open. The text states that the specification of the frozen cost vectors is not established beyond the source description. |
| SC-04 accounting bridge and corporate claim | Conservative: equity bridge not applied; no per-share value or market comparison. |
| SC-05 phases, growth and reinvestment | Open; the text no longer claims that the growth/ROIC identity funds growth. |
| SC-06 losses, taxes, terminal profit | Terminal policy explicit; the quarterly loss and symmetric tax rule of `dated_valuation.py` is now stated. |
| SC-07 date, clock and residual flows | Resolved by the 24 October dated clock. |
| SC-08 finite resources and closure | Open; reserve life outside the model, terminal alternatives tabulated. |
| SC-09 vintage and algorithm authority | Resolved for the gold option layer (24 October q = 0.40% calibration and rolling OOS); 12 August results kept in one dated table. |
| SC-10 recovery of omitted content | Conservative: source articles cited, content not re-inserted. |
| SC-11 numerical conventions | Resolved: pseudo-random paths, standard errors across paths, type-7 linear quantiles as computed. |
| SC-12 bibliographic identities | Resolved except Eichengreen-Hausmann-Panizza (2003), now cited together with Eichengreen (1996). |

No decision is presented as approved by the authors.

## 4. Corrections from the earlier review

Both editions: 17 full quarters follow the 2026Q3 stub (18 valued); GLD
carry justified by the declining gold backing and gold futures; early exercise
described as numerically negligible; Feller binds for the jump models and the
Heston optimum lies on the boundary (the relaxed fit, with vol of vol about
1.16, violates it); Heston simulation described as full truncation, as in
`gold_paths.py`; Article 7 order selection reported with the corrected grid, which admits the zero-order model and selects no lag; price-error ranking qualified (vega-weighted loss is nested,
price RMSE is not); the introduction and the DCF chapter no longer promise a
per-share value or market comparison; internal run identifiers, file paths
and workflow language removed; uncited bibliography entries removed and the
Diebold-Mariano reference added. The Paper's 7 September and 5 October
technical-audit supplements (q = 0, earlier numbers) were removed.

## 5. Editorial consolidation

| Topic | Definitive location | Removed elsewhere |
| --- | --- | --- |
| Brownian motion, Ito, GBM, Black-Scholes | Ch. 4 | Re-derivations in ch. 6 and ch. 8 |
| Jump-diffusion, compensator, Levy drift | Ch. 8 (`sec:jump-diffusion`, `rem:levy-drift`) | Restatements in ch. 4 and ch. 6 (ch. 6 keeps simulation notation) |
| Stochastic volatility, Merton/Heston/Bates comparison | Ch. 8 (`sec:sv-theory`, `sec:bates-model`, `sec:model-comparison`) | Three internal restatements in ch. 8; SDEs in ch. 9 |
| Hawkes process and Bates-Hawkes dynamics | Ch. 9 (`sec:hawkes-definition`, `sec:bh-dynamics`) | Ch. 8 restatement; repeated route descriptions in ch. 9; duplicate intensity figure |
| Returns, ACF, rolling correlation, HC errors | Ch. 5 | Ch. 7 definitions |
| Production identity, cost model, copper design | Ch. 10, ch. 10 copper | Ch. 3 duplicates |
| Valuation clock and controlled design | Ch. 12 (`sec:valuation-clock`, `sec:controlled-design`) | Ch. 3, ch. 10, ch. 11, ch. 14 restatements |
| Proxy caveats, limitations, headline results | Ch. 12 and ch. 14 | Repeated lists in ch. 9, 11, 12, front matter |
| 12 August (q = 0) calibration results | One dated table in ch. 9 | Scattered paragraphs |

All S044 corrections inside removed blocks were kept or moved to the
definitive location. No citation key or unique figure was removed; one
duplicate figure (same Hawkes path and seed) was removed. Two never-compiled
chapter files and the self-blocked August source generator were removed.

| Measure | 24 October | 17 November |
| --- | --- | --- |
| Long edition pages | 212 | 197 |
| Long edition words (PDF text) | 101,412 | 94,169 |
| Display equations in source | 747 | 668 |
| Paper pages | 10 | 10 |

## 6. Reproducibility

Checked: both editions compile with pdfLaTeX without errors, undefined
references or uncited entries; the generated results file is byte-identical
in both editions; numbers were reconciled with `outputs/paper_audit_20261024/`
and the Article 7 CSV outputs. Not re-executed: calibration, OOS and
valuation pipelines (they need licensed row-level option data kept locally).
No numerical result was changed in this revision.
