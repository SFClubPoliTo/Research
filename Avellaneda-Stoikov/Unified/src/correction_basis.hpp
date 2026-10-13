#pragma once
#include "full_hjb_residual.hpp"

namespace hft3 {
// Exact product jet, including spatial cross terms from localization.
// up/down are values at neighboring inventories, for both operands.
template<std::size_t M> ValueJet<M> product(const ValueJet<M>& a, const ValueJet<M>& b) noexcept {
    ValueJet<M> out;
    out.value=a.value*b.value; out.dt=a.dt*b.value+a.value*b.dt;
    out.up=a.up*b.up; out.down=a.down*b.down;
    for (std::size_t i=0;i<M;++i) {
        out.gradient[i]=a.gradient[i]*b.value+a.value*b.gradient[i];
        for (std::size_t j=0;j<M;++j)
            out.hessian[i][j]=a.hessian[i][j]*b.value+a.value*b.hessian[i][j]
                +a.gradient[i]*b.gradient[j]+b.gradient[i]*a.gradient[j];
    }
    return out;
}
template<std::size_t M> ValueJet<M> add_correction(ValueJet<M> base, const ValueJet<M>& correction) noexcept {
    base.value+=correction.value; base.dt+=correction.dt;
    base.up+=correction.up; base.down+=correction.down;
    for(std::size_t i=0;i<M;++i) {
        base.gradient[i]+=correction.gradient[i];
        for(std::size_t j=0;j<M;++j) base.hessian[i][j]+=correction.hessian[i][j];
    }
    return base;
}
} // namespace hft3
