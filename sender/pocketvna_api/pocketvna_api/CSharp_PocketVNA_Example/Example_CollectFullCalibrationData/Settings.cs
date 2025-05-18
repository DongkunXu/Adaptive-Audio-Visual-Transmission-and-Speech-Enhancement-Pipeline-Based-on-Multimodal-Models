using pocketvna;
using PocketVNA_Example;

namespace Example_CollectFullCalibrationData
{
    public class Settings
    {
        public static readonly PocketVNA.FrequencyRange FrequencyRange = new PocketVNA.FrequencyRange(450.Mhz(), 470.Mhz());
        public const int STEPS = 200;
        public const string CalibrationDumpFileName = "fullCalibrationPack.dump";
    }
}
