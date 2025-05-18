#pragma once

/** @file
 *  @defgroup API pocketVna API
*/

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) || defined(WIN32)
#  ifdef PVNA_SHARED_LIB
#     define PVNA_EXPORTED  __declspec(dllexport)
#  else
#     define PVNA_EXPORTED  __declspec(dllimport)
#  endif
#  define CCALL __cdecl
#else
#  define PVNA_EXPORTED __attribute__((visibility ("default")))
#  define CCALL
#endif

#if defined(__GNUC__) || defined(__GNUG__) || defined(__clang__)
#   define PVNA_DEPRECATED  __attribute__((deprecated))
#elif defined(_MSC_VER)
#   define PVNA_DEPRECATED  __declspec(deprecated)
#else
#   define PVNA_DEPRECATED
#endif

#include <stdint.h>
#include <wchar.h>

enum PocketVnaAccessEnum {PVNA_Denied     = 0x00,
                          PVNA_ReadAccess = 0x01,
                          PVNA_WriteAccess= 0x02,
                          PVNA_Granted    = PVNA_ReadAccess | PVNA_WriteAccess,
                          PVNA_Busy       = 0x10
                          };
enum ConnectionInterfaceCode {
    CIface_HID = 0x10,
    CIface_VCI = 0x20,
};

enum PocketVNAConstantsEnum {
    MAX_ARRAY_SIZE=1000000,
    MAX_AVERAGE_VALUE=100,
    INTERNAL_BUFFER_SIZE=100,
    CALL_CALLBACK_AFTER_EACH_POINTS=3
};

enum PocketVNADistribution {
    PVNADist_Linear=1,
    PVNADist_Log=2
};

enum PocketVNAOptions {
    PVNAOpt_LogLevel
};

enum PocketVnaTransmissionEnum{ PVNA_SNone = 0x00,

                                PVNA_S21    = 0x0001,
                                PVNA_S11    = 0x0002,
                                PVNA_S12    = 0x0004,
                                PVNA_S22    = 0x0008,

                                PVNA_S13    = 0x0010,
                                PVNA_S14    = 0x0040,
                                PVNA_S23    = 0x0020,
                                PVNA_S24    = 0x0080,

                                PVNA_S31    = 0x0100,
                                PVNA_S32    = 0x0400,
                                PVNA_S41    = 0x0200,
                                PVNA_S42    = 0x0800,

                                PVNA_S33    = 0x1000,
                                PVNA_S34    = 0x4000,
                                PVNA_S43    = 0x2000,
                                PVNA_S44    = 0x8000,
};

enum SomeTransmissionConsts {
    PVNA_2P_FORWARD  = PVNA_S11 | PVNA_S21,
    PVNA_2P_BACKWARD = PVNA_S12 | PVNA_S22,
    PVNA_2P_ALL   = PVNA_2P_FORWARD | PVNA_2P_BACKWARD
};

enum PocketVNAContinueCodeEnum { PVNA_Cancel = 0, PVNA_Continue = 1 };

/**  \class PocketVnaResultEnum
 * @brief The PocketVnaResultEnum contains all possible codes api can return
 *
 */
enum PocketVnaResultEnum { PVNA_Res_Ok = 0x0, PVNA_Res_NoDevice,
                           PVNA_Res_NoMemoryError, PVNA_Res_CanNotInitialize,
                           PVNA_Res_BadDescriptor,

                           PVNA_Res_DeviceLocked,

                           PVNA_Res_NoDevicePath, PVNA_Res_NoAccess, PVNA_Res_FailedToOpen,
                           PVNA_Res_InvalidHandle,
                           PVNA_Res_BadTransmission, PVNA_Res_UnsupportedTransmission,
                           PVNA_Res_BadFrequency,
                           PVNA_Res_DataReadFailure, PVNA_Res_EmptyResponse, PVNA_Res_IncompleteResponse,
                           PVNA_Res_FailedToWriteRequest,
                           PVNA_Res_ArraySizeTooBig, PVNA_Res_BadResponse,

                           PVNA_Res_DeviceResponseSection,

                           PVNA_Res_Response_UNKNOWN_MODE, PVNA_Res_Response_UNKNOWN_PARAMETER,
                           PVNA_Res_Response_NOT_INITIALIZED,
                           PVNA_Res_Response_FREQ_TOO_LOW,  PVNA_Res_Response_FREQ_TOO_HIGH,
                           PVNA_Res_Response_OutOfBound,    PVNA_Res_Response_UNKNOWN_VARIABLE,
                           PVNA_Res_Response_UNKNOWN_ERROR, PVNA_Res_Response_BAD_FORMAT,

                           PVNA_Res_ExtendedSection,
                           PVNA_Res_ScanCanceled,

                           PVNA_Res_Rfmath_Section,
                           PVNA_Res_No_Data,

                           PVNA_Res_LIBUSB_Error,
                           PVNA_Res_LIBUSB_CanNotSelectInterface,
                           PVNA_Res_LIBUSB_Timeout,
                           PVNA_Res_LIBUSB_Busy,

                           PVNA_Res_VCI_PrepareScanError,
                           PVNA_Res_VCI_Response_Error,
                           PVNA_Res_EndLEQStart,

                           PVNA_Res_VCI_Failed2OpenProbablyDriver,
                           PVNA_Res_HID_AdditionalError,

                           PVNA_Res_NotImplemented,
                           PVNA_Res_BadArgument,

                           PVNA_Res_Fail=0xFFFF,
                         };

enum PocketVnaInternalControlVariable {
    PVNA_CtrlVar_MeasurementsMode = 0x0907,
    PVNA_CtrlVar_ConsistencyLevel = 0x09C0,
};
enum PocketVnaControlVariableValue {
    PVNA_CtrlVar_Consistency_Off =0x0D,
    PVNA_CtrlVar_Consistency_ON  =0x0E,
    PVNA_CtrlVar_Consistency_Full=0x0A,

    PVNA_CtrlVar_Meas_RawMeas           = 0x01,
    PVNA_CtrlVar_Meas_CaliMeas          = 0x02,
    PVNA_CtrlVar_Meas_InternalCaliShort = 0x03,
    PVNA_CtrlVar_Meas_InternalCaliOpen  = 0x04,
    PVNA_CtrlVar_Meas_InternalCaliLoad  = 0x05,
    PVNA_CtrlVar_Meas_InternalShort     = 0x06,
    PVNA_CtrlVar_Meas_InternalOpen      = 0x07,
    PVNA_CtrlVar_Meas_InternalLoad      = 0x08,
    PVNA_CtrlVar_Meas_InternalThru      = 0x09,
    PVNA_CtrlVar_Meas_InternalCaliThru  = 0x0a,
};

typedef enum PocketVnaTransmissionEnum PVNA_NetworkParameter;
typedef int PVNA_NetworkParameters;

typedef enum PocketVnaAccessEnum PVNA_Access;
typedef enum PocketVNAContinueCodeEnum PVNA_ContinueCode;
typedef enum PocketVnaResultEnum PVNA_Res;

typedef void* PVNA_DeviceHandler;

typedef void* PVNA_UserDataPtr;
typedef PVNA_ContinueCode (*PVNA_PFN_Progress_Func) (PVNA_UserDataPtr, uint32_t);

typedef struct PocketVNaProgressCallBack {
    PVNA_UserDataPtr    data;
    PVNA_PFN_Progress_Func proc;
} PVNA_ProgressCallBack;


typedef struct PocketVnaDeviceDesc {
    const char * path;
    PVNA_Access access;

    const wchar_t * serial_number;

    const wchar_t * manufacturer_string;
    const wchar_t * product_string;

    uint16_t release_number;

    uint16_t pid;
    uint16_t vid;
    uint16_t ciface_code; //value from ConnectionInterfaceCode

    struct PocketVnaDeviceDesc * next;
} PVNA_DeviceDesc;


typedef struct ImitComplexD {
    double real;
    double imag;
} PVNA_Sparam;


typedef uint64_t PVNA_Frequency;
typedef uint32_t PVNA_Size;
typedef uint16_t AveragingQuality;

// ------------- Driver stuff -----------------------------------
    /** @brief Get driver version and PI number
     *
     *  Stores driver version into @p version and PI (3.141592..) into @p info
        @ingroup API
        @param version A pointer (IOW reference) to Descriptor's Pointer. Should not be NULL
        @param info    A pointer (IOW reference) where PI double number will be stored. It can be NULL

        @returns
            Always returns 'Ok'.
    */
    PVNA_EXPORTED PVNA_Res pocketvna_driver_version(uint16_t * version, double *info);

    /** @brief Close driver
     *
     *  It would be nice to call it when you do not need the library anymore

        @ingroup API

        @returns
            Always returns 'Ok'.
    */
    PVNA_EXPORTED PVNA_Res pocketvna_close(void);

    /** @brief Explains for \ref PocketVnaResultEnum "Error Code"
     *
     * @param code  An error code PVNA_Res (PocketVnaResultEnum)
     * @returns C-string
    */
    PVNA_EXPORTED const char * pocketvna_result_string(PVNA_Res code);

    /** @brief allows to set some driver configuration.
     *    for internal use mostly.
     *    For loglevel and usb-engine call it before any @fn pocketvna_list_devices
     * @param opt   - option code
     * @param value - int value
    */
    PVNA_EXPORTED void pocketvna_set_option(enum PocketVNAOptions opt, int64_t value);

// ------------- Pre-connect stuff ------------------------------

    /** @brief Get all PocketVna devices connected

        It accepts a reference to a pointer of PocketVnaDeviceDesc as @p list and if there is any device detected it will return a pointer to first descriptor.
        Pay attention that you can act with list as with array (with size element);
        Also you can walk through descriptors for each Descriptor contains pointer to next Descriptor
        Descriptor should be used in 'pocketvna_get_device_handle_for'.
        If you don't need @p list anymore clear it with 'pocketvna_free_list'

        @ingroup API
        @param list A pointer (IOW reference) to Descriptor's Pointer. If function fails it will be NULL
        @param size A the number of devices will be returned. If cuntion fails it will be 0.

        @returns
            This function returns Result (PocketVnaResult). For example on success it will be 'Ok'.
              Or 'NoDevice' if there is no device detected
    */
    PVNA_EXPORTED PVNA_Res pocketvna_list_devices(PVNA_DeviceDesc ** list, uint16_t * size);

    /** @brief Clear an enumeration of devices

        It Accepts @p list created with 'pocketvna_list_devices()', frees a memory taken with list and Zero @p list itself

        @ingroup API
        @param list A pointer (IOW reference) to Descriptor's Pointer. If function success @p list become NULL

        @returns
            This function returns Result (PocketVnaResult) and alwasy 'Ok'.
    */
    PVNA_EXPORTED PVNA_Res pocketvna_free_list(PVNA_DeviceDesc ** list);

    /** @brief Helper for working with list for systems that are not able to interact arrays of structs
     *  @returns
     *      If @list is invalid or NULL than it returns 0, otherwise actual number
    */
    PVNA_EXPORTED uint16_t pocketvna_helper_descriptors_count(PVNA_DeviceDesc * list);

    /** @brief Helper for working with list for systems that are not able to interact arrays of structs
     *  @returns
     *      If @list is invalid or NULL than it returns NULL, otherwise actual number
    */
    PVNA_EXPORTED const char * pocketvna_helper_descriptor_get_path(PVNA_DeviceDesc * list, uint16_t index);

    /** @brief Helper for working with list for systems that are not able to interact arrays of structs
     *  @returns
     *      If @list is invalid or NULL than it returns 0, otherwise actual VID
    */
    PVNA_EXPORTED uint16_t pocketvna_helper_descriptor_get_vid(PVNA_DeviceDesc * list, uint16_t index);

    /** @brief Helper for working with list for systems that are not able to interact arrays of structs
     *  @returns
     *      If @list is invalid or NULL than it returns 0, otherwise actual PID
    */
    PVNA_EXPORTED uint16_t pocketvna_helper_descriptor_get_pid(PVNA_DeviceDesc * list, uint16_t index);

    /** @brief Helper for working with list for systems that are not able to interact arrays of structs
     *  @returns
     *      If @list is invalid or NULL than it returns 0, otherwise actual ConnectionInterfaceCode
    */
    PVNA_EXPORTED enum ConnectionInterfaceCode pocketvna_helper_descriptor_get_interface(PVNA_DeviceDesc * list, uint16_t index);

    /** @brief Helper for working with list for systems that are not able to interact arrays of structs
     *  @returns
     *      If @list is invalid or NULL than it returns 0, otherwise actual SN
    */
    PVNA_EXPORTED const wchar_t * pocketvna_helper_descriptor_get_SN(PVNA_DeviceDesc * list, uint16_t index);

    /** @brief Helper for working with list for systems that are not able to interact arrays of structs
     *  @returns
     *      If @list is invalid or NULL than it returns BadDescriptor, otherwise the same as  @see pocketvna_get_device_handle_for
    */
    PVNA_EXPORTED PVNA_Res pocketvna_helper_descriptor_get_handler(PVNA_DeviceDesc * list, uint16_t index, PVNA_DeviceHandler * handle);

// ------------- Connect stuff ----------------------------------
    /** @brief Open device using a descriptor
     *
     *  It accepts @p desc which is taken from pocketvna_list_devices(), opens a device and returns @p handle to a device

        @ingroup API
        @param desc A pointer (IOW reference) to Descriptor.
        @param handle A pointer to a Handle. It should be NULL if call failed or NotNULL on success

        @returns
            This function returns Result (PocketVnaResult). For example 'Ok' on success
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_get_device_handle_for(const PVNA_DeviceDesc* desc, PVNA_DeviceHandler * handle);

    /** @brief Open any device found
     *  It is not convenient to work with list_devices/free_list/get_device_handle_for especially for very specific environment like
     * LabView or Matlab. This one skips it. It just try search any device and connect against it.

        @ingroup API
        @param handle A pointer to a Handle. It should be NULL if call failed or NotNULL on success

        @returns
            This function returns Result (PocketVnaResult). For example 'Ok' on success
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_get_first_device_handle(PVNA_DeviceHandler *);

    /** @brief Close device using a descriptor
     *
     *  It accepts @p handle which is taken from pocketvna_get_device_handle_for() and closes a device

        @ingroup API
        @param handle A pointer to Device. IN-OUT

        @returns
            This function returns Result (PocketVnaResult). For example 'Ok' on success
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_release_handle(PVNA_DeviceHandler *);

    /** @brief Check whether Network Parameter (trasmission) is supported
     *
     *  It accepts @p handle which is taken from pocketvna_get_device_handle_for() and @p param (S11 Or S21 ...)
     *  Newer devices support full 2 port scan. Previously, only S11 and S21 modes were supported

        @ingroup API
        @param handle A pointer to Device.
        @param param  A Transmission, Network Parameter

        @returns
            This function returns Result (PocketVnaResult). For example 'Ok' on success
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_is_transmission_supported(const PVNA_DeviceHandler, const PVNA_NetworkParameter);

    /** @brief Check whether @p handler is valid
     *
     *  It accepts @p handle which is taken from pocketvna_get_device_handle_for() and checks whether it valid
     * This would be useful to check if device is gone, disconnected so on

        @ingroup API
        @param handle A pointer to Device.

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_is_valid(const PVNA_DeviceHandler);

    /** @brief Get device firmware version
     *
     *  It accepts @p handle which is taken from pocketvna_get_device_handle_for() and
     * and writes into @p version address Firmware version which is usually 2bytes hex value
     * 1st-highbyte is a Major version, 2nd-lowbyte is a Minor version. For example V = '1.5' is 0x105; Version 1.6 is 0x106

        @ingroup API
        @param handle  A pointer to Device.
        @param version A pointer (reference) to 2-byte variable. Can not be NULL

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_version(const PVNA_DeviceHandler handle, uint16_t * version);

    /** @brief Get device Characteristic Impedance
     *
     *  It accepts @p handle which is taken from pocketvna_get_device_handle_for() and
     *  a reference to double variable as @p R. Usually Characteristic Impedance is 50 Ohms.
     *  Characteristic Impedance also known as LoadOhm, Reference Resistance, Reference Impedance, Zero Impedance so on
     *  The actual value will be stored in under adress of @p R parameter

        @ingroup API
        @param handle  A pointer to Device.
        @param R       A pointer (reference) double variable. Can not be NULL

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_get_characteristic_impedance(const PVNA_DeviceHandler handle, double * R);

    /** @brief Get valid frequency range IOW a range device can handle
     *
     *  Usually it is [1; 6G]Hz for PocketVNA v1.5-2.2. But does not mean that device processes correctly this range entirely
     * IOW device does not return error for this range

        @ingroup API
        @param handle  A pointer to Device.
        @param from    A pointer (reference) where to save lowest frequency a device can handle
        @param to      A pointer (reference) where to save highest frequency a device can handle

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_get_valid_frequency_range(const PVNA_DeviceHandler handle, PVNA_Frequency * from, PVNA_Frequency * to);

    /** @brief Get reasonable frequency range IOW a range device can process correctly
     *
     *  Usually it is narrower than Valid range ([1; 6G]Hz for PocketVNA v1.5-2.2).

        @ingroup API
        @param handle  A pointer to Device.
        @param from    A pointer (reference) where to save lowest frequency a device can process correctly
        @param to      A pointer (reference) where to save highest frequency a device can process correctly

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_get_reasonable_frequency_range(const PVNA_DeviceHandler handle, PVNA_Frequency * from, PVNA_Frequency * to);

//-------------- Query stuff ------------------------------------

    /** @brief Query device for some Network Parameters for particular frequency
     *
     *  It accepts @p handle and gets Network parameters @p params

        @ingroup API
        @param handle    A pointer to Device.
        @param frequency A frequency value. Usually it should be between a Valid Frequency Range ([1; 6G]Hz for PocketVNA v1.5-2.2). But
    it would be better to use Reasonable Range
        @param average   A average times to ask hardware. Usually should be between [1; 1000]
        @param params    Network Parameters that should be taken: S11 or S21 or S12 or S22. Use '|' to combine
        @param s11       Pointer to SParam structure (pair of double). S11 Network Parameter will be here is @p params asked for it
        @param s21       Pointer to SParam structure (pair of double). S21 Network Parameter will be here is @p params asked for it
        @param s12       Pointer to SParam structure (pair of double). S21 Network Parameter will be here is @p params asked for it
        @param s22       Pointer to SParam structure (pair of double). S22 Network Parameter will be here is @p params asked for it

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid, or any other 'Result'
    */
    PVNA_DEPRECATED
    PVNA_EXPORTED PVNA_Res   pocketvna_single_query(const PVNA_DeviceHandler,
                                          const PVNA_Frequency,
                                          const AveragingQuality, const PVNA_NetworkParameters,
                                          PVNA_Sparam * s11,  PVNA_Sparam * s21,
                                          PVNA_Sparam * s12,  PVNA_Sparam * s22);


    /** @brief Query device for some Network Parameters using a set of frequencies
     *
     *  It accepts @p handle and gets Network parameters @p params for each frequency in @p frequencies array

        @ingroup API
        @param handle      A pointer to Device.
        @param frequencies A frequency array. Usually each element should be between a Valid Frequency range
        @param size        A size of frequency array and all sXXa arrays that are requested
        @param average     A average times to ask hardware. Usually should be between [1; 1000]
        @param params      Network Parameters that should be taken: S11 or S21 or S12 or S22. Use '|' to combine
        @param s11a      Array to SParam structures (pairs of double). S11 Network Parameters will be here is @p params asked for it
        @param s21a      Array to SParam structures (pairs of double). S21 Network Parameters will be here is @p params asked for it
        @param s12a      Array to SParam structures (pairs of double). S21 Network Parameters will be here is @p params asked for it
        @param s22a      Array to SParam structures (pairs of double). S22 Network Parameters will be here is @p params asked for it
        @param progress  Callback structure. It if is not NULL callee will be notified about currently processed index of frequency

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid, or any other 'Result'
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_multi_query(const PVNA_DeviceHandler,
                                        const PVNA_Frequency *, const PVNA_Size,
                                        const AveragingQuality, const PVNA_NetworkParameters,
                                        PVNA_Sparam * s11a, PVNA_Sparam * s21a,
                                        PVNA_Sparam * s12a, PVNA_Sparam * s22a,
                                        PVNA_ProgressCallBack * progress);

    /** @brief The same as pocketvna_multi_query but accepts C function as callback
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_multi_query_with_cproc(const PVNA_DeviceHandler,
                                        const PVNA_Frequency *, const PVNA_Size,
                                        const AveragingQuality, const PVNA_NetworkParameters,
                                        PVNA_Sparam * s11a, PVNA_Sparam * s21a,
                                        PVNA_Sparam * s12a, PVNA_Sparam * s22a,
                                        PVNA_PFN_Progress_Func);

    /** @brief Query device for some Network Parameters using a distribution formula
     *
     *   It accepts @p handle and gets Network parameters @p params. Frequency point is calculated by distribution formula
     *  Distributions:
     *    Linear:      (@p start * 1000 + ((@p end - @p start) * 1000 / (@p steps - 1)) * index) / 1000
     *       (Pay Attention: all numbers are integers. Last element is forced to be equalt to @p end)
     *    Logarithmic: (@p from * powf((float)to / from, (float)index / (steps - 1)))
     *       Formula is taken from 10 ** (lg from +  ( lg to - lg from ) * index /  (steps - 1)). 4-bytes float are used
     *       Pay attention: arithmetic is pretty imprecise on a device

        @ingroup API
        @param handle   A pointer to Device
        @param start    Start Frequency
        @param end      End Frequency. Should be greater than @p start
        @param steps    Number of frequency points
        @param distr    A code for distribution formula (Linear)
        @param average  A average times to ask hardware. Usually should be between [1; 1000]
        @param params   Network Parameters that should be taken: S11 or S21 or S12 or S22. Use '|' to combine
        @param s11a      Array to SParam structures (pairs of double). S11 Network Parameters will be here is @p params asked for it
        @param s21a      Array to SParam structures (pairs of double). S21 Network Parameters will be here is @p params asked for it
        @param s12a      Array to SParam structures (pairs of double). S21 Network Parameters will be here is @p params asked for it
        @param s22a      Array to SParam structures (pairs of double). S22 Network Parameters will be here is @p params asked for it
        @param progress  Callback structure. It if is not NULL callee will be notified about currently processed index of frequency

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid, or any other 'Result'
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_range_query(
            const PVNA_DeviceHandler,
            const PVNA_Frequency start, const PVNA_Frequency end, const PVNA_Size, enum PocketVNADistribution,
            const AveragingQuality, const PVNA_NetworkParameters,
            PVNA_Sparam * s11a, PVNA_Sparam * s21a,
            PVNA_Sparam * s12a, PVNA_Sparam * s22a,
            PVNA_ProgressCallBack *
    );

    /** @brief Query device for some Network Parameters using a distribution formula
     *
     *  It is the same as 'pocketvna_range_query' but accepts plain C function as callback
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_range_query_with_cproc(
            const PVNA_DeviceHandler,
            const PVNA_Frequency start, const PVNA_Frequency end, const PVNA_Size, enum PocketVNADistribution,
            const AveragingQuality, const PVNA_NetworkParameters,
            PVNA_Sparam * s11a, PVNA_Sparam * s21a,
            PVNA_Sparam * s12a, PVNA_Sparam * s22a,
            PVNA_PFN_Progress_Func
    );


    /** @brief Move a device into Firmware Update Mode
     *  Pay attention that it requires some special software (it works on Windows/Linux only) to Upload new firmware onto device.
     * This driver does not support Firmware Update for now. It just enters firmware into UPGRADE mode. Then either flip or DFU-PROGRAMMER can be used
     *

        @ingroup API
        @param handle      A pointer to Device.

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid, or any other 'Result'
    */
    PVNA_DEPRECATED
    PVNA_EXPORTED PVNA_Res   pocketvna_enter_dfu_mode(const PVNA_DeviceHandler);


    PVNA_EXPORTED PVNA_Res   pocketvna_info_get_firmware_version(const PVNA_DeviceHandler, uint16_t * version);

    /** @brief Service function. Checks if parameter is supported. All devices older than v 1.6 support Full Network (4 parameters)
     *
        @ingroup API
        @param handle      A pointer to Device.
        @param kalvin_temperature A pointer where the temperature to store

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid, or any other 'Result'
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_info_get_param_supported(const PVNA_DeviceHandler, const PVNA_NetworkParameter);

    /** @brief Service function. Reads temperature sensor.
     *  It is available on new firmwares only > 2.10. It is not available for PocketVNA v 1.5 and 2.0
     *  Devices unsupported this feature return error
     *

        @ingroup API
        @param handle      A pointer to Device.
        @param kalvin_temperature A pointer where the temperature to store

        @returns
            This function returns Result: 'Ok' on success, 'PVNA_Res_InvalidHandle' if handle is invalid, or any other 'Result'
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_info_get_temperature(const PVNA_DeviceHandler, double * kalvin_temperature);

    /// For internal use only. Don't use them
    PVNA_EXPORTED PVNA_Res   pocketvna_info_get_variable(const PVNA_DeviceHandler, const uint8_t * _6bytes_code,
                                                         uint8_t * _6bytesForOld_64ForNew);
    PVNA_EXPORTED PVNA_Res   pocketvna_info_set_variable(const PVNA_DeviceHandler, const uint16_t code, const uint8_t * bytes, uint16_t size);


//       ~~~ Debug Stuff ~~~
    /** @brief Sends debug request to a device. Probably you do not need this call ever
     *
     *  This call can help to test connection and API. Usually it returns 8 bytes response. For example some USB/HID Api
     * requires first byte to be '0'. But sometimes ignores it. Request may help to see if 5th and 8th elements are expected (13) and first should be '0'
        response[0] - should be OK (IOW 0)
        response[1] - version counter. Rarely changed variable. Now it is 3
        response[2] - garbage
        response[3] - size of the response. Usually 8
        response[4] - Always is 13;

        index 5 and 6 contain size of an operational internal buffer
        response[5] = HIGBYTE16(sizeof(InternalBuffer))
        response[6] = LOWBYTE16(sizeof(InternalBuffer))

        response[7] - Always 13

        This call also fills an internal buffer (InternalBuffer) with values with "i % 256" pattern

        @ingroup API
        @param handle  A pointer to Device.
        @param buffer  A byte buffer. It should point to valid memory area of @p size elements
        @param size    A size of a byte @p buffer. After a call it will contain actual number of bytes written into @p buffer
        @returns
            This function returns Result (PocketVnaResult). For example 'Ok' on success, or 'InvalidHandle' if handle is closed or invalid so on
    */
    PVNA_DEPRECATED
    PVNA_EXPORTED PVNA_Res   pocketvna_debug_request(const PVNA_DeviceHandler, uint8_t * buffer, uint32_t * size);

    /** @brief Reads an operational internal buffer on a device. Probably you do not need this call EVER!
     *
     *  Device has an internal buffer that may contain some auxiliar information or an extended error report
     *  Also pocketvna_debug_request() fills it with "i % 256" pattern. So it can be used for debug purposes.
     *  An actual size of a buffer can be obtained by pocketvna_debug_request() too 6th and 7th elements (high and low bytes respectively)

        @ingroup API
        @param handle  A pointer to Device.
        @param buffer  A byte buffer. It should point to valid memory area of @p size elements
        @param size    A size of a byte @p buffer. After a call it will contain actual number of bytes written into @p buffer
        @returns
            This function returns Result (PocketVnaResult). For example 'Ok' on success, or 'InvalidHandle' if handle is closed or invalid so on
    */
    PVNA_DEPRECATED
    PVNA_EXPORTED PVNA_Res   pocketvna_debug_read_buffer(const PVNA_DeviceHandler, uint8_t * buffer, uint32_t * size);

    /** @brief fills PVNA_SParams arrays with known/predictable values
     *
     *  Check optimizations works; Check ABI is compatible. Probably should be used for unit-tests only.
     * For example Python has kind of 'reflection' API. We return SParam as a structure as a pair of doubles
     * We can treat array of such pairs as double-sized array of single doubles instead. Or use some other way.
     * For example treat array of SParam as array of C++ complex but this is pretty illegal. To test such optimization works on current distribution this function can be used
     *  Fills p1 using pattern ( i -- zerobased index )
     *       p1[i].real = Pi / (i+1)
             p1[i].imag = 1. / p1[i].real
             p2[i].real = Pi * i
             p2[i].imag = Pi ^ (i+1)
    */
    PVNA_EXPORTED PVNA_Res   pocketvna_debug_response(const PVNA_DeviceHandler, const PVNA_Size size,
                                                     PVNA_Sparam * p1, PVNA_Sparam * p2);

// ------------- Aux,rfmath stuff ------------------------------
    /**
     * @brief pocketvna_rfmath_calibrate_transmission
     *   Applies Simple compensation algorithm for transmission mode (S21 forward or S12 backward)
     * @param raw_meas_mn  raw measurements that should be calibrated. S21 for forward (or S12 for backward). Should not be NULL
     * @param open_thru_mn calibration data for Open (unconnected) ports. S21 (or S12). Should not be NULL
     * @param thru_mn      calibration data for Through (connected ports). S21 (or S12). Should not be NULL
     * @param size         size of all arrays. Should be greater than 0
     * @param dut_mn       results, output array, calibrated data. Should not be NULL
     * @return  No_Data if any pointer is NULL or size is 0. Otherwise returns Ok
     */
    PVNA_EXPORTED PVNA_Res pocketvna_rfmath_calibrate_transmission(
            const PVNA_Sparam * raw_meas_mn,
            const PVNA_Sparam * open_thru_mn, const PVNA_Sparam * thru_mn,
            const PVNA_Size,
            PVNA_Sparam * dut_mn
    );

    /**
     * @brief pocketvna_rfmath_calibrate_reflection
     *    Applies Simple compensatino algorithm for reflection mode (S11 or S22)
     * @param raw_meas_mm raw uncalibrated measurements S11 (or S22). Should not be NULL
     * @param short_mm    calibration data for short standard. S11 (or S22). Should not be NULL
     * @param open_mm     calibration data for open standard. S11 (or S22). Should not be NULL
     * @param load_mm     calibration data for load (50 Ohm) standard. S11 (or S22). Should not be NULL
     * @param size        size of all arrays. Should be greater than 0
     * @param Z0          Characteristic Impedance, Z0
     * @param dut_mm      results, output array, calibrated data. . Should not be NULL
     * @return No_Data if any pointer is NULL or size is 0. Otherwise returns Ok
     */
    PVNA_EXPORTED PVNA_Res pocketvna_rfmath_calibrate_reflection(
            const PVNA_Sparam * raw_meas_mm,
            const PVNA_Sparam * short_mm, const PVNA_Sparam * open_mm, const PVNA_Sparam * load_mm,
            const PVNA_Size,
            double Z0,
            PVNA_Sparam * dut_mm
    );

    /**
     * @brief Force Unlock for all devices connected
     *    Forces unlocking for a locked device. It is usefull for linux only.
     *       Linux does not clear named mutexes/semaphores if app was crashed/killed and calls no destructor/disposal function
     *    !It unlocks all connected devices
     */
    PVNA_EXPORTED PVNA_Res pocketvna_force_unlock_devices(void);

// ------------- 4 - Port support. New 4-Port devices only ------------------------------
    typedef PVNA_Sparam * PVNA_SParamRef;
    /**
     * @brief 4-Port scan for a frequency list
     *   Scan 4-Port network (up-to 16) at once. Accepts list of Sparameter pointers
     *   Make sure each parameter required parameter not null and has the same size as frequrencies
     *   To Get NetworkParameter's position in @p sparams_refs use  @fn PVNA_4P_INDEX_FOR_PARAM()
     *  @param sparams_refs -- list of pointers. Each pointer is an array of SParams (Complex numbers). The index is PVNA_4P_INDEX_FOR_PARAM()
     */
    PVNA_EXPORTED PVNA_Res pocketvna_4p_scan(const PVNA_DeviceHandler, const PVNA_Frequency *, const PVNA_Size,
                                          const AveragingQuality, const PVNA_NetworkParameters,
                                          PVNA_SParamRef sparams_refs[16],
                                          PVNA_ProgressCallBack *);
    /**
     * @brief 4-Port scan for a frequency list with C function pointer as progress
     *  The same as  pocketvna_4p_scan() (wrapper around it) but accepts Plain C-function as a callback for progres
     */
    PVNA_EXPORTED PVNA_Res pocketvna_4p_scan_with_cproc(const PVNA_DeviceHandler, const PVNA_Frequency *, const PVNA_Size,
                                          const AveragingQuality, const PVNA_NetworkParameters,
                                          PVNA_SParamRef sparams_refs[16],
                                          PVNA_PFN_Progress_Func);

    /**
     * @brief 4-Port scan for a frequency range
     *   Scan 4-Port network (up-to 16) at once. Accepts list of Sparameter pointers
     *   Make sure each parameter required parameter not null and has the same size as frequrencies
     *   To Get NetworkParameter's position in @p sparams_refs use  @fn PVNA_4P_INDEX_FOR_PARAM()
     *  @param sparams_refs -- list of pointers. Each pointer is an array of SParams (Complex numbers). The index is PVNA_4P_INDEX_FOR_PARAM()
     */
    PVNA_EXPORTED PVNA_Res pocketvna_4p_scan_4range(const PVNA_DeviceHandler,
                                          const PVNA_Frequency start, const PVNA_Frequency end, const PVNA_Size, enum PocketVNADistribution,
                                          const AveragingQuality, const PVNA_NetworkParameters,
                                          PVNA_SParamRef sparams_refs[16],
                                          PVNA_ProgressCallBack *);

    /**
     * @brief 4-Port scan for a frequency list with C function pointer as progress
     *  The same as  pocketvna_4p_scan_4range() (wrapper around it) but accepts Plain C-function as a callback for progres
     */
    PVNA_EXPORTED PVNA_Res pocketvna_4p_scan_4range_with_cproc(const PVNA_DeviceHandler,
                                          const PVNA_Frequency start, const PVNA_Frequency end, const PVNA_Size, enum PocketVNADistribution,
                                          const AveragingQuality, const PVNA_NetworkParameters,
                                          PVNA_SParamRef sparams_refs[16],
                                          PVNA_PFN_Progress_Func);

    /**
     * @brief Helper for 4-Port scan for frequencies (with separated arguments)
     *   4-Port scan. This is a helper for For rest languages (python,C#...).
     *   It is easier to pass 16 parameters than a single array of pointers
     *   Wrapps around  pocketvna_4p_scan_with_cproc()
     */
    PVNA_EXPORTED PVNA_Res pocketvna_4p_scan_separate(const PVNA_DeviceHandler, const PVNA_Frequency *, const PVNA_Size,
                                          const AveragingQuality, const PVNA_NetworkParameters,

                                          PVNA_Sparam * s11, PVNA_Sparam * s12,  PVNA_Sparam * s13, PVNA_Sparam * s14,
                                          PVNA_Sparam * s21, PVNA_Sparam * s22,  PVNA_Sparam * s23, PVNA_Sparam * s24,
                                          PVNA_Sparam * s31, PVNA_Sparam * s32,  PVNA_Sparam * s33, PVNA_Sparam * s34,
                                          PVNA_Sparam * s41, PVNA_Sparam * s42,  PVNA_Sparam * s43, PVNA_Sparam * s44,

                                          PVNA_PFN_Progress_Func);

    /**
     * @brief Helper for 4-Port scan for a range (with separated arguments)
     * @details 4-Port scan for a range. This is a helper for For rest languages (python,C#...).
     *   It is easier to pass 16 parameters than a single array of pointers
     *   Wrapper for pocketvna_4p_scan_4range_with_cproc()
     */
    PVNA_EXPORTED PVNA_Res pocketvna_4p_scan_4range_separate(const PVNA_DeviceHandler,
                                          const PVNA_Frequency start, const PVNA_Frequency end, const PVNA_Size, enum PocketVNADistribution,
                                          const AveragingQuality, const PVNA_NetworkParameters,

                                          PVNA_Sparam * s11, PVNA_Sparam * s12,  PVNA_Sparam * s13, PVNA_Sparam * s14,
                                          PVNA_Sparam * s21, PVNA_Sparam * s22,  PVNA_Sparam * s23, PVNA_Sparam * s24,
                                          PVNA_Sparam * s31, PVNA_Sparam * s32,  PVNA_Sparam * s33, PVNA_Sparam * s34,
                                          PVNA_Sparam * s41, PVNA_Sparam * s42,  PVNA_Sparam * s43, PVNA_Sparam * s44,

                                          PVNA_PFN_Progress_Func);


    /**
     * @brief Set control variable. For "pVNA 6G" devices only
     * @details set control variable on a device.
     * For example: enable/disable calibration
     */
    PVNA_EXPORTED PVNA_Res pocketvna_pVNA6G_set_ctrl_var(const PVNA_DeviceHandler,
                                                         const enum PocketVnaInternalControlVariable,
                                                         const enum PocketVnaControlVariableValue);


    /**
     * @brief Get a control variable. For "pVNA 6G" devices only
     * @details reading control variable on a device.
     * @value out code for value. In case of success one of PocketVnaControlVariableValue's values. -1 if value was not returned
     */
    PVNA_EXPORTED PVNA_Res pocketvna_pVNA6G_get_ctrl_var(const PVNA_DeviceHandler,
                                                         const enum PocketVnaInternalControlVariable,
                                                         int * value);


    /**
     * @brief Get a status struct. For "pVNA 6G" devices only
     * @details reading device's internal status buffer.
     * @param dstbuffer   predefined buffer where to write data to. Pass NULL to get required data size. If return value is OK buffer will be filled with status bytes
     * @param inoutsize NON-NULL pointer. Should contain size of  @p dstbuffer. After function completes it stores number of written bytes, or required buffer size if @p dstbuffer is NULL
     */
    PVNA_EXPORTED PVNA_Res pocketvna_pVNA6G_get_status(const PVNA_DeviceHandler,
                                                         uint8_t * dstbuffer,
                                                         PVNA_Size * inoutsize);


    /**
     * @brief Index for parameter in 16elms array of pointers
     * @details  Kind of macro. Helper to find out position for network parameter
     *  in pocketvna_4p_scan() pocketvna_4p_scan_with_cproc(), pocketvna_4p_scan_4range() and pocketvna_4p_scan_4range_with_cproc()
     * @return returns index in 16 elms array
     */
    static inline int PVNA_4P_INDEX_FOR_PARAM(const PVNA_NetworkParameter p) {
        switch ( p ) {
        case PVNA_S11:    return  0;
        case PVNA_S12:    return  1;
        case PVNA_S13:    return  2;
        case PVNA_S14:    return  3;

        case PVNA_S21:    return  4;
        case PVNA_S22:    return  5;
        case PVNA_S23:    return  6;
        case PVNA_S24:    return  7;

        case PVNA_S31:    return  8;
        case PVNA_S32:    return  9;
        case PVNA_S33:    return 10;
        case PVNA_S34:    return 11;

        case PVNA_S41:    return 12;
        case PVNA_S42:    return 13;
        case PVNA_S43:    return 14;
        case PVNA_S44:    return 15;

        case PVNA_SNone:
            break;
        }
        return -1;
    }


#ifdef __cplusplus
}
#endif

