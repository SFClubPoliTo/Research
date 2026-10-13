# Finite-horizon density for the restricted CIR/marked-Hawkes family

This argument concerns the exact continuous-time coefficient family implemented
in `physical_measure.py`. It establishes a probability-measure construction
under explicit assumptions. It does not establish estimation, identification,
particle-filter convergence, predictive performance or corporate value.

The marked-process change-of-measure formula is the general Girsanov formula
in [Schönbucher, Theorem 1](https://www.econstor.eu/bitstream/10419/78414/1/bgse15_2001.pdf).
The need to establish a true density, beyond algebraic intensity changes, is
discussed by [Sokol and Hansen](https://doi.org/10.1080/07362994.2015.1040890).
The bounds and localization argument below are derived here for this project's
restricted family; neither reference validates these empirical fits.

## Assumptions and density

Fix a finite horizon T, deterministic finite initial states v0>=0 and lambda0>=0,
and finite constant coefficients. Under Q, v is nonnegative CIR with positive
kappa_Q, theta_Q and xi. The two Brownian motions have covariance matrix
C=[[1,rho],[rho,1]], |rho|<1. The counting intensity functional satisfies
d lambda_Q=beta(baseline-lambda_Q)dt+alpha dN, with nonnegative baseline, alpha
and beta. Its jump marks have conditional distribution N(mu_Q,sigma_J²), with
sigma_J>0 whenever the jump process is active. Excitation depends on event
counts and not on mark sizes. The Q processes are nonexplosive.

Use constant eta=(eta_S,eta_v), c>0 and b, and impose
kappa_P=kappa_Q-xi*eta_v>0. The Brownian log density is

    integral sqrt(v)*eta' C^-1 dW_Q - 1/2 integral v*eta' C^-1 eta dt.

The jump likelihood has kernel
Y(j)=c exp(b*j-b*mu_Q-b²*sigma_J²/2), and log density

    sum_events log Y(J) - (c-1)*integral lambda_Q dt.

Continuous and discontinuous density local martingales have zero mutual
quadratic covariation. Their product gives the candidate joint density Z.
Localized Girsanov yields Brownian shifts dW_Q=dW_P+eta sqrt(v)dt,
intensity c*lambda_Q, and normal marks with mean mu_Q+b*sigma_J². No
independence assumption between the density factors is required.

## Uniform entropy of the localized densities

Take increasing localizing times tau_n bounding states and event counts, so
the stopped density is a true martingale; Gaussian marks have the exponential
moments needed by this localized construction. Let P_n have density
Z_(T wedge tau_n). The stopped CIR expectation obeys

    E_Pn[v_(t wedge tau_n)] <= v0+kappa_Q*theta_Q*t,

because the physical mean-reversion contribution -kappa_P*v is nonpositive.
Dropping the negative Hawkes decay contribution and applying Gronwall gives

    E_Pn[lambda_Q,(t wedge tau_n)]
       <= (lambda0+beta*baseline*T)*exp(c*alpha*t).

Consequently these bounds hold uniformly over n:

    E_Pn[integral_0^(T wedge tau_n) v dt]
       <= v0*T+kappa_Q*theta_Q*T²/2 = B_v;
    E_Pn[integral_0^(T wedge tau_n) lambda_Q dt]
       <= T*(lambda0+beta*baseline*T)*exp(c*alpha*T) = B_lambda.

Define gamma=eta' C^-1 eta/2 and
H_J=c*log(c)-c+1+c*b²*sigma_J²/2. Taking the stopped log-density expectation
under P_n, centered Brownian integrals disappear and conditional normal mark
entropy gives

    E_Q[Z_(T wedge tau_n)*log Z_(T wedge tau_n)]
       <= gamma*B_v+H_J*B_lambda < infinity,

uniformly in n. For the no-jump case the jump contribution is zero. For
constant-intensity Poisson jumps (alpha=beta=0), B_lambda=lambda0*T and the
jump entropy term is exact.

## Consequence and boundaries

The uniform entropy bound implies uniform integrability of the stopped
densities (x log x is superlinear, with a bounded negative part). Their
nonnegative local-martingale limit therefore has E_Q Z_T=1. Finite state
integrals, finitely many marks and strictly positive Y imply Z_T>0 Q-almost
surely. Thus P and Q are equivalent on the finite-horizon sigma field for
this exact family. This is not a claim of uniform integrability as T tends
to infinity.

Stationarity c*alpha<beta is a separate long-run modelling restriction, not
needed for this finite-horizon entropy argument. A zero Q compensator remains
zero under P. Mark-dependent excitation, state-dependent tilts, different
variance specifications or a changed initial-state law require a separate
proof. The finite-horizon bound is conservative; its magnitude is not an
estimated risk premium or a fit statistic. The Brownian Novikov test remains
an independent sufficient diagnostic, rather than a necessary condition.
