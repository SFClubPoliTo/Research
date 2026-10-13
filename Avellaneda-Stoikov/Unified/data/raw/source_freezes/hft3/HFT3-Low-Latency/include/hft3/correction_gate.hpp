#pragma once
#include <cmath>
#include <stdexcept>

namespace hft3 {
struct GateJet { double value, first, second; };
// C2 transition: zero for r<=lower, one for r>=upper.
class SmoothGate {
    double lower_, inverse_width_;
public:
    SmoothGate(double lower, double upper) : lower_(lower), inverse_width_(1/(upper-lower)) {
        if (!(std::isfinite(lower) && std::isfinite(upper) && upper>lower &&
              std::isfinite(inverse_width_))) throw std::invalid_argument("Invalid gate interval");
    }
    GateJet evaluate(double r) const {
        if (!std::isfinite(r)) throw std::invalid_argument("Non-finite gate coordinate");
        const double x=(r-lower_)*inverse_width_;
        if (x<=0) return {0,0,0};
        if (x>=1) return {1,0,0};
        return {x*x*x*(10+x*(-15+6*x)),
                30*x*x*(1-x)*(1-x)*inverse_width_,
                60*x*(1-x)*(1-2*x)*inverse_width_*inverse_width_};
    }
};
} // namespace hft3
