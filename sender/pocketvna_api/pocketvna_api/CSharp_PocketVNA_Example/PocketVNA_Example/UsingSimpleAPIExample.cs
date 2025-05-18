using System;
using pocketvna;
using System.Diagnostics;
using System.Numerics;
using System.Collections.Generic;
using System.Collections;
using System.Linq;

namespace PocketVNA_Example
{
    class UsingSimpleAPIExample
    {
        public static void RunExample()
        {
            querryDriverVersion();
            checkMessageCodes();

            var handler = OpenFirstDeviceIfAvailable();

            if (! handler.IsZero() )
            {
                RunExampleForValidHandler(handler);
                RunScanButCancelIt(handler);
            }
            else
            {
                Debug.Assert(!PocketVNA.IsValid(handler), "Device was not opened, so handler should be invalid anyway");
            }

            PocketVNA.Close(ref handler);
            Debug.Assert(handler.IsZero());
        }

        private static void querryDriverVersion()
        {
            ushort version = 0;
            double pi = -1;

            ///> This function returns version and PI. Pi is required to check correctness of binding
            PocketVNA.driver_version(ref version, ref pi);

            Console.WriteLine("Version: " + version + ",  should be PI: " + pi);
            Debug.Assert(version == PocketVNA.CurrentVersion, "It is not very important check. But API can be changed significantly");
            Debug.Assert( Utils.Equals(pi, Math.PI, 1E-15) );
        }

        private static void checkMessageCodes()
        {
            {
                var str = PocketVNA.Result2String(PocketVNA.Result.Ok);

                Console.WriteLine("Version: Result.Ok >> " + str);
                Debug.Assert(str.ToLower() == "ok");
            }
            {
                var str = PocketVNA.Result2String(PocketVNA.Result.InvalidHandle);

                Console.WriteLine("Version: Result.InvalidHandle >> " + str);
                Debug.Assert(str.ToLower() == "device gone");
            }
            {
                var str = PocketVNA.Result2String(PocketVNA.Result.ScanCanceled);

                Console.WriteLine("Version: Result.InvalidHandle >> " + str);
                Debug.Assert(str.ToLower() == "scan is canceled manually");
            }
            {
                var str = PocketVNA.Result2String(PocketVNA.Result.No_Data);

                Console.WriteLine("Version: Result.No_Data >> " + str);
                Debug.Assert(str.ToLower() == "some parameter is not set");
            }            
        }

        private static PocketVNA.Handler OpenFirstDeviceIfAvailable()
        {
            PocketVNA.DeviceDesc[] devices = PocketVNA.ListDevices();

            int deviceIndexCounter = 0;
            foreach ( var descriptor in devices )
            {
                string manufacturer = descriptor.Manufacturer;
                string productName = descriptor.Product;
                string serialNumber = descriptor.SerialNumber;
                string systemDevicePath = descriptor.Path;
                string releaseNumber = descriptor.ReleaseNumber.ToString("X");
                string pid = descriptor.PID.ToString("X");
                string vid = descriptor.VID.ToString("X");

                Console.WriteLine($"Device {++deviceIndexCounter}).\t Author: {manufacturer}, Name: {productName}, Path: {systemDevicePath}, Version: {releaseNumber}, {pid}&{vid}, interface{descriptor.ConnectionInterface}");
            }

            var hidDescriptors = from PocketVNA.DeviceDesc descriptor in devices
                    where descriptor.ConnectionInterface == PocketVNA.ConnectionInterfaceCode.CIface_HID
                    select descriptor;
            if ( hidDescriptors.Count() > 0 )
            {
                var handler = PocketVNA.Open(hidDescriptors.First());

                return handler;
            }
            return new PocketVNA.Handler();
        }


        private static void RunScanButCancelIt(PocketVNA.Handler handler)
        {
            try
            {
                Debug.Assert(PocketVNA.IsValid(handler), "Valid handler is expected");
                ScanMeasurementWithCancel(handler);
                Debug.Assert(false, "should not go this way");
            }
            catch ( PocketVNA.DeviceGone )
            {
                Console.WriteLine("Looks kind of Device is disconnected");
            }
            catch ( PocketVNA.ScanCanceled )
            {
                Console.WriteLine("Scan is Canceled");
            }
        }


        private static void RunExampleForValidHandler(PocketVNA.Handler handler)
        {
            try {
                // in theory it may be invalid in case of coincidence: 
                //    * something is wrong with Operation System
                //    * you are a very quick and disconnected a device
                Debug.Assert(PocketVNA.IsValid(handler), "Valid handler is expected");

                QuerryDeviceProperties(handler);
                ScanMeasurement(handler);
                ScanMeasurementFullNetwork(handler);

            }
            catch ( PocketVNA.DeviceGone )
            {
                Console.WriteLine("Looks kind of Device is disconnected");
            } 
            catch ( PocketVNA.PocketVNAException e )
            {
                Console.WriteLine("Error Happened: " + e.Message);
            }
        }

        private static void QuerryDeviceProperties(PocketVNA.Handler handler)
        {
            Debug.Assert(!handler.IsZero(), "Handler should not be Zero");

            ///> Check if handler is valid (device is connected still)
            bool handlerValid = PocketVNA.IsValid(handler);

            if (handlerValid)
            {
                ///> Check supported Modes
                bool isS11Supported = PocketVNA.IsSupported(handler, PocketVNA.Transmission.S11);
                bool isS21Supported = PocketVNA.IsSupported(handler, PocketVNA.Transmission.S21);
                bool isS12Supported = PocketVNA.IsSupported(handler, PocketVNA.Transmission.S12);
                bool isS22Supported = PocketVNA.IsSupported(handler, PocketVNA.Transmission.S22);

                string[] supportedModesStrings = {
                    isS11Supported ? "S11" : "",
                    isS21Supported ? "S21" : "",
                    isS12Supported ? "S12" : "",
                    isS22Supported ? "S22" : ""
                };
                Console.WriteLine("Supports: " + String.Join(", ", supportedModesStrings));


                ///> Check version of Firmware
                uint firmwareVersion = PocketVNA.Version(handler);

                Console.WriteLine("Firmware VERSION: " + firmwareVersion.ToString("X"));


                ///> Get Characteristic Impedance/Z0
                double z0 = PocketVNA.CharacteristicImpedance(handler);

                Console.WriteLine("Z0: " + z0);


                ///> Valid Frequency Range: frequency range device/driver can accept
                var validRange = PocketVNA.ValidFrequencyRange(handler);

                Console.WriteLine("Valid Frequency Range: " + validRange);


                ///> Reasonable Frequency Range: frequency range for which device returns reasonable result
                var reasonableRange = PocketVNA.ValidFrequencyRange(handler);

                Console.WriteLine("Valid Frequency Range: " + reasonableRange);
            }
        }


        private static void ScanMeasurementFullNetwork(PocketVNA.Handler handler)
        {
            Console.WriteLine("Scanning measurements for Full");

            ulong[] frequencies = { 100.Khz(), 2.Mhz(), 3.Mhz() };
            ushort average = 5;
            PocketVNA.Transmission[] modes = { PocketVNA.Transmission.S11,
                PocketVNA.Transmission.S22, PocketVNA.Transmission.S21, PocketVNA.Transmission.S12 };

            ///> Scan for given frequency vector
            ///> Pay attention: if some Network Parameter is not set explicitly it will be 0. 
            var scanned = PocketVNA.Scan(handler, frequencies, average, modes, (total, currentIndex) =>
            {
                Console.Write("Currenlty: " + currentIndex + " of " + total + "\r");

                return PocketVNA.Progress.Continue;
            });

            Complex zero = new Complex(0, 0);
            Console.WriteLine("\nScanned Data: ");
            Debug.Assert(scanned.frequencies == frequencies, "frequencies should be expected");
            for (int i = 0; i < frequencies.Length; ++i)
            {
                Debug.Assert(!Utils.Equals(scanned.s11[i], zero), " S11 should not be zero: " + scanned.s11[i]);
                Debug.Assert(!Utils.Equals(scanned.s21[i], zero), " S21 should not be zero: " + scanned.s21[i]);
                Debug.Assert(!Utils.Equals(scanned.s12[i], zero), " S12 should not be zero: " + scanned.s12[i]);
                Debug.Assert(!Utils.Equals(scanned.s22[i], zero), " S22 should not be zero: " + scanned.s22[i]);

                Console.WriteLine("{" + scanned.s11[i] + ", " + scanned.s12[i] + ", \n"
                                      + scanned.s21[i] + ", " + scanned.s22[i] + "} ");
            }
            Console.WriteLine();
        }


        private static void ScanMeasurement(PocketVNA.Handler handler)
        {
            Console.WriteLine("Scanning measurements for S11 and S22");

            ulong[] frequencies = { 100000, 2000000, 3000000, 5000000, 8000000, 10000000, 2000000000, 5000000000 };
            ushort average = 5;
            PocketVNA.Transmission[] modes = { PocketVNA.Transmission.S11, PocketVNA.Transmission.S22 };

            ///> Scan for given frequency vector
            ///> Pay attention: if some Network Parameter is not set explicitly it will be 0. 
            var scanned = PocketVNA.Scan(handler, frequencies, average, modes, (total, currentIndex) =>
            {
                Console.Write("Currenlty: " + currentIndex + " of " + total + "\r");

                return PocketVNA.Progress.Continue;
            });

            Complex zero = new Complex(0, 0);
            Console.WriteLine("\nScanned Data: ");
            Debug.Assert(scanned.frequencies == frequencies, "frequencies should be expected");
            for (int i = 0; i < frequencies.Length; ++i)
            {
                Debug.Assert(!Utils.Equals(scanned.s11[i], zero), " S11 should not be zero: " + scanned.s11[i]);
                Debug.Assert(Utils.Equals(scanned.s21[i], zero), " S21 should be zero: " + scanned.s21[i]);
                Debug.Assert(Utils.Equals(scanned.s12[i], zero), " S12 should be zero: " + scanned.s12[i]);
                Debug.Assert(!Utils.Equals(scanned.s22[i], zero), " S22 should not be zero: " + scanned.s22[i]);

                Console.WriteLine("{" + scanned.s11[i] + ", " + scanned.s12[i] + ", \n"
                                      + scanned.s21[i] + ", " + scanned.s22[i] + "} ");
            }
            Console.WriteLine();
        }


        private static void ScanMeasurementWithCancel(PocketVNA.Handler handler)
        {
            Console.WriteLine("Scanning measurements should be canceled");
            ulong[] frequencies = Utils.GenerateLineSpaceFrequencies(5000000, 100000000, 100);
            ushort average = 5;
            PocketVNA.Transmission[] modes = { PocketVNA.Transmission.S11 };

            ///> Scan for given frequency vector
            ///> Pay attention: if some Network Parameter is not set explicitly it will be 0. 
            var scanned = PocketVNA.Scan(handler, frequencies, average, modes, (total, currentIndex) =>
            {
                Console.Write("Currenlty: " + currentIndex + " of " + total + "\r");                

                return currentIndex > 10 ? PocketVNA.Progress.Cancel : PocketVNA.Progress.Continue;
            });

            Debug.Assert(false, "Should be canceled");
            Console.WriteLine();
        }
    }
}
