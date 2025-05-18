using System;
using System.Diagnostics.Contracts;
using System.Linq;

using pocketvna;
using Example_CollectFullCalibrationData;
using PocketVNA_Example;

namespace Example_TakeMeasurementsAndCalibrateOverDumpedData
{
    public class BuiltInCompensationAlgorithm
    {
        public static PocketVNA.SNetwork Apply(CalibrationDataSet calibration, PocketVNA.SNetwork rawMeasurements)
        {
            Contract.Assert(rawMeasurements.frequencies.SequenceEqual(calibration.frequencies));
            Contract.Assert( Utils.AreEqual(rawMeasurements.z0, calibration.Z0, 1E-10) );

            return new PocketVNA.SNetwork(
                rawMeasurements.frequencies,
                PocketVNA.CalibrateReflection(rawMeasurements.s11, calibration.shortS11, calibration.openS11, calibration.loadS11, rawMeasurements.z0),

                PocketVNA.CalibrateTransmission(rawMeasurements.s21, calibration.openS21, calibration.thruS21),
                PocketVNA.CalibrateTransmission(rawMeasurements.s12, calibration.openS12, calibration.thruS12),

                PocketVNA.CalibrateReflection(rawMeasurements.s22, calibration.shortS22, calibration.openS22, calibration.loadS22, rawMeasurements.z0),
                rawMeasurements.z0
            );
        }
    }
}
