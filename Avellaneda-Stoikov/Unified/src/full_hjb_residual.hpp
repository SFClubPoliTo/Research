#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <cstddef>

namespace hft3 {
// Jet of the cash/price-separated certainty-equivalent theta, not utility V.
template<std::size_t M> struct ValueJet {
    double value{}, dt{}, up{}, down{};
    std::array<double, M> gradient{};
    std::array<std::array<double, M>, M> hessian{};
};

struct ControlParameters {
    double gamma{0.2}, arrival{14.0}, decay{1.15};
    int inventory_limit{6};
    double min_offset{0.02}, max_offset{4.0};
    void validate() const {
        if (!(std::isfinite(gamma) && gamma > 0 && std::isfinite(arrival) && arrival >= 0 &&
              std::isfinite(decay) && decay > 0 && inventory_limit > 0 &&
              std::isfinite(min_offset) && std::isfinite(max_offset) &&
              min_offset >= 0 && max_offset >= min_offset))
            throw std::invalid_argument("Invalid control parameters");
    }
};

class ArrivalHamiltonian {
    ControlParameters p_;
public:
    explicit ArrivalHamiltonian(ControlParameters p = {}) : p_(p) { p_.validate(); }
    double offset(double gain) const noexcept {
        return std::clamp(std::log1p(p_.gamma / p_.decay) / p_.gamma - gain,
                          p_.min_offset, p_.max_offset);
    }
    double at(double delta, double gain) const noexcept {
        return p_.arrival * std::exp(-p_.decay * delta) *
               (-std::expm1(-p_.gamma * (delta + gain))) / p_.gamma;
    }
    double operator()(double gain) const noexcept { return at(offset(gain), gain); }
    const ControlParameters& parameters() const noexcept { return p_; }
};

struct ResidualTerms {
    double time{}, drift{}, diffusion{}, inventory_risk{}, arrivals{};
    double total() const noexcept { return time + drift + diffusion + inventory_risk + arrivals; }
};

// HFT2 model: dZ_i=-lambda_i Z_i dt+dB, same B for every i;
// price Brownian motion independent of B. Hence covariance is 1*1^T.
template<std::size_t M> class FullHjbResidual {
    static_assert(M > 0);
    std::array<double, M> rates_;
    ArrivalHamiltonian arrival_;
public:
    explicit FullHjbResidual(std::array<double, M> rates, ControlParameters p = {})
        : rates_(rates), arrival_(p) {
        for (double rate : rates_) if (!(std::isfinite(rate) && rate > 0))
            throw std::invalid_argument("OU rates must be positive finite");
    }
    ResidualTerms evaluate(int q, const std::array<double,M>& z, double variance,
                           const ValueJet<M>& theta) const {
        const auto& p = arrival_.parameters();
        if (q < -p.inventory_limit || q > p.inventory_limit ||
            !(std::isfinite(variance) && variance >= 0))
            throw std::invalid_argument("State outside model domain");
        auto finite = [](double x) { if (!std::isfinite(x)) throw std::invalid_argument("Non-finite jet/state"); };
        finite(theta.value); finite(theta.dt); finite(theta.up); finite(theta.down);
        double grad_sum = 0, hessian_sum = 0, drift = 0;
        for (std::size_t i=0; i<M; ++i) {
            finite(z[i]); finite(theta.gradient[i]);
            grad_sum += theta.gradient[i];
            drift -= rates_[i] * z[i] * theta.gradient[i];
            for (std::size_t j=0; j<M; ++j) {
                finite(theta.hessian[i][j]);
                hessian_sum += theta.hessian[i][j];
            }
        }
        ResidualTerms result{theta.dt, drift,
            0.5 * (hessian_sum - p.gamma * grad_sum * grad_sum),
            -0.5 * p.gamma * static_cast<double>(q) * q * variance, 0};
        if (q < p.inventory_limit) result.arrivals += arrival_(theta.up-theta.value);
        if (q > -p.inventory_limit) result.arrivals += arrival_(theta.down-theta.value);
        if (!std::isfinite(result.total())) throw std::overflow_error("Residual overflow; rescale the problem");
        return result;
    }
};

template<std::size_t M> ValueJet<M> embed_scalar(
    const std::array<double,M>& weights, double value, double dt,
    double dy, double dyy, double up, double down) noexcept {
    ValueJet<M> result; result.value=value; result.dt=dt; result.up=up; result.down=down;
    for (std::size_t i=0; i<M; ++i) {
        result.gradient[i]=weights[i]*dy;
        for (std::size_t j=0; j<M; ++j) result.hessian[i][j]=weights[i]*weights[j]*dyy;
    }
    return result;
}
} // namespace hft3
