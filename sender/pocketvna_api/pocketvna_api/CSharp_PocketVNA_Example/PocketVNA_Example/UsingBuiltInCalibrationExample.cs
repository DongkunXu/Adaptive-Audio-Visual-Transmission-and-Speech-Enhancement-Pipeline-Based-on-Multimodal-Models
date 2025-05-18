using System;
using System.Numerics;
using System.Linq;
using System.Text;
using System.Diagnostics;
using System.Diagnostics.Contracts;
using pocketvna;

namespace PocketVNA_Example
{
    class UsingBuiltInCalibrationExample
    {
        private static readonly PocketVNA.SNetwork uncalibrated = CalibrationData.uncalibrated;
        private static readonly PocketVNA.SNetwork shortReflectionStandard = CalibrationData.shortReflectionStandard;
        private static readonly PocketVNA.SNetwork openReflectionStandard  = CalibrationData.openReflectionStandard;
        private static readonly PocketVNA.SNetwork loadReflectionStandard  = CalibrationData.loadReflectionStandard;
        private static readonly PocketVNA.SNetwork openTransmissionStandard = CalibrationData.openTransmissionStandard;
        private static readonly PocketVNA.SNetwork thruTransmissionStandard = CalibrationData.thruTransmissionStandard;
        private static readonly PocketVNA.SNetwork calibratedDUT            = CalibrationData.calibratedDUT;

        public static void RunExample()
        {
            Console.WriteLine("Running BuiltIn Calibration Functions");

            runS11Calibration();
            runS21Calibration();
            runS12Calibration();
            runS22Calibration();

            runFullNetworkCalibration();

            Console.WriteLine("OK");
        }

        private static void runS11Calibration()
        {
            checkReflectionDataIsCoherent();

            var dutS11 = PocketVNA.CalibrateReflection(uncalibrated.s11,
                                               shortReflectionStandard.s11, openReflectionStandard.s11, loadReflectionStandard.s11, uncalibrated.z0);

            Utils.assertComplexArraysEqual(calibratedDUT.s11, dutS11);
        }

        private static void checkReflectionDataIsCoherent()
        {
            Contract.Assert(
                uncalibrated.frequencies == shortReflectionStandard.frequencies &&
                uncalibrated.frequencies == openReflectionStandard.frequencies &&
                uncalibrated.frequencies == loadReflectionStandard.frequencies,
                "should be for the same frequency points"
            );
            // Zero Impedances should be the same (to have very close values). Otherwise Normalization is required
            Contract.Assert(
                    Equals(uncalibrated.z0, shortReflectionStandard.z0) &&
                    Equals(uncalibrated.z0, openReflectionStandard.z0 )&&
                    Equals(uncalibrated.z0, loadReflectionStandard.z0 ),
                    "should have the same Zero-Impedance. Otherwise re-normalization is required"
                    );
        }

        private static void checkTransmissionDataIsCoherent()
        {
            Contract.Assert(
                uncalibrated.frequencies == openTransmissionStandard.frequencies &&
                uncalibrated.frequencies == thruTransmissionStandard.frequencies
            );
            // Zero Impedances should be the same (to have very close values). Otherwise Normalization is required
            Contract.Assert(Utils.Equals(uncalibrated.z0, openTransmissionStandard.z0) &&
                    Utils.Equals(uncalibrated.z0, thruTransmissionStandard.z0)
            );
        }

        private static void runS21Calibration()
        {
            checkTransmissionDataIsCoherent();

            var dutS21 = PocketVNA.CalibrateTransmission(uncalibrated.s21,
                                               openTransmissionStandard.s21, thruTransmissionStandard.s21);

            Utils.assertComplexArraysEqual(calibratedDUT.s21, dutS21);
        }


        private static void runS12Calibration()
        {
            checkTransmissionDataIsCoherent();

            var dutS12 = PocketVNA.CalibrateTransmission(uncalibrated.s12,
                                               openTransmissionStandard.s12, thruTransmissionStandard.s12);

            Utils.assertComplexArraysEqual(calibratedDUT.s12, dutS12);
        }

        private static void runS22Calibration()
        {
            checkReflectionDataIsCoherent();

            var dutS22 = PocketVNA.CalibrateReflection(uncalibrated.s22,
                                               shortReflectionStandard.s22, openReflectionStandard.s22, loadReflectionStandard.s22, uncalibrated.z0);

            Utils.assertComplexArraysEqual(calibratedDUT.s22, dutS22);
        }

        private static void runFullNetworkCalibration()
        {
            var calibrated = PocketVNA.CalibrateFullNetwork(uncalibrated,
                                 shortReflectionStandard, openReflectionStandard, loadReflectionStandard,
                                 openTransmissionStandard, thruTransmissionStandard);

            Debug.Assert(calibratedDUT.frequencies == calibrated.frequencies, "frequency should be the same");
            Debug.Assert(Utils.Equals(calibratedDUT.z0, calibrated.z0));

            Utils.assertComplexArraysEqual(calibratedDUT.s11, calibrated.s11);
            Utils.assertComplexArraysEqual(calibratedDUT.s21, calibrated.s21);
            Utils.assertComplexArraysEqual(calibratedDUT.s12, calibrated.s12);
            Utils.assertComplexArraysEqual(calibratedDUT.s22, calibrated.s22);
        }
    }
}
