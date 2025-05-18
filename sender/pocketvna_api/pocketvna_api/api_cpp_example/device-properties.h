#pragma once

#include <cstdint>
#include <utility>

#include "predefines.h"

struct DeviceProperties {
    bool isS11, isS21,
         isS12, isS22;
    FreqRange validRange;
    FreqRange reasonableRange;
    double z0;
};
