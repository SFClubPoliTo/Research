#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>
#include "hft3/rough_lift.hpp"
#include "hft3/policy.hpp"

static double percentile(std::vector<std::uint64_t> v, double p) {
    if (v.empty()) return 0.0;
    const std::size_t k = static_cast<std::size_t>(p * static_cast<double>(v.size()-1));
    std::nth_element(v.begin(), v.begin()+k, v.end());
    return static_cast<double>(v[k]);
}

int main() {
    using clock = std::chrono::steady_clock;
    constexpr std::size_t M = 6;
    constexpr std::size_t N = 200000;

    hft3::RoughLift<M>::Vec decay{0.992, 0.985, 0.970, 0.940, 0.880, 0.770};
    hft3::RoughLift<M>::Vec weights{0.45, 0.22, 0.13, 0.09, 0.07, 0.04};
    hft3::RoughLift<M> lift(decay, weights);

    constexpr int q_min = -6, q_max = 6;
    constexpr std::size_t y_points = 121;
    constexpr double y_min = -1.0, y_max = 1.0;
    const std::size_t rows = static_cast<std::size_t>(q_max - q_min + 1);

    std::vector<double> bid(rows * y_points), ask(rows * y_points);
    for (std::size_t qi = 0; qi < rows; ++qi) {
        const int q = q_min + static_cast<int>(qi);
        for (std::size_t j = 0; j < y_points; ++j) {
            const double y = y_min + (y_max-y_min) * static_cast<double>(j) / (y_points-1);
            const auto idx = qi*y_points + j;
            bid[idx] = 0.65 + 0.035*q + 0.08*y;
            ask[idx] = 0.65 - 0.035*q + 0.08*y;
        }
    }
    hft3::PolicySurfaceView policy(bid, ask, q_min, q_max, y_min, y_max, y_points);

    // All inputs are allocated and generated outside the hot loop.
    std::mt19937_64 rng(42);
    std::normal_distribution<double> normal(0.0, 0.01);
    std::uniform_int_distribution<int> qdist(q_min, q_max);
    std::vector<hft3::RoughLift<M>::Vec> shocks(N);
    std::vector<int> inventory(N);
    for (std::size_t n = 0; n < N; ++n) {
        for (auto& x : shocks[n]) x = normal(rng);
        inventory[n] = qdist(rng);
    }

    std::vector<std::uint64_t> ns;
    ns.reserve(N);
    volatile double sink = 0.0;

    for (std::size_t n = 0; n < N; ++n) {
        const auto t0 = clock::now();
        const double y = lift.update_and_aggregate(shocks[n]);
        const auto q = policy.lookup(inventory[n], y);
        sink += q.bid + q.ask;
        const auto t1 = clock::now();
        ns.push_back(static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count()
        ));
    }

    const double mean = std::accumulate(ns.begin(), ns.end(), 0.0) / static_cast<double>(ns.size());
    std::cout << "iterations=" << N << '\n'
              << "mean_ns=" << mean << '\n'
              << "p50_ns=" << percentile(ns, 0.50) << '\n'
              << "p95_ns=" << percentile(ns, 0.95) << '\n'
              << "p99_ns=" << percentile(ns, 0.99) << '\n'
              << "p999_ns=" << percentile(ns, 0.999) << '\n'
              << "sink=" << sink << '\n';

    return 0;
}
