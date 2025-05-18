using System;
using pocketvna;
using System.Numerics;
using System.Diagnostics;
using System.IO;

namespace PocketVNA_Example
{
    class CompensationCollector
    {
        /// Scan Settings
        private static readonly PocketVNA.FrequencyRange RANGE = new PocketVNA.FrequencyRange(2.Mhz(), 3.Mhz());
        private const int STEPS = 100;
        private const ushort FirmwareAverage = 10;

        // scan stuff
        private readonly PocketVNADevice device;
        private readonly ulong[] frequencies;

        // measurements
        public class TakenData
        {
            public Complex[] shortS11, openS11, loadS11;
            public Complex[] shortS22, openS22, loadS22;
            public Complex[] openS21, thruS21;
            public Complex[] openS12, thruS12;
            public double Z0;
            public ulong[] frequencies;

            public PocketVNA.SNetwork rawMeasurements;
        }

        readonly TakenData takenData;
        

        public static TakenData Run()
        {
            if (PocketVNADevice.IsAnyDeviceConnected())
            {
                var device = PocketVNADevice.Open(PocketVNA.ConnectionInterfaceCode.CIface_HID);

                if (device == null)
                {
                    Console.WriteLine("Could not connect");
                }
                else
                {
                    return CollecteCompensationData(device);
                }
            }
            return null;
        }

        private static TakenData CollecteCompensationData(PocketVNADevice device)
        {
            var frequencies = Utils.GenerateLineSpaceFrequencies(RANGE, STEPS);
            var dataCollector = new CompensationCollector(device, frequencies);

            dataCollector.CollectData();
            dataCollector.StoreData();
            

            return dataCollector.takenData;
        }

        CompensationCollector(PocketVNADevice device, ulong[] frequencies)
        {
            this.device = device;
            this.frequencies = frequencies;
            takenData = new TakenData();
        }

        private void CollectData()
        {
            try
            {
                TakeMeasurements();
            }
            catch ( PocketVNA.DeviceGone )
            {
                Print("Looks like device has disappeared");
                throw;
            } 
            catch ( PocketVNA.PocketVNAException e )
            {
                Print("Querry is failed: " + e.Message);
                throw;
            }
        }

        private void StoreData()
        {
            takenData.Z0 = device.Z0;
            takenData.frequencies = frequencies;
        }

        private void TakeMeasurements()
        {
            Print("Take calibration data");

            if (device.DeviceProperties.supportS11) {
                Print("Taking data for calibration S11: \n");
                TakeShortS11();
                TakeOpenS11();
                TakeLoadS11();
            }

            if (device.DeviceProperties.supportS22) {
                Print("Taking data for calibration S22: \n");
                TakeShortS22();
                TakeOpenS22();
                TakeLoadS22();
            }

            TakeTransmissionOpen();
            TakeTransmissionThru();

            Print("Calibration Data is taken");

            Print("Take DUT measurements: (raw uncalibrated)");
            TakeRawMeasurements();

            Print("done");
        }

        private static void Print(string message)
        {
            Console.WriteLine(message);
        }

        private static void RawInput(string message)
        {
            Print(message + "...");
            Console.ReadKey();
            Console.Write("Ok\r");
        }

        private PocketVNA.SNetwork Scan(PocketVNA.ProgressCallback onProgress,  params PocketVNA.Transmission[] modes)
        {
            return device.Scan(frequencies, FirmwareAverage, onProgress, modes);
        }

        private static PocketVNA.Progress OnProgress(int total, int index)
        {
            Console.Write("" + index + " / " + total + "\r");
            return PocketVNA.Progress.Continue;
        }

        // Short
        private void TakeShortS11() {
            RawInput("Connect SHORT to Port-1. Press Enter to Take S11 short: ");
            var net = Scan(OnProgress, PocketVNA.Transmission.S11);

            // We have queried S11 Only. Others are zero
            takenData.shortS11 = net.s11;
        }

        private void TakeShortS22() {
            RawInput("Connect SHORT to Port-2. Press Enter to Take S22 short: ");
            var net = Scan(OnProgress, PocketVNA.Transmission.S22);

            takenData.shortS22 = net.s22;
        }

        // Open
        private void TakeOpenS11() {
            RawInput("Connect OPEN to Port-1. Press Enter to Take S11 open: ");
            var net = Scan(OnProgress, PocketVNA.Transmission.S11);

            takenData.openS11 = net.s11;
        }

        void TakeOpenS22() {
            RawInput("Connect OPEN to Port-2. Press Enter to Take S22 open: ");
            var net = Scan(OnProgress, PocketVNA.Transmission.S22);

            takenData.openS22 = net.s22;
        }

        // LOAD
        void TakeLoadS11() {
            RawInput("Connect LOAD to Port-1. Press Enter to Take S11 load: ");
            var net = Scan(OnProgress, PocketVNA.Transmission.S11);

            takenData.loadS11 = net.s11;
        }

        void TakeLoadS22() {
            RawInput("Connect LOAD to Port-2. Press Enter to Take S22 load: ");
            var net = Scan(OnProgress, PocketVNA.Transmission.S22);

            takenData.loadS22 = net.s22;
        }

        // OPEN TRANSMISION
        void TakeTransmissionOpen() {
            RawInput("Leave Port-1 and Port-2 open. Press Enter to Take Transmission Open: ");
            PocketVNA.SNetwork net;

            if (device.DeviceProperties.supportS21 && device.DeviceProperties.supportS12)
            {
                net = Scan(OnProgress, PocketVNA.Transmission.S21, PocketVNA.Transmission.S12);

                takenData.openS21 = net.s21;
                takenData.openS12 = net.s12;
            } else {
                Debug.Assert(device.DeviceProperties.supportS21, "Device should support S21 and S11 anyway");
                net = Scan(OnProgress, PocketVNA.Transmission.S21);

                takenData.openS21 = net.s21;
            }
        }

        // THRU
        void TakeTransmissionThru() {
            RawInput("Connect Port-1 and Port-2 with coaxial cable. Press Enter to Take Thru: ");
            PocketVNA.SNetwork net;

            if (device.DeviceProperties.supportS21 && device.DeviceProperties.supportS12)
            {
                net = Scan(OnProgress, PocketVNA.Transmission.S21, PocketVNA.Transmission.S12);

                takenData.thruS21 = net.s21;
                takenData.thruS12 = net.s12;
            }
            else
            {
                Debug.Assert(device.DeviceProperties.supportS21, "Device should support S21 and S11 anyway");
                net = Scan(OnProgress, PocketVNA.Transmission.S21);

                takenData.thruS21 = net.s21;
            }
        }

        void TakeRawMeasurements() { 
            // Now, take raw data that should be calibrated
            // if device supports Full 2-Port network scan, then all parameters are taken
            // otherwise only supported(S11 and S21)
            RawInput("Connect any device to take raw measurements");
            var network = device.ScanAllSupportedModes(frequencies, FirmwareAverage, OnProgress);

            takenData.rawMeasurements = network;
        }

    }
}
