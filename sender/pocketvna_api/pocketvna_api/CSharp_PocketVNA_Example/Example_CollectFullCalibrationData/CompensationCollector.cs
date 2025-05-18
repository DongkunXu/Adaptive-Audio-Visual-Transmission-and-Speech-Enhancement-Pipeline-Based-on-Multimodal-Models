using System;
using System.Collections.Generic;

using pocketvna;

namespace Example_CollectFullCalibrationData
{
    class CompensationCollector
    {
        public enum KitNum { SinglePortCalKit, TwoPortCalKit }

        /// Scan Settings
        private const ushort FirmwareAverage = 5;

        // scan stuff
        private readonly PocketVNADevice device;
        private readonly ulong[] frequencies;
        private readonly KitNum kitnum;

        readonly CalibrationDataSet takenData;

        public static CalibrationDataSet CollecteCompensationData(PocketVNADevice device, ulong[] frequencies, KitNum kitnum = KitNum.TwoPortCalKit)
        {
            
            var dataCollector = new CompensationCollector(device, frequencies, kitnum);

            dataCollector.CollectData();
            dataCollector.ApplyFrequenciesAndZ0();

            return dataCollector.takenData;
        }

        CompensationCollector(PocketVNADevice device, ulong[] frequencies, KitNum kitnum)
        {
            this.device = device;
            this.frequencies = frequencies;
            this.kitnum = kitnum;
            takenData = new CalibrationDataSet
            {
                modes = device.SupportedModes
            };
        }

        private void CollectData()
        {
            try
            {
                TakeMeasurements();
            }
            catch (PocketVNA.DeviceGone)
            {
                Print("Looks like device has disappeared");
                throw;
            }
            catch (PocketVNA.PocketVNAException e)
            {
                Print("Querry is failed: " + e.Message);
                throw;
            }
        }

        private void ApplyFrequenciesAndZ0()
        {
            takenData.Z0 = device.Z0;
            takenData.frequencies = frequencies;            
        }

        private static Tuple<Standard, PocketVNA.Transmission[]> MakePair(Standard standard, params PocketVNA.Transmission[] modes)
        {
            return new Tuple<Standard, PocketVNA.Transmission[]>(standard, modes);
        }

        private Dictionary<string, Tuple<Standard, PocketVNA.Transmission[]>> GetTasks()
        {
            switch (kitnum)
            {
                case KitNum.SinglePortCalKit:
                    return new Dictionary<string, Tuple<Standard, PocketVNA.Transmission[]>> {
                        {  "Connect SHORT to Port-1. Press Enter to Take short S11: ",  MakePair(Standard.Short, PocketVNA.Transmission.S11) },
                        {  "Connect OPEN  to Port-1. Press Enter to Take open S11:  ",  MakePair(Standard.Open, PocketVNA.Transmission.S11) },
                        {  "Connect LOAD  to Port-1. Press Enter to Take load S11:  ",  MakePair(Standard.Load, PocketVNA.Transmission.S11) },

                        {  "Connect SHORT to Port-2. Press Enter to Take short S22: ",  MakePair(Standard.Short, PocketVNA.Transmission.S22) },
                        {  "Connect OPEN  to Port-2. Press Enter to Take open S22:  ",  MakePair(Standard.Open,  PocketVNA.Transmission.S22) },
                        {  "Connect LOAD  to Port-2. Press Enter to Take load S22:  ",  MakePair(Standard.Load,  PocketVNA.Transmission.S22) },

                        {"Leave Port-1 and Port-2 open. Press Enter to Take Transmission Open: ",   MakePair(Standard.Open, PocketVNA.Transmission.S21, PocketVNA.Transmission.S12) },
                        {"Connect Port-1 and Port-2 with coaxial cable. Press Enter to Take Thru: ", MakePair(Standard.Through, PocketVNA.Transmission.S21, PocketVNA.Transmission.S12) },
                    };
                case KitNum.TwoPortCalKit:
                    return new Dictionary<string, Tuple<Standard, PocketVNA.Transmission[]>> {
                        {  "Connect SHORT to Port-1 and to Port-2. Press Enter to Take shorts: ",  MakePair(Standard.Short, PocketVNA.Transmission.S11, PocketVNA.Transmission.S22) },
                        {  "Connect OPEN  to Port-1 and to Port-2. Press Enter to Take opens:  ",  MakePair(Standard.Open, PocketVNA.Transmission.S11, PocketVNA.Transmission.S22) },
                        {  "Connect LOAD  to Port-1 and to Port-2. Press Enter to Take loads:  ",  MakePair(Standard.Load, PocketVNA.Transmission.S11, PocketVNA.Transmission.S22) },

                        {"Leave Port-1 and Port-2 open. Press Enter to Take Transmission Open: ",   MakePair(Standard.Open, PocketVNA.Transmission.S21, PocketVNA.Transmission.S12) },
                        {"Connect Port-1 and Port-2 with coaxial cable. Press Enter to Take Thru: ", MakePair(Standard.Through, PocketVNA.Transmission.S21, PocketVNA.Transmission.S12) },
                    };
            }
            throw new Exception("Unexpected kitnum #" + kitnum);
        }

        private void TakeMeasurements()
        {
            Print("*Take calibration data Wizard*");
            Print("* Make sure you have 2-Port Calibration Kit (IOW: two sets of Short, Open and Load standards (fittings) *");

            var map = GetTasks();

            foreach ( var set in map )
            {
                ScanRequiredAndPutIntoCalibrationData(set.Key, set.Value);
            }

            Print("* Calibration Data is taken *");
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

        private PocketVNA.SNetwork Scan(PocketVNA.ProgressCallback onProgress, params PocketVNA.Transmission[] modes)
        {
            return device.Scan(frequencies, FirmwareAverage, onProgress, modes);
        }

        private static PocketVNA.Progress OnProgress(int total, int index)
        {
            Console.Write("" + index + " / " + total + "\r");
            return PocketVNA.Progress.Continue;
        }

        private void ScanRequiredAndPutIntoCalibrationData(string message, Tuple<Standard, PocketVNA.Transmission[]> sms)
        {
            RawInput(message);
            var net = Scan(OnProgress, sms.Item2);

            foreach ( PocketVNA.Transmission m in sms.Item2 )
            {
                takenData.Set(sms.Item1, m, net.Get(m));
            }           
        }

    }
}
