#pragma once
#include <algorithm>
#include <cstddef>
#include <span>
#include <utility>

namespace hft3 {

struct QuoteOffsets {
    double bid;
    double ask;
};

class PolicySurfaceView final {
public:
    PolicySurfaceView(std::span<const double> bid,
                      std::span<const double> ask,
                      int q_min,
                      int q_max,
                      double y_min,
                      double y_max,
                      std::size_t y_points) noexcept
        : bid_(bid), ask_(ask), q_min_(q_min), q_max_(q_max),
          y_min_(y_min), y_max_(y_max), y_points_(y_points),
          inv_dy_((y_points > 1 && y_max > y_min)
                    ? (static_cast<double>(y_points - 1) / (y_max - y_min))
                    : 0.0) {}

    [[nodiscard]] inline QuoteOffsets lookup(int q, double y) const noexcept {
        q = std::clamp(q, q_min_, q_max_);
        y = std::clamp(y, y_min_, y_max_);

        const auto q_idx = static_cast<std::size_t>(q - q_min_);
        const double pos = (y - y_min_) * inv_dy_;
        const auto j0 = static_cast<std::size_t>(pos);
        const auto j1 = std::min(j0 + 1, y_points_ - 1);
        const double a = pos - static_cast<double>(j0);

        const std::size_t row = q_idx * y_points_;
        const double b0 = bid_[row + j0];
        const double b1 = bid_[row + j1];
        const double a0 = ask_[row + j0];
        const double a1 = ask_[row + j1];

        return {
            b0 + a * (b1 - b0),
            a0 + a * (a1 - a0)
        };
    }

private:
    std::span<const double> bid_;
    std::span<const double> ask_;
    int q_min_;
    int q_max_;
    double y_min_;
    double y_max_;
    std::size_t y_points_;
    double inv_dy_;
};

} // namespace hft3
