# Integration S045: S044 revision merged into the 24 October reports

Date: 17 November 2026. Branch `integrato/barrick-s045` of this repository.

This note records how the externally prepared S044 revision of the unified
report (28 of 75 audit interventions applied to an earlier draft) was
combined with the 24 October corrections already published here, and what
was changed afterwards in both report editions. Earlier states remain
recoverable from Git: commit `25b4bca` is the 24 October version; the S044
baseline corresponds, chapter by chapter, to the repository state of commit
`98fd945`.

## 1. Merge of the S044 interventions (US-001)

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
| 07 gold econometrics | INT-043, 045 | Conflicts resolved in favour of 24 October: the corrected code no longer clips the GPH estimate, so the S044 description of post-estimation clipping (0.452/0.490, m = 37) describes superseded code. INT-045 (snapshot labelling) merged. |
| 08 volatility, jumps, affine | INT-020, 025, 026, 027, 028 | Eight conflicts resolved in favour of S044 (conditional Gaussian mixtures, Gil-Pelaez with initial spot and improper integral, correlated-driver caveat, cumulants of compound jumps). Citations and the label `eq:SV_kurtosis` restored. |
| 09 option calibration | INT-030 | Conflicts resolved in favour of S044 (Hawkes empty-history initialization; the alpha = 0 limit is an inhomogeneous Poisson law, constant intensity also needs lambda_0 = lambda_bar). Hawkes citation restored. |
| 10 operations and EBITDA | INT-031 | Conflict resolved in favour of S044 (grams to troy ounces, not tonnes; kappa separate from the conversion). Label `eq:production` restored. |

S044 used two suppressive macros, `\sourceref` (printed "source item") and
`\sourcecitation` (printed "[source audit]"), which this report does not
define. They were replaced by real `\eqref` cross-references; the
uncited repository mark was dropped (INT-056).
