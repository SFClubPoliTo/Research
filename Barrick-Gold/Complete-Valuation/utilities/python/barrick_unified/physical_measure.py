"""Restricted Q-to-P coefficient maps, not estimated physical forecasts.

Convention: dW_Q = dW_P + eta*sqrt(v)*dt; nu_P=c*exp(b*j)/M_Q(b)*nu_Q.
These algebraic maps do not certify the density martingale, data fit or DCF.
"""
from dataclasses import dataclass
import math


def _finite(*values):
    if not all(math.isfinite(x) for x in values):
        raise ValueError("parameters must be finite")


@dataclass(frozen=True)
class NormalJumpMap:
    intensity_ratio: float
    mean_q: float
    mean_p: float
    std: float

    @property
    def compensator_q(self):
        return math.expm1(self.mean_q + .5*self.std**2)

    @property
    def compensator_p(self):
        return math.expm1(self.mean_p + .5*self.std**2)


def normal_jump_map(mean_q, std_q, intensity_ratio, mark_tilt):
    """Normal Esscher marks; separate positive intensity ratio c.

    The kernel is c*exp(b*j - b*mu_Q - .5*b*b*sigma_J**2).
    A zero Q compensator measure remains zero, regardless of c.
    """
    _finite(mean_q,std_q,intensity_ratio,mark_tilt)
    if std_q <= 0 or intensity_ratio <= 0:
        raise ValueError("nondegenerate marks and positive finite intensity ratio required")
    return NormalJumpMap(intensity_ratio,mean_q,mean_q+mark_tilt*std_q**2,std_q)


def variance_map(kappa_q,theta_q,xi,variance_brownian_shift):
    """Linear square-root Brownian shift preserves kappa*theta and xi.

    The shift sign refers to dW_Q=dW_P+eta_v*sqrt(v)dt. It is
    a restriction of this family, not a universal measure-change identity.
    """
    _finite(kappa_q,theta_q,xi,variance_brownian_shift)
    if min(kappa_q,theta_q,xi) <= 0:
        raise ValueError("positive CIR coefficients required")
    kp=kappa_q-xi*variance_brownian_shift
    if kp <= 0:
        raise ValueError("physical variance mean reversion must be positive")
    return {"kappa":kp,"theta":kappa_q*theta_q/kp,"xi":xi}


def hawkes_map(lambda0_q,baseline_q,alpha_q,beta,intensity_ratio):
    """Unmarked exponential Hawkes closure for constant compensator scaling.

    lambda_P=c*lambda_Q on the same counting history: baseline and alpha
    scale by c, beta stays fixed. Stationarity is explicitly imposed here.
    """
    _finite(lambda0_q,baseline_q,alpha_q,beta,intensity_ratio)
    if min(lambda0_q,baseline_q,alpha_q)<0 or beta<=0 or intensity_ratio<=0:
        raise ValueError("invalid intensity parameters")
    if alpha_q>=beta or intensity_ratio*alpha_q>=beta:
        raise ValueError("both Hawkes branching ratios must be below one")
    c=intensity_ratio
    return dict(lambda0=c*lambda0_q,lambda_bar=c*baseline_q,
                alpha=c*alpha_q,beta=beta,branching_ratio=c*alpha_q/beta)


def physical_total_return_drift(carry_q,variance,price_brownian_shift,lambda_q,jump_map):
    """P compensated price drift includes both Brownian and jump premia.

    carry_q is r-q for a supported spot/ETF model or zero for a
    fixed-delivery future with deterministic rates, never the delivery slope.
    """
    _finite(carry_q,variance,price_brownian_shift,lambda_q)
    if variance<0 or lambda_q<0:raise ValueError("negative state")
    return (carry_q+price_brownian_shift*variance+
            lambda_q*(jump_map.intensity_ratio*jump_map.compensator_p-jump_map.compensator_q))


def diffusion_novikov_horizon(kappa_q,xi,rho,eta_price,eta_variance):
    """Sufficient Brownian-density horizon under the constant-coefficient Q CIR.

    Novikov requires E_Q exp(0.5 ||eta||^2_C^-1 integral(v dt)) finite.
    Its CIR Riccati equation is B'=gamma-kappa_Q*B+0.5*xi^2*B^2,
    B(0)=0. Return its explosion time, or infinity when there is none.
    This checks the diffusion density only, not the marked point process,
    identification, shared initial states or future parameter stability.
    """
    _finite(kappa_q,xi,rho,eta_price,eta_variance)
    if kappa_q<=0 or xi<=0 or abs(rho)>=1:raise ValueError('invalid CIR/correlation')
    norm_squared=(eta_price**2-2*rho*eta_price*eta_variance+eta_variance**2)/(1-rho**2)
    discriminant=kappa_q**2-xi**2*norm_squared
    if discriminant>=0:return math.inf
    root=math.sqrt(-discriminant)
    return 2*(math.pi/2+math.atan(kappa_q/root))/root


def restricted_joint_entropy_bound(*, horizon, variance0, kappa_q, theta_q, xi,
                                   rho, eta_price, eta_variance, lambda0=0.,
                                   baseline=0., alpha=0., beta=0.,
                                   intensity_ratio=1., mark_tilt=0., mark_std=0.):
    """Finite-horizon entropy bound for the stated continuous-time family.

    Under localized changed laws, E[v_stopped] <= v0+kappa_Q*theta_Q*t
    and E[lambda_Q_stopped] <= (lambda0+beta*baseline*T)*exp(c*alpha*t).
    Uniform stopped-density entropy gives uniform integrability and E_Q Z_T=1.
    This requires square-root Brownian shifts, constant normal-mark tilts,
    and unmarked linear Hawkes excitation. It does not certify a discretized
    likelihood, empirical fit, inference, or an unspecified broader model.
    See utilities/docs/RESTRICTED-JOINT-DENSITY.md for the complete argument.
    """
    _finite(horizon,variance0,kappa_q,theta_q,xi,rho,eta_price,eta_variance,
            lambda0,baseline,alpha,beta,intensity_ratio,mark_tilt,mark_std)
    if horizon<=0 or min(kappa_q,theta_q,xi,intensity_ratio)<=0 or abs(rho)>=1:
        raise ValueError('invalid horizon, CIR coefficients, correlation or intensity ratio')
    if min(variance0,lambda0,baseline,alpha,beta,mark_std)<0:
        raise ValueError('negative initial state or jump coefficient')
    kappa_p=kappa_q-xi*eta_variance
    if kappa_p<=0:
        raise ValueError('this certificate requires positive physical mean reversion')
    active_jumps=bool(lambda0 or baseline or alpha)
    if active_jumps and mark_std<=0:
        raise ValueError('active normal jumps require positive mark standard deviation')
    gamma=.5*(eta_price**2-2*rho*eta_price*eta_variance+eta_variance**2)/(1-rho**2)
    c=intensity_ratio
    jump_entropy=max(0., c*math.log(c)-c+1.+.5*c*(mark_tilt*mark_std)**2)
    variance_integral_bound=variance0*horizon+.5*kappa_q*theta_q*horizon**2
    _finite(gamma,jump_entropy,variance_integral_bound,c*alpha*horizon)
    terms=[]
    if gamma:
        terms.append(math.log(gamma)+math.log(variance_integral_bound))
    intensity_prefactor=horizon*(lambda0+beta*baseline*horizon)
    _finite(intensity_prefactor)
    if jump_entropy and intensity_prefactor:
        terms.append(math.log(jump_entropy)+math.log(intensity_prefactor)+c*alpha*horizon)
    if not terms:
        log_bound=None
        bound=0.
    else:
        maximum=max(terms)
        log_bound=maximum+math.log(sum(math.exp(value-maximum) for value in terms))
        bound=math.exp(log_bound) if log_bound<math.log(float.fromhex('0x1.fffffffffffffp+1023')) else None
    return dict(status='RESTRICTED_CONTINUOUS_TIME_FINITE_HORIZON_BOUND',
                horizon_years=horizon,kappa_p=kappa_p,
                entropy_upper_bound=bound,log_entropy_upper_bound=log_bound,
                brownian_entropy_coefficient=gamma,jump_entropy_coefficient=jump_entropy,
                requires_normal_marks_and_unmarked_linear_hawkes=True,
                empirical_or_discrete_likelihood_admission=False)
