// USE to compile mkoctfile  -v -Wl,/home/mntmnt/Projects/projectadc/device-api/libPocketVnaApi_x64.so pocketvna-octave.cc
#include <octave/oct.h>
#include <octave/ov-struct.h>
#include <octave/parse.h>
#include <octave/dRowVector.h>
#include <octave/Range.h>
#include <octave/uint64NDArray.h>
#include <octave/CNDArray.h>
#include <octave/CRowVector.h>

#include <string>
#include <map>

#include "pocketvna.h"

namespace {
    const auto ResultField        = "RESULT";
    const auto ResultExplanation  = "RESULT_EXPLAIN";
    const auto ErrorMsgField      = "error";
    const auto DeviceHandlerField = "DEVICE_HANDLE";
    const auto s11Str="s11", s21Str="s21",
               s12Str="s12", s22Str="s22";

    PVNA_NetworkParameter str2Param(const std::string & value) {
        const static std::map<std::string,PVNA_NetworkParameter> accordance = {
            {s11Str, PVNA_S11},
            {s21Str, PVNA_S21},
            {s12Str, PVNA_S12},
            {s22Str, PVNA_S22},
        };
        auto found = accordance.find(value);
        if ( found != accordance.end() ) {
            return found->second;
        } else {
            octave_stdout << "Unsupported parameter `" << value << "'\n";
            return PVNA_SNone;
        }
    }

    template<class Arguments>
    PVNA_NetworkParameters readParameters(const Arguments & args) {
        PVNA_NetworkParameters params = PVNA_SNone;

        if ( args.length() > 4 ) {
            for ( int i = 4; i < args.length(); ++i ) {
                params = params | str2Param(args(i).string_value());
            }
            return params;
        } else {
            return PVNA_2P_ALL;
        }
    }

    octave_value createError(const std::string & message, const std::string & explanation) {
        octave_scalar_map st;  
        st.assign(ResultField,       false);
        st.assign(ErrorMsgField,     message);
        st.assign(ResultExplanation, explanation);
        return octave_value(st);//#octave_value(ComplexNDArray(dim_vector(0, 2, 2)));
    }

    octave_value createOk() {
        octave_scalar_map st;  
        st.assign(ResultField,       true);
        st.assign(ErrorMsgField,     "Ok");
        st.assign(ResultExplanation, "Everything is fine");
        return octave_value(st);
    }

    std::string res2str(PVNA_Res r) {
        return pocketvna_result_string(r);
    }

    std::string join(const std::vector<std::string> & list) {
        std::string result;
        result.reserve(list.size() * 5);
        for ( size_t i = 0; i < list.size(); ++i ) {
            result += list[i];
            if ( i != list.size() - 1 ) {
                result += "/";
            }
        }
        return result;
    }

    RowVector mkRange(PVNA_Frequency from, PVNA_Frequency to) {
        RowVector kindOfRange;
        kindOfRange.resize(2);
        kindOfRange(0) = (from);
        kindOfRange(1) = (to);
        return kindOfRange;
    }
    
}

octave_value_list driverVersion() {
    uint16_t version = 0.;
    double info      = 0.;
    PVNA_Res r = pocketvna_driver_version(&version, &info);
    
    if ( r != PVNA_Res_Ok ) {
        return createError("Failed driver_version request", res2str(r));
    }
    
    octave_scalar_map st;
    st.assign(ResultField,true);
    st.assign("VERSION",  version);
    st.assign("PI",       info);
    
    return octave_value (st);
}

octave_value listDevices() {
    PVNA_DeviceDesc * list = 0;
    uint16_t sz = 0;
    PVNA_Res r = pocketvna_list_devices(&list, &sz);

    if ( r != PVNA_Res_Ok && r != PVNA_Res_NoDevice ) {
       octave_stdout << "driver_version returned non-OK status: " << res2str(r) << "\n";
       return RowVector();
    }     

    if ( r == PVNA_Res_NoDevice )  {
       octave_stdout << "\nThere is No device available\n";
       return RowVector();
    }

    octave_value_list retval;
    retval.resize (sz);

    for ( size_t i = 0; i < sz; ++i ) {
        octave_scalar_map st;
        std::wstring sn = list[i].serial_number; 
        std::wstring ven= list[i].manufacturer_string;
        std::wstring nm = list[i].product_string;
        st.assign ("index",      i);
        st.assign ("path",       list[i].path);
        st.assign ("SN",         std::string(sn.begin(), sn.end()) );
        st.assign ("vendor",     std::string(ven.begin(),ven.end()) );
        st.assign ("name",       std::string(nm.begin(), nm.end()) );
        st.assign ("version",    list[i].release_number);
        st.assign ("permissions",list[i].access);
        st.assign ("VID",        list[i].vid );
        st.assign ("PID",        list[i].pid );
        st.assign ("iface",      list[i].ciface_code);
        switch ( list[i].ciface_code ) {
        case CIface_HID: st.assign ("ifaceStr",   "HID");  break;
        case CIface_VCI: st.assign ("ifaceStr",   "VCI");  break;
        default:         st.assign ("ifaceStr",   "<?>");  break;
        }
        retval(i) = st;
    }

    pocketvna_free_list(&list);

    return octave_value(retval);
}

octave_value openDevice(const octave_scalar_map & mp) {
//    const int index       = mp.getfield("index").int_value();
    const std::string pth = mp.getfield("path").string_value();
    std::string tmp = mp.getfield("SN").string_value();
    const std::wstring sn(tmp.begin(), tmp.end());

    tmp = mp.getfield("vendor").string_value();
    const std::wstring vendor(tmp.begin(), tmp.end());
    tmp = mp.getfield("name").string_value();
    const std::wstring  name(tmp.begin(), tmp.end());

    const uint16_t vers = mp.getfield("version").uint_value();

    const uint16_t vid  = mp.getfield("VID").uint_value();
    const uint16_t pid  = mp.getfield("PID").uint_value();

    PVNA_DeviceDesc desc;
    desc.path = pth.c_str();
    desc.manufacturer_string = vendor.c_str();
    desc.pid = pid;
    desc.vid = vid;
    desc.product_string = name.c_str();
    desc.release_number = vers;
    desc.serial_number  = sn.c_str();
    desc.ciface_code    = mp.getfield("iface").uint_value();
    desc.next= 0;

    PVNA_DeviceHandler handle;
    PVNA_Res r = pocketvna_get_device_handle_for(&desc, &handle);

    octave_scalar_map st;

    st.assign (ResultField,        r == PVNA_Res_Ok);
    st.assign (ErrorMsgField,      r == PVNA_Res_Ok ? "OK" : "FAILED");
    st.assign (ResultExplanation,  res2str(r));
    st.assign (DeviceHandlerField, (uint64_t)handle);

    return octave_value(st);
}

octave_value deviceVersion(const octave_value & l) {
    static_assert(sizeof(PVNA_DeviceHandler) <= sizeof(uint64_t), "SHOULD be compatible with uint64");

    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());
    uint16_t ver = 0;

    PVNA_Res r = pocketvna_version(handle, &ver);
    
    octave_scalar_map st;

    if ( r != PVNA_Res_Ok ) {
        return createError("Failed pocketvna_version", res2str(r));        
    }

    st.assign (ResultField, true);
    st.assign ("VERSION",   ver);

    return octave_value(st);
}

octave_value closeDevice( const octave_value & l ) {
    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());

    PVNA_Res r = pocketvna_release_handle(&handle);
    if ( r != PVNA_Res_Ok ) {
        return createError("Failed pocketvna_release_handle", res2str(r));
    }

    return createOk();
}

octave_value forceUnlock() {
    auto r = pocketvna_force_unlock_devices();
    if ( r == PVNA_Res_Ok ) {
        return createOk();
    } else {
        return createError("Failed pocketvna_force_unlock_devices",  res2str(r));
    }
}

octave_value getSettings(const octave_value & l ) {
    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());

    octave_scalar_map st;
    st.assign(ResultField, false);

    std::vector<std::string> supportedModes;
    supportedModes.reserve(4);

    //PVNA_Res_InvalidHandle;PVNA_Res_Ok;PVNA_Res_UnsupportedTransmission

    // S11?
    PVNA_Res r = pocketvna_is_transmission_supported(handle, PVNA_S11);
    if ( r == PVNA_Res_InvalidHandle ) {
        return createError("pocketvna_is_transmission_supported(PVNA_S11) failed", "Handler is invalid");
    } else if ( r == PVNA_Res_Ok ) supportedModes.push_back(s11Str);

    // S21?
    r = pocketvna_is_transmission_supported(handle, PVNA_S21);
    if ( r == PVNA_Res_InvalidHandle ) {
        return createError("pocketvna_is_transmission_supported(PVNA_S21) failed", "Handler is invalid");
    } else if ( r == PVNA_Res_Ok ) supportedModes.push_back(s21Str);

    // S12?
    r = pocketvna_is_transmission_supported(handle, PVNA_S12);
    if ( r == PVNA_Res_InvalidHandle ) {
        return createError("pocketvna_is_transmission_supported(PVNA_S12) failed", "Handler is invalid");
    } else if ( r == PVNA_Res_Ok ) supportedModes.push_back(s12Str);

    // S22?
    r = pocketvna_is_transmission_supported(handle, PVNA_S22);
    if ( r == PVNA_Res_InvalidHandle ) {
        return createError("pocketvna_is_transmission_supported(PVNA_S22) failed", "Handler is invalid");
    } else if ( r == PVNA_Res_Ok ) supportedModes.push_back(s22Str);

    //--------------------------------------------------


    double z0 = 0.;
    r = pocketvna_get_characteristic_impedance(handle, &z0);
    if ( r != PVNA_Res_Ok ) {
        return createError("pocketvna_get_characteristic_impedance failed", res2str(r) );
    }

    PVNA_Frequency valid_from = 0, valid_to = 0;
    r = pocketvna_get_valid_frequency_range(handle, &valid_from, &valid_to);
    if ( r != PVNA_Res_Ok ) {
        return createError("pocketvna_get_valid_frequency_range failed", res2str(r) );
    }


    PVNA_Frequency rsnbl_from = 0, rsnbl_to = 0;
    r = pocketvna_get_reasonable_frequency_range(handle, &rsnbl_from, &rsnbl_to);
    if ( r != PVNA_Res_Ok ) {
        return createError("pocketvna_get_reasonable_frequency_range failed", res2str(r) );
    }


    auto validRange     = mkRange(valid_from, valid_to);
    auto reasonableRange= mkRange(rsnbl_from, rsnbl_to);

    st.assign(ResultField,            true);
    st.assign("MODES",                join(supportedModes));
    st.assign("VALID_FREQUENCY",      validRange);
    st.assign("REASONABLE_FREQUENCY", reasonableRange);
    st.assign("Z0",                   z0);

    return octave_value( st );
}

octave_value isConnectionValid(const octave_value & l) {
     PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(l.uint64_value());

     if (! handle ) return octave_value(false);

     PVNA_Res r = pocketvna_is_valid(handle);

     return octave_value(r == PVNA_Res_Ok);
}


octave_value scanData(const octave_value & hc,
                      const NDArray & freq,
                      const unsigned avg,
                      PVNA_NetworkParameters params) {
    PVNA_DeviceHandler handle = (PVNA_DeviceHandler)(hc.uint64_value());    

    if (! handle ) {
        return createError("bad handle", "no handle provided" );
    }

    int length = freq.numel(); // length() is deprecated

    std::vector<uint64_t> frequencies(length, 0);
    for ( int i = 0; i < length; ++i ) {
        frequencies[i] = freq.elem(i, 0, 0);
    }

    size_t sz = frequencies.size();

    std::vector<PVNA_Sparam> s11(sz, {0., .0}), s21(sz, {0., .0}),
                             s12(sz, {0., .0}), s22(sz, {0., .0});

    PVNA_Res r = pocketvna_multi_query( handle, frequencies.data(), sz, avg,
                           params,
                           &s11[0], &s21[0],
                           &s12[0], &s22[0], nullptr );

    if ( r != PVNA_Res_Ok ) {
        return createError("failed to scan", res2str(r));
    }

    octave_idx_type szi = sz;
    ComplexNDArray res(dim_vector(szi, 2, 2));

    for ( size_t i = 0; i < sz; ++i ) {
        res(i, 0, 0) = std::complex<double>(s11[i].real, s11[i].imag);
        res(i, 1, 0) = std::complex<double>(s21[i].real, s21[i].imag);
        res(i, 0, 1) = std::complex<double>(s12[i].real, s12[i].imag);
        res(i, 1, 1) = std::complex<double>(s22[i].real, s22[i].imag);
    }

    octave_scalar_map st;
    st.assign(ResultField,  true);
    st.assign("Network", octave_value(res));

    return octave_value(st);
}

DEFUN_DLD (pocketvna_octave, args, , "'Interrogate'  pocketVNA device.\n"
                                     "\t driver_version -- driver version\n"
                                     "\t list    -- enumerate available devices\n"
                                     "\t open    -- opens device by its description received by 'list'. Returns a handle\n"
                                     "\t version -- device version, accepts handle\n"
                                     "\t close   -- closes device by handle\n"
                                     "\t unlock  -- Force Unlocking 'used' device. Useful for linux\n"
                                     "\t settings-- returns hashmap with device settings like frequency range, Z0, supported modes. Accepts handle \n"
                                     "\t valid?  -- checks whether a handle is valid\n"
                                     "\t scan    -- accepts handle, frequency (range or vector) and Average factor. + list of parameters as strings. Returns array of 2x2 matrices\n"
                                     "") {
    if ( args.length() > 0 && args(0).is_string() ) {
        std::string functionCode = args(0).string_value ();
  
        if ( functionCode == "driver_version" ) {
            return driverVersion();
        } else if ( functionCode == "list" ) {
            return listDevices();
        } else if ( functionCode == "open" ) {
            return openDevice(args(1).scalar_map_value());
        } else if ( functionCode == "version" ) {
            return deviceVersion(args(1));
        } else if ( functionCode == "close" ) {
            return closeDevice(args(1));
        } else if ( functionCode == "unlock" ) {
            return forceUnlock();
        } else if ( functionCode == "settings" ) {
            //pocketvna_get_characteristic_impedance
            //pocketvna_get_valid_frequency_range
            //pocketvna_get_reasonable_frequency_range
            return getSettings(args(1));
        } else if ( functionCode == "valid?" ) {
            return isConnectionValid(args(1));
        } else if ( functionCode == "scan" ) {
            if ( args.length() < 3 ) {
                return createError("handle(1st) and frequencies (2nd) arguments are missing",
                                   "no handle provided; no frequencies provided"
                );
            }
            octave_value h  = args(1);
            NDArray f  = args(2).array_value();
            const unsigned avg = args.length() > 3 ? args(3).uint_value() : 1;
            PVNA_NetworkParameters params = readParameters(args);
            if ( params == PVNA_SNone ) {
                return createError("no parameters", "No Network Paremeters requested");                
            }
  
            if ( f.dim2() > f.dim1() ) f = f.transpose();
  
            return octave_value( scanData(h, f, avg, params) );
        }
    }
    
    print_usage();

    return octave_value(false);
}
