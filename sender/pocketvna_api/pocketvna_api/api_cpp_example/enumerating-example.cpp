#include "device-enumerator.h"
#include "predefines.h"
#include <iostream>

using namespace std;

namespace {
    void printDescriptor(size_t index, const PVNA_DeviceDesc & desc) {
        cout << "Desc #" << index << endl;
        cout << "\tPath: " << desc.path << ", "
             << "PERMISSIONS: " << ( desc.access & PVNA_ReadAccess ? "R" : "") << (desc.access & PVNA_WriteAccess ? "W" : "") << ", "
             << "S/N: " << wstring(desc.serial_number) << ", "
             << "Manufacturer: " << wstring(desc.manufacturer_string) << ", "
             << "Product: " << wstring(desc.product_string) << ", "
             << "Release: " << hex << desc.release_number << ", "
             << "VID&PID: " << desc.vid << "&" << desc.pid << ", "
             << "Connection Interface: " << (desc.ciface_code == CIface_VCI ? "VCI" : "HID")
             << dec << endl;
    }
}

void runEnumerationExample() {
    try {
        DeviceEnumerator enumerator;

        cout << "Number of found devices: " << enumerator.size() << endl;
        for ( size_t i = 0; i < enumerator.size(); ++i ) {
            printDescriptor(i, enumerator.at(i));
        }
    } catch ( const runtime_error & e ) {
        cerr << "Failed to enumerate: " << e.what() << endl;
    }
}
