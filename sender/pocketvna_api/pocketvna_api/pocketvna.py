"""@package pocketvna
Python binding for pocketvna API
# @file
#  @defgroup API pocketVna API
"""

#import ctypes
from ctypes import *
import os
import sys
import platform


NUMPY= None
try:
    import numpy
    NUMPY= True
except ImportError:
    NUMPY= False

SKRF = None
try:
    import skrf
    SKRF = True
except ImportError:
    SKRF = False

def priv_architecture_():
    #if sys.version_info >= (2,7):
    arch, maxsize  = platform.architecture()[0], 0 #sys.maxsize
    if arch.startswith('32'):   # and not (maxsize > 2 ** 32):
        return '_x32'
    elif arch.startswith('64'): # and (maxsize > 2 ** 32):
        return '_x64'
    else:
        return ''


def priv_get_os_():
    if os.name == 'nt' or sys.platform.startswith('win32'):
        return "windows"
    elif sys.platform.startswith('linux'):
        return "linux"
    elif sys.platform.startswith('darwin'):
        return "macos"
    else:
        return None

BaseName = 'PocketVnaApi'
ARCH     = priv_architecture_()
OS       = priv_get_os_()
## API_VERSION_SEARCH_TAG
VERSION  = 110  # Version in target dll/so/dylib driver

def priv_find_file_(filename, thispath):
    for fn in os.listdir(os.path.join(thispath)):
        if (filename in fn) and ( (".so" in fn) or (".dll" in fn) or (".dylib" in fn) ):
            return os.path.join(thispath, fn)
    return None

def priv_compound(bn, architect=''):
    return bn + architect

def priv_load_library_(orig_fn):
    global PVNA
    pocketvna_path = os.path.dirname(os.path.abspath(__file__))
    try:
        PVNA = CDLL(orig_fn)
        return PVNA
    except OSError:
        another_try = priv_find_file_(priv_compound(BaseName, ARCH), pocketvna_path)
        if another_try is None:
            another_try = priv_find_file_(priv_compound(BaseName), pocketvna_path)

        if another_try is None:
            raise

        #print('WARNING: Could not load "{}" by systempath. Trying another one "{}"'.format(orig_fn, another_try))
        print('WARNING: Could not load "'+str(orig_fn)+'" by systempath. Trying another one "'+str(another_try)+'"')

        PVNA = CDLL(another_try)
        return PVNA



def priv_get_lib_name_():
    if OS == "windows":
        #return '{}{}'.format(BaseName, ARCH)
        return priv_compound(BaseName, ARCH)
    elif OS == 'linux':
        #return 'lib{}{}.so'.format(BaseName, ARCH)
        return 'lib' + priv_compound(BaseName, ARCH) + '.so'
    elif OS == 'macos':
        #return 'lib{}{}.dylib'.format(BaseName, ARCH)
        return 'lib' + priv_compound(BaseName, ARCH) + '.dylib'
    else:
        #return '{}{}'.format(BaseName, ARCH)
        return priv_compound(BaseName, ARCH)

pocketvna = priv_load_library_(priv_get_lib_name_())

PVNA = pocketvna


def inc():
    global EnumCount

    if EnumCount is None:
        EnumCount = 0

    v = EnumCount
    EnumCount = EnumCount + 1

    return v

EnumCount = 0

class Result:
    OK            = inc()
    NoDevice      = inc()
    NoMemory      = inc()
    InitError     = inc()
    BadDescriptor = inc()

    DeviceLocked  = inc()

    BadDevicePath = inc()
    AcessDenied   = inc()
    CouldNotOpen  = inc()
    InvalidHandle = inc()

    BadTrans      =inc()
    UnsupportedTrans=inc()
    BadFrequency  = inc()  #12
    ReadFailure   =inc()
    EmptyResponse =inc()
    IncompleteResponse=inc()
    WriteFailure  =inc()
    ArrayTooBig   =inc()
    BadResponse   =inc()

    RESP_Unused_Firmware_Section  =inc()

    DEV_UnknownMode =inc() #20
    DEV_UnknownParam=inc()
    DEV_NoInit      =inc()
    DEV_LowFreq     =inc()
    DEV_HighFreq    =inc()
    DEV_OutOfBound  =inc()
    DEV_UnknownVar  =inc()
    DEV_UnknownError=inc()
    DEV_BadFormat   =inc()

    RESP_Unused_Extended = inc()
    RESP_ScanCanceled    = inc()

    RESP_MATH_Section    = inc()
    RESP_Res_No_Data     = inc()

    PVNA_Res_LIBUSB_Error= inc()
    PVNA_Res_LIBUSB_CanNotSelectInterface= inc()
    PVNA_Res_LIBUSB_Timeout= inc()
    PVNA_Res_LIBUSB_Busy   = inc()

    PVNA_Res_VCI_PrepareScanError= inc()
    PVNA_Res_VCI_Response_Error= inc()
    PVNA_Res_EndLEQStart       = inc()

    PVNA_Res_VCI_Failed2OpenProbablyDriver = inc()
    PVNA_Res_HID_AdditionalError = inc()

    PVNA_Res_NotImplemented  = inc()
    PVNA_Res_BadArgument     = inc()

    PVNA_Res_Fail=0xFFFF

class ConnectionInterfaceCode:
    CIface_HID = 0x10
    CIface_VCI = 0x20

class Access:
    Denied = 0x00
    Read   = 0x01
    Write  = 0x02
    Busy   = 0x10

class NetworkParams:
    Non   = 0x00
    S21   = 0x0001
    S11   = 0x0002
    S12   = 0x0004
    S22   = 0x0008

    S13   = 0x0010
    S14   = 0x0040
    S23   = 0x0020
    S24   = 0x0080

    S31   = 0x0100
    S32   = 0x0400
    S41   = 0x0200
    S42   = 0x0800

    S33   = 0x1000
    S34   = 0x4000
    S43   = 0x2000
    S44   = 0x8000

    ALL_2P   = S11 | S21 | S12 | S22
    PORT1 = S11 | S21
    PORT2 = S22 | S12
    REFL  = S11 | S22
    TRANS = S21 | S12

    class Util2Port:
        AllSupported = '*'

    class Util4Port:
        ALL        =0xFFFF
        Path1      =0x000F
        Path2      =0xF000
        Reflections=0x900A
        BothPaths  = Path1|Path2

    def to_matrix_indeces(param):
        accordance = {
            NetworkParams.S11: (0,0),
            NetworkParams.S12: (0,1),
            NetworkParams.S13: (0,2),
            NetworkParams.S14: (0,3),

            NetworkParams.S21: (1,0),
            NetworkParams.S22: (1,1),
            NetworkParams.S23: (1,2),
            NetworkParams.S24: (1,3),

            NetworkParams.S31: (2,0),
            NetworkParams.S32: (2,1),
            NetworkParams.S33: (2,2),
            NetworkParams.S34: (2,3),

            NetworkParams.S41: (3,0),
            NetworkParams.S42: (3,1),
            NetworkParams.S43: (3,2),
            NetworkParams.S44: (3,3),
        }
        return accordance[param]

class Distributions:
    Linear = 0x01
    Logarithmic = 0x02

Cancel = 0
Continue = 1

class DeviceDescriptor(Structure):
    _fields_ = [
                ("path",       c_char_p),   # Path to device
                ("access",     c_uint32),   # Flags whether we have R or W rights. Useful on Linux
                ("sn",         c_wchar_p),  # Serial Number
                ("vendor",     c_wchar_p),  #
                ("product",    c_wchar_p),
                ("version",    c_uint16),
                ("pid",        c_uint16),
                ("vid",        c_uint16),
                ("ifaceCode",  c_uint16),   # since 0.70 it contains interface code from ConnectionInterfaceCode
                ("next",       c_void_p)
     ]

class Priv_SParam(Structure):
    _fields_ = [
        ("real", c_double),
        ("imag", c_double)
    ]

class DriverOptionsEnum:
    LogLevel=0x00
    class LogLevelsEnum:
        none    =0
        critical=1
        warning =2
        info    =3
        debug   =4

class CtrlVars:
    MeasurementsMode = 0x0907
    ConsistencyLevel = 0x09C0

    class ConsistencyLevelValue:
        Off =0x0D
        ON  =0x0E
        Full=0x0A

    class MeasurementsModeValue:
        RawMeas           = 0x01
        CaliMeas          = 0x02
        InternalCaliShort = 0x03
        InternalCaliOpen  = 0x04
        InternalCaliLoad  = 0x05
        InternalShort     = 0x06
        InternalOpen      = 0x07
        InternalLoad      = 0x08
        InternalThru      = 0x09
        InternalCaliThru  = 0x0a


DeviceHandler        = c_void_p
UserData             = c_void_p
DeviceDescriptorList = POINTER(DeviceDescriptor)
ReturnType           = c_uint
DeviceHandlerPtr     = POINTER(DeviceHandler)
NetworkParam         = c_uint
Frequency            = c_uint64
FrequencyPtr         = POINTER(Frequency)
Average              = c_uint16
Version              = c_uint16
Priv_SParamRef       = POINTER(Priv_SParam)
Priv_SParamArray     = (POINTER(c_double))
Priv_SParams4Port    = POINTER( POINTER(c_double) )
Priv_ContinueCode    = c_uint
Distribution         = c_uint
# typedef PVNA_ContinueCode (*PVNA_PFN_Progress_Func) (PVNA_UserDataPtr, uint32_t);
ProgressProc         = CFUNCTYPE(Priv_ContinueCode, UserData, c_uint32)

# -----------------------------------------------------
def to_progress_proc(callback):
    return ProgressProc(callback) if callback is not None else ProgressProc(0) # lambda u, current_index: Continue # as lambda: idle proc

def zeros_Priv_SParams(size):
    return numpy.zeros(size * 2, dtype=numpy.float64)

def reinterpret_doubles_as_complex(array):
    assert array.dtype == numpy.float64
    return array.view(dtype=numpy.complex128)

def to_ptr(numpy_Priv_SParams):
    return numpy_Priv_SParams.ctypes.data_as(POINTER(c_double))

def freq2ptr(numpy_Priv_SParams):
    return numpy_Priv_SParams.ctypes.data_as(POINTER(c_uint64))

def complex_at(sa, idx):
    return complex(sa[idx * 2], sa[idx * 2 + 1])

def zeros_complex(size):
    return numpy.zeros(size, dtype=numpy.complex128)


def commplexArray2SParams(complex_array):
    sz  = len( complex_array )
    dut = zeros_Priv_SParams(sz)
    for i in range(0, sz):
        dut[i * 2] = complex_array[i].real
        dut[i * 2 + 1] = complex_array[i].imag
        #    return complex(sa[idx * 2], sa[idx * 2 + 1])

    return dut

def copyComplexesIntoSParams(complex_list, sparams_list):
    assert len(complex_list) * 2 == len(sparams_list)

    for i in range(0, len(complex_list)):
        sparams_list[i * 2] = complex_list[i].real
        sparams_list[i * 2 + 1] = complex_list[i].imag

def copySParamsIntoComplexes(sparams_list):
    assert (len(sparams_list) % 2) == 0
    sz = len(sparams_list) // 2
    res = [0j] * sz
    for i in range(0, sz):
        res[i] = complex_at(sparams_list, i)

    return res

def to_complex_lists(scan_sparam_list, points_count, total_param_count):
    assert len(scan_sparam_list) == total_param_count

    result_list = [ [0j]*points_count for i in range(0, total_param_count) ]
    assert len(result_list)    == total_param_count
    assert len(result_list[0]) == points_count

    for arrayIndex in range(0, total_param_count):
        for pointIndex in range(0, points_count ):
            result_list[arrayIndex][pointIndex] = complex_at(scan_sparam_list[arrayIndex], pointIndex)

    return result_list

# -----------------------------------------------------

class PocketVnaError(RuntimeError):
    def __init__(self, message):
        super(RuntimeError, self).__init__(message)

class PocketVnaScanCanceled(PocketVnaError):
    def __init__(self, message):
        super(PocketVnaError, self).__init__(message)


class PocketVnaAPIError(PocketVnaError):
    def code(self):
        return self.error_code

    def __init__(self, message, error_code):
        super(PocketVnaError, self).__init__(message + '[' + Result2Str(error_code) + ']')

        # Now for your custom code...
        self.error_code = error_code

class PocketVnaUnexpectedBehavior(PocketVnaError):
    def __init__(self, message):
        super(PocketVnaError, self).__init__(message)

class PocketVnaHandlerInvalid(PocketVnaError):
    def __init__(self):
        super(PocketVnaError, self).__init__("Handler is not valid or device has been gone")

class PocketVnaAccessDenied(PocketVnaError):
    def __init__(self, additional):
        if OS == "linux":
            super(PocketVnaError, self).__init__('Access Denied. Probably you have no RW Permissions to use the device. '+
                "Try to create *.rules file, Or modify permissions with chmod, or use sudo. "+
                "Main sign of this problem is you see the device its SN,Product so on but can not connect. "+
                str(additional))
        else:
            super(PocketVnaError, self).__init__("Access Denied. For some reason you have no permission to connect to device")

def check_OK(code, message):
    if code != Result.OK:
        if code == Result.InvalidHandle:
            raise PocketVnaHandlerInvalid()
        if code == Result.AcessDenied:
            raise PocketVnaAccessDenied(':(')
        if code == Result.RESP_ScanCanceled:
            raise PocketVnaScanCanceled('scan canceled manually (by callback)')
        raise PocketVnaAPIError(message, code)


## ------------- Connect stuff ----------------------------------


# PVNA_EXPORTED PVNA_Res pocketvna_driver_version(uint16_t * version, double *info);
PVNA.pocketvna_driver_version.argtypes = [POINTER(Version), POINTER(c_double)]
PVNA.pocketvna_driver_version.restype  = ReturnType

def driver_version():
    p1 = Version (0)
    p2 = c_double (0.0)

    r = PVNA.pocketvna_driver_version(byref(p1), byref(p2))

    check_OK( r, "Could not get Driver Version" )

    return p1.value, p2.value

# PVNA_EXPORTED void pocketvna_set_option(enum PocketVNAOptions opt, int64_t value);
PVNA.pocketvna_set_option.argtypes = [c_uint, c_int64]
PVNA.pocketvna_set_option.restype  = None  # https://docs.python.org/3.6/library/ctypes.html#return-types

# @option_code from DriverOptionsEnum.*
# @value       from subclass DriverOptionsEnum.*Enum.
def set_driver_option(option_code, value):
    PVNA.pocketvna_set_option(option_code, value)

# PVNA_EXPORTED PVNA_Res   pocketvna_close();
PVNA.pocketvna_close.restype  = ReturnType

def close_api():
    r = PVNA.pocketvna_close()
    check_OK( r, "Close API should be always OK" )

# PVNA_EXPORTED const char * pocketvna_result_string(PVNA_Res code);
PVNA.pocketvna_result_string.argtypes = [ReturnType]
PVNA.pocketvna_result_string.restype  = c_char_p

def result_string(error_code):
    msg = PVNA.pocketvna_result_string(error_code)
    if sys.version_info >= (3,0):
        msg = msg.decode('utf-8')

    return msg

def Result2Str(error_code):
    text = result_string(error_code)
    return text + '(' + str(error_code) + ')'

# PVNA_Res   pocketvna_list_devices(PVNA_DeviceDesc ** list, uint16_t * size);
PVNA.pocketvna_list_devices.argtypes = [POINTER(DeviceDescriptorList), POINTER(c_uint16)]
PVNA.pocketvna_list_devices.restype  = ReturnType

def list_devices():
    lst = DeviceDescriptorList()
    sz = c_uint16(0)

    r = PVNA.pocketvna_list_devices(byref(lst), byref(sz))

    if r == Result.NoDevice: return [], 0

    check_OK(r, "Failed to enumerate devices")

    return lst, sz.value

# PVNA_Res   pocketvna_free_list(PVNA_DeviceDesc ** list);
PVNA.pocketvna_free_list.argtypes = [POINTER(DeviceDescriptorList)]
PVNA.pocketvna_free_list.restype  = ReturnType

def free_list(lst):
    r = PVNA.pocketvna_free_list(byref(lst))

    check_OK(r, "Failed to free_list")

    if bool(lst):
        raise PocketVnaUnexpectedBehavior("free_list should Zero a reference. API returned OK status but the reference is not NULL")


## ------------- Connect stuff ----------------------------------

#     PVNA_Res   pocketvna_get_device_handle_for(const PVNA_DeviceDesc* desc, PVNA_DeviceHandler * handle)
PVNA.pocketvna_get_device_handle_for.argtypes = [POINTER(DeviceDescriptor), DeviceHandlerPtr]
PVNA.pocketvna_get_device_handle_for.restype  = ReturnType

def get_device_handler(desc_ptr):
    h = DeviceHandler()
    r = PVNA.pocketvna_get_device_handle_for(desc_ptr, byref(h))

    check_OK(r, "Failed to get device handler")

    if not bool(h):
        raise PocketVnaUnexpectedBehavior("Handler is invalid. API reported Ok status but handler is invalid")

    return h

#     PVNA_Res   pocketvna_release_handle(PVNA_DeviceHandler * handle)
PVNA.pocketvna_release_handle.argtypes = [DeviceHandlerPtr]
PVNA.pocketvna_release_handle.restype  = ReturnType
def release_handler(handler):
    assert handler is not None

    r = PVNA.pocketvna_release_handle(byref(handler))

    check_OK(r, "Failed to release handler")

    if bool(handler):
        raise PocketVnaUnexpectedBehavior("release_handler should Zero a reference. API returned Ok status but handler is not NULL")

#    PVNA_Res   pocketvna_get_first_device_handle(PVNA_DeviceHandler * handle);
PVNA.pocketvna_get_first_device_handle.argtypes = [DeviceHandlerPtr]
PVNA.pocketvna_get_first_device_handle.restype  = ReturnType

def get_first_available_device_handler():
    h = DeviceHandler()
    r = PVNA.pocketvna_get_first_device_handle(byref(h))

    check_OK(r, "Failed to get device handler")

    if not bool(h):
        raise PocketVnaUnexpectedBehavior("Handler is invalid. API reported Ok status but handler is invalid")

    return h

def create_simulator_description():
    return aux_convert_dictionary_into_descriptor_structure({
        "path": b"simulation",  "SN": "SIMULATOR", "product": "pocketvna", "vendor": "martin",
        "version": 0x100, "ProductId": 0x100, "VendorId": 0x100,
        "InterfaceCode": ConnectionInterfaceCode.CIface_HID})

def open_simulation_device():
    desc = create_simulator_description()

    return get_device_handler(desc)

## *******************************************************************


#     PVNA_Res   pocketvna_is_transmission_supported(const PVNA_DeviceHandler handle, const PVNA_NetworkParam param);
PVNA.pocketvna_is_transmission_supported.argtypes = [DeviceHandler, NetworkParam]
PVNA.pocketvna_is_transmission_supported.restype  = ReturnType

def supports_network_parameter(handler, param):
    r = PVNA.pocketvna_is_transmission_supported(handler, param)

    if r == Result.UnsupportedTrans:
        return False

    if r == Result.OK:
        return True

    check_OK(r, "Failed to ask whether a transmission supported")

    return None

#     PVNA_Res   pocketvna_is_valid(const PVNA_DeviceHandler handle);
PVNA.pocketvna_is_valid.argtypes = [DeviceHandler]
PVNA.pocketvna_is_valid.restype  = ReturnType

def is_valid(handler):
    if not bool(handler): return None

    r = PVNA.pocketvna_is_valid(handler)

    if r == Result.InvalidHandle:
        return False

    if r == Result.OK:
        return True

    check_OK(r, "Failed to check whether the handler is valid")

    return None

#     PVNA_Res   pocketvna_version(const PVNA_DeviceHandler handle, uint16_t * version);
PVNA.pocketvna_version.argtypes = [DeviceHandler, POINTER(Version)]
PVNA.pocketvna_version.restype  = ReturnType

def get_version(handle):
    ver = Version(0)

    r = PVNA.pocketvna_version(handle, byref(ver))

    check_OK(r, "Failed to get a firmware version")

    return ver.value

#     PVNA_Res   pocketvna_get_characteristic_impedance(const PVNA_DeviceHandler handle, double * R);
PVNA.pocketvna_get_characteristic_impedance.argtypes = [DeviceHandler, POINTER(c_double)]
PVNA.pocketvna_get_characteristic_impedance.restype  = ReturnType

def get_characteristic_impedance(handle):
    rr = c_double(0.0)

    r = PVNA.pocketvna_get_characteristic_impedance(handle, byref(rr))

    check_OK(r, "Failed to get a Characteristic Impedance (aka Reference Resistance/Impedance, Zero Resistance/Impedance)")


    return rr.value

#  PVNA_Res   pocketvna_get_valid_frequency_range(const PVNA_DeviceHandler handle, PVNA_Frequency * from, PVNA_Frequency *to);
PVNA.pocketvna_get_valid_frequency_range.argtypes = [DeviceHandler, FrequencyPtr, FrequencyPtr]
PVNA.pocketvna_get_valid_frequency_range.restype  = ReturnType

def get_valid_frequency_range(handle):
    start = Frequency(0)
    end   = Frequency(0)

    r = PVNA.pocketvna_get_valid_frequency_range(handle, byref(start), byref(end))

    check_OK(r, "Failed to get Allowed Frequency Range")

    return start.value, end.value

#     PVNA_Res   pocketvna_get_reasonable_frequency_range(const PVNA_DeviceHandler handle, PVNA_Frequency * from, PVNA_Frequency *to);

PVNA.pocketvna_get_reasonable_frequency_range.argtypes = [DeviceHandler, FrequencyPtr, FrequencyPtr]
PVNA.pocketvna_get_reasonable_frequency_range.restype  = ReturnType

def get_reasonable_frequency_range(handle):
    start = Frequency(0)
    end   = Frequency(0)

    r = PVNA.pocketvna_get_reasonable_frequency_range(handle, byref(start), byref(end))

    check_OK(r, "Failed to get Reasonable Frequency Range")

    return start.value, end.value

#     PVNA_Res   pocketvna_single_query(const PVNA_DeviceHandler handle, const PVNA_Frequency frequency, const uint16_t average,
#                                           const PVNA_NetworkParam params,
#                                           PVNA_SParam * s11,  PVNA_SParam * s21,
#                                           PVNA_SParam * s12,  PVNA_SParam * s22);
# -------------------------------------
PVNA.pocketvna_single_query.argtypes = [DeviceHandler, Frequency, Average,
                                            NetworkParam,
                                            Priv_SParamRef,  Priv_SParamRef,
                                            Priv_SParamRef,  Priv_SParamRef ]
PVNA.pocketvna_single_query.restype  = ReturnType

def scan_frequency(handle, freq, avg, netparams):
    s11,  s21 = Priv_SParam(0.0, 0.0),  Priv_SParam(0.0, 0.0)
    s12,  s22 = Priv_SParam(0.0, 0.0),  Priv_SParam(0.0, 0.0)

    r = PVNA.pocketvna_single_query(handle, Frequency(freq), c_uint16(avg),
                                         NetworkParam(netparams),
                                         byref(s11), byref(s21),
                                         byref(s12), byref(s22)
    )

    check_OK( r, 'Failed to scan for frequency ' + str(freq) )


    return complex(s11.real, s11.imag), complex(s21.real, s21.imag), complex(s12.real, s12.imag),  complex(s22.real, s22.imag)

#     PVNA_Res   pocketvna_multi_query(const PVNA_DeviceHandler handle, const PVNA_Frequency * frequencies, const uint32_t size,
#                                         const uint16_t average, const PVNA_NetworkParam params,
#                                         PVNA_SParam * s11a, PVNA_SParam * s21a,
#                                         PVNA_SParam * s12a, PVNA_SParam * s22a,
#                                         PVNA_ProgressCallBack * progress);
# PVNA.pocketvna_multi_query.argtypes = [DeviceHandler, FrequencyPtr, c_uint32,
#                                             Average,  NetworkParam,
#                                             Priv_SParamArray, Priv_SParamArray,
#                                             Priv_SParamArray, Priv_SParamArray,
#                                             c_void_p]
# PVNA.pocketvna_multi_query.restype  = ReturnType

#   PVNA_EXPORTED PVNA_Res   pocketvna_multi_query_with_cproc(const PVNA_DeviceHandler handle,
#                                       const PVNA_Frequency * frequencies, const uint32_t size,
#                                       const uint16_t average, const PVNA_NetworkParam params,
#                                       PVNA_Sparam * s11a, PVNA_Sparam * s21a,
#                                       PVNA_Sparam * s12a, PVNA_Sparam * s22a,
#                                       PVNA_PFN_Progress_Func progress);
PVNA.pocketvna_multi_query_with_cproc.argtypes = [DeviceHandler, FrequencyPtr, c_uint32,
                                        Average,  NetworkParam,
                                        Priv_SParamArray, Priv_SParamArray,
                                        Priv_SParamArray, Priv_SParamArray,
                                        ProgressProc]
PVNA.pocketvna_multi_query_with_cproc.restype  = ReturnType

def pyth27fix_pocketvna_multi_query_with_cproc_wrapper(device_handle, freqs_ptr, count,
                                        average,  network_params,
                                        s11, s21, s12, s22,
                                        callback):
    return PVNA.pocketvna_multi_query_with_cproc(device_handle, freqs_ptr, count,
                                average, network_params,
                                s11, s21, s12, s22,
                                callback)

def scan_frequencies(handle, freqs, avg, netparams, callback):
    const_total_params_count = 4
    freq   = numpy.array(freqs, numpy.uint64)
    size   = len(freq)

    ses  = [ zeros_Priv_SParams(size) for i in range(0,const_total_params_count) ]

    r = pyth27fix_pocketvna_multi_query_with_cproc_wrapper(handle, freq2ptr(freq), c_uint32(size),
                                Average(avg), NetworkParam(netparams),
                                *[ to_ptr(ses[i]) for i in range(0,const_total_params_count) ],
                                callback=to_progress_proc(callback)
    )

    check_OK(r, "Failed to scan a set of frequencies")

    rses = [ reinterpret_doubles_as_complex(ses[i]) for i in range(0,const_total_params_count) ]

    assert len(rses) == 4

    return rses # s11, s21, s12, s22


def scan_frequencies_no_numpy(handle, freqs, avg, netparams, callback):
    const_total_param_count = 4
    sz = len(freqs)
    frquencies=Frequency * sz
    ftopass =frquencies(*list(freqs))

    dsz = sz * 2
    sarray = c_double * dsz
    rses = [ sarray(*list([0]*dsz)) for i in range(0, const_total_param_count) ]

    r = pyth27fix_pocketvna_multi_query_with_cproc_wrapper(handle, ftopass, c_uint32(sz),
                                Average(avg), NetworkParam(netparams),
                                *rses,
                                callback=to_progress_proc(callback)
    )

    check_OK(r, "Failed to scan a set of frequencies no-numpy variant")

    result = to_complex_lists(rses, sz, const_total_param_count)

    return result # s11, s21, s12, s22

#    PVNA_EXPORTED PVNA_Res   pocketvna_range_query_with_cproc(
#            const PVNA_DeviceHandler handle,
#            const PVNA_Frequency start, const PVNA_Frequency end, const uint32_t size, enum PocketVNADistribution distr,
#            const uint16_t average, const PVNA_NetworkParam params,
#            PVNA_Sparam * s11a, PVNA_Sparam * s21a,
#            PVNA_Sparam * s12a, PVNA_Sparam * s22a,
#            PVNA_PFN_Progress_Func progress
#    );
PVNA.pocketvna_range_query_with_cproc.argtypes = [DeviceHandler,
                                        Frequency, Frequency, c_uint32, Distribution,
                                        Average,  NetworkParam,
                                        Priv_SParamArray, Priv_SParamArray,
                                        Priv_SParamArray, Priv_SParamArray,
                                        ProgressProc]
PVNA.pocketvna_range_query_with_cproc.restype   = ReturnType

def pyth27fix_pocketvna_range_query_with_cproc_wrapper(device_handler,
                                        start_frequency, end_frequency, count, distribution,
                                        averaging,  network_param,
                                        s11, s21, s12, s22,
                                        callback):
    return PVNA.pocketvna_range_query_with_cproc(device_handler,
                                        start_frequency, end_frequency, count, distribution,
                                        averaging,  network_param,
                                        s11, s21, s12, s22,
                                        callback)

def scan_frequencies_for_range(handle, startFreq, endFreq, steps, distibution, avg, netparams, callback):
    const_total_params_count = 4
    ses  = [ zeros_Priv_SParams(steps) for i in range(0,const_total_params_count) ]

    startFreq, endFreq = int(startFreq), int(endFreq)

    r = pyth27fix_pocketvna_range_query_with_cproc_wrapper(handle,
                Frequency(startFreq), Frequency(endFreq), c_uint32(steps), c_uint(distibution),
                Average(avg), NetworkParam(netparams),
                *[ to_ptr(ses[i]) for i in range(0,const_total_params_count) ],
                callback=to_progress_proc(callback)
    )

    check_OK(r, "Failed to scan for a frequency range")

    rses = [ reinterpret_doubles_as_complex(ses[i]) for i in range(0,const_total_params_count) ]

    assert len(rses) == 4

    return rses

def scan_frequencies_for_range_no_numpy(handle, startFreq, endFreq, steps, distibution, avg, netparams, callback):
    const_total_param_count = 4
    dsz = steps * 2
    sarray = c_double * dsz
    rs = [sarray(*list([0]*dsz)) for i in range(0,const_total_param_count)]
    startFreq, endFreq = int(startFreq), int(endFreq)

    r = pyth27fix_pocketvna_range_query_with_cproc_wrapper(handle,
                Frequency(startFreq), Frequency(endFreq), c_uint32(steps), c_uint(distibution),
                Average(avg), NetworkParam(netparams),
                *rs,
                callback=to_progress_proc(callback)
    )

    check_OK(r, "Failed to scan for a frequency range no-numpy variant")

    result = to_complex_lists(rs, steps, const_total_param_count)

    return result

## --- For test purposes
#PVNA_Res   pocketvna_debug_response(const PVNA_DeviceHandler handle, const uint32_t size, PVNA_Sparam * p1, PVNA_Sparam * p2)
PVNA.pocketvna_debug_response.argtypes = [DeviceHandler, c_uint32,
                                            Priv_SParamArray, Priv_SParamArray]
PVNA.pocketvna_debug_response.restype  = ReturnType

def debug_response(handle, size):
    ps = [ zeros_Priv_SParams(size) for i in range(0,2) ]

    r = PVNA.pocketvna_debug_response(handle,  c_uint32(size),
                                      *[ to_ptr(ps[i]) for i in range(0,2) ])

    check_OK(r, "Failed to get debug_response")

    rs = [reinterpret_doubles_as_complex(ps[i]) for i in range(0,2)]

    return rs

def debug_response_no_numpy(handle, size):
    dsz = size * 2
    sarray = c_double * dsz

    ps = [ sarray(*list([0]*dsz)) for i in range(0,2) ]

    r = PVNA.pocketvna_debug_response(handle,  c_uint32(size), *ps)

    check_OK(r, "Failed to get debug_response no numpy variant")

    result =  to_complex_lists(ps, size, 2)

    return result

## ***


# ------ INFO subset: request some state from firmware immediately ----------------------------------------
#   PVNA_Res   pocketvna_info_get_firmware_version(const PVNA_DeviceHandler handle, uint16_t * version);
PVNA.pocketvna_info_get_firmware_version.argtypes = [DeviceHandler, POINTER(Version)]
PVNA.pocketvna_info_get_firmware_version.restype  = ReturnType

def info_get_firmware_version(handle):
    ver = Version(0)

    r = PVNA.pocketvna_info_get_firmware_version(handle, byref(ver))

    check_OK(r, "Failed to get a firmware version")

    return ver.value

#  PVNA_Res   pocketvna_info_get_param_supported(const PVNA_DeviceHandler handle, const PVNA_NetworkParam params);
PVNA.pocketvna_info_get_param_supported.argtypes = [DeviceHandler, NetworkParam]
PVNA.pocketvna_info_get_param_supported.restype  = ReturnType

def info_get_param_supported(handle, netparam):
    r = PVNA.pocketvna_info_get_param_supported(handle, NetworkParam(netparam))
    if r == Result.UnsupportedTrans:
        return False

    if r == Result.OK:
        return True

    check_OK(r, "Failed to ask whether a transmission supported")

    return None

# PVNA_EXPORTED PVNA_Res   pocketvna_info_get_temperature(const PVNA_DeviceHandler handle, double * kalvin_temperature)
PVNA.pocketvna_info_get_temperature.argtypes = [DeviceHandler, POINTER(c_double)]
PVNA.pocketvna_info_get_temperature.restype  = ReturnType

def info_get_temperature(handle):
    p2 = c_double (0.0)

    r = PVNA.pocketvna_info_get_temperature(handle, byref(p2))

    check_OK( r, "Could not get Temperature" )

    return p2.value

# PVNA_EXPORTED PVNA_Res   pocketvna_info_get_variable(const PVNA_DeviceHandler handle, const uint8_t * _6bytes_code, uint8_t * _6bytes_output);
PVNA.pocketvna_info_get_variable.argtypes = [DeviceHandler, POINTER(c_uint8), POINTER(c_uint8)]
PVNA.pocketvna_info_get_variable.restype  = ReturnType

def info_get_variable(handle, _6bytes):
    request = numpy.array(_6bytes, dtype=numpy.uint8)
    request = numpy.resize(request, 6)

    # Previous
    output  = numpy.zeros(64, dtype=numpy.uint8)

    r = PVNA.pocketvna_info_get_variable(handle, request.ctypes.data_as(POINTER(c_uint8)),   output.ctypes.data_as(POINTER(c_uint8)) )

    check_OK( r, "Could not get Internal Variable" )

    return output


# //-------------- Query stuff ------------------------------------
PVNA.pocketvna_force_unlock_devices.argtypes = []
PVNA.pocketvna_force_unlock_devices.restype  = ReturnType

def force_unlock():
    r = PVNA.pocketvna_force_unlock_devices()
    check_OK(r, "Failed to Unlock Devices")


# PVNA_EXPORTED PVNA_Res pocketvna_rfmath_calibrate_transmission(
#             const PVNA_Sparam * raw_meas_mn,
#             const PVNA_Sparam * open_thru_mn, const PVNA_Sparam * thru_mn,
#             const uint32_t size,
#             PVNA_Sparam * dut_mn
#     );
PVNA.pocketvna_rfmath_calibrate_transmission.argtypes = [
                Priv_SParamArray,                    # meas
                Priv_SParamArray, Priv_SParamArray,  # open, thru
                c_uint32,
                Priv_SParamArray                     # dut-calibrated
]
PVNA.pocketvna_rfmath_calibrate_transmission.restype  = ReturnType

def calibrate_transmission_numpy(raw_meas_mn, open_mn, thru_mn):
    if not NUMPY:
        raise NotImplementedError("no numpy library imported")

    size = len(raw_meas_mn)
    if size != len(open_mn) or size != len(thru_mn):
        raise RuntimeError("calibrate_transmission: all arguments should be of the same size")

    raw   = commplexArray2SParams(raw_meas_mn)
    opn   = commplexArray2SParams(open_mn)
    thru  = commplexArray2SParams(thru_mn)
    dut   = zeros_Priv_SParams(size)

    r = PVNA.pocketvna_rfmath_calibrate_transmission(to_ptr(raw), to_ptr(opn), to_ptr(thru), c_uint32(size), to_ptr(dut))
    check_OK(r, "transmission calibration")

    return reinterpret_doubles_as_complex(dut)

def calibrate_transmission_no_numpy(raw_meas_mn, open_mn, thru_mn):
    size = len(raw_meas_mn)
    if size != len(open_mn) or size != len(thru_mn):
        raise RuntimeError("calibrate_transmission: all arguments should be of the same size")

    dsz = size * 2
    sarray = c_double * dsz

    raw   = sarray(*list([0.0]*dsz))
    copyComplexesIntoSParams(raw_meas_mn, raw)

    opn   = sarray(*list([0.0]*dsz))
    copyComplexesIntoSParams(open_mn, opn)

    thru  = sarray(*list([0.0]*dsz))
    copyComplexesIntoSParams(thru_mn, thru)

    dut   = sarray(*list([0.0]*dsz))

    r = PVNA.pocketvna_rfmath_calibrate_transmission((raw),
        (opn), (thru),
        c_uint32(size),
        (dut)
    )
    check_OK(r, "transmission calibration")

    return copySParamsIntoComplexes(dut)

# PVNA_EXPORTED PVNA_Res pocketvna_rfmath_calibrate_reflection(
#             const PVNA_Sparam * raw_meas_mm,
#             const PVNA_Sparam * short_mm, const PVNA_Sparam * open_mm, const PVNA_Sparam * load_mm,
#             const uint32_t size,
#             double Z0,
#             PVNA_Sparam * dut_mm
#     );
PVNA.pocketvna_rfmath_calibrate_reflection.argtypes = [
                Priv_SParamArray,                    # meas
                Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, # short, open, load
                c_uint32,   # size
                c_double,   # Z0
                Priv_SParamArray                     # dut-calibrated
]
PVNA.pocketvna_rfmath_calibrate_reflection.restype  = ReturnType

def calibrate_reflection_numpy(raw_meas_mm, short_mm, open_mm, load_mm, z0):
    if not NUMPY:
        raise NotImplementedError("no numpy library imported")

    size = len(raw_meas_mm)
    if size != len(short_mm) or size != len(open_mm) or size != len(load_mm):
        raise RuntimeError("calibrate_reflection (numpy): all arguments should be of the same size")

    raw   = commplexArray2SParams(raw_meas_mm)
    sht   = commplexArray2SParams(short_mm)
    opn   = commplexArray2SParams(open_mm)
    load  = commplexArray2SParams(load_mm)

    dut   = zeros_Priv_SParams(size)

    r = PVNA.pocketvna_rfmath_calibrate_reflection(to_ptr(raw),
        to_ptr(sht), to_ptr(opn), to_ptr(load),
        c_uint32(size), c_double(z0),
        to_ptr(dut))
    check_OK(r, "reflection calibration")

    return reinterpret_doubles_as_complex(dut)

def calibrate_reflection_no_numpy(raw_meas_mm, short_mm, open_mm, load_mm, z0):
    size = len(raw_meas_mm)
    if size != len(short_mm) or size != len(open_mm) or size != len(load_mm):
        raise RuntimeError("calibrate_reflection: all arguments should be of the same size")
    dsz = size * 2
    sarray = c_double * dsz

    raw   = sarray(*list([0.0]*dsz))
    copyComplexesIntoSParams(raw_meas_mm, raw)

    sht   = sarray(*list([0.0]*dsz))
    copyComplexesIntoSParams(short_mm, sht)

    opn   = sarray(*list([0.0]*dsz))
    copyComplexesIntoSParams(open_mm, opn)

    load  = sarray(*list([0.0]*dsz))
    copyComplexesIntoSParams(load_mm, load)

    dut   = sarray(*list([0.0]*dsz))

    r = PVNA.pocketvna_rfmath_calibrate_reflection((raw),
        (sht), (opn), (load),
        c_uint32(size), c_double(z0),
        (dut))
    check_OK(r, "reflection calibration")

    return copySParamsIntoComplexes(dut)



# PVNA_EXPORTED PVNA_Res pocketvna_4p_scan_separate_with_cproc(const PVNA_DeviceHandler, const PVNA_Frequency *, const PVNA_Size,
#                  const uint16_t average, const PVNA_NetworkParameters,
#
#                  PVNA_Sparam * s11, PVNA_Sparam * s12,  PVNA_Sparam * s13, PVNA_Sparam * s14,
#                  PVNA_Sparam * s21, PVNA_Sparam * s22,  PVNA_Sparam * s23, PVNA_Sparam * s24,
#                  PVNA_Sparam * s31, PVNA_Sparam * s32,  PVNA_Sparam * s33, PVNA_Sparam * s34,
#                  PVNA_Sparam * s41, PVNA_Sparam * s42,  PVNA_Sparam * s43, PVNA_Sparam * s44,
#
#                  PVNA_PFN_Progress_Func);
PVNA.pocketvna_4p_scan_separate.argtypes = [DeviceHandler, FrequencyPtr, c_uint32,
                                        Average,  NetworkParam,
                                        Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,
                                        Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,
                                        Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,
                                        Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,

                                        ProgressProc]
PVNA.pocketvna_4p_scan_separate.restype   = ReturnType

def pyth27fix_pocketvna_4p_scan_separate_wrapper(device_handler,
                frequency_ptr, count,
                average,  network_param,
                s11, s12, s13, s14,
                s21, s22, s23, s24,
                s31, s32, s33, s34,
                s41, s42, s43, s44,
                callback):
    return PVNA.pocketvna_4p_scan_separate(device_handler, frequency_ptr, count, average,  network_param,
                s11, s12, s13, s14,
                s21, s22, s23, s24,
                s31, s32, s33, s34,
                s41, s42, s43, s44,
                callback)

def scan_frequencies_4Port(handle, freqs, avg, netparams, callback = None):
    if not NUMPY:
        raise NotImplementedError("no numpy library imported")

    freq   = numpy.array(freqs, numpy.uint64)
    size   = len(freq)

    complex_size = size*2 # twice for float is used instead of complex
    matrix_of_arrays = numpy.zeros((4,4,complex_size), dtype=numpy.float64)
    flat_list_of_arrays = matrix_of_arrays.reshape((16, complex_size))

    r = pyth27fix_pocketvna_4p_scan_separate_wrapper(handle, freq2ptr(freq), c_uint32(size),
            Average(avg), NetworkParam(netparams),
            *[  to_ptr(flat_list_of_arrays[i]) for i in range(0, 16) ],
            callback=to_progress_proc(callback)
    )

    check_OK(r, "Failed to scan a set of frequencies")

    return flat_list_of_arrays.view(dtype=numpy.complex128).reshape((4,4,size))

def scan_frequencies_4Port_nonumpy(handle, freqs, avg, netparams, callback = None):
    sz = len(freqs)
    frquencies=Frequency * sz
    ftopass =frquencies(*list(freqs))

    dsz = sz * 2
    sarray = c_double * dsz
    total_size=16
    rses = [sarray(*list([0]*dsz)) for i in range(0,total_size)]

    r = pyth27fix_pocketvna_4p_scan_separate_wrapper(handle, ftopass, c_uint32(sz),
            Average(avg), NetworkParam(netparams),
            *rses,
            callback=to_progress_proc(callback)
    )
    # ------

    check_OK(r, "Failed to scan a set of frequencies no-numpy variant")

    result_list = to_complex_lists(rses, sz, total_size)

    assert len(result_list) == 16    

    matrix = [
        [  result_list[ 0], result_list[ 1], result_list[ 2], result_list[ 3] ],
        [  result_list[ 4], result_list[ 5], result_list[ 6], result_list[ 7] ],
        [  result_list[ 8], result_list[ 9], result_list[10], result_list[11] ],
        [  result_list[12], result_list[13], result_list[14], result_list[15] ]
    ]

    return matrix


# PVNA_EXPORTED PVNA_Res pocketvna_4p_scan_4range_separate(const PVNA_DeviceHandler handle,
#                                       const PVNA_Frequency start, const PVNA_Frequency end, const PVNA_Size size, enum PocketVNADistribution distribution,
#                                       const AveragingQuality average, const PVNA_NetworkParameters parameters,

#                                       PVNA_Sparam * s11, PVNA_Sparam * s12,  PVNA_Sparam * s13, PVNA_Sparam * s14,
#                                       PVNA_Sparam * s21, PVNA_Sparam * s22,  PVNA_Sparam * s23, PVNA_Sparam * s24,
#                                       PVNA_Sparam * s31, PVNA_Sparam * s32,  PVNA_Sparam * s33, PVNA_Sparam * s34,
#                                       PVNA_Sparam * s41, PVNA_Sparam * s42,  PVNA_Sparam * s43, PVNA_Sparam * s44,

#                                       PVNA_PFN_Progress_Func callback) {
PVNA.pocketvna_4p_scan_4range_separate.argtypes = [DeviceHandler,
                                    Frequency, Frequency, c_uint32, Distribution,
                                    Average,  NetworkParam,

                                    Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,
                                    Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,
                                    Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,
                                    Priv_SParamArray, Priv_SParamArray, Priv_SParamArray, Priv_SParamArray,

                                    ProgressProc]
PVNA.pocketvna_4p_scan_4range_separate.restype   = ReturnType

def pyth27fix_pocketvna_4p_scan_4range_separate_wrapper(device_handler,
            start_frequency, end_frequency, count, distribution,
            average,  network_param,
            s11, s12, s13, s14,
            s21, s22, s23, s24,
            s31, s32, s33, s34,
            s41, s42, s43, s44,
            callback):
    return PVNA.pocketvna_4p_scan_4range_separate(device_handler,
            start_frequency, end_frequency, count, distribution,
            average,  network_param,
            s11, s12, s13, s14,
            s21, s22, s23, s24,
            s31, s32, s33, s34,
            s41, s42, s43, s44,
            callback)

def scan_frequencyRange_4Port(handle, startFreq, endFreq, steps, distibution, avg, netparams, callback):
    if not NUMPY:
        raise NotImplementedError("no numpy library imported")

    startFreq, endFreq = int(startFreq), int(endFreq)

    complex_size = steps*2 # twice for float is used instead of complex
    matrix_of_arrays = numpy.zeros((4,4,complex_size), dtype=numpy.float64)
    flat_list_of_arrays = matrix_of_arrays.reshape((16, complex_size))

    r = pyth27fix_pocketvna_4p_scan_4range_separate_wrapper(handle,
            Frequency(startFreq), Frequency(endFreq), c_uint32(steps), c_uint(distibution),
            Average(avg), NetworkParam(netparams),
            *[  to_ptr(flat_list_of_arrays[i]) for i in range(0, 16) ],
            callback=to_progress_proc(callback)
    )

    check_OK(r, "Failed to scan a set of frequencies")

    return flat_list_of_arrays.view(dtype=numpy.complex128).reshape((4,4,steps))

def scan_frequencyRange_4Port_nonumpy(handle, startFreq, endFreq, steps, distibution, avg, netparams, callback):
    dsz = steps * 2
    sarray = c_double * dsz
    total_size=16
    rses = [sarray(*list([0]*dsz)) for i in range(0,total_size)]

    startFreq, endFreq = int(startFreq), int(endFreq)

    r = pyth27fix_pocketvna_4p_scan_4range_separate_wrapper(handle,
            Frequency(startFreq), Frequency(endFreq), c_uint32(steps), c_uint(distibution),
            Average(avg), NetworkParam(netparams),   *rses,
            callback=to_progress_proc(callback)
    )
    # ------

    check_OK(r, "Failed to scan a set of frequencies no-numpy variant")

    result_list = to_complex_lists(rses, steps, total_size)

    assert len(result_list) == 16

    matrix = [
        [  result_list[ 0], result_list[ 1], result_list[ 2], result_list[ 3] ],
        [  result_list[ 4], result_list[ 5], result_list[ 6], result_list[ 7] ],
        [  result_list[ 8], result_list[ 9], result_list[10], result_list[11] ],
        [  result_list[12], result_list[13], result_list[14], result_list[15] ]
    ]

    return matrix


#PVNA_EXPORTED PVNA_Res   pocketvna_info_set_variable(const PVNA_DeviceHandler, const uint16_t code, const uint8_t * bytes, uint16_t size);
PVNA.pocketvna_info_set_variable.argtypes = [DeviceHandler, c_uint16, POINTER(c_uint8), c_uint16]
PVNA.pocketvna_info_set_variable.restype  = ReturnType

def set_internal_variable(handle, code_2bytes, data_bytes):
    buff_type = c_uint8 * len(data_bytes)
    buffpt    = buff_type(*list(data_bytes))
    size      = c_uint16(len(data_bytes))

    r = PVNA.pocketvna_info_set_variable(handle, c_uint16(code_2bytes), buffpt, size)

    check_OK(r, "Failed to read device internal buffer")

    return r == Result.OK


# PVNA_EXPORTED PVNA_Res pocketvna_pVNA6G_set_ctrl_var(const PVNA_DeviceHandler,
#                                                         const enum PocketVnaInternalControlVariable,
#                                                         const enum PocketVnaControlVariableValue);
PVNA.pocketvna_pVNA6G_set_ctrl_var.argtypes = [ DeviceHandler, c_int, c_int ]
PVNA.pocketvna_pVNA6G_set_ctrl_var.restype   = ReturnType

def set_pVNA6G_ctrl_var(handle, CtrlVar, value):
    r = PVNA.pocketvna_pVNA6G_set_ctrl_var(handle, c_int(CtrlVar), c_int(value))

    check_OK(r, "Failed to set device Ctrl Var")
    return r == Result.OK


# PVNA_EXPORTED PVNA_Res pocketvna_pVNA6G_get_ctrl_var(const PVNA_DeviceHandler,
#                                                         const enum PocketVnaInternalControlVariable,
#                                                         int * value);
PVNA.pocketvna_pVNA6G_get_ctrl_var.argtypes = [ DeviceHandler, c_uint, POINTER(c_int) ]
PVNA.pocketvna_pVNA6G_get_ctrl_var.restype   = ReturnType

def get_pVNA6G_ctrl_var(handle, CtrlVar):
    value = c_int(0x00)
    var   = c_uint(CtrlVar)

    r = PVNA.pocketvna_pVNA6G_get_ctrl_var(handle, var, byref(value))

    check_OK(r, "Failed to read device Ctrl Var")
    return value.value


# PVNA_Res pocketvna_pVNA6G_get_status(const PVNA_DeviceHandler handle,
#                                      uint8_t * dstbuffer, PVNA_Size * inoutsize)
PVNA.pocketvna_pVNA6G_get_status.argtypes = [ DeviceHandler,
                                              POINTER(c_uint8), POINTER(c_uint32) ]
PVNA.pocketvna_pVNA6G_get_status.restype   = ReturnType

def get_pVNA6G_status(handle):
    required_size = c_uint(0)
    r = PVNA.pocketvna_pVNA6G_get_status(handle, None, byref(required_size))
    check_OK(r, "Failed to read device status: get required size")

    size = required_size.value
    assert required_size.value > 0

#    buff  = numpy.zeros(s, dtype=numpy.uint8)
#    buffpt=buff.ctypes.data_as(POINTER(c_uint8))
    buffer_type = c_uint8 * size
    buffpt    = buffer_type(*list([0x00] * size))
    inoutsize = c_uint(size)
    r = PVNA.pocketvna_pVNA6G_get_status(handle, buffpt, byref(inoutsize))
    check_OK(r, "Failed to read device status")
    assert inoutsize.value > 0

    return [buffpt[i] for i in range(0,inoutsize.value)]


# ----------- DRIVER --------------------------------------------
def aux_convert_descriptor_structure_into_dictionary(descriptor, idx = -1):
    return dict({"index": idx,
                "path": descriptor.path,
                "version": descriptor.version,
                "SN": descriptor.sn,
                "product": descriptor.product,
                "vendor": descriptor.vendor,
                "read": bool(descriptor.access&Access.Read),
                "write": bool(descriptor.access&Access.Write),
                "ProductId": descriptor.pid,
                "VendorId": descriptor.vid,
                "InterfaceCode": descriptor.ifaceCode
        })

def aux_convert_dictionary_into_descriptor_structure(dicInfo):
    does_not_matter =  Access.Write
    return DeviceDescriptor(dicInfo["path"], does_not_matter, dicInfo["SN"],
                dicInfo["vendor"],    dicInfo["product"],  dicInfo["version"],
                dicInfo["ProductId"], dicInfo["VendorId"], dicInfo["InterfaceCode"],
                None
            )

def skrfNetwork(frequency, s11, s21, s12, s22, z0=50.0, name=''):
    s = numpy.zeros((len(frequency), 2, 2), dtype=numpy.complex128)
    s[:,0,0], s[:,0,1] = s11, s12
    s[:,1,0], s[:,1,1] = s21, s22

    ntwk = skrf.Network(s=s, frequency=skrf.Frequency.from_f(frequency, unit='hz'), z0=z0, name=name)
    return ntwk


class Driver:
    def enumerate(self):
        if bool(self.list):
            free_list(self.list)
            self.size = 0

        self.list, self.size = list_devices()

        return self.list, self.size

    def count(self):
        return self.size

    def get_raw_handle(self):
        return self.handle

    def ext_get_devices_list(self):
        res = []
        for idx in range(0, self.size):
            d = self.info_at(idx)
            if bool(d):
                res.append(d)
        return res

    def info_at(self, idx):
        if self.size == 0 or self.size <= idx:
            return dict({})

        desc = self.list[idx]

        return aux_convert_descriptor_structure_into_dictionary(desc, idx)

    # May help to check if connection was established and was not invalidated yet 
    def isHandleSet(self):
        return bool(self.handle)

    def valid(self):
        if not self.isHandleSet(): return False

        if is_valid(self.handle):
            return True
        else:
            self.handle = None
            return False

    def safe_connect_to(self, idx_or_dict):
        try:
            if isinstance(idx_or_dict, dict):
                desc = aux_convert_dictionary_into_descriptor_structure(idx_or_dict)
                return self.ext_connect_to(desc)
            elif isinstance(idx_or_dict, (int)):
                return self.connect_to(idx_or_dict)
            else:
                print('unknown type. Should be dict or idx')
                return None
        except PocketVnaAPIError:
            return False
        except:
            return None

    def ext_connect_to(self, descriptor):
        self.internal_release_connection()
        assert isinstance(descriptor, DeviceDescriptor), "should be instance of DeviceDescriptor"
        try:
            self.info   = aux_convert_descriptor_structure_into_dictionary(descriptor)
            self.handle = get_device_handler(descriptor)
            return True
        except PocketVnaAccessDenied:
            i = self.info
            self.handle, self.info   = None, {}
            raise PocketVnaAccessDenied(str(i))
        except:
            self.handle, self.info   = None, {}
            raise

    def connect_to(self, idx):
        if self.size == 0 or self.size <= idx:
            return False

        return self.ext_connect_to(self.list[idx])

    def connect_to_first(self, ifaceCode = ConnectionInterfaceCode.CIface_HID):
        for i in range(0, self.count()):
            info = self.info_at(i)
            if info["InterfaceCode"] == ifaceCode:
                return self.safe_connect_to(info)

        return None

    def connect_to_simulator(self):
        self.internal_release_connection()

        self.handle = open_simulation_device()
        self.info   = create_simulator_description()
        return True

    # TODO: rename. It's actually a firmware version. Name is confusing
    def version(self):
        if not bool(self.handle): return None

        try:
            return get_version(self.handle)
        except PocketVnaHandlerInvalid:
            self.handle, self.info   = None, {}
            raise

    def Z0(self):
        if not bool(self.handle): return None

        try:
            return get_characteristic_impedance(self.handle)
        except PocketVnaHandlerInvalid:
            self.handle, self.info   = None, {}
            raise

    def valid_frequency_range(self):
        if not bool(self.handle): return None

        try:
            return get_valid_frequency_range(self.handle)
        except PocketVnaHandlerInvalid:
            self.handle, self.info   = None, {}
            raise

    def reasonable_frequency_range(self):
        if not bool(self.handle): return None

        try:
            return get_reasonable_frequency_range(self.handle)
        except PocketVnaHandlerInvalid:
            self.handle, self.info   = None, {}
            raise

    def has_network_param(self, Priv_SParam):
        if not bool(self.handle): return None

        try:
            return supports_network_parameter(self.handle, Priv_SParam)
        except PocketVnaHandlerInvalid:
            self.handle, self.info   = None, {}
            raise

    def has_s11(self):
        return self.has_network_param(NetworkParams.S11)

    def has_s21(self):
        return self.has_network_param(NetworkParams.S21)

    def has_s12(self):
        return self.has_network_param(NetworkParams.S12)

    def has_s22(self):
        return self.has_network_param(NetworkParams.S22)

    def internal_release_connection(self):
        try:
            if self.valid():
                release_handler(self.handle)
        except PocketVnaHandlerInvalid:
            pass
        finally:
            self.handle, self.info   = None, {}

    def close(self):
        try:
            if self.isHandleSet():
                release_handler(self.handle)
            if bool(self.list):
                free_list(self.list)
        except PocketVnaHandlerInvalid:
            pass
        finally:
            self.handle, self.info  = None, {}
            self.list,   self.size  = [],   0

    def single_scan(self, freq, avg, netparams):
        if not bool(self.handle): return [None]*4

        try:
            return scan_frequency(self.handle, freq, avg, netparams)
        except PocketVnaHandlerInvalid:
            self.handle, self.info   = None, {}
            raise

    # This is a helper function: that convert @netparams into form acceptable with API. For example AllSupported is a string-code
    # it is rather private function
    def get_supported_params(self, netparams):
        np = netparams

        # It is a helper: if AllSupported flag is passed we select all available. Otherwise we use @netparams as is
        if netparams == NetworkParams.Util2Port.AllSupported:
            np = NetworkParams.Non
            if self.has_s11(): np = np | NetworkParams.S11
            if self.has_s21(): np = np | NetworkParams.S21
            if self.has_s12(): np = np | NetworkParams.S12
            if self.has_s22(): np = np | NetworkParams.S22

        return np

    def scan_NoNumpy(self, freqs, avg, netparams, callback = None):
        if len(freqs) < 1: return [] * 4
        if not bool(self.handle): return [None]*4

        np = self.get_supported_params(netparams)

        return scan_frequencies_no_numpy(self.handle, freqs, avg, np, callback)

    def scan_WithNumpy(self, freqs, avg, netparams, callback = None):
        if len(freqs) < 1: return [numpy.array([], dtype=numpy.complex128)] * 4
        if not bool(self.handle): return [None]*4

        np = self.get_supported_params(netparams)

        return scan_frequencies(self.handle, freqs, avg, np, callback)

    def scan4p_WithNumpy(self, freqs, avg, netparams, callback):
        if len(freqs) < 1: return numpy.zeros((4,4,0), dtype=numpy.complex128)
        if not bool(self.handle): return None

        np = self.get_supported_params(netparams)
        return scan_frequencies_4Port(self.handle, freqs, avg, np, callback)

    def scan4p_WithoutNumpy(self, freqs, avg, netparams, callback):
        if len(freqs) < 1: return [ [[],[]], [[],[]] ]
        if not bool(self.handle): return None

        np = self.get_supported_params(netparams)
        return scan_frequencies_4Port_nonumpy(self.handle, freqs, avg, np, callback)

    def scan4range_WithNumpy(self, startFreq, endFreq, steps, dist, avg, netparams, callback):
        if steps < 1: return [numpy.array([], dtype=numpy.complex128)] * 4
        if not bool(self.handle): return [None]*4

        np = self.get_supported_params(netparams)
        return scan_frequencies_for_range(self.handle, startFreq, endFreq, steps, dist, avg, np, callback)

    def scan4range_NoNumpy(self, startFreq, endFreq, steps, dist, avg, netparams, callback):
        if steps < 1: return [numpy.array([], dtype=numpy.complex128)] * 4
        if not bool(self.handle): return [None]*4

        np = self.get_supported_params(netparams)
        return scan_frequencies_for_range_no_numpy(self.handle, startFreq, endFreq, steps, dist, avg, np, callback)

    def scan4ports_range_WithNumpy(self, startFreq, endFreq, steps, dist, avg, netparams, callback):
        if steps < 1: return numpy.zeros((4,4,0), dtype=numpy.complex128)
        if not bool(self.handle): return None

        np = self.get_supported_params(netparams)
        return scan_frequencyRange_4Port(self.handle, startFreq, endFreq, steps, dist, avg, np, callback)

    def scan4ports_range_WithoutNumpy(self, startFreq, endFreq, steps, dist, avg, netparams, callback):
        if steps < 1: return [ [[],[]], [[],[]] ]
        if not bool(self.handle): return None

        np = self.get_supported_params(netparams)
        return scan_frequencyRange_4Port_nonumpy(self.handle, startFreq, endFreq, steps, dist, avg, np, callback)

    def scan4range(self, startFreq, endFreq, steps, dist, avg, netparams, callback = None):
        if NUMPY: return self.scan4range_WithNumpy( startFreq, endFreq, steps, dist, avg, netparams, callback)
        else:     return self.scan4range_NoNumpy(   startFreq, endFreq, steps, dist, avg, netparams, callback )

    def scan(self, freqs, avg, netparams, callback = None):
        if NUMPY: return self.scan_WithNumpy(freqs, avg, netparams, callback )
        else:     return self.scan_NoNumpy(  freqs, avg, netparams, callback )

    def scan4ports(self, freqs, avg, netparams, callback = None):
        if NUMPY: return self.scan4p_WithNumpy(freqs, avg, netparams, callback)
        else: return self.scan4p_WithoutNumpy(freqs, avg, netparams, callback)

    def scan4ports_range(self, startFreq, endFreq, steps, dist, avg, netparams, callback = None):
        if NUMPY: return self.scan4ports_range_WithNumpy(startFreq, endFreq, steps, dist, avg, netparams, callback)
        else: return self.scan4ports_range_WithoutNumpy(startFreq, endFreq, steps, dist, avg, netparams, callback)

    def debugscan(self, sz, nonumpy = False):
        if not bool(self.handle): return [None]*2

        if NUMPY and not nonumpy: return debug_response(self.handle, sz)
        else:     return debug_response_no_numpy(self.handle, sz)

    # ---- Info section
    def get_info_firmware_version(self):
        if not bool(self.handle): return -1

        return info_get_firmware_version(self.handle)

    def get_info_param_supported(self, netparam):
        if not bool(self.handle): return None

        return info_get_param_supported(self.handle, netparam)

    def get_info_device_temperature(self):
        if not bool(self.handle): return None
        return info_get_temperature(self.handle)

    def get_info_device_internal_settings(self, _6bytes):
        if not bool(self.handle): return None
        return info_get_variable(self.handle, _6bytes)

    def __init__(self):
        self.list, self.handle, self.size = None, None, 0
        self.enumerate()

    def __del__(self):
        try:
            self.close()
        except:
            print('#__del__ Exception')

    def devinfo(self):
        return self.info

    def isHID(self):
        return self.valid() and (self.devinfo()["InterfaceCode"] == ConnectionInterfaceCode.CIface_HID)

    def isVCI(self):
        return self.valid() and (self.devinfo()["InterfaceCode"] == ConnectionInterfaceCode.CIface_VCI)

    def scan_skrf_network(self, freq, avg, callback = None):
        if not SKRF: raise RuntimeError("skrf (scikit-rf) library was not imported.")

        s11, s21, s12, s22 = self.scan(freq, avg,  NetworkParams.Util2Port.AllSupported, callback)

        s = numpy.zeros((len(freq), 2, 2), dtype=numpy.complex128)

        s[:,0,0], s[:,0,1] = s11, s12
        s[:,1,0], s[:,1,1] = s21, s22

        ntwk = skrf.Network()

        ntwk.s         = s
        ntwk.frequency = skrf.Frequency.from_f(freq, unit='hz')
        ntwk.z0        = self.Z0()

        return ntwk

## Helpers
def kHz(val):
    return val * 1000
def MHz(val):
    return kHz(val * 1000)
def GHz(val):
    return MHz(val * 1000)

def are_descriptors_the_same(dict1, dict2):
    return dict1["path"] == dict2["path"] and dict1["ProductId"] == dict2["ProductId"] and dict1["VendorId"]  == dict2["VendorId"]
