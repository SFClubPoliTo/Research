# 🧩 Numerical interfaces

`full_hjb_residual.hpp` evaluates the declared common-noise certainty-equivalent HJB with bounded arrival controls. Its input jet includes time, spatial and neighboring-inventory values. `correction_basis.hpp` preserves all product derivatives; `correction_gate.hpp` provides a C2 scalar transition with first and second derivatives.

`scalar_baseline.hpp` evolves the transformed value with nonnegative Markov-chain transition rates and CFL-controlled time stepping. It exports time-zero values; time-dependent policy export and full convergence checks remain open.

The inherited `rough_lift.hpp` and `policy.hpp` remain starter interfaces. Their demo surfaces are artificial. A validated finite-horizon policy, coefficient solver and online correction engine are not implemented yet.
