using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.Numerics;
using pocketvna;

namespace Example_CollectFullCalibrationData
{
    public class CalibrationDataSet
    {
        public Complex[] shortS11, openS11, loadS11;
        public Complex[] shortS22, openS22, loadS22;
        public Complex[] openS21, thruS21;
        public Complex[] openS12, thruS12;
        public double Z0;
        public ulong[] frequencies;
        public PocketVNA.Transmission[] modes;

        public void Set(Standard standard, PocketVNA.Transmission transmission, Complex[] snn)
        {
            var sm = new StandardMode(standard, transmission);

            if (StandardMode.ShortS11.Equals(sm)) shortS11 = snn;
            else if (StandardMode.OpenS11.Equals(sm)) openS11 = snn;
            else if (StandardMode.LoadS11.Equals(sm)) loadS11 = snn;

            else if (StandardMode.ShortS22.Equals(sm)) shortS22 = snn;
            else if (StandardMode.OpenS22.Equals(sm)) openS22 = snn;
            else if (StandardMode.LoadS22.Equals(sm)) loadS22 = snn;

            else if (StandardMode.OpenS21.Equals(sm)) openS21 = snn;
            else if (StandardMode.ThruS21.Equals(sm)) thruS21 = snn;

            else if (StandardMode.OpenS12.Equals(sm)) openS12 = snn;
            else if (StandardMode.ThruS12.Equals(sm)) thruS12 = snn;

            else throw new Exception("Unexpected Standard&Mode pair #" + standard + transmission);
        }

    }
}
