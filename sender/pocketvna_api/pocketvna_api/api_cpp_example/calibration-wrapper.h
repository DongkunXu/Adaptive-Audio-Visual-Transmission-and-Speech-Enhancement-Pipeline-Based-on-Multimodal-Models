#pragma once

#include "pocketvna.h"
#include <cassert>

#include "predefines.h"


ComplexVector calibrateReflection(const ComplexVector raw_meas_mm,
                                  const ComplexVector short_mm, const ComplexVector open_mm, const ComplexVector load_mm,
                                  double z0) {
    assert( raw_meas_mm.size() == short_mm.size() &&
            raw_meas_mm.size() == open_mm.size() &&
            raw_meas_mm.size() == load_mm.size());
    assert(! raw_meas_mm.empty() );

    auto meas = convert(raw_meas_mm);
    auto shrt = convert(short_mm);
    auto open = convert(open_mm);
    auto load = convert(load_mm);

    std::vector<PVNA_Sparam> dut(raw_meas_mm.size(), PVNA_Sparam{0., 0.});
    auto r = pocketvna_rfmath_calibrate_reflection(meas.data(), shrt.data(), open.data(), load.data(),
                                          static_cast<uint32_t>(raw_meas_mm.size()), z0,
                                          dut.data());

    assert(r == PVNA_Res_Ok);

    return convert(dut);
}

ComplexVector calibrateTransmission(const ComplexVector raw_meas_mn,
                                  const ComplexVector open_mn, const ComplexVector thru_mn) {
    assert( raw_meas_mn.size() == open_mn.size() &&
            raw_meas_mn.size() == thru_mn.size() );
    assert(! raw_meas_mn.empty() );

    auto meas = convert(raw_meas_mn);
    auto open = convert(open_mn);
    auto thru = convert(thru_mn);

    std::vector<PVNA_Sparam> dut(raw_meas_mn.size(), PVNA_Sparam{0., 0.});
    auto r = pocketvna_rfmath_calibrate_transmission(meas.data(), open.data(), thru.data(),
                                                static_cast<uint32_t>(raw_meas_mn.size()),
                                                dut.data());

    assert(r == PVNA_Res_Ok);

    return convert(dut);
}



Network calibrateFullNetwork(const Network & meas,
                  const Network & shorts, const Network & opens, const Network & loads,
                  const Network & openThrus, const Network & thruThrus
                  ) {
    assert(meas.frequency == shorts.frequency &&
           meas.frequency == opens.frequency &&
           meas.frequency == loads.frequency &&
           meas.frequency == openThrus.frequency &&
           meas.frequency == thruThrus.frequency );

    assert(equals(meas.z0, shorts.z0) &&
           equals(meas.z0, opens.z0) &&
           equals(meas.z0, loads.z0) &&
           equals(meas.z0, openThrus.z0) &&
           equals(meas.z0, thruThrus.z0) );

    return {
        meas.frequency,
        calibrateReflection(meas.s11, shorts.s11, opens.s11, loads.s11, meas.z0),
        calibrateTransmission(meas.s21, openThrus.s21, thruThrus.s21),
        calibrateTransmission(meas.s12, openThrus.s12, thruThrus.s12),
        calibrateReflection(meas.s22, shorts.s22, opens.s22, loads.s22, meas.z0),
        meas.z0
    };
}

