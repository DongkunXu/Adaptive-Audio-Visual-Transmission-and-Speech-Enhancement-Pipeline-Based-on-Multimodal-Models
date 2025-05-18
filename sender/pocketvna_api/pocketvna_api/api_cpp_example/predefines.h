#pragma once

#include "pocketvna.h"
#include <stdexcept>
#include <vector>
#include <complex>

#include <iostream>
#include <iomanip>

#include "literals.h"

struct PocketVNAException : std::runtime_error {
    explicit PocketVNAException(const std::string & msg):std::runtime_error(msg) {}
};

template<PVNA_Res Code>
struct SpecialException : PocketVNAException {
    SpecialException():PocketVNAException(pocketvna_result_string(Code)) {}
};

using DeviceGone = SpecialException<PVNA_Res_InvalidHandle>;
using ScanCanceled = SpecialException<PVNA_Res_ScanCanceled>;
using AccessDenied = SpecialException<PVNA_Res_NoAccess>;

constexpr long double Pi { 3.141592653589793238462643383279502884L };

using Complex = std::complex<double>;
using ComplexVector = std::vector<Complex>;
using Freq = uint64_t;
using FrequencyArray = std::vector<Freq>;
using FreqRange = std::pair<Freq, Freq>;

struct Network {
    FrequencyArray frequency;
    ComplexVector s11, s21, s12, s22;
    double z0;
};
struct Params {
    Freq freq;
    Complex s11, s21, s12, s22;
    double z0;
};

inline ComplexVector convert(const std::vector<PVNA_Sparam> & sps) {
    ComplexVector res(sps.size());
    for ( size_t i = 0; i < sps.size(); ++i ) res[i] = Complex(sps[i].real, sps[i].imag);
    return res;
}

inline  std::vector<PVNA_Sparam> convert(const ComplexVector & sps) {
    std::vector<PVNA_Sparam> res(sps.size());
    for ( size_t i = 0; i < sps.size(); ++i ) res[i] = PVNA_Sparam{sps[i].real(), sps[i].imag()};

    return res;
}

inline bool equals(double exp, double val, double eps = 1E-10) {
    return std::abs( exp - val ) <= eps;
}

inline bool equals(Complex exp, Complex val) {
    return equals(exp.real(), val.real()) && equals(exp.imag(), val.imag());
}

inline std::ostream & operator<<(std::ostream & out, const std::wstring & s) { std::wcout << s << std::flush; return out; }

inline std::ostream & operator<<(std::ostream & out, const FreqRange & range) {
    out << "[" << range.first << "; " << range.second << "]";
    return out;
}


