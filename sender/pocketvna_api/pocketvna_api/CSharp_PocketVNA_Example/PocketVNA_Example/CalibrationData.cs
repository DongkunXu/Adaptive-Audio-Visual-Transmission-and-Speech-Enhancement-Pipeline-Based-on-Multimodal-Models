using System;
using pocketvna;
using System.Numerics;

namespace PocketVNA_Example
{
    class CalibrationData
    {
        private static ulong MHz(int v)
        {
            return (ulong)v * 1000000;
        }

        private static Complex C(double r, double i)
        {
            return new Complex(r, i);
        }

        public static readonly ulong[] freq = new ulong[] { MHz(1), MHz(2), MHz(3) };
        public static readonly Complex[] ignored = new Complex[freq.Length];
        public static readonly double Z0 = 50.0;
        public static readonly PocketVNA.SNetwork uncalibrated = new PocketVNA.SNetwork(
            freq,
            new Complex[] { C(1.0, +4e-05), C(1.0, +3e-05), C(1.0, 2.0E-05) },
            new Complex[] { C(-2270.0, -1010.0), C(-3480.0, -770.0), C(-2933.0, 648.0) },
            new Complex[] { C(-1380.0, -1690.0), C(-730.0, -1570.0), C(-2100.0, 1180.0) },
            new Complex[] { C(1.0, +1.0e-05), C(1.0, -2e-06), C(1.0, -2e-05) },
            Z0);

        public static readonly PocketVNA.SNetwork shortReflectionStandard = new PocketVNA.SNetwork(
            freq,
            new Complex[] { C(495607.8, +158961.6), C(422794.4, -77247.0), C(258956.2, -256262.0) },
            ignored,
            ignored,
            new Complex[] { C(361065.2, -215336.2), C(147570.4, -341318.8), C(-68243.4, -341182.2) },
            Z0
        );

        public static readonly PocketVNA.SNetwork openReflectionStandard = new PocketVNA.SNetwork(
            freq,
            new Complex[] { C(-103507.6, +103030.2), C(-39050.0, +151186.0), C(46518.4, +163327.2) },
            ignored,
            ignored,
            new Complex[] { C(16711.4, +108657.4), C(74518.6, +90616.0), C(110157.8, +35605.4) },
            Z0
        );

        public static readonly PocketVNA.SNetwork loadReflectionStandard = new PocketVNA.SNetwork(
            freq,
            new Complex[] { C(107190.6, +185938.2), C(159541.2, +128062.6), C(180890.8, +43653.8) },
            ignored,
            ignored,
            new Complex[] { C(191258.4, +32263.0), C(157767.8, -61217.8), C(84613.4, -131882.6) },
            Z0
        );

        public static readonly PocketVNA.SNetwork openTransmissionStandard = new PocketVNA.SNetwork(
            freq,
            ignored,
            new Complex[] { C(1159.6, -750.4), C(2114.4, -68.2), C(2046.2, +443.4) },
            new Complex[] { C(34.2, -1773.4), C(477.6, -1705.4), C(1910.0, -1296.2) },
            ignored,
            Z0
        );

        public static readonly PocketVNA.SNetwork thruTransmissionStandard = new PocketVNA.SNetwork(
            freq,
            ignored,
            new Complex[] { C(445712.4, +139863.0), C(313045.6, -210936.8), C(-11186.6, -337464.8) },
            new Complex[] { C(289138.6, -141807.0), C(21247.0, -283341.0), C(-174717.8, -157904.2) },
            ignored,
            Z0
        );

        public static readonly PocketVNA.SNetwork calibratedDUT = new PocketVNA.SNetwork(
           freq,
           new Complex[] {
                  C(0.606576756035065, +0.762588073517888),
                  C(0.513267531550349, +0.9791358538146341),
                  C(0.235892205955221, +1.0616400454600028) },
           new Complex[] {
                  C(-0.007180986213496086  , + 0.0016874101047902755),
                  C(-0.011275636438731433  , - 0.009904048451696977),
                  C(-2.8395798205189582e-05, - 0.014736475042388703)
            },
           new Complex[] {
                  C(-0.004075270223455314, - 0.00168546296895949),
                  C(-0.000792659613743921, - 0.004229355008451727),
                  C(0.005751344808592438 , - 0.019118771834241523)
           },
           new Complex[] {
                  C(0.8069678649875225, + 0.7892394729459603),
                  C(0.6180166034864449, + 0.852233905016351),
                  C(0.5742805835193814, + 0.7886191880642951)
           },
           Z0
        );
    }
}
