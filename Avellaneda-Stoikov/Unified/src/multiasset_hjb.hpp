#pragma once
#include "full_hjb_residual.hpp"

namespace hft3 {
// Z has K factors in total; q has N traded assets. Price and factor noises
// are independent. Covariance matrices are supplied by the model builder.
template<std::size_t N, std::size_t K> struct MultiassetJet {
    double value{}, dt{};
    std::array<double,N> up{}, down{};
    std::array<double,K> gradient{};
    std::array<std::array<double,K>,K> hessian{};
};

template<std::size_t N, std::size_t K>
double multiasset_residual(
    const MultiassetJet<N,K>& f, const std::array<int,N>& q,
    const std::array<double,K>& z, const std::array<double,K>& rates,
    const std::array<std::array<double,K>,K>& factor_cov,
    const std::array<std::array<double,N>,N>& price_cov,
    const ControlParameters& p) {
    // This specialization has common gamma and arrival/quote constraints.
    ArrivalHamiltonian ham(p);
    double result=f.dt;
    for(std::size_t i=0;i<K;++i) {
        result-=rates[i]*z[i]*f.gradient[i];
        for(std::size_t j=0;j<K;++j)
            result+=.5*factor_cov[i][j]*(f.hessian[i][j]-p.gamma*f.gradient[i]*f.gradient[j]);
    }
    for(std::size_t i=0;i<N;++i) {
        if(std::abs(q[i])>p.inventory_limit) throw std::invalid_argument("Inventory outside domain");
        for(std::size_t j=0;j<N;++j)
            result-=.5*p.gamma*q[i]*price_cov[i][j]*q[j];
        if(q[i]<p.inventory_limit) result+=ham(f.up[i]-f.value);
        if(q[i]>-p.inventory_limit) result+=ham(f.down[i]-f.value);
    }
    if(!std::isfinite(result)) throw std::runtime_error("Nonfinite multiasset residual");
    return result;
}
} // namespace hft3
