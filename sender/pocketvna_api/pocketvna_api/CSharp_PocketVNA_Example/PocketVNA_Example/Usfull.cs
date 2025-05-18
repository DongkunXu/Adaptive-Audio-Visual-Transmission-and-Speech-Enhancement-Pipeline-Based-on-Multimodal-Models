using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PocketVNA_Example
{
    public static class UlongExtensions
    {
        private const ulong K = 1000;

        public static ulong Ghz(this ulong i)
        {
            return i * K * K * K;
        }

        public static ulong Mhz(this ulong i)
        {
            return i * K * K;
        }

        public static ulong Khz(this ulong i)
        {
            return i * K;
        }

        public static ulong Ghz(this int i)
        {
            return ((ulong)i).Ghz();
        }

        public static ulong Mhz(this int i)
        {
            return ((ulong)i).Mhz();
        }

        public static ulong Khz(this int i)
        {
            return ((ulong)i).Khz();
        }
    }
}
