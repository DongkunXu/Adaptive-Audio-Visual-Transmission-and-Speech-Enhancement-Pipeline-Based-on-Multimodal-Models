using System.Runtime.InteropServices;
using System;
using System.Diagnostics;
using System.Numerics;
using System.Diagnostics.Contracts;

namespace pocketvna
{
    using DeviceHandler = IntPtr;
    using FrequencyValue = UInt64;
    public class PocketVNA
    {
#if (ARCHITECTURE_x64)
        public const string Dll = "PocketVnaApi_x64.dll";
#elif (ARCHITECTURE_x32)
        public const string Dll = "PocketVnaApi_x32.dll";
#else
        public const string Dll = "PocketVnaApi.dll";
#endif

        // API_VERSION_SEARCH_TAG
        public const uint CurrentVersion = 110;

        public enum Result : uint
        {
            Ok = 0x0,
            NoDevice,
            NoMemoryError,
            CanNotInitialize,
            BadDescriptor,

            DeviceLocked,

            NoDevicePath,
            NoAccess,
            FailedToOpen,
            InvalidHandle,
            BadTransmission,
            UnsupportedTransmission,
            BadFrequency,
            DataReadFailure,
            EmptyResponse,
            IncompleteResponse,
            FailedToWriteRequest,
            ArraySizeTooBig,
            BadResponse,

            DeviceResponseSection,

            Response_UNKNOWN_MODE,
            Response_UNKNOWN_PARAMETER,
            Response_NOT_INITIALIZED,
            Response_FREQ_TOO_LOW,
            Response_FREQ_TOO_HIGH,
            Response_OutOfBound,
            Response_UNKNOWN_VARIABLE,
            Response_UNKNOWN_ERROR,
            Response_BAD_FORMAT,

            ExtendedSection,
            ScanCanceled,

            Rfmath_Section,
            No_Data,

            LIBUSB_Error,
            LIBUSB_CanNotSelectInterface,
            LIBUSB_Timeout,
            LIBUSB_Busy,

            VCI_PrepareScanError,
            VCI_Response_Error,
            EndLEQStart,

            PVNA_Res_VCI_Failed2OpenProbablyDriver,
            PVNA_Res_HID_AdditionalError, // Rather a warning

            PVNA_Res_NotImplemented,
            PVNA_Res_BadArgument,

            Incorrect =0xFFFF
        };

        public enum AccessEnum : uint
        {
            PVNA_Denied      = 0x00,
            PVNA_ReadAccess  = 0x01,
            PVNA_WriteAccess = 0x02,
            PVNA_Granted     = 0x01 | 0x02,
            PVNA_Busy        = 0x10
        };

        public enum Transmission : uint
        {
            None = 0x00,

            S21 = 0x0001,
            S11 = 0x0002,
            S12 = 0x0004,
            S22 = 0x0008,

            S13 = 0x0010,
            S14 = 0x0040,
            S23 = 0x0020,
            S24 = 0x0080,

            S31 = 0x0100,
            S32 = 0x0400,
            S41 = 0x0200,
            S42 = 0x0800,

            S33 = 0x1000,
            S34 = 0x4000,
            S43 = 0x2000,
            S44 = 0x8000,
        };

        public enum Progress : uint
        {
            Cancel = 0, 
            Continue = 1
        }
        public enum ConnectionInterfaceCode : uint
        {
            /// <summary>
            /// @CIface_HID: must work by default. Does not require drivers
            /// </summary>
            CIface_HID = 0x10,
            /// <summary>
            /// @CIface_VCI: on windows requires installation special USB driver
            /// </summary>
            CIface_VCI = 0x20,
        }

        public class PocketVNAException : Exception
        {
            private readonly Result code;

            public PocketVNAException(string message, Result code) : 
                base(message + ": " + Result2String(code) +  " (" + code.ToString() + ") ")
            {
                this.code = code;
            }

            public Result Code()
            {
                return code;
            }
        }

        public class DeviceIsAlreadyUsed : PocketVNAException
        {
            public DeviceIsAlreadyUsed(string message, Result code):
                base(message, code)
            { }
        }
        public class DeviceGone : Exception
        {
            public DeviceGone():base("device is disconnected (or handler is corrupted)") { }
        }

        public class ScanCanceled : Exception
        {
            public ScanCanceled():base("scan is canceled manually") { }
        }

        public class Handler
        {
            internal DeviceHandler handler;

            public Handler(DeviceHandler h)
            {
                handler = h;
            }

            public Handler()
            {
                handler = DeviceHandler.Zero;
            }


            public DeviceHandler Address
            {
                get { return handler; }
            }

            public bool IsZero()
            {
                return handler == DeviceHandler.Zero;
            }
        }

        [StructLayout(LayoutKind.Sequential, Pack = 0, CharSet = CharSet.Ansi)]
        public readonly struct DeviceDesc
        {
            [MarshalAs(UnmanagedType.LPStr)] //const char * path;
            public readonly string Path;

            public readonly AccessEnum access;

            [MarshalAs(UnmanagedType.LPWStr)] //const wchar_t * serial_number;
            public readonly string SerialNumber;

            [MarshalAs(UnmanagedType.LPWStr)]  //const wchar_t * manufacturer_string;
            public readonly string Manufacturer;

            [MarshalAs(UnmanagedType.LPWStr)]
            public readonly string Product;  //const wchar_t * product_string;

            public readonly UInt16 ReleaseNumber;
            public readonly UInt16 PID;
            public readonly UInt16 VID;
            readonly UInt16 connectionInterfaceCode; // represents interface
            public readonly IntPtr next; //PocketVnaDeviceDesc *

            public ConnectionInterfaceCode ConnectionInterface
            {
                get
                {
                    if ( connectionInterfaceCode != (uint)ConnectionInterfaceCode.CIface_HID && 
                        connectionInterfaceCode != (uint)ConnectionInterfaceCode.CIface_VCI )
                    {
                        throw new Exception("Unknown value of connectionInterfaceCode field: " + connectionInterfaceCode);
                    }
                    return (ConnectionInterfaceCode)connectionInterfaceCode;
                }
            }

            internal DeviceDesc(string path, string sn, string manufacturer, string product,
                ushort releaseNum, ushort pid, ushort vid, ConnectionInterfaceCode ifaceCode ) {
                Path = path;
                access = AccessEnum.PVNA_Granted;
                SerialNumber = sn;
                Manufacturer = manufacturer;
                Product = product;
                ReleaseNumber = releaseNum;
                PID = pid;
                VID = vid;
                connectionInterfaceCode = (ushort)ifaceCode;
                next = IntPtr.Zero;
            }
        }

        [StructLayout(LayoutKind.Sequential, Pack = 0)]
        public struct ComplexS
        {
            public double real;
            public double imag;

            public ComplexS(Complex c)
            {
                real = c.Real;
                imag = c.Imaginary;
            }

            public Complex ToComplex()
            {
                return new Complex(real, imag);
            }
        }

        public static Tuple<int,int> Index4(Transmission t)
        {
            switch (t)
            {
                case Transmission.S11: return Tuple.Create(0,0);
                case Transmission.S12: return Tuple.Create(0,1);
                case Transmission.S13: return Tuple.Create(0,2);
                case Transmission.S14: return Tuple.Create(0,3);
                case Transmission.S21: return Tuple.Create(1,0);
                case Transmission.S22: return Tuple.Create(1,1);
                case Transmission.S23: return Tuple.Create(1,2);
                case Transmission.S24: return Tuple.Create(1,3);
                case Transmission.S31: return Tuple.Create(2,0);
                case Transmission.S32: return Tuple.Create(2,1);
                case Transmission.S33: return Tuple.Create(2,2);
                case Transmission.S34: return Tuple.Create(2,3);
                case Transmission.S41: return Tuple.Create(3,0);
                case Transmission.S42: return Tuple.Create(3,1);
                case Transmission.S43: return Tuple.Create(3,2);
                case Transmission.S44: return Tuple.Create(3,3);
                
                default:
                    throw new Exception("Unexpected Transmission #" + t);
            }
        }

        public struct SNetwork
        {
            public FrequencyValue[] frequencies;
            public Complex[] s11, s12,
                             s21, s22;
            public double z0;           

            public SNetwork(FrequencyValue[] freqs, 
                Complex[] s11, Complex[] s21, 
                Complex[] s12, Complex[] s22, 
                double z0)
            {
                Contract.Assert(freqs.Length == s11.Length &&
                    freqs.Length == s21.Length &&
                    freqs.Length == s12.Length &&
                    freqs.Length == s22.Length
                    );
                Contract.Assert(z0 > 0);

                this.frequencies = freqs;
                this.s11 = s11;
                this.s21 = s21;
                this.s12 = s12;
                this.s22 = s22;
                this.z0 = z0;
            }

            public int Size
            {
                get
                {
                    Debug.Assert(s11.Length == s21.Length);
                    Debug.Assert(s11.Length == s12.Length);
                    Debug.Assert(s11.Length == s22.Length);
                    return s11.Length;
                }
            }

            public bool IsEmpty
            {
                get { return Size < 1; }
            }

            public Complex[] Get(Transmission m)
            {
                switch( m )
                {
                    case Transmission.S11:
                        return s11;
                    case Transmission.S21:
                        return s21;
                    case Transmission.S12:
                        return s12;
                    case Transmission.S22:
                        return s22;
                    default:
                        throw new Exception("Unexpected Transmission #" + m);
                }
            }
        }

        public struct SNetwork4Port
        {
            public FrequencyValue[] frequencies;
            public Complex[,][] parameters;
            public double z0;

            public SNetwork4Port(FrequencyValue[] frequencies,
                Complex[,][] parameters,
                double z0)
            {
                Contract.Assert(frequencies.Length == parameters[0,0].Length );
                Contract.Assert(z0 > 0);

                this.frequencies = frequencies;
                this.parameters  = parameters;
                this.z0 = z0;
            }

            public int Size
            {
                get
                {
                    Debug.Assert(parameters[1, 1].Length == parameters[0, 1].Length);
                    return frequencies.Length;
                }
            }

            public bool IsEmpty
            {
                get { return Size < 1; }
            }

            public Complex[] Get(Transmission t)
            {
                var indeces = Index4(t);
                return parameters[indeces.Item1, indeces.Item2];
            }
        }

        public class FrequencyRange
        {
            public readonly FrequencyValue from;
            public readonly FrequencyValue to;
            public FrequencyRange(FrequencyValue from, FrequencyValue to)
            {
                this.from = from;
                this.to = to;
            }

            public override string ToString()
            {
                return "[" + from + "Hz; " + to + "Hz]";
            }
        }

        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        public delegate Progress ProgressCallbackProc(IntPtr userData, UInt32 index);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_driver_version")]
        public static extern Result driver_version(ref ushort version, ref double info);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_close")]
        public static extern Result close();

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_result_string")]
        private static extern IntPtr result_string(Result code);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_list_devices")]
        private static extern Result list_devices(
            ref IntPtr list, // Unfortunately, it is very hard to Marshal automatically "DeviceDesc ** list" in 64bit-mingw, so it should be made 'by hand'
            ref UInt16 size);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_free_list")]
        private static extern Result free_list(ref IntPtr list);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_get_device_handle_for")]
        private static extern Result get_device_handle_for(ref DeviceDesc desc, out DeviceHandler handle);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_release_handle")]
        private static extern Result release_handle(ref DeviceHandler handle);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_is_transmission_supported")]
        private static extern Result is_transmission_supported(DeviceHandler handle, Transmission param);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_is_valid")]
        private static extern Result is_valid(DeviceHandler handle);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_version")]
        private static extern Result pocketvna_version(DeviceHandler handle, out ushort version);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_get_characteristic_impedance")]
        private static extern Result characteristic_impedance(DeviceHandler handle, out double z0);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_get_valid_frequency_range")]
        private static extern Result valid_frequency_range(DeviceHandler handle, out FrequencyValue from, out FrequencyValue to);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_get_reasonable_frequency_range")]
        private static extern Result reasonable_frequency_range(DeviceHandler handle, out FrequencyValue from, out FrequencyValue to);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_multi_query")]
        private static extern Result multi_query(DeviceHandler handle, FrequencyValue[] frequencies, uint size,
                                        ushort average, uint transmissionModes,
                                        [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s11a,
                                        [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s21a,
                                        [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s12a,
                                        [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s22a,
                                        IntPtr callbackProc);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_multi_query_with_cproc")]
        private static extern Result multi_query_with_callback(DeviceHandler handle, FrequencyValue[] frequencies, uint size,
                                       ushort average, uint transmissionModes,
                                       [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s11a,
                                       [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s21a,
                                       [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s12a,
                                       [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
                                        ComplexS[] s22a,
                                       ProgressCallbackProc callbackProc);



        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_debug_response")]
        private static extern Result debug_response(DeviceHandler handle, uint size,
                                                   ref ComplexS[] p1, ref ComplexS[] p2);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_rfmath_calibrate_transmission")]
        private static extern Result rfmath_calibrate_transmission(
             [In, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] raw_meas_mn,
             [In, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] open_thru_mn,
             [In, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] thru_mn,
             uint size,
             [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] dut_mn);

        [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_rfmath_calibrate_reflection")]
        private static extern Result rfmath_calibrate_reflection(
            [In, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] raw_meas_mm,
            [In, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[]  short_mm,
            [In, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] open_mm,
            [In, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] load_mm,
            uint size,
            double Z0,
            [Out, MarshalAsAttribute(UnmanagedType.LPArray)]
             ComplexS[] dut_mm);

         [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, EntryPoint = "pocketvna_4p_scan_separate")]
         private static extern Result scan_4port(
            DeviceHandler handle, FrequencyValue[] frequencies, uint size,
            ushort average, uint transmissionModes,
            /// ---------------
                   /// P11-4
            [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s11, [Out, MarshalAsAttribute(UnmanagedType.LPArray)]  ComplexS[] s12,
                    [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s13, [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s14,
                   /// P21-4
            [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s21, [Out, MarshalAsAttribute(UnmanagedType.LPArray)]  ComplexS[] s22,
                    [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s23, [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s24,
                   /// P31-4
            [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s31, [Out, MarshalAsAttribute(UnmanagedType.LPArray)]  ComplexS[] s32,
                    [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s33, [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s34,
                   /// P41-4
            [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s41, [Out, MarshalAsAttribute(UnmanagedType.LPArray)]  ComplexS[] s42,
                    [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s43, [Out, MarshalAsAttribute(UnmanagedType.LPArray)] ComplexS[] s44,

            /// ---------------
           ProgressCallbackProc callbackProc
         );

        private static ComplexS[,][] GenerateMatrix(int size, ushort portcount)
        {
            ComplexS[,][] result = new ComplexS[portcount, portcount][];

            for (int p1 = 0; p1 < 4; ++p1)
            {
                for (int p2 = 0; p2 < 4; ++p2)
                {
                    result[p1, p2] = new ComplexS[size];
                }
            }

            return result;
        }

        private static ComplexS[,][] Scan4Port(Handler handle, FrequencyValue[] frequencies, ushort average, uint transmissionModes, ProgressCallbackProc callbackProc)
        {
            ComplexS[,][] result = GenerateMatrix(frequencies.Length, 4);

            var res = scan_4port(handle.handler, frequencies, (uint)frequencies.Length,
                average, transmissionModes,
                result[0, 0], result[0, 1], result[0, 2], result[0, 3],
                result[1, 0], result[1, 1], result[1, 2], result[1, 3],
                result[2, 0], result[2, 1], result[2, 2], result[2, 3],
                result[3, 0], result[3, 1], result[3, 2], result[3, 3],
                callbackProc
                );

            if (res == Result.Ok)
            {
                return result;
            }

            throw new PocketVNAException("Failed to open device", res);
        }

        public static SNetwork4Port Scan4Port(Handler handle, FrequencyValue[] frequencies, ushort average, Transmission[] transmissionModes, ProgressCallbackProc callbackProc)
        {
            var flags = ConvertToFlags(transmissionModes);

            var res = Scan4Port(handle, frequencies, average, flags, callbackProc);
            double z0 = CharacteristicImpedance(handle);

            return new SNetwork4Port(frequencies, Convert(res), z0);
        }

        public static string Result2String(Result res)
        {
            IntPtr constChartPtr = result_string(res);
            Debug.Assert(constChartPtr != IntPtr.Zero, "Function should not return null-pointer");
            return Marshal.PtrToStringAnsi(constChartPtr);
        }

        public static DeviceDesc[] ListDevices()
        {
            DeviceDesc[] mangagedArray;

            IntPtr arrayPointer = IntPtr.Zero; // = new PocketVNA.PocketVNA.PocketVnaDeviceDesc[10];
            ushort size = 0;

            var res = list_devices(ref arrayPointer, ref size);

            if (Result.NoDevice == res) return new DeviceDesc[0];

            if (Result.Ok != res)
            {
                throw new PocketVNAException("Failed list device", res);
            }

            if (arrayPointer == IntPtr.Zero) return new DeviceDesc[0];

            mangagedArray = new DeviceDesc[size];

            IntPtr ins = new IntPtr(arrayPointer.ToInt64());
            for (uint index = 0; index < size; ++index)
            {                
                mangagedArray[index] = Marshal.PtrToStructure<DeviceDesc>(ins);
                ins = mangagedArray[index].next;
            }

            res = free_list(ref arrayPointer);

            Debug.Assert(arrayPointer == IntPtr.Zero, "It should zero pointer");
            Debug.Assert(res == Result.Ok, "Should always return OK");

            return mangagedArray;
        }

        public static Handler Open(DeviceDesc desc)
        {
            DeviceHandler handle = DeviceHandler.Zero;
            var res = get_device_handle_for(ref desc, out handle);

            if (res == Result.FailedToOpen) return new Handler(DeviceHandler.Zero);
            if (res == Result.Ok)
            {
                Debug.Assert(handle != DeviceHandler.Zero, "Can not be equal to zero");
                return new Handler(handle);
            }

            if (res == Result.BadDescriptor) throw new PocketVNAException("Bad Device Description", res);
            if (res == Result.NoAccess) throw new PocketVNAException("Access denied", res);
            if (res == Result.DeviceLocked) throw new DeviceIsAlreadyUsed("Device is used by another program", res);

            throw new PocketVNAException("Failed to open device", res);
        }

        public static DeviceDesc SimulatorDescriptor()
        {
            return new DeviceDesc(
                "simulation", "SIMULATOR", "martin", "pocketvna",
                0x100, 0x100, 0x100, ConnectionInterfaceCode.CIface_HID);
        }

        public static Handler OpenSimulator()
        {
            return Open(SimulatorDescriptor());
        }

        public static void Close(ref Handler handler)
        {
            if (handler.IsZero()) return;

            var res = release_handle(ref handler.handler);

            Debug.Assert(handler.IsZero(), "release_handler should zero handler");
            Debug.Assert(res == Result.Ok, "Should be OK");
        }

        public static bool IsSupported(Handler handle, Transmission param)
        {
            var res = is_transmission_supported(handle.Address, param);

            if (Result.InvalidHandle == res) throw new DeviceGone();

            if (Result.Ok == res) return true;
            if (Result.UnsupportedTransmission == res) return false;

            throw new PocketVNAException("Failed to querry supported mode", res);
        }

        public static bool IsValid(Handler handle)
        {
            if (handle.IsZero()) return false;

            var res = is_valid(handle.Address);

            Debug.Assert(res == Result.Ok || res == Result.InvalidHandle, "Only 2 values can be returned");

            return res == Result.Ok;
        }

        public static ushort Version(Handler handle)
        {
            ushort version = 0;
            var res = pocketvna_version(handle.Address, out version);

            if (res == Result.InvalidHandle) throw new DeviceGone();

            Debug.Assert(res == Result.Ok);

            return version;
        }

        public static double CharacteristicImpedance(Handler handle)
        {
            double z0 = 0.0;
            var res = characteristic_impedance(handle.Address, out z0);

            if (res == Result.InvalidHandle) throw new DeviceGone();

            Debug.Assert(res == Result.Ok);

            return z0;
        }

        public static FrequencyRange ValidFrequencyRange(Handler handle)
        {
            FrequencyValue from = 0, to = 0;
            var res = valid_frequency_range(handle.Address, out from, out to);

            if (res == Result.InvalidHandle) throw new DeviceGone();

            Debug.Assert(res == Result.Ok);

            return new FrequencyRange(from, to);
        }

        public static FrequencyRange ReasonableFrequencyRange(Handler handle)
        {
            FrequencyValue from = 0, to = 0;
            var res = reasonable_frequency_range(handle.Address, out from, out to);

            if (res == Result.InvalidHandle) throw new DeviceGone();

            Debug.Assert(res == Result.Ok);

            return new FrequencyRange(from, to);
        }

        public delegate Progress ProgressCallback(int totalSize, int currentIndex);

        private static uint ConvertToFlags(Transmission[] modes)
        {
            Contract.Assert(modes != null, "modes should not be null");
            Contract.Assert(modes.Length > 0, "modes should not be empty");

            uint flags = (uint)Transmission.None;
            foreach (Transmission t in modes)
            {
                flags |= (uint)t;
            }

            Contract.Assert(flags != (uint)Transmission.None);
            return flags;
        }

        public static SNetwork Scan(Handler handle, FrequencyValue[] frequencies,
            ushort average, Transmission[] modes, ProgressCallback progress)
        {
            Contract.Assert(modes != null, "modes should not be null");
            Contract.Assert(frequencies.Length > 0, "no reason to call scan for empty frequencies");

            uint m = ConvertToFlags(modes);

            ComplexS[] s11 = new ComplexS[frequencies.Length], s21 = new ComplexS[frequencies.Length],
                       s12 = new ComplexS[frequencies.Length], s22 = new ComplexS[frequencies.Length];

            ProgressCallbackProc proc = null;
            if (progress != null)
            {
                proc = (userPtr, curIndex) => progress(frequencies.Length, (int)curIndex);
            }

            double z0 = CharacteristicImpedance(handle);

            var res = multi_query_with_callback(handle.Address,
                frequencies, (uint)frequencies.Length,
                average, m,
                s11, s21,
                s12, s22,
                proc
            );
            if (res == Result.InvalidHandle) throw new DeviceGone();
            if (res == Result.ScanCanceled) throw new ScanCanceled();

            if (res != Result.Ok) throw new PocketVNAException("Failed scan", res);

            return new SNetwork(frequencies,
                Convert(s11), 
                Convert(s21), 
                Convert(s12), 
                Convert(s22), z0
            );
        }

        private static Complex[] Convert(ComplexS[] ca)
        {
            var res = new Complex[ca.Length];
            for ( int i = 0; i < ca.Length; ++i )
            {
                res[i] = ca[i].ToComplex();
            }

            return res;
        }

        private static Complex[,][] Convert(ComplexS[,][] scanmatrix)
        {
            Contract.Assert(scanmatrix.GetLength(0) == scanmatrix.GetLength(1), "It should be square matrix");
            Contract.Assert(scanmatrix.GetLength(0) > 0 && scanmatrix.GetLength(0) <= 4, "It should be 1x1 to 4x4 matrix");

            int portcount = scanmatrix.GetLength(0);
            Complex[,][] result = new Complex[portcount, portcount][];
            for ( int p1 = 0; p1 < portcount; ++p1)
            {
                for ( int p2 = 0; p2 < portcount; ++p2 )
                {
                    result[p1, p2] = Convert(scanmatrix[p1, p2]);
                }
            }
            return result;
        }

        private static ComplexS[] Convert(Complex[] ca)
        {
            var res = new ComplexS[ca.Length];
            for (int i = 0; i < ca.Length; ++i)
            {
                res[i] = new ComplexS(ca[i]);
            }

            return res;
        }

        public static Complex[] CalibrateReflection(Complex[] rawMeasSmm,
            Complex[] shortSmm, Complex[] openSmm, Complex[] loadSmm, double z0)
        {
            Contract.Assert(
                rawMeasSmm.Length == shortSmm.Length &&
                rawMeasSmm.Length == openSmm.Length &&
                rawMeasSmm.Length == loadSmm.Length,
                "All parameters should be of the same size"
                );
            Contract.Assert(z0 > 0.0, "Z0 should be given");

            var meas = Convert(rawMeasSmm);
            var shrt = Convert(shortSmm);
            var open = Convert(openSmm);
            var load = Convert(loadSmm);

            var dut = new ComplexS[rawMeasSmm.Length];

            var r = rfmath_calibrate_reflection(meas, shrt, open, load, (uint)meas.Length, z0, dut);
            Debug.Assert(r == Result.Ok || r == Result.No_Data);

            return Convert(dut);
        }

        public static Complex[] CalibrateTransmission(Complex[] rawMeasSmn,
            Complex[] openSmn, Complex[] thruSmn)
        {
            Contract.Assert(
                rawMeasSmn.Length == openSmn.Length &&
                rawMeasSmn.Length == thruSmn.Length, 
                "All parameters should be of the same size"
                );

            var meas = Convert(rawMeasSmn);
            var open = Convert(openSmn);
            var thru = Convert(thruSmn);

            var dut = new ComplexS[rawMeasSmn.Length];

            var r = rfmath_calibrate_transmission(meas, open, thru, (uint)meas.Length, dut);
            Debug.Assert(r == Result.Ok || r == Result.No_Data);

            return Convert(dut);
        }

        private static bool Equals(double exp, double res)
        {
            return Math.Abs(exp - res) <= 1E-8;
        }

        public static SNetwork CalibrateFullNetwork(SNetwork meas, 
            SNetwork shorts, SNetwork opens, SNetwork loads, 
            SNetwork openThrus, SNetwork thruThrus)
        {
           Contract.Assert(meas.frequencies == shorts.frequencies &&
               meas.frequencies == opens.frequencies &&
               meas.frequencies == loads.frequencies &&
               meas.frequencies == openThrus.frequencies &&
               meas.frequencies == thruThrus.frequencies);

            Contract.Assert(Equals(meas.z0, shorts.z0) &&
                   Equals(meas.z0, opens.z0) &&
                   Equals(meas.z0, loads.z0) &&
                   Equals(meas.z0, openThrus.z0) &&
                   Equals(meas.z0, thruThrus.z0));

            return new SNetwork(
                meas.frequencies,
                CalibrateReflection(meas.s11, shorts.s11, opens.s11, loads.s11, meas.z0),
                CalibrateTransmission(meas.s21, openThrus.s21, thruThrus.s21),
                CalibrateTransmission(meas.s12, openThrus.s12, thruThrus.s12),
                CalibrateReflection(meas.s22, shorts.s22, opens.s22, loads.s22, meas.z0),
               meas.z0);
        }
    }
}
