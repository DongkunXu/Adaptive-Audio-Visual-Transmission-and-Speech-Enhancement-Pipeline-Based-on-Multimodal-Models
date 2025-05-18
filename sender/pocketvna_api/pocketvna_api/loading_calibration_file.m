classdef loading_calibration_file
   methods
      function sdut = calibrateReflection(~, sxm, s11, z0, loadohm)
          sdut=calibrateReflectionFormula(sxm, s11, z0, loadohm);
      end
      function sdut = calibrateTransmission(~, sxm, s21)
          sdut = calibrateTransmissionFormula(sxm, s21);
      end

      function cali = readCaliData(~, FileName)
          cali = readCalibration(FileName);
      end
      
      function newCali = interpolateCaliData(~,cali,newFrequencies)
          newCali=interpolate(cali,newFrequencies);
      end
   end
end


function newCali = interpolate(cali,newFrequencies)
    newCali.frequencies=newFrequencies;
    newCali.ok=cali.ok;
    newCali.z0=cali.z0;
    newCali.CalKitZstd=cali.CalKitZstd;

    newCali.s11=interpolateReflection(cali.frequencies,  cali.s11, newFrequencies);
    newCali.s21=interpolateTransmission(cali.frequencies,cali.s21, newFrequencies);
    newCali.s12=interpolateTransmission(cali.frequencies,cali.s12, newFrequencies);
    newCali.s22=interpolateReflection(cali.frequencies,  cali.s22, newFrequencies);
end

% Interpolate s11 calibration data over SXM's frequencies
function sdut = calibrateReflectionFormula(sxm, s11, z0, loadohm)
    openr = gamma2z(s11.open, z0);
    loadr = gamma2z(s11.load, z0);
    shorr = gamma2z(s11.short,z0);
    zxmr  = gamma2z(sxm,   z0);

    zdut = calibrateZ(loadohm, openr, loadr, zxmr, shorr);
    sdut=z2gamma(zdut, z0);
end

% Interpolate s11 calibration data over SXM's frequencies
function sdut = calibrateTransmissionFormula(sxm, s21)
    sdut=(sxm - s21.open) ./ (s21.thru - s21.open);
end

function zdut=calibrateZ(Zstd, Zo, Zsm, Zxm, Zs)
    zdut = (Zstd * (Zo - Zsm) .*(Zxm - Zs)) ./ ((Zsm - Zs).*(Zo - Zxm));
end

function cali = readCalibration(FileName)
    cali.ok = false;

    lines = splitlines(fileread( FileName ));
    if (lines{1}) == '#PVNA1##SIMPLE-2PORT'
        settings=readSettings(lines);
        [frequencies,  s11, s21,  s22, s12]=readData(lines);
        z0 = 50.0; % set jic
        if isKey(settings,'Z0')
            z0 = str2double(settings('Z0'));
        elseif isKey(settings,'RR')
            z0 = str2double(settings('RR'));
        end
        zstd=z0;
        if isKey(settings,'LOADSTD')
            zstd = str2double(settings('LOADSTD'));
        end
        fprintf("Z0: %f, Zstd: %f\n", z0, zstd);
        cali.ok = s11.ok || s21.ok || s12.ok || s22.ok;
        cali.frequencies = frequencies;
        cali.s11=s11;   cali.s21=s21;
        cali.s12=s12;   cali.s22=s22;
        cali.z0=z0;
        cali.CalKitZstd=zstd;
    else
        fprintf('Unsupported calibration file: %\n', (lines{1}));
    end
end

function data=readSettings(lines)
    data=containers.Map('A','A');
    for i = 2:length(lines)
        line=lines{i};
        if startsWith(line,'!') && contains(line,':')
            colonIndex=strfind(line,':');
            k=extractBetween(line,2,colonIndex(1)-1);
            s=extractBetween(line,colonIndex(1)+1,length(line));
            fprintf("[%s]+[%s]\n", k{1}, strtrim(s{1}));
            data(k{1})=strtrim(s{1});
        end
    end
end

function [frequencies,  s11, s21,  s22, s12]=readData(lines)
    frequencies = [];
    short11=[];  open11 = [];  load11 = [];
    openS21=[];  thru21 = [];
    short22=[];  open22 = [];  load22 = [];
    openS12=[];  thru12 = [];
    
    x11.ok = false;   x21.ok = false;
    x12.ok = false;   x22.ok = false;

    [from,to] = findDataArea(lines);
    if from ~= 0 && to ~= 0 && from < to
        titlesLine=lines{from+1};
        titles=split(titlesLine,';');
        disp(titles{1});

        freqIndex   = find(contains(titles,'FRQ'));
        shrt11Index = find(contains(titles,'ShortZ11'));
        open11Index = find(contains(titles,'OpenZ11'));
        load11Index = find(contains(titles,'LoadZ11'));
        
        open21Index = find(contains(titles,'OpenS21'));
        thru21Index = find(contains(titles,'ThroughS21'));
        
        open12Index = find(contains(titles,'OpenS12'));
        thru12Index = find(contains(titles,'ThroughS12'));
        
        shrt22Index = find(contains(titles,'ShortZ22'));
        open22Index = find(contains(titles,'OpenZ22'));
        load22Index = find(contains(titles,'LoadZ22'));

        for i=(from+2):(to-1)
            line=lines{i};
            columns=split(line,';');
            frequencies = [frequencies  str2double(columns{freqIndex})];
            % ========================
            if shrt11Index
                short11 = [short11  conv2complex(columns{shrt11Index})];
            end
            if open11Index
                open11  = [open11  conv2complex(columns{open11Index})];
            end
            if load11Index
                load11  = [load11  conv2complex(columns{load11Index})];
            end
            if open21Index
                openS21 = [openS21  conv2complex(columns{open21Index})];
            end
            if thru21Index
                thru21  = [thru21  conv2complex(columns{thru21Index})];
            end
            % ------
            % ========================
            if shrt22Index
                short22 = [short22  conv2complex(columns{shrt22Index})];
            end
            if open22Index
                open22  = [open22  conv2complex(columns{open22Index})];
            end
            if load22Index
                load22  = [load22  conv2complex(columns{load22Index})];
            end
            if open12Index
                openS12 = [openS12 conv2complex(columns{open12Index})];
            end
            if thru12Index
                thru12  = [thru12  conv2complex(columns{thru12Index})];
            end
            % ------
        end
        
        %- -- --
        if ~isempty(shrt11Index) && ~isempty(open11Index) && ~isempty(load11Index)
            x11.ok   = true;
            x11.short= short11;
            x11.open = open11;
            x11.load = load11;            
        end
        
        if ~isempty(open21Index) && ~isempty(thru21Index)
            x21.ok   = true;
            x21.open = openS21;
            x21.thru = thru21;
        end
        
        if ~isempty(open12Index) && ~isempty(thru12Index)
            x12.ok   = true;
            x12.open = openS12;
            x12.thru = thru12;
        end

        if ~isempty(shrt22Index) && ~isempty(open22Index) && ~isempty(load22Index)
            x22.ok   = true;
            x22.short= short22;
            x22.open = open22;
            x22.load = load22;
        end
    end
    
    s11 = x11;  s21 = x21;
    s12 = x12;  s22 = x22;
end

function c=conv2complex(col)
    xx=split(col,',');
    if length(xx) == 2
        c=complex(str2double(xx{1}), str2double(xx{2}));
    else
        c=complex(0.0);
    end
end

function [from,to]=findDataArea(lines)
    from=0;
    to=0;
    for i = 2:length(lines)
        line=lines{i};
        if startsWith(line,'{STARTCALI:')
            if from ~= 0
                fprintf("Error: from `{STARTCALI:` happens again\n");
            end
            from=i;
        end
        if startsWith(line,'}ENDCALI')
            if to ~= 0
                fprintf("Error: from `}ENDCALI` happens again\n");
            end
            to=i;
        end
    end
end

%------ Interpolation -----------------------------------------
function i21=interpolateTransmission(frequencies,s21, newFrequencies)
    i21.ok = s21.ok;
    if s21.ok
        assert(length(s21.open) == length(s21.thru),   'should be of the same size');
        assert(length(s21.open) == length(frequencies),'should be of the same size');

        i21.open = interp1(frequencies,s21.open, newFrequencies,'spline');
        i21.thru = interp1(frequencies,s21.thru, newFrequencies,'spline');
    end
end

function i11=interpolateReflection(frequencies,s11, newFrequencies)
    i11.ok = s11.ok;
    if s11.ok
        assert(length(s11.short) == length(s11.open), 'should be of the same size');
        assert(length(s11.short) == length(s11.load), 'should be of the same size');
        assert(length(s11.short) == length(frequencies), 'should be of the same size');

        i11.short= interp1(frequencies,s11.short,newFrequencies,'spline');
        i11.open = interp1(frequencies,s11.open, newFrequencies,'spline');
        i11.load = interp1(frequencies,s11.load, newFrequencies,'spline');
    end
end
