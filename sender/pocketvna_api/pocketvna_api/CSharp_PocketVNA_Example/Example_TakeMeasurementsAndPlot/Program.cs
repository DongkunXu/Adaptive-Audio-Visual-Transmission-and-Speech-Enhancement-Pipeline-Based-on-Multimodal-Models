using System;
using System.Windows.Forms;

using pocketvna;
using Example_CollectFullCalibrationData;

namespace Example_TakeMeasurementsAndPlot
{
    static class Program
    {
        private static PocketVNADevice device;
        private static CalibrationDataSet calibrationData;

        [STAThread]
        static void Main()
        {
            Console.WriteLine("DIRECTORY: " + System.IO.Directory.GetCurrentDirectory());
            device = OpenDevice();
            calibrationData = LoadCalibrationDataDump();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new PlotExample(device, calibrationData));
        }

        private static PocketVNADevice OpenDevice()
        {
            try
            {
                return PocketVNADevice.Open(PocketVNA.ConnectionInterfaceCode.CIface_HID);
            }
            catch ( PocketVNA.PocketVNAException e )
            {
                Console.Error.WriteLine("Open Failed: " + e);
                return null;
            }
        }

        private static CalibrationDataSet LoadCalibrationDataDump()
        {
            try
            {
                return CalibrationDump.Load(Settings.CalibrationDumpFileName);
            } catch ( Exception e )
            {
                Console.WriteLine("Loading calibration file failed: " + e);
                return null;
            }
        }
    }
}
