#include "pocketvna.h"
#include <iostream>
#include <cassert>
#include <vector>
#include <complex>
#include <cmath>

using namespace std;
using Complex = complex<double>;

namespace {
    inline std::ostream & operator<<(std::ostream & out, const Complex & v) {
        out << v.real() << (v.imag() >= 0 ? '+' : '-') << abs(v.imag()) << 'j';
        return out;
    }

    inline std::ostream & operator<<(std::ostream & out, const PVNA_Sparam & s) {
        out << Complex(s.real, s.imag) << "]";
        return out;
    }

    void printDescriptor(size_t index, const PVNA_DeviceDesc & desc) {
        cout << "Desc #" << index << endl;
        cout << "\tPath: " << desc.path << ", "
             << "PERMISSIONS: " << ( desc.access & PVNA_ReadAccess ? "R" : "") << (desc.access & PVNA_WriteAccess ? "W" : "") << ", ";

        wcout << L"S/N: " << wstring(desc.serial_number) << L", "
              << L"Manufacturer: " << wstring(desc.manufacturer_string) << L", "
              << L"Product: " << wstring(desc.product_string) << L", ";

        cout << "Release: " << hex << desc.release_number << ", "
             << "VID&PID: " << desc.vid << "&" << desc.pid << ", "
             << "Connection Interface: " << (desc.ciface_code == CIface_VCI ? "VCI" : "HID")
             << dec << endl;
    }

    std::string param2str(PVNA_NetworkParam param) {
        switch ( param ) {
        case PVNA_S21: return "S21";
        case PVNA_S11: return "S11";
        case PVNA_S12: return "S12";
        case PVNA_S22: return "S22";
        default:
            break;
        }
        return "";
    }

    void getSomeProperties(PVNA_DeviceHandler handler) {
        assert( handler );

        // Get Z0
        double R = 0.0;
        auto r = pocketvna_get_characteristic_impedance(handler, &R);
        if ( r == PVNA_Res_InvalidHandle ) {
            cerr << "DEVICE GONE.  " << endl;
            return;
        }

        assert ( r == PVNA_Res_Ok );
        cout << "Z0: " << r << endl;

        // Valid Frequency Range
        PVNA_Frequency from = 0, to = 0;
        r = pocketvna_get_valid_frequency_range(handler, &from, &to);
        if ( r == PVNA_Res_InvalidHandle ) {
            cerr << "DEVICE GONE.  " << endl;
            return;
        }

        assert ( r == PVNA_Res_Ok );
        cout << "Valid range: [" << from << ";" << to << "] Hz" << endl;

        // Valid Frequency Range
        r = pocketvna_get_reasonable_frequency_range(handler, &from, &to);
        if ( r == PVNA_Res_InvalidHandle ) {
            cerr << "DEVICE GONE.  " << endl;
            return;
        }

        assert ( r == PVNA_Res_Ok );
        cout << "Reasonable range: [" << from << ";" << to << "] Hz" << endl;

        /// GET Supported Parameters
        PVNA_NetworkParam params[] = {PVNA_S11, PVNA_S21, PVNA_S12, PVNA_S22};
        cout << "Supported Parameters: ";

        for ( auto param : params ) {
            r = pocketvna_is_transmission_supported(handler, param);
            if ( r == PVNA_Res_InvalidHandle ) {
                cerr << "DEVICE GONE.  " << endl;
                return;
            }
            cout << (r == PVNA_Res_Ok ? param2str(param) : "") << ", ";
        }
        cout << endl;
    }

    void demostrateSlitlyOptimizedScan(PVNA_DeviceHandler handler) {
        constexpr unsigned size = 5;
        PVNA_Frequency frequencies[size] = {1000000, 2000000, 3000000, 4000000, 5000000};

        const unsigned Averaging = 4;

        const Complex emptyvalue = 0.0;
        static_assert (sizeof(PVNA_Sparam) == sizeof(Complex), "This demonstration only for identical types");
        vector<Complex> s11(size, emptyvalue), s21(size, emptyvalue),
                s12(size, emptyvalue), s22(size, emptyvalue);

        auto r = pocketvna_multi_query(handler, frequencies, size, Averaging, PVNA_ALL,
                                       reinterpret_cast<PVNA_Sparam*>(s11.data()), reinterpret_cast<PVNA_Sparam*>(s21.data()),
                                       reinterpret_cast<PVNA_Sparam*>(s12.data()), reinterpret_cast<PVNA_Sparam*>(s22.data()),
                                       nullptr);
        if ( r == PVNA_Res_Ok ) {
            for ( size_t i = 0; i < size; ++i ) {
                cout << "[  [" << s11[i] << ", " << s12[i] << "], "
                     << "   [" << s21[i] << ", " << s22[i] << "]] " << endl;
            }
        } else {
            cerr << "Failed to scan: " << pocketvna_result_string(r) << endl;
        }
    }

    void demostrateScan(PVNA_DeviceHandler handler) {
        constexpr unsigned size = 5;
        PVNA_Frequency frequencies[size] = {1000000, 2000000, 3000000, 4000000, 5000000};

        const unsigned Averaging = 4;

        const PVNA_Sparam emptyvalue = { 0.0, 0.0 };
        std::vector<PVNA_Sparam> s11(size, emptyvalue), s21(size, emptyvalue),
                s12(size, emptyvalue), s22(size, emptyvalue);

        auto r = pocketvna_multi_query(handler, frequencies, size, Averaging, PVNA_ALL,
                                       s11.data(), s21.data(), s12.data(), s22.data(),
                                       nullptr);
        if ( r == PVNA_Res_Ok ) {
            for ( size_t i = 0; i < size; ++i ) {
                cout << "[  [" << s11[i] << ", " << s12[i] << "], "
                     << "   [" << s21[i] << ", " << s22[i] << "]] " << endl;
            }
        } else {
            cerr << "Failed to scan: " << pocketvna_result_string(r) << endl;
        }
    }

    void demonstrateGetPropertiesAndScan(PVNA_DeviceHandler handler) {
        assert( handler );

        getSomeProperties(handler);

        // We can check if handler is still valid
        auto r = pocketvna_is_valid(handler);
        if ( r == PVNA_Res_Ok ) {
            demostrateScan(handler);
            demostrateSlitlyOptimizedScan(handler);
        }
    }

    void demonstrateConnectAndGetPropertiesAndScan(const PVNA_DeviceDesc & desc) {
        PVNA_DeviceHandler deviceHandler = nullptr;

        auto r = pocketvna_get_device_handle_for(&desc, &deviceHandler);
        if ( r == PVNA_Res_Ok ) {
            demonstrateGetPropertiesAndScan(deviceHandler);

            r = pocketvna_release_handle(&deviceHandler);
            assert( deviceHandler == nullptr);
            assert( r == PVNA_Res_Ok );
        } else {
            cerr << "Error connection: (" << std::to_string((unsigned)r) << pocketvna_result_string(r) << endl;
        }
    }

    void demonstrateEnumeratingDevices() {
        PVNA_DeviceDesc * list = nullptr;
        uint16_t listSize = 0;

        PVNA_Res r = pocketvna_list_devices(&list, &listSize);
        switch ( r ) {
        case PVNA_Res_No_Data:
            cout << "No device" << endl;
            return;
        case PVNA_Res_Ok:
            cout << "Devices are found" << endl;
            break;
        default:
            cerr << "Error enumerating devices: (" << std::to_string((unsigned)r) << pocketvna_result_string(r) << endl;
            return;
        }

        ///
        assert( list && listSize > 0 );

        for ( unsigned i = 0; i < listSize; ++i ) {
            printDescriptor(i, list[i]);
        }

        demonstrateConnectAndGetPropertiesAndScan(list[0]); // connect to the first device

        /// It is important to free memory occupied by list
        if ( list ) {
            auto r = pocketvna_free_list(&list);
            assert( PVNA_Res_Ok == r ); //ONLY OK STATUS IS POSSIBLE
            assert( list == nullptr  ); //should zero list
        }
    }
}

void runUsingPlainAPIBindingExample() {
    demonstrateEnumeratingDevices();
}
