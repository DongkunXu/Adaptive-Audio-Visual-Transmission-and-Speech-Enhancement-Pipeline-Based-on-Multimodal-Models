#include "predefines.h"
#include "device.h"
#include "device-enumerator.h"
#include <iostream>
using namespace std;

namespace {
    void printParam(const Params & ntwk )  {
        cout << setprecision(5);
        cout << ntwk.freq << ": \n"
             << '\t' << ntwk.s11 << " \t" << ntwk.s21 << endl
             << '\t' << ntwk.s12 << " \t" << ntwk.s22 << endl;
    }

    void printNetwork(const Network & ntwk )  {
        cout << setprecision(5);

        for ( size_t i = 0; i < ntwk.frequency.size(); ++i ) {
            cout << ntwk.frequency[i] << ": \n"
                 << '\t' << ntwk.s11[i] << " \t" << ntwk.s21[i] << endl
                 << '\t' << ntwk.s12[i] << " \t" << ntwk.s22[i] << endl;
        }
    }

    void performScan(Device & device, unsigned networkParameter) {
        FrequencyArray freqs = { 2_MHz, 3_MHz, 4_MHz, 5_MHz, 6_MHz, 7_MHz, 8_MHz, 9_MHz, 10_MHz };
        size_t indexTracker = 0;
        const unsigned Averaging = 3;

        auto network = device.scan(freqs, Averaging, networkParameter, [&](size_t index) {
            indexTracker = index;
            cout << "Currently scanned index is: " << index << "\r" << flush;
            return true;
        });

        assert( indexTracker == freqs.size() );

        printNetwork(network);
    }

    void performScanAndCancelIt(Device & device) {
        FrequencyArray freqs = { 2_MHz, 3_MHz, 4_MHz, 5_MHz, 6_MHz, 7_MHz, 8_MHz, 9_MHz, 10_MHz };
        const unsigned Averaging = 4;

        auto network = device.scan(freqs, Averaging, PVNA_S11, [&](size_t index) {
            return index < 5;
        });

        printNetwork(network);
    }

    void checkBindingWorks(Device & device) {
        device.assertBindingWorks();
    }

    void runOpenDeviceAndScanExample(const PVNA_DeviceDesc & desc) {
        try {
            Device device( unique_ptr<DeviceHandler>(new DeviceHandler(&desc)) );
            auto props = device.getProperties();

            cout << "Device Properties:" << endl
                      << "\tZ0: " << props.z0 << endl
                      << "\tValid Frequency: " << props.validRange << endl
                      << "\tReasonable Frequency: " << props.reasonableRange << endl
                      << "\tSupported: " << (props.isS11 ? " S11 " : "") <<  (props.isS21 ? " S21 " : "")
                      << (props.isS12 ? " S12 " : "") << (props.isS22 ? " S22 " : "") << endl << endl;

            cout << "Check if binding is correct" << endl;
            checkBindingWorks(device);

            cout << "SINGLE POINT FULL SCAN" << endl;
            printParam( device.scan(500_KHz, 5, PVNA_ALL) );

            cout << "SINGLE POINT S22 SCAN" << endl;
            printParam( device.scan(2_MHz, 5, PVNA_S22) );

            cout << "FULL NETWORK SCAN: " << endl;
            performScan(device, PVNA_ALL);

            cout << "S21 only SCAN: " << endl;
            performScan(device, PVNA_S21);

            cout << "S11 and S21 only SCAN: " << endl;
            performScan(device, PVNA_FORWARD);

            cout << "Cancelable scan: " << endl;
            performScanAndCancelIt(device);

        } catch ( const ScanCanceled & ) {
            cerr << "Scan is stopped manually" << endl;
        } catch ( const  DeviceGone & ) {
            cerr << "Device is disconnected" << endl;
        }
    }
}

void runScanExample() {
    DeviceEnumerator enumerator;

    if ( enumerator.any() ) {
#ifdef JUST_CONNECT_TO_THE_FIRST_DEVICE
        runOpenDeviceAndScanExample(enumerator.at(0)); // Connect to the desired device (by description)
#else
        const ConnectionInterfaceCode desiredConnectionInterface = CIface_VCI;
        for ( size_t i = 0; i < enumerator.size(); ++i ) {
            if ( enumerator.at(i).ciface_code == desiredConnectionInterface ) {
                runOpenDeviceAndScanExample(enumerator.at(i)); // Connect to the desired device (by description) via interface
                return;
            }
        }

        cerr << "Interface/Device is not available" << endl;
#endif
    } else {
        cerr << "NO PocketVna device is connected" << endl;
    }
}
