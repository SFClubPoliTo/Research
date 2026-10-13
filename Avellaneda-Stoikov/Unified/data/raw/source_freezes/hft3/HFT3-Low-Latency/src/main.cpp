#include <array>
#include <cmath>
#include <iostream>
#include <vector>
#include "hft3/rough_lift.hpp"
#include "hft3/policy.hpp"

int main() {
    constexpr std::size_t M = 6;
    hft3::RoughLift<M>::Vec decay{0.992, 0.985, 0.970, 0.940, 0.880, 0.770};
    hft3::RoughLift<M>::Vec weights{0.45, 0.22, 0.13, 0.09, 0.07, 0.04};
    hft3::RoughLift<M> lift(decay, weights);

    constexpr int q_min = -6, q_max = 6;
    constexpr std::size_t y_points = 121;
    constexpr double y_min = -1.0, y_max = 1.0;
    const std::size_t rows = static_cast<std::size_t>(q_max - q_min + 1);

    std::vector<double> bid(rows * y_points);
    std::vector<double> ask(rows * y_points);

    for (std::size_t qi = 0; qi < rows; ++qi) {
        const int q = q_min + static_cast<int>(qi);
        for (std::size_t j = 0; j < y_points; ++j) {
            const double y = y_min + (y_max-y_min) * static_cast<double>(j) / (y_points-1);
            const std::size_t idx = qi * y_points + j;
            // Placeholder surface: replace with offline HJB/corrector output.
            bid[idx] = 0.65 + 0.035*q + 0.08*y;
            ask[idx] = 0.65 - 0.035*q + 0.08*y;
        }
    }

    hft3::PolicySurfaceView policy(bid, ask, q_min, q_max, y_min, y_max, y_points);

    hft3::RoughLift<M>::Vec innovation{0.01, -0.02, 0.005, 0.003, -0.001, 0.004};
    const double y = lift.update_and_aggregate(innovation);
    const auto quote = policy.lookup(2, y);

    std::cout << "y=" << y
              << " bid_offset=" << quote.bid
              << " ask_offset=" << quote.ask << '\n';
    return 0;
}
