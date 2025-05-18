using System;
using pocketvna;

namespace Example_CollectFullCalibrationData
{
    readonly struct StandardMode : IEquatable<StandardMode>
    {
        readonly Standard standard;
        readonly PocketVNA.Transmission mode;

        public StandardMode(Standard standard, PocketVNA.Transmission mode)
        {
            this.standard = standard;
            this.mode = mode;
        }

        public override bool Equals(object obj)
        {
            if (obj == null) return false;
            return this.Equals((StandardMode)obj);
        }

        public override int GetHashCode()
        {
            return (int)standard * 1000 + (int)mode;
        }

        public bool Equals(StandardMode p)
        {
            return (standard == p.standard) && (mode == p.mode);
        }


        public static readonly StandardMode ShortS11 = new StandardMode(Standard.Short, PocketVNA.Transmission.S11);
        public static readonly StandardMode OpenS11 = new StandardMode(Standard.Open, PocketVNA.Transmission.S11);
        public static readonly StandardMode LoadS11 = new StandardMode(Standard.Load, PocketVNA.Transmission.S11);

        public static readonly StandardMode ShortS22 = new StandardMode(Standard.Short, PocketVNA.Transmission.S22);
        public static readonly StandardMode OpenS22 = new StandardMode(Standard.Open, PocketVNA.Transmission.S22);
        public static readonly StandardMode LoadS22 = new StandardMode(Standard.Load, PocketVNA.Transmission.S22);

        public static readonly StandardMode OpenS21 = new StandardMode(Standard.Open, PocketVNA.Transmission.S21);
        public static readonly StandardMode ThruS21 = new StandardMode(Standard.Through, PocketVNA.Transmission.S21);

        public static readonly StandardMode OpenS12 = new StandardMode(Standard.Open, PocketVNA.Transmission.S12);
        public static readonly StandardMode ThruS12 = new StandardMode(Standard.Through, PocketVNA.Transmission.S12);
    }
}
