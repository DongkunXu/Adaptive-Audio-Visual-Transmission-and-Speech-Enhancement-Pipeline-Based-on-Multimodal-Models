#include <iostream>
#include <iomanip>
#include <cassert>
#include <cmath>

#include "device-properties.h"

#include "pocketvna.h"
#include "scope-guard.h"


///> Check driver version.
void check_version() {
    uint16_t ver = 0;
    double pi = 0.;

    assert( PVNA_Res_Ok == pocketvna_driver_version(&ver, &pi) );

    std::cout << "CHECK driver_version call OK" << std::endl;
    std::cout << "\tVERSION = '" << ver << "'" << std::endl;

    /// It is for a developer. It is not required to make this check
    if ( std::abs(Pi - pi) > 1.E-10 ) {
        std::cerr << "\tPI IS INVALID: " << pi << std::endl;
        exit(EXIT_FAILURE);
    }
}

void runCalibrationExample();
void runOpenDeviceAndScanExample(const PVNA_DeviceDesc &);
void runEnumerationExample();
void runScanExample();
void runUsingPlainAPIBindingExample();

int main(int, char * []) {
    try {
        // It would be nice to clear resources by pocketvna_close()
        util::scope_guard([] { pocketvna_close(); });
        check_version();

        runUsingPlainAPIBindingExample();

        runEnumerationExample();
        runScanExample();

        runCalibrationExample();

        return 0;
    } catch ( ... ) {
        return EXIT_FAILURE;
    }
}
