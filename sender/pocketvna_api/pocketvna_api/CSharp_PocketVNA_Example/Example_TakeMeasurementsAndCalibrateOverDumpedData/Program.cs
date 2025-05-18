using System;

using System.Diagnostics;
using pocketvna;
using System.Linq;
using PocketVNA_Example;
using Example_CollectFullCalibrationData;

namespace Example_TakeMeasurementsAndCalibrateOverDumpedData
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("* Load dumped calibration, take measurements and calibrate *");
            var frequencies = Utils.GenerateLineSpaceFrequencies(Settings.FrequencyRange, Settings.STEPS);

            var restoredCalibration = LoadCalibrationDataDump();            

            var uncalibratedNetwork = ScanForFullNetwork(frequencies);

            var calibrated = BuiltInCompensationAlgorithm.Apply(restoredCalibration, uncalibratedNetwork);

            Debug.Assert(frequencies.SequenceEqual(calibrated.frequencies));

            Console.WriteLine(" END ");
        }

        private static CalibrationDataSet LoadCalibrationDataDump()
        {
            return CalibrationDump.Load(Settings.CalibrationDumpFileName);

        }

        private static PocketVNA.SNetwork ScanForFullNetwork(ulong[] frequencies)
        {
            using (var device = PocketVNADevice.Open(PocketVNA.ConnectionInterfaceCode.CIface_HID))
            {
                return device.ScanAllSupportedModes(frequencies, 4);
            }
        }
    }
}
