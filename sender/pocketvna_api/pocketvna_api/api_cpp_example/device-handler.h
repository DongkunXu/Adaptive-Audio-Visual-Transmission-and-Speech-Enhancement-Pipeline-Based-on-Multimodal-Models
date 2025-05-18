#pragma once

#include "pocketvna.h"
#include <stdexcept>
#include <string>
#include <cassert>
#include <memory>

///> RAII for device handler. Connects to device and release handler
struct DeviceHandler {
    PVNA_DeviceHandler handle {nullptr};

    DeviceHandler(const PVNA_DeviceDesc * desc) {
        PVNA_Res r;
        if ( PVNA_Res_Ok != (r = pocketvna_get_device_handle_for(desc, &handle)) ) {
            assert(handle == nullptr);
            throw std::runtime_error("can not connect to device. pocketvna_get_device_handle_for: " + std::to_string((unsigned)r));
        }
    }

    ~DeviceHandler() {
        if ( handle ) {
            pocketvna_release_handle(&handle);
            assert(handle == nullptr);
        }
    }

    DeviceHandler(const  DeviceHandler &) = delete;
    DeviceHandler(DeviceHandler &&) = delete;

    DeviceHandler& operator =(const  DeviceHandler &) = delete;
    DeviceHandler& operator =(DeviceHandler &&) = delete;
};

using DeviceHandlerPtr = std::unique_ptr<DeviceHandler>;
