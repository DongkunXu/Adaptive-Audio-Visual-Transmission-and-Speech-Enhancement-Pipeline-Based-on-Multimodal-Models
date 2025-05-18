#pragma once

#include <complex>

inline constexpr unsigned long long operator "" _KHz(unsigned long long v) { return v * 1000ULL; }
inline constexpr unsigned long long operator "" _MHz(unsigned long long v) { return v * 1000000ULL; }
inline constexpr unsigned long long operator "" _GHz(unsigned long long v) { return v * 1000000000ULL; }
inline constexpr unsigned long long operator "" _Hz(unsigned long long v) { return v; }

inline constexpr std::complex<double> operator "" _j(long double v) {
    return std::complex<double>{0.0, static_cast<double>(v)};
}

inline constexpr std::complex<double> operator "" _j(unsigned long long v) {
    return std::complex<double>{0.0, static_cast<double>(v)};
}

