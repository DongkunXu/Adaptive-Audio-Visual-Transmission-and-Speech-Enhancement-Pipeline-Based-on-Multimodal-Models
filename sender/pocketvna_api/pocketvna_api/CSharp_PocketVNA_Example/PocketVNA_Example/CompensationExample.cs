using System;

namespace PocketVNA_Example
{
    class CompensationExample
    {
        public static void RunExample()
        {
            var calibrationData = CompensationCollector.Run();
            var dutMatrices = CompensationAlgorithm.Run(calibrationData);

            Console.WriteLine("Data are calibrated: ");
            for ( int i = 0; i < dutMatrices.GetLength(0); ++i )
            {
                Console.WriteLine(calibrationData.frequencies[i] + "Hz:");
                Console.WriteLine("[ " + dutMatrices[i, 0, 0] + "    " + dutMatrices[i, 0, 1] + "\n" +
                                  "  " + dutMatrices[i, 1, 0] + "    " + dutMatrices[i, 1, 1] + "}");
            }
        }
    }
}
