#pragma once
#include <array>
#include <cstddef>

namespace hft3 {

template <std::size_t M>
class RoughLift final {
public:
    using Vec = std::array<double, M>;

    constexpr RoughLift(Vec decay, Vec weights, Vec initial = {}) noexcept
        : decay_(decay), weights_(weights), state_(initial) {}

    inline double update_and_aggregate(const Vec& innovation) noexcept {
        double y = 0.0;
        for (std::size_t i = 0; i < M; ++i) {
            state_[i] = decay_[i] * state_[i] + innovation[i];
            y += weights_[i] * state_[i];
        }
        return y;
    }

    [[nodiscard]] inline double aggregate() const noexcept {
        double y = 0.0;
        for (std::size_t i = 0; i < M; ++i) {
            y += weights_[i] * state_[i];
        }
        return y;
    }

    [[nodiscard]] constexpr const Vec& state() const noexcept { return state_; }

private:
    Vec decay_;
    Vec weights_;
    Vec state_;
};

} // namespace hft3
