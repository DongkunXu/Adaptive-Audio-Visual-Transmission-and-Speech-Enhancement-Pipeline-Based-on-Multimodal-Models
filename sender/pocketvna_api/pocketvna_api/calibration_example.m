calibration = loading_calibration_file;

%cali=calibration.readCaliData('s22_only.cali');
cali=calibration.readCaliData('screen_example_/main-calibration.cali');

if cali.ok
    spar=sparameters('screen_example_/__raw_data.s2p');
    
    icali=calibration.interpolateCaliData(cali, spar.Frequencies.');
    
    dut.frequencies = icali.frequencies;

    if icali.s11.ok
        dut.s11=calibration.calibrateReflection(extractP(spar, 1,1), icali.s11, icali.z0, icali.CalKitZstd);
        % Plotting
        f=figure('Name','S11- db+phase');
        %plot(dut.frequencies,db(dut.s11));
        plotyy(dut.frequencies,db(dut.s11),   dut.frequencies,angle(dut.s11));
    end
    if icali.s21.ok
        dut.s21=calibration.calibrateTransmission(extractP(spar, 2,1), icali.s21);
    end
    if icali.s12.ok
        dut.s12=calibration.calibrateTransmission(extractP(spar, 1,2), icali.s12);
    end
    if icali.s22.ok
        dut.s22=calibration.calibrateReflection(extractP(spar, 2,2), icali.s22, icali.z0, icali.CalKitZstd);
        % Plotting
        f=figure('Name','S22- db+phase');
        plotyy(dut.frequencies,db(dut.s22),   dut.frequencies,angle(dut.s22));
    end
else
    fprintf('Failed to load');
end

function r=db(complexarray)
    r=20*log10(abs(complexarray));
end

function v=extractP(sp,p1,p2)
    v=transpose( squeeze(sp.Parameters(p1,p2,:)) );
end
