#include "pocketvna.h"
#include <cassert>

#include "predefines.h"
#include "calibration-wrapper.h"

void runS11Calibration();
void runS21Calibration();
void runS12Calibration();
void runS22Calibration();
void runFullNetworkCalibration();

void runCalibrationExample() {
    std::cout << "RUN calibration example (test)" << std::endl;
    runS11Calibration();
    runS21Calibration();
    runS12Calibration();
    runS22Calibration();

    runFullNetworkCalibration();
    std::cout << "Calibration test - OK" << std::endl;
}


// Test Data
const FrequencyArray freq = { 1_MHz, 2_MHz, 3_MHz };
const ComplexVector  ignored(freq.size(), 0.0);
const double Z0 = 50.0;

const Network uncalibrated = {
    freq,
    ComplexVector({ 1.+4e-05_j,        1.+3e-05_j,       1.+2.e-05_j    }),
    ComplexVector({-2270.0-1010.0_j,  -3480.0-770.0_j,  -2933.0+648.0_j }),
    ComplexVector({-1380.0-1690.0_j,  -730.0 -1570.0_j, -2100.0+1180.0_j}),
    ComplexVector({ 1.+1.e-05_j,       1. - 2e-06_j,     1.-2e-05_j     }),
    Z0
};

const Network shortReflectionStandard = {
    freq,
    ComplexVector({ 495607.8+158961.6_j,   422794.4-77247.0_j,  258956.2-256262.0_j }),
    ignored,
    ignored,
    ComplexVector({ 361065.2-215336.2_j,  147570.4-341318.8_j,  -68243.4-341182.2_j }),
    Z0
};

const Network openReflectionStandard = {
    freq,
    ComplexVector({ -103507.6+103030.2_j, -39050.0+151186.0_j,  46518.4+163327.2_j  }),
    ignored,
    ignored,
    ComplexVector({ 16711.4+108657.4_j,   74518.6+90616.0_j,   110157.8+35605.4_j  }),
    Z0
};

const Network loadReflectionStandard = {
    freq,
    ComplexVector({ 107190.6+185938.2_j,  159541.2+128062.6_j, 180890.8+43653.8_j }),
    ignored,
    ignored,
    ComplexVector({  191258.4+32263.0_j,   157767.8-61217.8_j,  84613.4-131882.6_j   }),
    Z0
};

const Network openTransmissionStandard = {
    freq,
    ignored,
    ComplexVector({ 1159.6-750.4_j,       2114.4-68.2_j,       2046.2+443.4_j  }),
    ComplexVector({ 34.2-1773.4_j,        477.6-1705.4_j,      1910.0-1296.2_j }),
    ignored,
    Z0
};

const Network thruTransmissionStandard = {
    freq,
    ignored,
    ComplexVector({ 445712.4+139863.0_j,  313045.6-210936.8_j, -11186.6-337464.8_j  }),
    ComplexVector({ 289138.6-141807.0_j,  21247.0-283341.0_j,  -174717.8-157904.2_j }),
    ignored,
    Z0
};

const Network calibratedDUT = {
   freq,
   ComplexVector({(0.606576756035065+0.762588073517888_j),
          (0.513267531550349+0.9791358538146341_j),
          (0.235892205955221+1.0616400454600028_j) }),
   ComplexVector({(-0.007180986213496086+0.0016874101047902755_j),
          (-0.011275636438731433-0.009904048451696977_j),
          (-2.8395798205189582e-05-0.014736475042388703_j) }),
   ComplexVector({(-0.004075270223455314-0.00168546296895949_j),
          (-0.000792659613743921-0.004229355008451727_j),
          (0.005751344808592438-0.019118771834241523_j) }),
   ComplexVector({(0.8069678649875225+0.7892394729459603_j),
          (0.6180166034864449+0.852233905016351_j),
          (0.5742805835193814+0.7886191880642951_j) }),
   Z0
};

void checkReflectionDataIsCoherent() {
    // Frequency points should be the same. Otherwise operation is meaningless
    assert( uncalibrated.frequency == shortReflectionStandard.frequency &&
            uncalibrated.frequency == openReflectionStandard.frequency &&
            uncalibrated.frequency == loadReflectionStandard.frequency
            );
    // Zero Impedances should be the same (to have very close values). Otherwise Normalization is required
    assert( uncalibrated.z0 == shortReflectionStandard.z0 &&
            uncalibrated.z0 == openReflectionStandard.z0 &&
            uncalibrated.z0 == loadReflectionStandard.z0
            );
}

void checkTransmissionDataIsCoherent() {
    // Frequency points should be the same. Otherwise operation is meaningless
    assert( uncalibrated.frequency == openTransmissionStandard.frequency &&
            uncalibrated.frequency == thruTransmissionStandard.frequency
            );
    // Zero Impedances should be the same (to have very close values). Otherwise Normalization is required
    assert( uncalibrated.z0 == openTransmissionStandard.z0 &&
            uncalibrated.z0 == thruTransmissionStandard.z0
            );
}

void assertComplexArraysEqual(const ComplexVector & exp, const ComplexVector & res) {
    assert( exp.size() == res.size() );
    for ( size_t i = 0; i < exp.size(); ++i ) {
        assert( equals( exp[i].real() , res[i].real() ) );
        assert( equals( exp[i].imag() , res[i].imag() ) );
    }
}

void runS11Calibration() {
    checkReflectionDataIsCoherent();

    auto dut_s11 = calibrateReflection(uncalibrated.s11,
                                       shortReflectionStandard.s11, openReflectionStandard.s11, loadReflectionStandard.s11, uncalibrated.z0);

    assertComplexArraysEqual(calibratedDUT.s11, dut_s11 );
}

void runS21Calibration() {
    checkTransmissionDataIsCoherent();

    auto dut_s21 = calibrateTransmission(uncalibrated.s21,
                                       openTransmissionStandard.s21, thruTransmissionStandard.s21);

    assertComplexArraysEqual( calibratedDUT.s21, dut_s21 );
}

void runS12Calibration() {
    checkTransmissionDataIsCoherent();

    auto dut_s12 = calibrateTransmission(uncalibrated.s12,
                                       openTransmissionStandard.s12, thruTransmissionStandard.s12);

    assertComplexArraysEqual( calibratedDUT.s12, dut_s12 );
}

void runS22Calibration() {
    checkReflectionDataIsCoherent();

    auto dut_s22 = calibrateReflection(uncalibrated.s22,
                                       shortReflectionStandard.s22, openReflectionStandard.s22, loadReflectionStandard.s22, uncalibrated.z0);

     assertComplexArraysEqual(calibratedDUT.s22, dut_s22 );
}

void runFullNetworkCalibration() {
    auto calibrated = calibrateFullNetwork(uncalibrated,
                         shortReflectionStandard,  openReflectionStandard, loadReflectionStandard,
                         openTransmissionStandard, thruTransmissionStandard);

    assert( calibratedDUT.frequency == calibrated.frequency );
    assert( equals( calibratedDUT.z0, calibrated.z0 ) );

    assertComplexArraysEqual(calibratedDUT.s11, calibrated.s11 );
    assertComplexArraysEqual(calibratedDUT.s21, calibrated.s21 );
    assertComplexArraysEqual(calibratedDUT.s12, calibrated.s12 );
    assertComplexArraysEqual(calibratedDUT.s22, calibrated.s22 );
}


