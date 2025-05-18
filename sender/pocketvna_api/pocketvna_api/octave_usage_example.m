clear pocketvna_octave

# Check Driver Version and PI.May help to detect ABI issues
dv = pocketvna_octave("driver_version");
# It is expected that it is always run successfully
printf("Version: %d,  PI: %f\n", dv.VERSION, dv.PI);

# List Available Devices
devices = pocketvna_octave("list");
if length(devices) > 0
    printf("Devices: ");
    disp(devices);
    printf("\n");
else
    printf("No Device connected");
    return;
end

# Open Very first Device
device = pocketvna_octave("open", devices(1));
if ! device.RESULT
    printf("Cannot open due %s\n", device.RESULT_EXPLAIN);
    return;
end

function last_words ()
  disp ("Bye bye!!");
endfunction
atexit ("last_words");

# No we can work with device
global handle
handle = device.DEVICE_HANDLE;

# Get Device Version
deviceVersions = pocketvna_octave("version",  handle);
if deviceVersions.RESULT
   printf("DEVICE VERSION: 0x%x\n", deviceVersions.VERSION);
else
   printf("Getting Device version failed\n")
   pocketvna_octave("close", handle);
   return;
end

# Get Some Settings
settings = pocketvna_octave("settings", handle);
if settings.RESULT
    printf("Valid Frequency Range: [%f,%f] \n", min(settings.VALID_FREQUENCY),      max(settings.VALID_FREQUENCY));
    printf("Reasonable Freq Range: [%f,%f] \n", min(settings.REASONABLE_FREQUENCY), max(settings.REASONABLE_FREQUENCY));
    printf("Z0: %f\n", settings.Z0);
    printf("Supported Modes: ");
    disp(settings.MODES);
    printf("\n");
else
   printf("settings failed");
   pocketvna_octave("close", handle);
   return;
end

# Check if device is valid still
is_valid = pocketvna_octave("valid?", handle);
if is_valid
   printf("Connection is valid\n");
else 
   printf("Connection is INVALID\n");
   pocketvna_octave("close", handle);
   return;
end

# ---------------------------------------------------------------------
function scan4 (frequencies,avg, varargin)
    global handle;
    net  = pocketvna_octave("scan", handle, frequencies, avg,varargin{:});
    if net.RESULT
        printf("Network: %d\n",length(frequencies) );
        disp(size(net.Network) );
        disp(net.Network);
    else
        printf("Network scan failed: %s (%s)\n", net.error, net.RESULT_EXPLAIN);
    endif
endfunction

# Scan by range
printf("Full Network scan for Range\n");
frequencyRange = 100000:100005;
scan4(frequencyRange,4)


# Scan by range 2
printf("Full Network scan for Range2\n");
frequencyRange2 = 1000000:2000000:30000000
scan4(frequencyRange2, 1)

# Scan Full Network by Vector
printf("Full Network scan for Vector\n");
frequencyVector=[100000, 2000000, 4000000000];
scan4(frequencyVector, 1)


# Should fail
printf("Full Network with error\n");
outOfRange=[9E+9];
scan4(outOfRange, 1);

# Scan S11 Only
printf("S11 Only Network\n");
anotherScan=[1E+9];
scan4(anotherScan, 1, 's11');

# Scan Reflections  Only
printf("Reflections Only Network\n");
anotherScan=[1E+9,2E+9,3E+9];
scan4(anotherScan, 1, 's11', 's22');

# Scan Transmissions  Only
printf("Transmissions Only Network\n");
anotherScan=[1E+9,2E+9,3E+9];
scan4(anotherScan, 1, 's21', 's12');

printf("exiting\n");
pocketvna_octave("close", handle);
