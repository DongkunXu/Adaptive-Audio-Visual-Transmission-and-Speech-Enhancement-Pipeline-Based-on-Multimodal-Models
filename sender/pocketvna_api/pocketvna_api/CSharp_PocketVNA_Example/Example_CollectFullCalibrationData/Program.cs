using System;
using System.Linq;
using System.Diagnostics;

using PocketVNA_Example;
using static PocketVNA_Example.Utils;
using pocketvna;

namespace Example_CollectFullCalibrationData
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Start Compensation(Calibration) Data Collector");
            Console.WriteLine("Full Calibration " + Settings.FrequencyRange + "/" + Settings.STEPS);

            var frequencies   = Utils.GenerateLineSpaceFrequencies(Settings.FrequencyRange, Settings.STEPS);

            CalibrationDataSet calibrationData = CollectCalibrationDataFromDevice(frequencies);            

            CalibrationDump.Save(Settings.CalibrationDumpFileName, calibrationData);

            lets_make_sure_that_dump_is_stored_properly_and_loading_also_works_fine(Settings.CalibrationDumpFileName, calibrationData);           
        }

        private static CalibrationDataSet CollectCalibrationDataFromDevice(ulong[] frequencies)
        {
            using (var device = pocketvna.PocketVNADevice.Open(PocketVNA.ConnectionInterfaceCode.CIface_HID))
            {
                return CompensationCollector.CollecteCompensationData(device, frequencies);
            }
        }

        private static void lets_make_sure_that_dump_is_stored_properly_and_loading_also_works_fine(string filename, CalibrationDataSet ethalon)
        {
            var restoredCalibration = CalibrationDump.Load(filename);

            Debug.Assert( ethalon.frequencies.SequenceEqual(restoredCalibration.frequencies) );
            Debug.Assert( AreEqual(ethalon.Z0, restoredCalibration.Z0) );
            Debug.Assert( ethalon.modes.SequenceEqual(restoredCalibration.modes) );

            Debug.Assert( AreEqual(ethalon.shortS11, restoredCalibration.shortS11) );
            Debug.Assert( AreEqual(ethalon.openS11,  restoredCalibration.openS11)  );
            Debug.Assert( AreEqual(ethalon.loadS11,  restoredCalibration.loadS11)  );

            Debug.Assert( AreEqual(ethalon.shortS22, restoredCalibration.shortS22) );
            Debug.Assert( AreEqual(ethalon.openS22,  restoredCalibration.openS22)  );
            Debug.Assert( AreEqual(ethalon.loadS22,  restoredCalibration.loadS22)  );

            Debug.Assert( AreEqual(ethalon.openS21,  restoredCalibration.openS21) );
            Debug.Assert( AreEqual(ethalon.thruS21,  restoredCalibration.thruS21) );

            Debug.Assert( AreEqual(ethalon.openS12, restoredCalibration.openS12) );
            Debug.Assert( AreEqual(ethalon.thruS12, restoredCalibration.thruS12) );
        }
       
    }
}
