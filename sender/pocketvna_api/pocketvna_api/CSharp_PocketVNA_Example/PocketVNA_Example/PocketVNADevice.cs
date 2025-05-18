using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics.Contracts;
using System.Numerics;

namespace pocketvna
{
    public sealed class PocketVNADevice : IDisposable
    {
        public static class Math
        {
            public static Complex Gamma2Z(Complex gamma, double z0)
            {
                return z0 * (1 + gamma) / (1 - gamma);
            }

            public static Complex Z2Gamma(Complex z, double z0)
            {
                return (z - z0) / (z + z0);
            }

            // formula for compensation for Reflection (11/22) compensation. 
            private static Complex ReflectionCompensationFormula(Complex Zstd, Complex Zo, Complex Zsm, Complex Zs, Complex Zxm) {
                return (Zstd * (Zo - Zsm) * (Zxm - Zs)) / ((Zsm - Zs) * (Zo - Zxm));
            }

            // formula for compensation for S21/S12 (transmission)
            private static Complex TransmissionCompensationFormula(Complex Sxm, Complex So, Complex Sthru)
            {
                return (Sxm - So) / (Sthru - So);
            }

            public static Complex ReflectionCompensation(double Z0, Complex RawSnn, Complex ShortSnn, Complex OpenSnn, Complex LoadSnn) {
                Complex zstd = Z0;
                var zo = Gamma2Z(OpenSnn, Z0);
                var zsm = Gamma2Z(LoadSnn, Z0);
                var zs = Gamma2Z(ShortSnn, Z0);
                var zxm = Gamma2Z(RawSnn, Z0);

                var zdut = ReflectionCompensationFormula(zstd, zo, zsm, zs, zxm);

                return Z2Gamma(zdut, Z0);
            }

            // applying formula using calibration data + raw data
            public static Complex TransmissionCompensation(Complex RawSnm, Complex  OpenSnm, Complex ThruSnm) {
                return TransmissionCompensationFormula(RawSnm, OpenSnm, ThruSnm);
            }
        }

        public static bool IsAnyDeviceConnected()
        {
            var devices = PocketVNA.ListDevices();

            return devices.Length > 0;
        }

        public static PocketVNADevice Open(PocketVNA.ConnectionInterfaceCode interfaceCode)
        {
            var devices = PocketVNA.ListDevices();
            if (devices.Length < 1) return null;            

            // Find first by interfaceCode
            for ( uint i = 0; i < devices.Length; ++i )
            {
                if ( devices[i].ConnectionInterface == interfaceCode )
                {
                    return Open(devices[i]);
                }
            }

            return null;
        }

        public static PocketVNADevice Open(PocketVNA.DeviceDesc descriptor)
        {
            var handler = PocketVNA.Open(descriptor);

            if (handler.IsZero()) return null;


            var props = new Properties(
               PocketVNA.CharacteristicImpedance(handler),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S11),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S21),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S12),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S22),
               PocketVNA.ValidFrequencyRange(handler),
               PocketVNA.ReasonableFrequencyRange(handler)
           );

            return new PocketVNADevice(descriptor, handler, props);
        }

        public static PocketVNADevice OpenSimulator()
        {
            var handler = PocketVNA.OpenSimulator();

            if (handler.IsZero()) return null;


            var props = new Properties(
               PocketVNA.CharacteristicImpedance(handler),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S11),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S21),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S12),
               PocketVNA.IsSupported(handler, PocketVNA.Transmission.S22),
               PocketVNA.ValidFrequencyRange(handler),
               PocketVNA.ReasonableFrequencyRange(handler)
           );

            return new PocketVNADevice(PocketVNA.SimulatorDescriptor(), handler, props);
        }

        /// <summary>
        /// Opens first-most available connection. Be careful that it may be VCI interface which requires some special driver
        /// </summary>
        /// <returns></returns>
        public static PocketVNADevice Open()
        {
            var devices = PocketVNA.ListDevices();

            if (devices.Length < 1) return null;

            var descriptor = devices[0];

            return Open(descriptor);
        }

        public class Properties
        {
            public readonly double Z0;
            public readonly bool supportS11, supportS21, supportS12, supportS22;
            public readonly PocketVNA.FrequencyRange validRange;
            public readonly PocketVNA.FrequencyRange reasonableRange;

            internal Properties(double z0, bool has11, bool has21, bool has12, bool has22, 
                PocketVNA.FrequencyRange validrange, PocketVNA.FrequencyRange reasonablerange)
            {
                Z0 = z0;
                supportS11 = has11;
                supportS21 = has21;
                supportS12 = has12;
                supportS22 = has22;
                validRange = validrange;
                reasonableRange = reasonablerange;
            }
        }

        private PocketVNA.DeviceDesc descriptor;
        private PocketVNA.Handler handler;
        private Properties properties;

        private PocketVNADevice(PocketVNA.DeviceDesc desc, PocketVNA.Handler h, Properties props)
        {
            descriptor = desc;
            handler = h;
            properties = props;
        }

        ~PocketVNADevice()
        {
            PocketVNA.Close(ref handler);
        }

        public void Dispose()
        {
            PocketVNA.Close(ref handler);
            GC.SuppressFinalize(this);
        }

        public PocketVNA.SNetwork Scan(ulong[] frequencies, ushort firmwareAverage, PocketVNA.ProgressCallback onProgress,  params PocketVNA.Transmission[] modes)
        {
            Contract.Assert(modes.Length > 0, "at least one Transmission mode should be passed");
            try {
                ///> Pay attention: if some Network Parameter is not set explicitly it will be 0
                return PocketVNA.Scan(handler, frequencies, firmwareAverage, modes, onProgress);
            }
            catch ( PocketVNA.DeviceGone )
            {
                InvalidateDevice();
                throw;
            }
        }

        public PocketVNA.SNetwork Scan(ulong[] frequencies, ushort firmwareAverage, params PocketVNA.Transmission[] modes)
        {
            Contract.Assert(modes.Length > 0, "at least one Transmission mode should be passed");
            try
            {
                ///> Pay attention: if some Network Parameter is not set explicitly it will be 0
                return PocketVNA.Scan(handler, frequencies, firmwareAverage, modes, null);
            }
            catch (PocketVNA.DeviceGone)
            {
                InvalidateDevice();
                throw;
            }
        }

        public PocketVNA.SNetwork4Port Scan4Port(ulong[] frequencies, ushort firmwareAverage, PocketVNA.Transmission[] modes, PocketVNA.ProgressCallback onProgress = null)
        {
            Contract.Assert(modes.Length > 0, "at least one Transmission mode should be passed");
            try
            {
                ///> Pay attention: if some Network Parameter is not set explicitly it will be 0
                return PocketVNA.Scan4Port(handler, frequencies, firmwareAverage, modes, null);
            }
            catch (PocketVNA.DeviceGone)
            {
                InvalidateDevice();
                throw;
            }
        }

        public bool IsSupported(PocketVNA.Transmission t)
        {
            return PocketVNA.IsSupported(handler, t);
        }

        public PocketVNA.SNetwork ScanAllSupportedModes(ulong[] frequencies, ushort firmwareAverage, PocketVNA.ProgressCallback onProgress = null)
        {
            return Scan(frequencies, firmwareAverage, onProgress, SupportedModes);
        }

        public bool IsValid()
        {
            bool valid = PocketVNA.IsValid(handler);
            if (!valid) InvalidateDevice();
            return valid;
        }

        public Properties DeviceProperties
        {
            get { return properties; }

        }

        public double Z0
        {
            get { return properties.Z0; }
        }

        public PocketVNA.Transmission[] SupportedModes
        {
            get
            {
                var transmissions = new List<PocketVNA.Transmission>();
                if (DeviceProperties.supportS11) transmissions.Add(PocketVNA.Transmission.S11);
                if (DeviceProperties.supportS21) transmissions.Add(PocketVNA.Transmission.S21);
                if (DeviceProperties.supportS12) transmissions.Add(PocketVNA.Transmission.S12);
                if (DeviceProperties.supportS22) transmissions.Add(PocketVNA.Transmission.S22);

                return transmissions.ToArray();
            }
        }

        private void InvalidateDevice()
        {
            handler = new PocketVNA.Handler();
        }
    }
}
