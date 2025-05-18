using System;
using System.Diagnostics;
using System.Diagnostics.Contracts;
using System.Numerics;
using System.Collections.Generic;
using System.Linq;

namespace PocketVNA_Example
{
    public class Utils
    {
        public static bool IsZero(Complex complex)
        {
            const double eps = 1E-13;
            return AreEqual(complex, Complex.Zero, eps );
        }

        public static bool AreEqual(Complex[] exp, Complex[] real)
        {
            if (exp.Length != real.Length) return false;
            for (int i = 0; i < exp.Length; ++i)
            {
                if (!AreEqual(exp[i], real[i])) return false;
            }
            return true;
        }

        public static bool AreEqual(Complex exp, Complex real, double eps = 1E-13)
        {
            return AreEqual(exp.Real, real.Real, eps) && AreEqual(exp.Imaginary, real.Imaginary, eps);
        }

        public static bool AreEqual(double exp, double real, double eps = 1E-13)
        {
            return Math.Abs(exp - real) < eps;
        }

        public static bool Equals(double exp, double res, double eps = 1E-8)
        {
            return Math.Abs(exp - res) <= eps;
        }
        public static bool Equals(Complex exp, Complex res)
        {
            return Equals(exp.Real, res.Real) && Equals(exp.Imaginary, res.Imaginary);
        }

        public static void assertComplexArraysEqual(Complex[] s11, Complex[] dutS11)
        {
            Debug.Assert(s11.Length == dutS11.Length);
            for (int i = 0; i < s11.Length; ++i)
            {
                Debug.Assert(Equals(s11[i], dutS11[i]), "Values should be equal at # " + i + ". " + s11[i] + " vs " + dutS11[i]);
            }
        }

        static IEnumerable<double> LineSpace(double start, double end, int partitions) =>
                    Enumerable.Range(0, partitions + 1).Select(idx => idx != partitions ? start + (end - start) / partitions * idx : end);

        public static ulong[] GenerateLineSpaceFrequencies(double start, double end, int steps)
        {
            Contract.Assert(end > start);
            Contract.Assert(steps > 1);

            var query = LineSpace(start, end, steps);
            ulong[] frequencies = //query.Cast<ulong>().ToArray();
                query.Cast<object>().Select(o => Convert.ToUInt64(o.ToString(), 10)).ToArray();

            return frequencies;
        }

        public static ulong[] GenerateLineSpaceFrequencies(pocketvna.PocketVNA.FrequencyRange range, int steps)
        {
            return GenerateLineSpaceFrequencies(range.from, range.to, steps);
        }
    }
}
