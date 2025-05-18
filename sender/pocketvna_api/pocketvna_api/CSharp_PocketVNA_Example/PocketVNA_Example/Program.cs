using System;
using pocketvna;
using System.Diagnostics;

namespace PocketVNA_Example
{
    class Program
    {
        static void writeArchitecture()
        {
            Console.WriteLine("OS: " + (Environment.Is64BitOperatingSystem ? "64bit" : "32bit")
                + ", Process: " + (Environment.Is64BitProcess ? "64bit" : "32bit"));
            Console.WriteLine("DLL: " + PocketVNA.Dll);
        }

        static void Main(string[] args)
        {
            try {
                writeArchitecture();

                ChooseInterfaceByDescriptorExample.RunExample();

                UsingSimpleAPIExample.RunExample();
                UsingBuiltInCalibrationExample.RunExample();

                ///> Run compensation example
                CompensationExample.RunExample();

            }
            catch ( Exception e )
            {
                Console.Error.WriteLine("Exception: ", e.Message);
                throw;
            }
            System.Console.WriteLine("Press any key");
            Console.ReadKey();
        }
    }
}
