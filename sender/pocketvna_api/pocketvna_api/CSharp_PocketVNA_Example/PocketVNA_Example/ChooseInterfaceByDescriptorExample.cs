using pocketvna;
using System;

namespace PocketVNA_Example
{
    class ChooseInterfaceByDescriptorExample
    {
        public delegate bool SelectFunction(PocketVNA.DeviceDesc descriptor);

        public static void RunExample()
        {
            Console.WriteLine("START: example of choosing interface/connection");

            try
            {

                Connect2FirstInterfaceAvailable(PocketVNA.ConnectionInterfaceCode.CIface_VCI, "VCI interface");
                Connect2FirstInterfaceAvailable(PocketVNA.ConnectionInterfaceCode.CIface_HID, "HID interface");

                ConnectByDescriptor();
            } catch ( Exception e )
            {
                Console.Error.WriteLine("Error: " + e.Message);
            }

            Console.WriteLine("The END");
        }

        private static PocketVNA.DeviceDesc FindProperDescription(SelectFunction checker)
        {
            var enumeration = PocketVNA.ListDevices();
            if (enumeration.Length < 1)
            {
                throw new Exception("No Connection Available"); // DeviceDesc is a struct. So for simplicity let's throw.
            }

            foreach (var desc in enumeration)
            {
                if (checker(desc))
                {
                    return desc;
                }
            }

            throw new Exception("Descriptor is not found");
        }


        private static void ConnectByDescriptor()
        {
            Console.WriteLine("Choose a proper descriptor");
            /// Select a connection/device by some property
            var desciptor = FindProperDescription((des) => (des.ConnectionInterface == PocketVNA.ConnectionInterfaceCode.CIface_HID));

            using (var device = PocketVNADevice.Open(desciptor))
            {
                if (device != null)
                {
                    PrintInfo(device);
                }
                else
                {
                    Console.Error.WriteLine("Error! Could not open device");
                }
            }
        }



        private static void Connect2FirstInterfaceAvailable(PocketVNA.ConnectionInterfaceCode code, String message)
        {
            Console.WriteLine("Run " + message);
            using (var device = PocketVNADevice.Open(code))
            {
                if (device != null)
                {
                    PrintInfo(device);
                }
                else
                {
                    Console.Error.WriteLine("Error! Could not open device");
                }
            }
        }

        private static void PrintInfo(PocketVNADevice device)
        {
            Console.WriteLine(device.DeviceProperties.reasonableRange);
            Console.WriteLine((device.DeviceProperties.supportS11 ? "S11" : " X ") + (device.DeviceProperties.supportS12 ? "S12" : " X "));
            Console.WriteLine((device.DeviceProperties.supportS21 ? "S21" : " X ") + (device.DeviceProperties.supportS22 ? "S22" : " X "));
        }

    }
}
