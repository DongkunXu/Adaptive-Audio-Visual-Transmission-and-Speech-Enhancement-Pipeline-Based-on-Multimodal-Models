using System;
using System.IO;
using System.Linq;
using System.Numerics;
using pocketvna;
using System.Diagnostics;

namespace Example_CollectFullCalibrationData
{
    public class CalibrationDump
    {
        private const string TAG_START= "START";        
        private const string TAG_DataSection = "Data";
        private const string TAG_END = "END";

        internal static void Save(string filename, CalibrationDataSet calibration)
        {
            using (FileStream stream = new FileStream(filename, FileMode.Create))
            {
                using (BinaryWriter writer = new BinaryWriter(stream))
                {
                    WriteCalibration(writer, calibration);                    
                }
            }
        }

        private static void WriteCalibration(BinaryWriter writer, CalibrationDataSet calibration)
        {
            writer.Write(TAG_START);
            writer.Write(calibration.Z0);
            Write(writer, calibration.modes);
            Write(writer, calibration.frequencies);

            writer.Write(TAG_DataSection);

            Write(writer, calibration.shortS11);
            Write(writer, calibration.openS11);
            Write(writer, calibration.loadS11);

            Write(writer, calibration.shortS22);
            Write(writer, calibration.openS22);
            Write(writer, calibration.loadS22);

            Write(writer, calibration.openS21);
            Write(writer, calibration.thruS21);

            Write(writer, calibration.openS12);
            Write(writer, calibration.thruS12);

            writer.Write(TAG_END);
        }

        public static CalibrationDataSet Load(string filename)
        {
            using (FileStream stream = new FileStream(filename, FileMode.Open))
            {
                using (BinaryReader reader = new BinaryReader(stream))
                {
                    return ReadCalibration(reader);                    
                }
            }
        }

        private static CalibrationDataSet ReadCalibration(BinaryReader reader)
        {
            CalibrationDataSet calibration = new CalibrationDataSet();

            var tag = reader.ReadString();
            Debug.Assert(tag == TAG_START);

            calibration.Z0 = reader.ReadDouble();
            calibration.modes = ReadTransmissions(reader);
            calibration.frequencies = ReadFrequencies(reader);

            tag = reader.ReadString();
            Debug.Assert(tag == TAG_DataSection);

            calibration.shortS11 = ReadComplex(reader);
            calibration.openS11 = ReadComplex(reader);
            calibration.loadS11 = ReadComplex(reader);

            calibration.shortS22 = ReadComplex(reader);
            calibration.openS22 = ReadComplex(reader);
            calibration.loadS22 = ReadComplex(reader);

            calibration.openS21 = ReadComplex(reader);
            calibration.thruS21 = ReadComplex(reader);

            calibration.openS12 = ReadComplex(reader);
            calibration.thruS12 = ReadComplex(reader);

            tag = reader.ReadString();
            Debug.Assert(tag == TAG_END);

            return calibration;
        }

        private static ulong[] ReadFrequencies(BinaryReader reader)
        {
            int size = reader.ReadInt32();
            ulong[] frequences = new ulong[size];
            for (int i = 0; i < size; ++i)
            {
                frequences[i] = reader.ReadUInt64();
            }
            return frequences;
        }

        private static Complex[] ReadComplex(BinaryReader reader)
        {
            int size = reader.ReadInt32();
            Complex[] snn = new Complex[size];
            for (int i = 0; i < size; ++i)
            {
                double real = reader.ReadDouble();
                double imag = reader.ReadDouble();

                snn[i] =  new Complex(real, imag);
            }
            return snn;
        }

        private static void Write(BinaryWriter writer, Complex[] snn)
        {
            writer.Write(snn.Length);
            foreach ( var c in snn )
            {
                writer.Write(c.Real);
                writer.Write(c.Imaginary);
            }
        }

        private static void Write(BinaryWriter writer, ulong[] frequencies)
        {
            writer.Write(frequencies.Length);
            foreach( ulong f in frequencies )
            {
                writer.Write(f);
            }
        }

        private static void Write(BinaryWriter writer, PocketVNA.Transmission[] modes)
        {
            writer.Write( string.Join("/", modes.Select(mode => mode.ToString())) );
        }

        private static PocketVNA.Transmission[] ReadTransmissions(BinaryReader reader)
        {
            var modesStr = reader.ReadString();

            var strs = modesStr.Split(new string[] { "/" }, StringSplitOptions.RemoveEmptyEntries);
            var foo = strs.Select(s => (PocketVNA.Transmission)Enum.Parse(typeof(PocketVNA.Transmission), s));

            return foo.ToArray();
        }
    }
}
