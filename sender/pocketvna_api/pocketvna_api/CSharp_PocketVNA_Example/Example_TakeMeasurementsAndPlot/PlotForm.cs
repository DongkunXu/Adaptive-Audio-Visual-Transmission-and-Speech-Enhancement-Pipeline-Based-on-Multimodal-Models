using System;
using System.Windows.Forms;

using System.Windows.Forms.DataVisualization.Charting;
using System.Diagnostics;
using System.Diagnostics.Contracts;
using System.Collections.Generic;

using pocketvna;
using Example_CollectFullCalibrationData;
using PocketVNA_Example;
using Example_TakeMeasurementsAndCalibrateOverDumpedData;


namespace Example_TakeMeasurementsAndPlot
{
    public partial class PlotExample : Form
    {
        private PocketVNADevice    device;
        private readonly CalibrationDataSet calibrationData;

        private readonly ulong[] frequencies;

        private PocketVNA.SNetwork rawNetwork, calibratedNetwork;
        private bool measTaken;

        private Series curve;

        public PlotExample()
        {
            InitializeComponent();
        }

        public PlotExample(PocketVNADevice device, CalibrationDataSet calibrationData) : this()
        {
            this.device = device;
            this.calibrationData = calibrationData;
            if ( calibrationData != null )
            {
                frequencies = calibrationData.frequencies;
            }
            else
            {
                frequencies = Utils.GenerateLineSpaceFrequencies(Settings.FrequencyRange, Settings.STEPS);
            }
        }

        private void PlotForm_Load(object sender, EventArgs e)
        {
            InitGUI();
        }

        private void InitGUI()
        {
            checkBoxDeviceConnected.Checked = (device != null);
            checkBox_CaliFound.Checked = (calibrationData != null);
            checkBox_ApplyCalibration.Enabled = (calibrationData != null);
            radioButton_S11.Checked = true;
            buttonScan.Enabled = (device != null);

            buttonReleaseDevice.Visible = (device != null);

            rb_dB.Checked = true;
        }

        private void groupBoxMeas_Enter(object sender, EventArgs e)
        {
        }

        private void buttonScan_Click(object sender, EventArgs e)
        {
            Contract.Assert(frequencies != null && frequencies.Length > 0);            

            System.Threading.ThreadPool.QueueUserWorkItem(delegate {
                PerformScan();
            }, null);
        }

        private void PerformScan()
        {
            BeforeScan();
            try
            {
                measTaken = false;
                rawNetwork = device.ScanAllSupportedModes(frequencies, 4, OnProgress);
                calibratedNetwork = ApplyCalibration();
                
                measTaken = true;
            } 
            finally
            {
                AfterScan();
            }            
        }

        private void AfterScan()
        {
            InvokeUI(() => {
                buttonScan.Visible = true;
                plotPortGroup.Enabled = true;

                RePlot();
            });
        }

        private void BeforeScan()
        {
            InvokeUI(() =>
            {
                buttonScan.Visible = false;
                plotPortGroup.Enabled = false;
            });
        }

        private PocketVNA.SNetwork ApplyCalibration()
        {
            if (calibrationData != null)
            {
                return BuiltInCompensationAlgorithm.Apply(calibrationData, rawNetwork);
            }
            return new PocketVNA.SNetwork();
        }       

        private PocketVNA.Progress OnProgress(int total, int index)
        {
            SetProgressSafely(100.0 * index / total);
            return PocketVNA.Progress.Continue;
        }


        private void SetProgressSafely(double percent)
        {
            InvokeUI( () => {
                scanProgress.Value = (int)percent;
            });
        }

        private void InvokeUI(Action a)
        {
            this.Invoke(new MethodInvoker(a)); //BeginInvoke
        }

        private void RePlot()
        { 
            if (measTaken)
            {                
                RemovePreviousCurve();
                chart.Series.Add(CreateCurve());
                chart.ChartAreas[0].RecalculateAxesScale();
            }
        }

        private Series CreateCurve()
        {
            var trans = SelectedTransmission;
            var ntwk = GetActiveNetwork();
            var conv = SelectedFormat;

            curve = new Series("Plot " + trans, rawNetwork.Size)
            {
                ChartType = SeriesChartType.Line
            };

            for (int i = 0; i < ntwk.Size; ++i)
            {
                curve.Points.Add( new DataPoint(ntwk.frequencies[i], conv(ntwk.Get(trans)[i])) );
            }

            return curve;
        }       

        private void RemovePreviousCurve()
        {
            if (HasCurve)
            {
                chart.Series.Remove(curve);
            }
        }

        private bool HasCurve
        {
            get
            {
                return curve != null && chart.Series.Contains(curve);
            }
        }

        private PocketVNA.SNetwork GetActiveNetwork()
        {            
            if (IsCalibrationSelected)
            {
                return calibratedNetwork;
            }
            else
            {
                return rawNetwork;
            }            
        }

        private bool IsCalibrationSelected
        {
            get
            {
                return checkBox_ApplyCalibration.Enabled && checkBox_ApplyCalibration.Checked;
            }
        }

        private PocketVNA.Transmission SelectedTransmission
        {
            get
            {
                var radioButton2Transmission = new Dictionary<RadioButton, PocketVNA.Transmission>
                {
                    { radioButton_S11, PocketVNA.Transmission.S11},    {radioButton_S21, PocketVNA.Transmission.S21},
                    { radioButton_S12, PocketVNA.Transmission.S12},    {radioButton_S22, PocketVNA.Transmission.S22}
                };

                foreach ( var pair in radioButton2Transmission)
                {
                    if ( pair.Key.Checked )
                    {
                        return pair.Value;
                    }
                }
                Debug.Assert(false);
                return PocketVNA.Transmission.None;                
            }
        }

       
        private Conversions.FormatFunction SelectedFormat
        {
            get
            {
                if (rb_Mag.Checked)
                {
                    return Conversions.Magnitude;
                }
                else if (rb_Phase.Checked)
                {
                    return Conversions.Phase;
                }
                else
                {
                    return Conversions.dBels;
                }
            }
        }

        private void plotPortGroup_Enter(object sender, EventArgs e)
        {
        }

        private void radioButton_S12_CheckedChanged(object sender, EventArgs e)
        {
            RePlot();
        }

        private void radioButton_S21_CheckedChanged(object sender, EventArgs e)
        {
            RePlot();
        }

        private void rb_dB_CheckedChanged(object sender, EventArgs e)
        {
            chart.ChartAreas[0].AxisY.Title = "Magnitude (dB)";
            RePlot();
        }

        private void rb_Mag_CheckedChanged(object sender, EventArgs e)
        {
            chart.ChartAreas[0].AxisY.Title = "Magnitude";
            RePlot();
        }

        private void rb_Phase_CheckedChanged(object sender, EventArgs e)
        {
            chart.ChartAreas[0].AxisY.Title = "Phase (°)";
            RePlot();
        }

        private void checkBox_ApplyCalibration_CheckedChanged(object sender, EventArgs e)
        {
            if (measTaken)
            {                
                RePlot();
            }            
        }
       
        private void buttonReleaseDevice_Click(object sender, EventArgs e)
        {
            device.Dispose();
            device = null;
            InitGUI();
        }

        private void radioButton_S22_CheckedChanged(object sender, EventArgs e)
        {
            RePlot();
        }

        private void radioButton_S11_CheckedChanged(object sender, EventArgs e)
        {
            RePlot();
        }
    }
}
