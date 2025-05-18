#pragma once

#include "pocketvna.h"
#include <string>
#include <stdexcept>
#include <cassert>

///> RAII for enumerator. Lists available devices and frees list after use
class DeviceEnumerator {
    PVNA_DeviceDesc * list;
    uint16_t listSize;

public:
    DeviceEnumerator():list(nullptr), listSize(0) {
        PVNA_Res r;
        if ( PVNA_Res_Ok != (r = pocketvna_list_devices(&list, &listSize)) ) {
            if ( r != PVNA_Res_NoDevice ) { // NoDevice is rather a code/indication not an error
                throw std::runtime_error("bad pocketvna_list_devices: " + std::to_string((unsigned)r));
            }
        }
    }

    ~DeviceEnumerator() {
        if ( list ) {
            auto r = pocketvna_free_list(&list);
            assert(PVNA_Res_Ok == r); //ONLY OK STATUS IS POSSIBLE
            assert(list == nullptr); //should zero list
        }
    }

    bool any() const noexcept {  return list != nullptr && listSize > 0; }

    size_t size() const noexcept {
        return listSize;
    }

    DeviceEnumerator(const  DeviceEnumerator &)             = delete;
    DeviceEnumerator(DeviceEnumerator &&)                   = delete;

    const PVNA_DeviceDesc & at(size_t i) const {
        if ( i < listSize ) {
            return list[i];
        }
        throw std::out_of_range("index is out of range");
    }

    DeviceEnumerator& operator =(const  DeviceEnumerator &) = delete;
    DeviceEnumerator& operator =(DeviceEnumerator &&)       = delete;
};
