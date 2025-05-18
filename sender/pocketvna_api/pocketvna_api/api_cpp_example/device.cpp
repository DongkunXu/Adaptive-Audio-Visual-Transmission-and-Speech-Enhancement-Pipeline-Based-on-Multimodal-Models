#include "device.h"


void Device::check(PVNA_Res res, const std::string & str) {
    if ( res != PVNA_Res_Ok ) {
        if ( res == PVNA_Res_InvalidHandle ) {
            throw DeviceGone();
        } else if ( res == PVNA_Res_NoAccess ) {
            throw AccessDenied();
        } else if ( res == PVNA_Res_ScanCanceled ) {
            throw ScanCanceled();
        } else {
            throw PocketVNAException(str + ":" + pocketvna_result_string(res) + "(" + std::to_string(res) + ")");
        }
    }
}

bool Device::isTransmissionSupported(PVNA_NetworkParam p) {
    auto r = pocketvna_is_transmission_supported(handler().handle, p);
    if ( r != PVNA_Res_Ok  && r != PVNA_Res_UnsupportedTransmission ) {
        check(r, "Check if Networ Parameter is supported");
    }
    return r == PVNA_Res_Ok;
}

DeviceProperties Device::readProperties() {
    DeviceProperties props;

    double z0 = 0.0;
    auto r = pocketvna_get_characteristic_impedance(handler().handle, &z0);
    check(r, "Get Z0");

    FreqRange validRange = {0, 0};
    r = pocketvna_get_valid_frequency_range(handler().handle, &validRange.first, &validRange.second);
    check(r, "Get Valid Range");

    FreqRange reasonableRange = {0, 0};
    r = pocketvna_get_reasonable_frequency_range(handler().handle, &reasonableRange.first, &reasonableRange.second);
    check(r, "Get Reasonable Range");

    bool s11 = isTransmissionSupported(PVNA_S11),
         s21 = isTransmissionSupported(PVNA_S21),
         s12 = isTransmissionSupported(PVNA_S12),
         s22 = isTransmissionSupported(PVNA_S22) ;


    props.z0 = z0;
    props.validRange = validRange;
    props.reasonableRange = reasonableRange;
    props.isS11 = s11;
    props.isS21 = s21;
    props.isS12 = s12;
    props.isS22 = s22;

    return props;
}

Device::Device(DeviceHandlerPtr handler):
    handlerPtr(std::move(handler)) {
    properties = readProperties();
}

DeviceProperties Device::getProperties() const {
    return properties;
}

Network Device::scan(FrequencyArray freq, unsigned average, unsigned networkParameters, ProgressCallback callback) {
    const PVNA_Sparam def = { 0, 0 };
    std::vector<PVNA_Sparam> s11(freq.size(), def), s21(freq.size(), def),
                             s12(freq.size(), def), s22(freq.size(), def);

    ProgressListener listener { callback };
    auto proc = listener.toProc();

    auto r = pocketvna_multi_query(handler().handle,
                   freq.data(), freq.size(),
                   average, PVNA_NetworkParam(networkParameters),
                   s11.data(), s21.data(), s12.data(), s22.data(),
                   callback ? &proc : nullptr
    );
    check(r, "scan for frequency vector");

    return {
        freq,
        convert(s11), convert(s21),
        convert(s12), convert(s22),
        properties.z0
    };
}

Params Device::scan(Freq freq, unsigned avg, unsigned networkParameters) {
    PVNA_Sparam s11{0, 0}, s21{0,0}, s12{0, 0}, s22{0,0};

    auto r = pocketvna_single_query(handler().handle, freq, avg, PVNA_NetworkParam(networkParameters),
                                    &s11, &s21, &s12, &s22);
    check(r, "scan for single frequency point");

    return {
        freq,   Complex(s11.real, s11.imag),
                Complex(s21.real, s21.imag),
                Complex(s12.real, s12.imag),
                Complex(s22.real, s22.imag),
                properties.z0
    };
}

void Device::assertBindingWorks() {
    unsigned size = 4;

    unsigned sz = 4;
    std::vector<PVNA_Sparam> p1(sz, PVNA_Sparam{0,0}),
            p2(sz, PVNA_Sparam{0,0});

    auto r = pocketvna_debug_response(handler().handle, size,
                             p1.data(), p2.data());

    check(r, "debug response to check if data-memory layout is ok");

    for ( size_t idx = 0; idx < size; ++idx ) {
        auto v = Pi / (idx + 1);
        Complex exp(v, 1.0 / v);
        Complex exp2(Pi * idx, std::pow(Pi, (idx+1)) );

        assert( equals(exp,  Complex(p1[idx].real, p1[idx].imag) ) );
        assert( equals(exp2, Complex(p2[idx].real, p2[idx].imag) ) );
    }
}

