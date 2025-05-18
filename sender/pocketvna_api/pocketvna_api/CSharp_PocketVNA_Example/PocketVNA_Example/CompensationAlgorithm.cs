using pocketvna;
using System;
using System.Collections.Generic;
using System.Diagnostics.Contracts;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;

namespace PocketVNA_Example
{
    class CompensationAlgorithm
    {
        private readonly CompensationCollector.TakenData calibrationData;
        private readonly bool readyFor11;
        private readonly bool readyFor21;
        private readonly bool readyFor12;
        private readonly bool readyFor22;
        private readonly int size;

        public static Complex[,,] Run(CompensationCollector.TakenData data)
        {
            Contract.Assert(data != null, "Should not be null");
            Contract.Assert(!data.rawMeasurements.IsEmpty, "raw measurements expected");            
            Contract.Assert(data.Z0 > 1E-2, "Z0 is to be more than 0.0. It should be 50");
            Contract.Assert(data.frequencies.Length > 0, "frequency should be provided");
            Contract.Assert(data.rawMeasurements.Size == data.frequencies.Length, "raw measurements expected");

            var example = new CompensationAlgorithm(data);

            return example.Run();
        }

        private CompensationAlgorithm(CompensationCollector.TakenData data)
        {
            calibrationData = data;
            size = data.frequencies.Length;

            // check that calibration data for S11 is provided
            this.readyFor11 = data.shortS11 != null && data.openS11 != null && data.loadS11 != null;
            // check that calibration data for S22 is provided
            this.readyFor22 = data.shortS22 != null && data.openS22 != null && data.loadS22 != null;
            //# S21 is linked to S11, so ready for S21 should be ready for S11 too
            this.readyFor21 = data.thruS21  != null && data.openS21 != null && readyFor11;
            //# S12 is linked to S22, so ready for S12 should be ready for S22 too
            this.readyFor12 = data.thruS12  != null && data.openS12 != null && readyFor21;            

            if (readyFor11) Contract.Assert(data.shortS11.Length == size && data.openS11.Length == size && data.loadS11.Length == size);
            if (readyFor22) Contract.Assert(data.shortS22.Length == size && data.openS22.Length == size && data.loadS22.Length == size);
            if (readyFor21) Contract.Assert(data.thruS21.Length == size && data.openS21.Length == size);
            if (readyFor12) Contract.Assert(data.thruS12.Length == size && data.openS12.Length == size);
        }

        private Complex[,,] Run()
        {
            Complex[,,] dut = new Complex[size,2,2];

            for ( int i = 0; i < size; ++i )
            {
                if (readyFor11) {
                    dut[i, 0, 0] = PocketVNADevice.Math.ReflectionCompensation(
                        calibrationData.Z0, calibrationData.rawMeasurements.s11[i],
                        calibrationData.shortS11[i], calibrationData.openS11[i], calibrationData.loadS11[i]
                    );
                }
                if (readyFor21)
                {
                    dut[i, 1, 0] = PocketVNADevice.Math.TransmissionCompensation(
                        calibrationData.rawMeasurements.s21[i],
                        calibrationData.openS21[i], calibrationData.thruS21[i]
                    );
                }
                if (readyFor12)
                {
                    dut[i, 0, 1] = PocketVNADevice.Math.TransmissionCompensation(
                        calibrationData.rawMeasurements.s12[i],
                        calibrationData.openS12[i], calibrationData.thruS12[i]
                    );
                }
                if (readyFor22)
                {
                    dut[i, 1, 1] = PocketVNADevice.Math.ReflectionCompensation(
                        calibrationData.Z0, calibrationData.rawMeasurements.s22[i],
                        calibrationData.shortS22[i], calibrationData.openS22[i], calibrationData.loadS22[i]
                    );
                }
            }

            return dut;
        }
    }
}
