#pragma once

#include "pocketvna.h"
#include "predefines.h"

#include "progress-listener.h"
#include "device-handler.h"
#include "device-properties.h"

class Device {
    DeviceHandlerPtr handlerPtr;
    DeviceProperties properties;

    DeviceHandler & handler() {
        return *handlerPtr;
    }

    void check(PVNA_Res res, const std::string & str);

    bool isTransmissionSupported(PVNA_NetworkParam p);

    DeviceProperties readProperties() ;

public:
    explicit Device(DeviceHandlerPtr handler);

    DeviceProperties getProperties() const;

    Network scan(FrequencyArray freq, unsigned average, unsigned networkParameters, ProgressCallback callback);

    Params scan(Freq freq, unsigned avg, unsigned networkParameters);

    // This function is not important. It is an example. And it can help to check if there is no ABI/number-encoding issues.
    void assertBindingWorks();
};
