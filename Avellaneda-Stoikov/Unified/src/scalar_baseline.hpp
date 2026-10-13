#pragma once
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include "full_hjb_residual.hpp"

namespace hft3 {
struct ScalarConfig {
    ControlParameters control{};
    double horizon{1}, kappa{1.35}, eta2{0.20955182706132114};
    double var_y{0.0776117878004893}, sigma0{1.1}, beta{.75};
    double liq_linear{.60}, liq_vol{.28}, liq_quad{.18};
    double y_max{5*std::sqrt(.0776117878004893)}, cfl{.8};
    std::size_t points{121}, time_steps{390};
    // Zero preserves the t=0-only API. Otherwise save every stride plus endpoints.
    std::size_t snapshot_stride{0};
};
struct ScalarSolution {
    std::vector<double> y, theta;
    // Snapshots are ordered from terminal time backwards to zero.
    std::vector<double> times, history;
    std::size_t points{}, actual_steps{};
    int q_max{};
    double dt{}, minimum_u{}, maximum_u{};
    double at(int q,std::size_t j) const { return theta.at((q+q_max)*points+j); }
};

// Positive explicit Markov-chain scheme for u=exp(-gamma theta).
// Reflecting/truncated domain: outward state transitions are suppressed.
// Optional snapshots retain physical time, including both endpoints.
inline ScalarSolution solve_scalar_baseline(const ScalarConfig& c) {
    c.control.validate();
    auto nonnegative=[](double x) { return std::isfinite(x) && x>=0; };
    if (!(std::isfinite(c.horizon)&&c.horizon>0 && c.points>=3 && c.points<=10001 &&
          c.time_steps>0 && std::isfinite(c.y_max)&&c.y_max>0 &&
          c.cfl>0&&c.cfl<1 && nonnegative(c.kappa)&&nonnegative(c.eta2)&&
          nonnegative(c.var_y)&&nonnegative(c.sigma0)&&std::isfinite(c.beta)&&
          nonnegative(c.liq_linear)&&nonnegative(c.liq_vol)&&nonnegative(c.liq_quad)))
        throw std::invalid_argument("Invalid scalar grid/model");
    const auto& p=c.control;
    const auto ny=c.points;
    const std::size_t nq=2*static_cast<std::size_t>(p.inventory_limit)+1;
    const double dy=2*c.y_max/(ny-1);
    const double max_exit=c.eta2/(dy*dy)+c.kappa*c.y_max/dy+2*p.arrival*std::exp(-p.decay*p.min_offset);
    const double requested=c.horizon/c.time_steps;
    const auto substeps=static_cast<std::size_t>(std::max(1.,std::ceil(requested*max_exit/c.cfl)));
    if (substeps>100000 || c.time_steps>1000000) throw std::invalid_argument("Excessive scalar solve size");
    const std::size_t nt=c.time_steps*substeps;
    const double dt=c.horizon/nt;
    ScalarSolution out; out.points=ny; out.q_max=p.inventory_limit;out.actual_steps=nt;out.dt=dt;
    out.y.resize(ny);
    std::vector<double> variance(ny), left(ny),right(ny),u(nq*ny),next(u.size());
    for(std::size_t j=0;j<ny;++j) {
        const double y=-c.y_max+dy*j;
        out.y[j]=y;
        variance[j]=c.sigma0*c.sigma0*std::exp(c.beta*y-.5*c.beta*c.beta*c.var_y);
        const double drift=-c.kappa*y;
        left[j]=j>0 ? .5*c.eta2/(dy*dy)+std::max(-drift,0.)/dy : 0.;
        right[j]=j+1<ny ? .5*c.eta2/(dy*dy)+std::max(drift,0.)/dy : 0.;
        for(int q=-p.inventory_limit;q<=p.inventory_limit;++q) {
            const double cost=(c.liq_linear+c.liq_vol*std::sqrt(variance[j]))*std::abs(q)+c.liq_quad*q*q;
            u[(q+p.inventory_limit)*ny+j]=std::exp(p.gamma*cost);
        }
    }
    ArrivalHamiltonian ham(p);
    out.minimum_u=*std::min_element(u.begin(),u.end());
    out.maximum_u=*std::max_element(u.begin(),u.end());
    auto save=[&](std::size_t n) {
        out.times.push_back(c.horizon*(1.-static_cast<double>(n)/nt));
        for(double value:u) out.history.push_back(-std::log(value)/p.gamma);
    };
    if(c.snapshot_stride) {
        const auto count=nt/c.snapshot_stride+2;
        if(count>100000000/u.size()) throw std::invalid_argument("Snapshot memory budget exceeded");
        out.history.reserve(count*u.size());
        save(0);
    }
    for(std::size_t n=0;n<nt;++n) {
        for(int q=-p.inventory_limit;q<=p.inventory_limit;++q) for(std::size_t j=0;j<ny;++j) {
            const auto idx=(q+p.inventory_limit)*ny+j;
            const double current=u[idx];
            if(!(std::isfinite(current)&&current>0)) throw std::runtime_error("Nonpositive or overflowing transformed value");
            double rhs=.5*p.gamma*p.gamma*q*q*variance[j]*current;
            if(j>0) rhs+=left[j]*(u[idx-1]-current);
            if(j+1<ny) rhs+=right[j]*(u[idx+1]-current);
            auto jump=[&](double neighbor) {
                const double gain=(std::log(current)-std::log(neighbor))/p.gamma;
                const double delta=ham.offset(gain);
                return p.arrival*std::exp(-p.decay*delta)*(std::exp(-p.gamma*delta)*neighbor-current);
            };
            if(q<p.inventory_limit) rhs+=jump(u[idx+ny]);
            if(q>-p.inventory_limit) rhs+=jump(u[idx-ny]);
            next[idx]=current+dt*rhs;
            if(!(std::isfinite(next[idx])&&next[idx]>0)) throw std::runtime_error("Positivity failure: inspect CFL and model");
            out.minimum_u=std::min(out.minimum_u,next[idx]);
            out.maximum_u=std::max(out.maximum_u,next[idx]);
        }
        u.swap(next);
        if(c.snapshot_stride && ((n+1)%c.snapshot_stride==0 || n+1==nt)) save(n+1);
    }
    out.theta.resize(u.size());
    for(std::size_t i=0;i<u.size();++i) out.theta[i]=-std::log(u[i])/p.gamma;
    return out;
}
} // namespace hft3
