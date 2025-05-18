% Made with Mathworks Matlab R2017a (9.2.0.538062) on Windows, x64 bit
%    -- Make it run from scratch
%       1) Install MinGW Setup MINGW: https://www.mingw-w64.org/, 
%           *) I used Win-Builds  from https://www.mingw-w64.org/downloads/
%           *) Run it and install to a propper location
%       2) Find out MINGW_ROOT: folder with bin,lib,lib64,libexec so on
%       3) Put pocketvna.h, PocketVnaAPI_x64.dll, libusb-1.0.dll near this file
%       4) Make sure this file contains propper settings:MinGWROOT,dll name
%
%    -- Just info, you can ignore it
% MW_MINGW64_LOC -- path to mingw root: bin,lib,imports folders are there
% Ensure mingw root path and CopyPaste next line into Command Window
% setenv('MW_MINGW64_LOC','C:/MinGW'); mex -setup
%    -- Links
%   https://www.mathworks.com/help/coder/ug/mapping-matlab-types-to-cc-types.html
%   https://www.mathworks.com/matlabcentral/mlc-downloads/downloads/submissions/32306/versions/2/previews/Velleman_K8055/+vellboard/K8055D_h.m/index.html
%   https://github.com/CoppeliaRobotics/b0RemoteApiBindings/blob/master/matlab/b0RemoteApiProto.m
%

[scriptsFolder,~]=fileparts(mfilename('fullpath'));
MinGWRoot='C:/MinGW';  %!!! Make sure path is correct
disp(scriptsFolder);
addpath(fullfile(scriptsFolder));


% Probably later the proto can be defined
%loadlibrary('PocketVnaApi_x64.dll',  @pocketVNAproto)

if not(libisloaded('PocketVnaApi_x64'))
    setenv('MW_MINGW64_LOC',MinGWRoot);  mex -setup;
    loadlibrary('PocketVnaApi_x64', 'pocketvna.h')
end
%libfunctions('PocketVnaApi_x64')
%libfunctionsview('PocketVnaApi_x64');

% 1: Simplest function: get driver version
[pi,v,~,resStr] = driver_version();
fprintf('Version: %d, PI: %f, %s\n',v,pi,resStr);


% 2: Enumerate devices
done=main();
fprintf("I'm Done! %s\n",done);

% Main Functions
function done=main()
    [list,size,ok,~] = enumerate_devices();    
    if ok
        done = 'Success!';
        fprintf("There is some device %d\n", size);
        
        %[path,vid,pid,~,SN]=device_info(list, 1);
        %fprintf("Path: %s, %d&%d, SN:\n", path, vid, pid, SN);
        
        % Pay attention on index of device
        [handle,ok,err]=connect_to(list,0); 
        
        % now, we do not need list anymore
        [ok2,error2] = clear_enumeration(list);
        if ok2
            fprintf("Enum cleared. Error: %s\n", error2);
        else
            fprintf("Failed to cleared. Error: %s\n", error2);
        end
        
        % work with device
        processOpenedDevice(handle,ok,err);
    else
        done = 'No device';
    end
end

function processOpenedDevice(handle,ok,err) 
    if ok
        fprintf("Connected\n");
        example_CheckIfValid(handle);
        [ver,z0,validRng,goodRng,modes]=get_settings(handle);
        fprintf("Version %X, Z0=%f\n", ver, z0);
        fprintf("ValidRange: [%d; %d]\n",min(validRng),max(validRng));
        fprintf("Reasonable: [%d; %d]\n",min(goodRng),max(goodRng));
        fprintf("Support Modes:    %s\n",modes);
        
        fprintf("SCAN\n");
        frequencies=1000000:250000:30000000;
        [ok,~,s11,s21,s12,s22] = scanMeasurementsFull(handle,frequencies,1);
        if ok 
            disp("SCAN SUCCESS");
            disp(length(frequencies));
            disp(length(s11));
            disp(s11);
            plotyy(frequencies,db(s11),   frequencies,angle(s11));
        else
            disp("SCAN Failed! :(");
        end


        [~,err] = close_connection(handle);
        fprintf("Closing %s\n", err);
    else
        fprintf("Failed to open device %s\n", err);
    end
end

function r=db(complexarray)
    r=(abs(complexarray));
end

function example_CheckIfValid(handle)
    fprintf("Validation Example\n");
    [ok,~]=is_valid(handle);
    if ok
        fprintf("handle valid, as expected\n");
    else
        fprintf("INVALID HANDLE unexpectedly\n");
    end
end

% Function Wrappers
function [ok,err,s11,s21,s12,s22] = scanMeasurementsFull(handle,frequencies,avg)
%PVNA_EXPORTED PVNA_Res   pocketvna_multi_query(const PVNA_DeviceHandler handle,
%                                        const PVNA_Frequency * frequencies, const uint32_t size,
%                                        const uint16_t average, const PVNA_NetworkParam params,
%                                        PVNA_Sparam * s11a, PVNA_Sparam * s21a,
%                                        PVNA_Sparam * s12a, PVNA_Sparam * s22a,
%                                        PVNA_ProgressCallBack * progress);
    S21=1;S11=2;S12=4;S22=8;
    Full=S21+S11+S12+S22;

    sz = length(frequencies);
    s11Array=complexzeros(sz);
    s21Array=complexzeros(sz);
    s12Array=complexzeros(sz);
    s22Array=complexzeros(sz);

    result= calllib('PocketVnaApi_x64', 'pocketvna_multi_query',handle,frequencies,sz,avg,S11,s11Array,s21Array,s12Array,s22Array,libpointer());
    err   = result_str(result);
    switch result
    case 'PVNA_Res_Ok'
        s11=convert(s11Array,sz);
        s21=convert(s21Array,sz);
        s12=convert(s12Array,sz);
        s22=convert(s22Array,sz);
        ok = true;
    otherwise
        s11=complex(zeros(1,0,'double'),0);
        s21=complex(zeros(1,0,'double'),0);
        s12=complex(zeros(1,0,'double'),0);
        s22=complex(zeros(1,0,'double'),0);
        ok  = false;
        fprintf("Error pocketvna_multi_query %s\n", err);
    end
end

function complexArray= convert(c,sz)
    result=complex(zeros(1,sz,'double'),0);
    pls2=c;
    for i = 1:sz        
        x=pls2.value;
        result(i)=complex(x.real, x.imag);
        pls2=pls2+1;
    end
    complexArray=result;
end

function c= complexzeros(sz)
    ms(1).real=0.0;
    ms(1).imag=0.0;
    ms(sz).real=0.0; % prelocation???
    ms(sz).imag=0.0;
    for i = 1:sz
        ms(i).real=0.0;
        ms(i).imag=0.0;
    end
    ls=libstruct('ImitComplexD', ms);
    c=libpointer('ImitComplexD',ls);
end
function [version,z0,validRng,goodRng,modes] = get_settings(handle)
    % PVNA_EXPORTED PVNA_Res   pocketvna_is_transmission_supported(const PVNA_DeviceHandler handle, const PVNA_NetworkParam param);
    [version,~,~] = device_version(handle);
    [z0,~,~]      = device_z0(handle);
    [validRng,~,~]= valid_frequency_range(handle);
    [goodRng,~,~] = reasonable_frequency_range(handle);
    [modes,~]     = supported_modes(handle);
end

function [modes,ok] = supported_modes(handle)
    % PVNA_EXPORTED PVNA_Res   pocketvna_is_transmission_supported(const PVNA_DeviceHandler handle, const PVNA_NetworkParam param);
    %result= calllib('PocketVnaApi_x64', 'pocketvna_get_reasonable_frequency_range',handle,fromPtr,toPtr);
    S21=1;S11=2;S12=4;S22=8;
    modes_array={};
    ok=true;
    [supported,s,~] = is_mode_supported(handle,S11);
    ok = ok && s;
    if supported
        modes_array = [modes_array;'s11'];
    end
    [supported,s,~] = is_mode_supported(handle,S21);
    ok = ok && s;
    if supported
        modes_array = [modes_array;'s21'];        
    end
    [supported,s,~] = is_mode_supported(handle,S12);
    ok = ok && s;
    if supported
        modes_array = [modes_array;'s12'];
    end
    [supported,s,~] = is_mode_supported(handle,S22);
    ok = ok && s;
    if supported
        modes_array = [modes_array;'s22'];        
    end
    modes=strjoin(modes_array,'/');
end

function [supported,ok,err] = is_mode_supported(handle,param)
    % PVNA_EXPORTED PVNA_Res   pocketvna_is_transmission_supported(const PVNA_DeviceHandler handle, const PVNA_NetworkParam param);
    result= calllib('PocketVnaApi_x64', 'pocketvna_is_transmission_supported',handle,param);
    err   = result_str(result);
    switch result
    case 'PVNA_Res_Ok'
      ok = true;
      supported=true;
    case 'PVNA_Res_UnsupportedTransmission'
      ok = true;
      supported=false;
    otherwise
      ok  = false;
      supported=false;
      fprintf("Error pocketvna_is_transmission_supported %s\n", err);
    end
end

function [rng,ok,err] = valid_frequency_range(handle)
    % PVNA_EXPORTED PVNA_Res   pocketvna_get_valid_frequency_range(const PVNA_DeviceHandler handle, PVNA_Frequency * from, PVNA_Frequency * to);
    fromPtr= libpointer('uint64Ptr',0.0);
    toPtr  = libpointer('uint64Ptr',0.0);    
    
    result= calllib('PocketVnaApi_x64', 'pocketvna_get_valid_frequency_range',handle,fromPtr,toPtr);
    err   = result_str(result);
    switch result
    case 'PVNA_Res_Ok'
      ok = true;
      rng=[fromPtr.value,toPtr.value];
    otherwise
      ok  = false;
      rng = [0,0];
      fprintf("Error pocketvna_get_valid_frequency_range %s\n", err);
    end
end


function [rng,ok,err] = reasonable_frequency_range(handle)
    % PVNA_EXPORTED PVNA_Res   pocketvna_get_reasonable_frequency_range(const PVNA_DeviceHandler handle, PVNA_Frequency * from, PVNA_Frequency * to);
    fromPtr= libpointer('uint64Ptr',0.0);
    toPtr  = libpointer('uint64Ptr',0.0);    
    
    result= calllib('PocketVnaApi_x64', 'pocketvna_get_reasonable_frequency_range',handle,fromPtr,toPtr);
    err   = result_str(result);
    switch result
    case 'PVNA_Res_Ok'
      ok = true;
      rng=[fromPtr.value,toPtr.value];
    otherwise
      ok  = false;
      rng = [0,0];
      fprintf("Error pocketvna_get_reasonable_frequency_range %s\n", err);
    end
end


function [z0,ok,err] = device_z0(handle)
    % PVNA_EXPORTED PVNA_Res   pocketvna_get_characteristic_impedance(const PVNA_DeviceHandler handle, double * R);
    z0Ptr   = libpointer('doublePtr',0.0);
    
    result= calllib('PocketVnaApi_x64', 'pocketvna_get_characteristic_impedance', handle, z0Ptr);
    err   = result_str(result);
    z0    = z0Ptr.value; % 20D == 2.10
    switch result
    case 'PVNA_Res_Ok'
      ok = true;
    otherwise
      ok=false;
      fprintf("Error pocketvna_get_characteristic_impedance %s\n", err);
    end
end

function [version,ok,err] = device_version(handle)
    % PVNA_EXPORTED PVNA_Res   pocketvna_version(const PVNA_DeviceHandler handle, uint16_t * version);
    VersionPtr   = libpointer('uint16Ptr',0);
    
    result = calllib('PocketVnaApi_x64', 'pocketvna_version', handle, VersionPtr);
    err    = result_str(result);
    version= VersionPtr.value; % 20D == 2.10
    switch result
    case 'PVNA_Res_Ok'
      ok = true;
    otherwise
      ok=false;
      fprintf("Error pocketvna_version %s\n", err);
    end
end

function [handle,ok,err]=connect_to(list, index)
    %   PVNA_EXPORTED PVNA_Res pocketvna_helper_descriptor_get_handler(PVNA_DeviceDesc * list, uint16_t index, PVNA_DeviceHandler * handle);

    handle=libpointer('voidPtr');
    result = calllib('PocketVnaApi_x64', 'pocketvna_helper_descriptor_get_handler', list, index, handle);
    err= result_str(result);

    switch result
    case 'PVNA_Res_Ok'
      ok = true;
    otherwise
      disp('Failure OPEN!');
      ok=false;
      fprintf("Error %s\n", err);
    end
end

function [ok,err]=close_connection(handle)
    % PVNA_EXPORTED PVNA_Res   pocketvna_release_handle(PVNA_DeviceHandler * handle);
    result = calllib('PocketVnaApi_x64', 'pocketvna_release_handle', handle);
    err= result_str(result);
    switch result
    case 'PVNA_Res_Ok'      
      ok = true;    
    otherwise
      ok=false;
    end
end
% IsValid
function [ok,err]=is_valid(handle)
    %     PVNA_EXPORTED PVNA_Res   pocketvna_is_valid(const PVNA_DeviceHandler handle);
    result = calllib('PocketVnaApi_x64', 'pocketvna_is_valid', handle);
    err    = result_str(result);
    switch result
    case 'PVNA_Res_Ok'
      ok = true; 
    case 'PVNA_Res_InvalidHandle'
      ok = false;
    otherwise
      fprintf("Unexpected error for pocketvna_is_valid: %s\n",err);                
      ok=false;
    end
end

% ----------------
function [path,vid,pid,iface,SN] = device_info(list, index)
    %PVNA_EXPORTED uint16_t pocketvna_helper_descriptors_count(PVNA_DeviceDesc * list);

    %PVNA_EXPORTED const char * pocketvna_helper_descriptor_get_path(PVNA_DeviceDesc * list, uint16_t index);
    path = calllib('PocketVnaApi_x64', 'pocketvna_helper_descriptor_get_path', list, index);

    %PVNA_EXPORTED uint16_t pocketvna_helper_descriptor_get_vid(PVNA_DeviceDesc * list, uint16_t index);
    vid  = calllib('PocketVnaApi_x64', 'pocketvna_helper_descriptor_get_vid', list, index);

    %PVNA_EXPORTED uint16_t pocketvna_helper_descriptor_get_pid(PVNA_DeviceDesc * list, uint16_t index);
    pid  = calllib('PocketVnaApi_x64', 'pocketvna_helper_descriptor_get_pid', list, index);

    %PVNA_EXPORTED enum ConnectionInterfaceCode pocketvna_helper_descriptor_get_interface(PVNA_DeviceDesc * list, uint16_t index);
    iface= calllib('PocketVnaApi_x64', 'pocketvna_helper_descriptor_get_interface', list, index);

    %PVNA_EXPORTED const wchar_t * pocketvna_helper_descriptor_get_SN(PVNA_DeviceDesc * list, uint16_t index);
    %sns   = calllib('PocketVnaApi_x64', 'pocketvna_helper_descriptor_get_SN', list, index);
    % I'll add ASCII version for SN
    SN = "Unsupported for now. Matlab does not support wchar_t*";
end

function [listHandle,size,ok,resStr] = enumerate_devices()
    % preliminary set
    listHandle = libpointer('PocketVnaDeviceDescPtr'); 
    ok = false;

    listPtrPtr=libpointer('PocketVnaDeviceDescPtr');
    sizeHolder=0;
    sizePtr=libpointer('uint16Ptr',sizeHolder);
    %PVNA_EXPORTED PVNA_Res pocketvna_list_devices(PVNA_DeviceDesc ** list, uint16_t * size);
    result = calllib('PocketVnaApi_x64', 'pocketvna_list_devices', listPtrPtr, sizePtr);
    size=sizePtr.value;
    resStr=result_str(result);

    % don't use integer codes; or don't use if's for string
    switch result
    case 'PVNA_Res_Ok'
      disp('Ok')
      ok = true;
      listHandle=listPtrPtr;
    case 'PVNA_Res_NoDevice'
      disp('No Device!');
      [~,er]=clear_enumeration(listPtrPtr);
      fprintf("Clearing list after enum no-device: %s\n", er);
    otherwise
      disp('Failure!');
      fprintf("Error %s\n", resStr);      
      [~,er]=clear_enumeration(listPtrPtr);
      fprintf("Clearing list after enum failure: %s\n", er);      
    end
end

function [ok,er] = clear_enumeration(listHandle)
    % PVNA_EXPORTED PVNA_Res pocketvna_free_list(PVNA_DeviceDesc ** list);
    res = calllib('PocketVnaApi_x64', 'pocketvna_free_list', listHandle);

    er = result_str(res);
    ok = (res == 'PVNA_Res_Ok');    
end

function resStr = result_str(r)
    %PVNA_EXPORTED const char * pocketvna_result_string(PVNA_Res code);
    resStr = calllib('PocketVnaApi_x64','pocketvna_result_string',r);
end

function [pi,version,res,resStr] = driver_version()
    PiHolder     = 0.0;
    PiPtr        = libpointer('doublePtr',PiHolder);
    %get(PiPtr);
    VersionHolder= 00;
    VersionPtr   = libpointer('uint16Ptr',VersionHolder);

    %PVNA_EXPORTED PVNA_Res (uint16_t * version, double *info);
    res = calllib('PocketVnaApi_x64','pocketvna_driver_version',VersionPtr,PiPtr);
    version = VersionPtr.value;
    pi      = PiPtr.value;
    resStr  = result_str(res);
end 

