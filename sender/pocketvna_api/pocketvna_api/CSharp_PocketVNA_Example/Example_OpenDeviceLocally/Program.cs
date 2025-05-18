using System;
using System.Diagnostics;

using pocketvna;

using System.Linq;
using PocketVNA_Example;
using static PocketVNA_Example.Utils;

namespace PocketVNA_Example_OpenByDemand
{
    class Program
    {
        public delegate void DeviceTask(PocketVNADevice device);

        static void Main(string[] args)
        {
            Console.WriteLine("PROGRAM START");

            DeviceTask tasks = (DeviceTask)GetDeviceProperties + (DeviceTask)GetSingleS11Point;

            DeviceTask[] myTasks =
            {
                tasks,
                ScanFullNetwork
            };

            foreach (var task in myTasks)
            {
                PerformTaskWithDevice(task);
            }

            Console.WriteLine("PROGRAM END");
        }

        private static void PerformTaskWithDevice(DeviceTask task)
        {
            using (var device = PocketVNADevice.Open(PocketVNA.ConnectionInterfaceCode.CIface_HID))
            {
                if (device != null)
                {
                    task(device);
                } else
                {
                    Console.WriteLine("Could not open device for a task");
                }
            }
        }

        private static void GetDeviceProperties(PocketVNADevice device)
        {
            Console.WriteLine("*Task GetDeviceProperties*");
            Console.WriteLine("Z0 = " + device.Z0);
            Console.WriteLine("Reasonable Range: " + device.DeviceProperties.reasonableRange);
            Console.WriteLine("Valid Range:      " + device.DeviceProperties.validRange);


            Console.WriteLine("Supported Modes:  " + string.Join("/", device.SupportedModes.Select(mode => mode.ToString())));
        }

        private static void GetSingleS11Point(PocketVNADevice device)
        {
            Console.WriteLine("*Task GetSingleS11Point*");
            ulong frequency = 1.Mhz();

            var network = device.Scan(new ulong[] { frequency }, 5, PocketVNA.Transmission.S11);

            Debug.Assert(network.frequencies.Length == 1);
            Debug.Assert(network.frequencies[0] == frequency);
            Debug.Assert(network.s11.Length == 1);
            Debug.Assert(network.s21.Length == 1 && network.s12.Length == 1 && network.s22.Length == 1);
            Debug.Assert(IsZero(network.s12[0]) && IsZero(network.s21[0]) && IsZero(network.s22[0]));

            Console.Write("Scan for Frequency: " + frequency + " Hz");
            Console.WriteLine("S11: " + network.s11[0]);
        }

        private static void ScanFullNetwork(PocketVNADevice device)
        {
            Console.WriteLine("*Task ScanFullNetwork*");
            ulong[] frequencies = { 1.Mhz(), 2.Mhz(), 3.Mhz() };
            const ushort Average = 4;

            var network = device.ScanAllSupportedModes(frequencies, Average);

            Debug.Assert(network.frequencies.SequenceEqual(frequencies));

            for (int i = 0; i < network.Size; ++i)
            {
                Debug.Assert(!IsZero(network.s11[i]));
                Debug.Assert(!IsZero(network.s21[i]));
                Debug.Assert(!IsZero(network.s12[i]));
                Debug.Assert(!IsZero(network.s22[i]));
            }
        }       
    }
}
