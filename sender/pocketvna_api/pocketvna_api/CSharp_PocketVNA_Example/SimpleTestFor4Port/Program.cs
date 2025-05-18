using System;
using pocketvna;
using PocketVNA_Example;
using System.IO;
using System.Numerics;

/// <summary>
///   4-Port support works for Upcoming 4-port device  only
///   Highly likely you don't need this example!!!!
/// </summary>
namespace SimpleTestFor4Port
{
    class Program
    {
        private static PocketVNADevice Open(bool simulator = false)
        {
            if ( simulator )
            {
                return PocketVNADevice.OpenSimulator();
            } else
            {
                return PocketVNADevice.Open(PocketVNA.ConnectionInterfaceCode.CIface_HID);
            }            
        }


        static void Main(string[] args)
        {
            Console.WriteLine("Start simple 4-Port example");
            Console.WriteLine(">>> " + Directory.GetCurrentDirectory());

            using (var device = Open())
            {
                PerformCheckSupported(device);
                PerformCheckScan(device);
            }            

            Console.WriteLine("END");
        }

        static bool AreAllZeros(Complex[] array)
        {
            bool result = true;
            foreach (var s in array)
            {
                result = result && Utils.IsZero(s);
            }
            return result;
        }

        delegate void IteratorProc(int p1, int p2, PocketVNA.Transmission t);

        static void IterateOverAllPorts(IteratorProc proc)
        {
            PocketVNA.Transmission[,] transmissions = {
                { PocketVNA.Transmission.S11, PocketVNA.Transmission.S12, PocketVNA.Transmission.S13, PocketVNA.Transmission.S14 },
                { PocketVNA.Transmission.S21, PocketVNA.Transmission.S22, PocketVNA.Transmission.S23, PocketVNA.Transmission.S24 },
                { PocketVNA.Transmission.S31, PocketVNA.Transmission.S32, PocketVNA.Transmission.S33, PocketVNA.Transmission.S34 },
                { PocketVNA.Transmission.S41, PocketVNA.Transmission.S42, PocketVNA.Transmission.S43, PocketVNA.Transmission.S44 }
            };
            for (int p1 = 0; p1 < 4; ++p1)
            {
                for (int p2 = 0; p2 < 4; ++p2)
                {
                    proc(p1, p2, transmissions[p1, p2]);                    
                }
            }
        }

        static void PerformCheckScan(PocketVNADevice device)
        {
            ulong[] frequencies = { 1.Mhz(), 2.Mhz(), 3.Mhz(), 4.Mhz(), 5.Mhz() };


            IterateOverAllPorts((p1, p2, trans) =>
            {
                var matrix = device.Scan4Port(frequencies, 5, new PocketVNA.Transmission[]{ trans }, null);

                IterateOverAllPorts((port1, port2, trans2) => {
                    if ( port1 == p1 && port2 == p2 )
                    {
                        if ( AreAllZeros(matrix.Get(trans2)) ) 
                        {
                            Console.WriteLine("FAILED {0}{1}: should not be zeros", port1 + 1, port2 + 1);
                        }
                    } else
                    {
                        if (! AreAllZeros(matrix.Get(trans2)))
                        {
                            Console.WriteLine("FAILED {0}{1}. SHOULD BE ZEROS", port1 + 1, port2 + 1);
                        }
                    }
                });                    
            });
        }

        static void PerformCheckSupported(PocketVNADevice device)
        {
            PocketVNA.Transmission[,] transmissions = {
                { PocketVNA.Transmission.S11, PocketVNA.Transmission.S12, PocketVNA.Transmission.S13, PocketVNA.Transmission.S14 },
                { PocketVNA.Transmission.S21, PocketVNA.Transmission.S22, PocketVNA.Transmission.S23, PocketVNA.Transmission.S24 },
                { PocketVNA.Transmission.S31, PocketVNA.Transmission.S32, PocketVNA.Transmission.S33, PocketVNA.Transmission.S34 },
                { PocketVNA.Transmission.S41, PocketVNA.Transmission.S42, PocketVNA.Transmission.S43, PocketVNA.Transmission.S44 }
            };
            for (int p1 = 0; p1 < 4; ++p1)
            {
                for (int p2 = 0; p2 < 4; ++p2)
                {
                    if (!device.IsSupported(transmissions[p1, p2]))
                    {
                        Console.WriteLine("Is Not supported {0}{1}", p1 + 1, p2 + 1);
                    }
                }
            }
        }
    }
}
