using System;
using System.Numerics;

namespace Example_TakeMeasurementsAndPlot
{
    internal class Conversions
    {
        public delegate double FormatFunction(Complex s);

        public static double Magnitude(Complex c)
        {
            return c.Magnitude;
        }

        public static double dBels(Complex c)
        {
            return 20.0 * Math.Log10(Magnitude(c));
        }

        public static double Phase(Complex c)
        {
            return c.Phase * 180.0 / Math.PI;
        }
    }
}
