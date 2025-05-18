namespace Example_TakeMeasurementsAndPlot
{
    partial class PlotExample
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.Windows.Forms.DataVisualization.Charting.ChartArea chartArea2 = new System.Windows.Forms.DataVisualization.Charting.ChartArea();
            System.Windows.Forms.DataVisualization.Charting.Legend legend2 = new System.Windows.Forms.DataVisualization.Charting.Legend();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.buttonReleaseDevice = new System.Windows.Forms.Button();
            this.checkBox_CaliFound = new System.Windows.Forms.CheckBox();
            this.groupBoxFormat = new System.Windows.Forms.GroupBox();
            this.rb_Phase = new System.Windows.Forms.RadioButton();
            this.rb_Mag = new System.Windows.Forms.RadioButton();
            this.rb_dB = new System.Windows.Forms.RadioButton();
            this.checkBoxDeviceConnected = new System.Windows.Forms.CheckBox();
            this.plotPortGroup = new System.Windows.Forms.GroupBox();
            this.radioButton_S22 = new System.Windows.Forms.RadioButton();
            this.radioButton_S12 = new System.Windows.Forms.RadioButton();
            this.radioButton_S21 = new System.Windows.Forms.RadioButton();
            this.radioButton_S11 = new System.Windows.Forms.RadioButton();
            this.groupBoxMeas = new System.Windows.Forms.GroupBox();
            this.checkBox_ApplyCalibration = new System.Windows.Forms.CheckBox();
            this.buttonScan = new System.Windows.Forms.Button();
            this.chart = new System.Windows.Forms.DataVisualization.Charting.Chart();
            this.scanProgress = new System.Windows.Forms.ProgressBar();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).BeginInit();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.groupBoxFormat.SuspendLayout();
            this.plotPortGroup.SuspendLayout();
            this.groupBoxMeas.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.chart)).BeginInit();
            this.SuspendLayout();
            // 
            // splitContainer1
            // 
            this.splitContainer1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.splitContainer1.Location = new System.Drawing.Point(12, 12);
            this.splitContainer1.Name = "splitContainer1";
            // 
            // splitContainer1.Panel1
            // 
            this.splitContainer1.Panel1.Controls.Add(this.buttonReleaseDevice);
            this.splitContainer1.Panel1.Controls.Add(this.checkBox_CaliFound);
            this.splitContainer1.Panel1.Controls.Add(this.groupBoxFormat);
            this.splitContainer1.Panel1.Controls.Add(this.checkBoxDeviceConnected);
            this.splitContainer1.Panel1.Controls.Add(this.plotPortGroup);
            this.splitContainer1.Panel1.Controls.Add(this.groupBoxMeas);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.chart);
            this.splitContainer1.Size = new System.Drawing.Size(896, 483);
            this.splitContainer1.SplitterDistance = 238;
            this.splitContainer1.TabIndex = 1;
            // 
            // buttonReleaseDevice
            // 
            this.buttonReleaseDevice.Location = new System.Drawing.Point(7, 428);
            this.buttonReleaseDevice.Name = "buttonReleaseDevice";
            this.buttonReleaseDevice.Size = new System.Drawing.Size(75, 23);
            this.buttonReleaseDevice.TabIndex = 5;
            this.buttonReleaseDevice.Text = "Release Device";
            this.buttonReleaseDevice.UseVisualStyleBackColor = true;
            this.buttonReleaseDevice.Click += new System.EventHandler(this.buttonReleaseDevice_Click);
            // 
            // checkBox_CaliFound
            // 
            this.checkBox_CaliFound.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.checkBox_CaliFound.AutoSize = true;
            this.checkBox_CaliFound.Enabled = false;
            this.checkBox_CaliFound.Location = new System.Drawing.Point(9, 457);
            this.checkBox_CaliFound.Name = "checkBox_CaliFound";
            this.checkBox_CaliFound.Size = new System.Drawing.Size(90, 17);
            this.checkBox_CaliFound.TabIndex = 3;
            this.checkBox_CaliFound.Text = "calibration file";
            this.checkBox_CaliFound.UseVisualStyleBackColor = true;
            // 
            // groupBoxFormat
            // 
            this.groupBoxFormat.Controls.Add(this.rb_Phase);
            this.groupBoxFormat.Controls.Add(this.rb_Mag);
            this.groupBoxFormat.Controls.Add(this.rb_dB);
            this.groupBoxFormat.Location = new System.Drawing.Point(9, 184);
            this.groupBoxFormat.Name = "groupBoxFormat";
            this.groupBoxFormat.Size = new System.Drawing.Size(153, 97);
            this.groupBoxFormat.TabIndex = 2;
            this.groupBoxFormat.TabStop = false;
            this.groupBoxFormat.Text = "Format";
            // 
            // rb_Phase
            // 
            this.rb_Phase.AutoSize = true;
            this.rb_Phase.Location = new System.Drawing.Point(11, 65);
            this.rb_Phase.Name = "rb_Phase";
            this.rb_Phase.Size = new System.Drawing.Size(55, 17);
            this.rb_Phase.TabIndex = 3;
            this.rb_Phase.Text = "Phase";
            this.rb_Phase.UseVisualStyleBackColor = true;
            this.rb_Phase.CheckedChanged += new System.EventHandler(this.rb_Phase_CheckedChanged);
            // 
            // rb_Mag
            // 
            this.rb_Mag.AutoSize = true;
            this.rb_Mag.Location = new System.Drawing.Point(11, 42);
            this.rb_Mag.Name = "rb_Mag";
            this.rb_Mag.Size = new System.Drawing.Size(46, 17);
            this.rb_Mag.TabIndex = 2;
            this.rb_Mag.Text = "Mag";
            this.rb_Mag.UseVisualStyleBackColor = true;
            this.rb_Mag.CheckedChanged += new System.EventHandler(this.rb_Mag_CheckedChanged);
            // 
            // rb_dB
            // 
            this.rb_dB.AutoSize = true;
            this.rb_dB.Checked = true;
            this.rb_dB.Location = new System.Drawing.Point(11, 19);
            this.rb_dB.Name = "rb_dB";
            this.rb_dB.Size = new System.Drawing.Size(38, 17);
            this.rb_dB.TabIndex = 1;
            this.rb_dB.TabStop = true;
            this.rb_dB.Text = "dB";
            this.rb_dB.UseVisualStyleBackColor = true;
            this.rb_dB.CheckedChanged += new System.EventHandler(this.rb_dB_CheckedChanged);
            // 
            // checkBoxDeviceConnected
            // 
            this.checkBoxDeviceConnected.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.checkBoxDeviceConnected.AutoSize = true;
            this.checkBoxDeviceConnected.Enabled = false;
            this.checkBoxDeviceConnected.Location = new System.Drawing.Point(105, 457);
            this.checkBoxDeviceConnected.Name = "checkBoxDeviceConnected";
            this.checkBoxDeviceConnected.Size = new System.Drawing.Size(115, 17);
            this.checkBoxDeviceConnected.TabIndex = 2;
            this.checkBoxDeviceConnected.Text = "Device Connected";
            this.checkBoxDeviceConnected.UseVisualStyleBackColor = true;
            // 
            // plotPortGroup
            // 
            this.plotPortGroup.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.plotPortGroup.Controls.Add(this.radioButton_S22);
            this.plotPortGroup.Controls.Add(this.radioButton_S12);
            this.plotPortGroup.Controls.Add(this.radioButton_S21);
            this.plotPortGroup.Controls.Add(this.radioButton_S11);
            this.plotPortGroup.Location = new System.Drawing.Point(9, 90);
            this.plotPortGroup.Name = "plotPortGroup";
            this.plotPortGroup.Size = new System.Drawing.Size(153, 88);
            this.plotPortGroup.TabIndex = 1;
            this.plotPortGroup.TabStop = false;
            this.plotPortGroup.Text = "Plot Port";
            this.plotPortGroup.Enter += new System.EventHandler(this.plotPortGroup_Enter);
            // 
            // radioButton_S22
            // 
            this.radioButton_S22.AutoSize = true;
            this.radioButton_S22.Location = new System.Drawing.Point(78, 57);
            this.radioButton_S22.Name = "radioButton_S22";
            this.radioButton_S22.Size = new System.Drawing.Size(44, 17);
            this.radioButton_S22.TabIndex = 3;
            this.radioButton_S22.Text = "S22";
            this.radioButton_S22.UseVisualStyleBackColor = true;
            this.radioButton_S22.CheckedChanged += new System.EventHandler(this.radioButton_S22_CheckedChanged);
            // 
            // radioButton_S12
            // 
            this.radioButton_S12.AutoSize = true;
            this.radioButton_S12.Location = new System.Drawing.Point(78, 20);
            this.radioButton_S12.Name = "radioButton_S12";
            this.radioButton_S12.Size = new System.Drawing.Size(44, 17);
            this.radioButton_S12.TabIndex = 2;
            this.radioButton_S12.Text = "S12";
            this.radioButton_S12.UseVisualStyleBackColor = true;
            this.radioButton_S12.CheckedChanged += new System.EventHandler(this.radioButton_S12_CheckedChanged);
            // 
            // radioButton_S21
            // 
            this.radioButton_S21.AutoSize = true;
            this.radioButton_S21.Location = new System.Drawing.Point(17, 57);
            this.radioButton_S21.Name = "radioButton_S21";
            this.radioButton_S21.Size = new System.Drawing.Size(44, 17);
            this.radioButton_S21.TabIndex = 1;
            this.radioButton_S21.Text = "S21";
            this.radioButton_S21.UseVisualStyleBackColor = true;
            this.radioButton_S21.CheckedChanged += new System.EventHandler(this.radioButton_S21_CheckedChanged);
            // 
            // radioButton_S11
            // 
            this.radioButton_S11.AutoSize = true;
            this.radioButton_S11.Checked = true;
            this.radioButton_S11.Location = new System.Drawing.Point(17, 20);
            this.radioButton_S11.Name = "radioButton_S11";
            this.radioButton_S11.Size = new System.Drawing.Size(44, 17);
            this.radioButton_S11.TabIndex = 0;
            this.radioButton_S11.TabStop = true;
            this.radioButton_S11.Text = "S11";
            this.radioButton_S11.UseVisualStyleBackColor = true;
            this.radioButton_S11.CheckedChanged += new System.EventHandler(this.radioButton_S11_CheckedChanged);
            // 
            // groupBoxMeas
            // 
            this.groupBoxMeas.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBoxMeas.Controls.Add(this.checkBox_ApplyCalibration);
            this.groupBoxMeas.Controls.Add(this.buttonScan);
            this.groupBoxMeas.Location = new System.Drawing.Point(9, 3);
            this.groupBoxMeas.Name = "groupBoxMeas";
            this.groupBoxMeas.Size = new System.Drawing.Size(211, 81);
            this.groupBoxMeas.TabIndex = 0;
            this.groupBoxMeas.TabStop = false;
            this.groupBoxMeas.Text = "Measurements";
            this.groupBoxMeas.Enter += new System.EventHandler(this.groupBoxMeas_Enter);
            // 
            // checkBox_ApplyCalibration
            // 
            this.checkBox_ApplyCalibration.AutoSize = true;
            this.checkBox_ApplyCalibration.Location = new System.Drawing.Point(6, 19);
            this.checkBox_ApplyCalibration.Name = "checkBox_ApplyCalibration";
            this.checkBox_ApplyCalibration.Size = new System.Drawing.Size(67, 17);
            this.checkBox_ApplyCalibration.TabIndex = 1;
            this.checkBox_ApplyCalibration.Text = "Calibrate";
            this.checkBox_ApplyCalibration.UseVisualStyleBackColor = true;
            this.checkBox_ApplyCalibration.CheckedChanged += new System.EventHandler(this.checkBox_ApplyCalibration_CheckedChanged);
            // 
            // buttonScan
            // 
            this.buttonScan.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonScan.Location = new System.Drawing.Point(6, 42);
            this.buttonScan.Name = "buttonScan";
            this.buttonScan.Size = new System.Drawing.Size(75, 23);
            this.buttonScan.TabIndex = 0;
            this.buttonScan.Text = "Scan";
            this.buttonScan.UseVisualStyleBackColor = true;
            this.buttonScan.Click += new System.EventHandler(this.buttonScan_Click);
            // 
            // chart
            // 
            this.chart.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            chartArea2.AxisX.Title = "Frequency (Hz)";
            chartArea2.AxisY.Title = "??";
            chartArea2.Name = "ChartArea1";
            this.chart.ChartAreas.Add(chartArea2);
            legend2.Name = "Legend1";
            this.chart.Legends.Add(legend2);
            this.chart.Location = new System.Drawing.Point(3, 3);
            this.chart.Name = "chart";
            this.chart.Size = new System.Drawing.Size(648, 477);
            this.chart.TabIndex = 0;
            this.chart.Text = "chart1";
            // 
            // scanProgress
            // 
            this.scanProgress.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.scanProgress.Location = new System.Drawing.Point(0, -1);
            this.scanProgress.Name = "scanProgress";
            this.scanProgress.Size = new System.Drawing.Size(911, 10);
            this.scanProgress.TabIndex = 4;
            // 
            // PlotExample
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(911, 498);
            this.Controls.Add(this.scanProgress);
            this.Controls.Add(this.splitContainer1);
            this.Name = "PlotExample";
            this.Text = "Plot Example";
            this.Load += new System.EventHandler(this.PlotForm_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel1.PerformLayout();
            this.splitContainer1.Panel2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).EndInit();
            this.splitContainer1.ResumeLayout(false);
            this.groupBoxFormat.ResumeLayout(false);
            this.groupBoxFormat.PerformLayout();
            this.plotPortGroup.ResumeLayout(false);
            this.plotPortGroup.PerformLayout();
            this.groupBoxMeas.ResumeLayout(false);
            this.groupBoxMeas.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.chart)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.GroupBox groupBoxMeas;
        private System.Windows.Forms.Button buttonScan;
        private System.Windows.Forms.CheckBox checkBox_ApplyCalibration;
        private System.Windows.Forms.CheckBox checkBox_CaliFound;
        private System.Windows.Forms.CheckBox checkBoxDeviceConnected;
        private System.Windows.Forms.GroupBox plotPortGroup;
        private System.Windows.Forms.DataVisualization.Charting.Chart chart;
        private System.Windows.Forms.RadioButton radioButton_S11;
        private System.Windows.Forms.RadioButton radioButton_S22;
        private System.Windows.Forms.RadioButton radioButton_S12;
        private System.Windows.Forms.RadioButton radioButton_S21;
        private System.Windows.Forms.ProgressBar scanProgress;
        private System.Windows.Forms.GroupBox groupBoxFormat;
        private System.Windows.Forms.RadioButton rb_Phase;
        private System.Windows.Forms.RadioButton rb_Mag;
        private System.Windows.Forms.RadioButton rb_dB;
        private System.Windows.Forms.Button buttonReleaseDevice;
    }
}

