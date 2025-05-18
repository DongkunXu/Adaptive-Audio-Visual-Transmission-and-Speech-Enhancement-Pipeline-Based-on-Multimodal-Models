import pocketvna

import unittest
import numpy
import signal

driver = None
try:
    driver = pocketvna.Driver()
except:
    driver = None
    print("Unfortunately, can not open driver!")
    exit(6)

def sigterm_handler(signal, frame):
    # save the state here or do whatever you want
    print('booyah! bye bye')
    if driver is not None:
        driver.close()


signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGABRT, sigterm_handler)
signal.signal(signal.SIGINT,  sigterm_handler)
signal.signal(signal.SIGSEGV, sigterm_handler)
AVERAGE = 5
def DeafultConnect(driver):
    #return driver.connect_to(0)
    return driver.connect_to_first(ifaceCode = pocketvna.ConnectionInterfaceCode.CIface_HID)
    #return driver.connect_to_first(ifaceCode = pocketvna.ConnectionInterfaceCode.CIface_VCI)


class TestDriver1Initial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = driver
        cls.count_driver = driver.count()

    @classmethod
    def tearDownClass(cls):
        cls.count_driver = 0
        #cls.driver = None
        #cls.count_driver = 0

    def test_driver_is_created(self):
        self.assertIsNotNone(TestDriver1Initial.driver)

    def test_driver_version(self):
        v, pi = pocketvna.driver_version()

        self.assertEqual(v, pocketvna.VERSION)
        self.assertAlmostEqual(pi, 3.141592653589793)

    def test_there_is_any_driver(self):
        self.assertGreater(TestDriver1Initial.count_driver, 0)

    def test_should_connect_to_first_device(self):
        self.assertTrue( DeafultConnect(TestDriver1Initial.driver) )
        self.assertTrue( TestDriver1Initial.driver.valid() )

    def _assertMessageEquals(self, exp, res):
        s = res.decode('utf-8')
        self.assertEqual(exp, s)

    def test_should_get_expected_error_message_for_code(self):
        text = pocketvna.result_string(pocketvna.Result.OK)
        self.assertEqual("Ok", text)

        text = pocketvna.result_string(pocketvna.Result.InvalidHandle)
        self.assertEqual("device gone", text)

        text = pocketvna.result_string(pocketvna.Result.BadResponse)
        self.assertEqual("unexpected/corrupted device response", text)

        text = pocketvna.result_string(pocketvna.Result.RESP_Res_No_Data)
        self.assertEqual("some parameter is not set", text)

        text = pocketvna.result_string(pocketvna.Result.PVNA_Res_EndLEQStart)
        self.assertEqual("end frequency should be greater than the start frequency", text)

        text = pocketvna.result_string(pocketvna.Result.PVNA_Res_BadArgument)
        self.assertEqual("bad function's arguments", text)

        text = pocketvna.result_string(pocketvna.Result.PVNA_Res_NotImplemented)
        self.assertEqual("The call is not implemented for current device", text)

        text = pocketvna.result_string(pocketvna.Result.PVNA_Res_BadArgument)
        self.assertEqual("bad function's arguments", text)

        text = pocketvna.result_string(pocketvna.Result.PVNA_Res_BadArgument + 1)
        self.assertEqual("<Unexpected_Error_Code>!", text)

        text = pocketvna.result_string(pocketvna.Result.PVNA_Res_Fail)
        self.assertEqual("<is non implemented>", text)

        text = pocketvna.result_string(pocketvna.Result.PVNA_Res_Fail + 1)
        self.assertEqual("<Unexpected_Error_Code>!", text)


def genFrequency(size):
    sz = size
    freq = numpy.zeros(sz, dtype=numpy.uint64)
    for i in range(0, freq.size): freq[i] = 1000000 + i * 100
    return freq


class TestDriver2(unittest.TestCase):
    def _assertComplexNotNear(self, c1, cexp):
        self.assertNotAlmostEqual(c1.real, cexp.real)
        self.assertNotAlmostEqual(c1.imag, cexp.imag)

    def _assertComplexNear(self, c1, cexp):
        self.assertAlmostEqual(c1.real, cexp.real)
        self.assertAlmostEqual(c1.imag, cexp.imag)

    def _assertZeros(self, complexes):
        self.assertTrue( all(v == 0+0j for v in complexes) )

    def _assertNotZeros(self, complexes):
        self.assertTrue( all(v != 0+0j for v in complexes) )

    def test_version_and_Network_parameters_Support(self):
        firmware_version = driver.version()

        iss11, iss21 = driver.has_s11(),   driver.has_s21()
        iss12, iss22 = driver.has_s12(),   driver.has_s22()

        ## FIRMWARE VERSION ON THE DEVICE
        firmware_version = driver.version()

        self.assertGreater(firmware_version, 0)

        self.assertTrue(iss11)
        self.assertTrue(iss21)

        if firmware_version > 0x105:
            self.assertTrue(iss12)
            self.assertTrue(iss22)

    def test_should_get_characteristic_impedance(self):
        RR = driver.Z0()

        self.assertAlmostEqual(RR, 50.00)

    def test_should_return_expected_valid_frequency_range(self):
        start, end = driver.valid_frequency_range()

        self.assertEqual(start,  1)
        self.assertEqual(end,    6000000000)

    def test_should_return_expected_reasonable_frequency_range(self):
        start, end = driver.reasonable_frequency_range()

        self.assertEqual(start, 500000)
        self.assertEqual(end,   4000000000)

    def test_should_fails_for_too_low_frequency(self):
        try:
            s11, s21, s12, s22 = driver.single_scan(0, 10, pocketvna.NetworkParams.ALL_2P)
        except pocketvna.PocketVnaAPIError as e:
            self.assertTrue(True, "We excpect APIERrror")
            self.assertEqual(e.code(), pocketvna.Result.BadFrequency)
        except: self.assertTrue(False, "Unexpected Exception")
        else:   self.assertTrue(False, "Should Throw Exception")

    def test_should_fails_for_too_high_frequency(self):
        try:
            s11, s21, s12, s22 = driver.single_scan(6000000001, 10, pocketvna.NetworkParams.ALL_2P)
        except pocketvna.PocketVnaAPIError as e:
            self.assertTrue(True, "We excpect APIERrror")
            self.assertEqual(e.code(), pocketvna.Result.BadFrequency)
        except: self.assertTrue(False, "Unexpected Exception")
        else:   self.assertTrue(False, "Should Throw Exception")

    ## Checking on S is 0 + 0i or not are not good for device can return 0.0 + 0i in theory
    def test_should_return_paramterers_for_min_valid_frequency(self):
        s11, s21, s12, s22 = driver.single_scan(1, 10, pocketvna.NetworkParams.ALL_2P)
        self._assertComplexNotNear(s11, complex(0.0, 0.0))
        self._assertComplexNotNear(s21, complex(0.0, 0.0))
        self._assertComplexNotNear(s12, complex(0.0, 0.0))
        self._assertComplexNotNear(s22, complex(0.0, 0.0))

    ## Checking on S is 0 + 0i or not are not good for device can return 0.0 + 0i in theory
    def test_should_return_paramterers_for_max_valid_frequency(self):
        s11, s21, s12, s22 = driver.single_scan(6000000000, 10, pocketvna.NetworkParams.ALL_2P)
        self._assertComplexNotNear(s11, complex(0.0, 0.0))
        self._assertComplexNotNear(s21, complex(0.0, 0.0))
        self._assertComplexNotNear(s12, complex(0.0, 0.0))
        self._assertComplexNotNear(s22, complex(0.0, 0.0))

    ## Checking on S is 0 + 0i or not are not good for device can return 0.0 + 0i in theory
    def test_should_scan_S11_parameter(self):
        s11, s21, s12, s22 = driver.single_scan(1000000000, 1,  pocketvna.NetworkParams.S11)
        self._assertComplexNotNear(s11, complex(0.0, 0.0))
        self._assertComplexNear(s21, complex(0.0, 0.0))
        self._assertComplexNear(s12, complex(0.0, 0.0))
        self._assertComplexNear(s22, complex(0.0, 0.0))

    ## Checking on S is 0 + 0i or not are not good for device can return 0.0 + 0i in theory
    def test_should_scan_s21_parameter(self):
        s11, s21, s12, s22 = driver.single_scan(2000000000, 100,  pocketvna.NetworkParams.S21)
        self._assertComplexNear(s11, complex(0.0, 0.0))
        self._assertComplexNotNear(s21, complex(0.0, 0.0))
        self._assertComplexNear(s12, complex(0.0, 0.0))
        self._assertComplexNear(s22, complex(0.0, 0.0))

    ## Checking on S is 0 + 0i or not are not good for device can return 0.0 + 0i in theory
    def test_should_scan_s12_parameter(self):
        s11, s21, s12, s22 = driver.single_scan(3000000000, 10,  pocketvna.NetworkParams.S12)
        self._assertComplexNear(s11, complex(0.0, 0.0))
        self._assertComplexNear(s21, complex(0.0, 0.0))
        self._assertComplexNotNear(s12, complex(0.0, 0.0))
        self._assertComplexNear(s22, complex(0.0, 0.0))

    def test_should_scan_s22_parameters(self):
        s11, s21, s12, s22 = driver.single_scan(4000000000, 10,  pocketvna.NetworkParams.S22)
        self._assertComplexNear(s11, complex(0.0, 0.0))
        self._assertComplexNear(s21, complex(0.0, 0.0))
        self._assertComplexNear(s12, complex(0.0, 0.0))
        self._assertComplexNotNear(s22, complex(0.0, 0.0))

    def test_should_scan_all_network_parameters(self):
        sz   = 40
        freq = genFrequency(sz)

        counters = { "index": 0, "calls": 0 }

        def on_progress(userdata, index):
            counters["index"]  = index
            counters["calls"] += 1
            return pocketvna.Continue

        s11, s21, s12, s22 = driver.scan(freq, 10,  pocketvna.NetworkParams.ALL_2P, on_progress)

        self.assertEqual(counters["index"],   sz)
        self.assertGreater(counters["calls"], 0)

        self.assertEqual(s11.size, sz)
        self._assertNotZeros(s11)
        self.assertEqual(s21.size, sz)
        self._assertNotZeros(s22)
        self.assertEqual(s12.size, sz)
        self._assertNotZeros(s12)
        self.assertEqual(s22.size, sz)
        self._assertNotZeros(s22)

    def test_should_scan_all_network_parameters(self):
        sz   = 40
        freq = genFrequency(sz)

        counters = { "index": 0, "calls": 0 }

        s11, s21, s12, s22 = driver.scan(freq, 10,  pocketvna.NetworkParams.ALL_2P, None)

        self.assertEqual(s11.size, sz)
        self._assertNotZeros(s11)
        self.assertEqual(s21.size, sz)
        self._assertNotZeros(s22)
        self.assertEqual(s12.size, sz)
        self._assertNotZeros(s12)
        self.assertEqual(s22.size, sz)
        self._assertNotZeros(s22)


    def test_should_scan_network_for_range_withNumpy(self):
        startFreq, endFreq = 1000000, 32000000
        steps = 100
        avg = 2
        params = pocketvna.NetworkParams.S11
        dist = pocketvna.Distributions.Linear

        s11, s21, s12, s22 = driver.scan4range_WithNumpy(startFreq, endFreq, steps, dist, avg, params, None)

        for item in [s11, s21, s12, s22]:
            self.assertEqual(len(item), steps)
            self.assertTrue( isinstance(item, numpy.ndarray ) )

        for item in [s21, s12, s22]:
            self._assertZeros(item)

        self._assertNotZeros(s11)


    def test_should_scan_network_for_range_withoutNumpy(self):
        startFreq, endFreq = 1000000, 32000000
        steps = 10
        avg = 2
        params = pocketvna.NetworkParams.ALL_2P
        dist = pocketvna.Distributions.Logarithmic

        s11, s21, s12, s22 = driver.scan4range_NoNumpy(startFreq, endFreq, steps, dist, avg, params, None)

        for item in [s11, s21, s12, s22]:
            self.assertEqual(len(item), steps)
            self.assertTrue( isinstance(item, list ) )
            self._assertNotZeros(item)


    def test_should_scan_all_network_parameters_Numpy(self):
        sz   = 40
        freq = genFrequency(sz)

        counters = { "index": 0, "calls": 0 }

        def on_progress(userdata, index):
            counters["index"]  = index
            counters["calls"] += 1
            return pocketvna.Continue

        s11, s21, s12, s22 = driver.scan_WithNumpy(freq, 10,  pocketvna.NetworkParams.ALL_2P, on_progress)

        self.assertEqual(counters["index"],   sz)
        self.assertGreater(counters["calls"], 0)


        self.assertEqual(len(s11), sz)
        self._assertNotZeros(s11)
        self.assertEqual(len(s21), sz)
        self._assertNotZeros(s22)
        self.assertEqual(len(s12), sz)
        self._assertNotZeros(s12)
        self.assertEqual(len(s22), sz)
        self._assertNotZeros(s22)

    def test_should_scan_all_network_parameters_NoNumpy(self):
        sz   = 23
        freq = genFrequency(sz)

        counters = { "index": 0, "calls": 0 }

        def on_progress(userdata, index):
            counters["index"]  = index
            counters["calls"] += 1
            return pocketvna.Continue

        s11, s21, s12, s22 = driver.scan_NoNumpy(freq, 2,  pocketvna.NetworkParams.ALL_2P, on_progress)

        self.assertEqual(counters["index"],   sz)
        self.assertGreater(counters["calls"], 0)

        self.assertEqual(len(s11), sz)
        self._assertNotZeros(s11)
        self.assertEqual(len(s21), sz)
        self._assertNotZeros(s22)
        self.assertEqual(len(s12), sz)
        self._assertNotZeros(s12)
        self.assertEqual(len(s22), sz)
        self._assertNotZeros(s22)

    def test_should_scan_all_network_parameters_NoNumpy_NoProgressCallback(self):
        sz   = 23
        freq = genFrequency(sz)

        s11, s21, s12, s22 = driver.scan_NoNumpy(freq, 5,  pocketvna.NetworkParams.ALL_2P)

        self.assertEqual(len(s11), sz)
        self._assertNotZeros(s11)
        self.assertEqual(len(s21), sz)
        self._assertNotZeros(s22)
        self.assertEqual(len(s12), sz)
        self._assertNotZeros(s12)
        self.assertEqual(len(s22), sz)
        self._assertNotZeros(s22)

    def test_should_scan_all_network_parameters_Numpy_NoProgressCallback(self):
        sz   = 23
        freq = genFrequency(sz)

        s11, s21, s12, s22 = driver.scan_WithNumpy(freq, 5,  pocketvna.NetworkParams.ALL_2P)

        self.assertEqual(s11.size, sz)
        self._assertNotZeros(s11)
        self.assertEqual(s21.size, sz)
        self._assertNotZeros(s22)
        self.assertEqual(s12.size, sz)
        self._assertNotZeros(s12)
        self.assertEqual(s22.size, sz)
        self._assertNotZeros(s22)

    def test_should_cancel_scan_network_parameters(self):
        sz = 500
        freq = genFrequency(sz)

        try:
            # Ignore scanned results.
            driver.scan(freq, 8,  pocketvna.NetworkParams.PORT1,
                lambda u, current_index: pocketvna.Cancel if current_index > 10 else pocketvna.Continue
            )
            self.assertTrue(False)
        except pocketvna.PocketVnaScanCanceled:
            self.assertTrue(True)

    def test_should_scan_S11_network_parameters(self):
        sz = 35
        freq = genFrequency(sz)

        s11, s21, s12, s22 = driver.scan(freq, 8,  pocketvna.NetworkParams.S11)

        self.assertEqual(s11.size, sz)
        self._assertNotZeros(s11)
        self.assertEqual(s21.size, sz)
        self._assertZeros(s21)
        self.assertEqual(s12.size, sz)
        self._assertZeros(s12)
        self.assertEqual(s22.size, sz)
        self._assertZeros(s22)

    def test_should_scan_S21_network_parameters(self):
        sz = 12
        freq = genFrequency(sz)

        s11, s21, s12, s22 = driver.scan(freq, 2,  pocketvna.NetworkParams.S21)

        self.assertEqual(s11.size, sz)
        self._assertZeros(s11)
        self.assertEqual(s21.size, sz)
        self._assertNotZeros(s21)
        self.assertEqual(s12.size, sz)
        self._assertZeros(s12)
        self.assertEqual(s22.size, sz)
        self._assertZeros(s22)

    def test_should_read_debug_response(self):
        sz = 4

        rc1, rc2 = driver.debugscan(sz)

        PI = 3.141592653589793238462643383279502884
        for idx in range(0, sz):
            v = PI / (idx + 1)
            exp = complex(v, 1.0 / v)
            exp2= complex(PI * idx, PI ** (idx+1))

            self._assertComplexNear(exp, rc1[idx])
            self._assertComplexNear(exp2,rc2[idx])

    def test_should_read_debug_response_NoNumpy(self):
        sz = 4

        rc1, rc2 = driver.debugscan(sz, nonumpy = True)

        PI = 3.141592653589793238462643383279502884
        for idx in range(0, sz):
            v = PI / (idx + 1)
            exp = complex(v, 1.0 / v)
            exp2= complex(PI * idx, PI ** (idx+1))

            self._assertComplexNear(exp, rc1[idx])
            self._assertComplexNear(exp2,rc2[idx])

    def test_should_read_firmware_version_immediately_for_107(self):
        driver_version, _ = pocketvna.driver_version()
        version_from_description = driver.version()
        if version_from_description !=  0x107:
            print("test_should_read_firmware_version_immediately_for_107 test is disabled. Functions get_info_* is not exposed")
            return

        self.assertTrue(version_from_description ==  0x107, "This query does not exist on elder firmware")
        # API_VERSION_SEARCH_TAG
        self.assertTrue(driver_version >= 51, "This query does not exist on elder driver")


        # works for version 0x107. It does not exist on elder driver/firmware
        version_taken_dirrectly = driver.get_info_firmware_version()

        self.assertEqual(version_taken_dirrectly, version_from_description, \
                "Version from description and from firmware should be equal")

        self.assertEqual(version_taken_dirrectly, 0x107, "Unexpected version" + str(version_taken_dirrectly))

    def test_should_read_firmware_version_immediately_for_newer_devcies(self):
        driver_version, _ = pocketvna.driver_version()
        version_from_description = driver.version()
        if version_from_description <  0x107:
            print("test_should_read_firmware_version_immediately_for_newer_devcies test is disabled. Functions get_info_* is not exposed")
            return
        if driver.devinfo()["InterfaceCode"] == pocketvna.ConnectionInterfaceCode.CIface_VCI:
            with self.assertRaises(pocketvna.PocketVnaAPIError) as cm:
                driver.get_info_firmware_version()
            raised = cm.exception
            self.assertEqual(pocketvna.Result.PVNA_Res_Fail, raised.error_code, msg="expected error")
        else:
            self.assertTrue(version_from_description >  0x107, "This query does not exist on elder firmware")
            # API_VERSION_SEARCH_TAG
            self.assertTrue(driver_version >= 51, "This query does not exist on elder driver")


            # works for version 0x107. It does not exist on elder driver/firmware
            version_taken_dirrectly = driver.get_info_firmware_version()

            self.assertEqual(version_taken_dirrectly, version_from_description, \
                    "Version from description and from firmware should be equal")

    def test_should_read_firmware_supports_mode_for_old_devices(self):
        driver_version, _ = pocketvna.driver_version()
        version_from_description = driver.version()

        if version_from_description >-  0x107:
            print("test_should_read_firmware_supports_mode_for_old_devices test is disabled. This test if for 1.5 firmware/device. 1 Path")
            return

        self.assertTrue(version_from_description >=  0x107, "This query does not exist on elder firmware")
        # API_VERSION_SEARCH_TAG
        self.assertTrue(driver_version >= 51, "This query does not exist on elder driver")

        # works for version 0x107. It does not exist on elder driver/firmware
        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S11)
        self.assertTrue(supported, " S11 is to be supported anyway")

        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S21)
        self.assertTrue(supported, " S21 is to be supported anyway")

        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S12)
        self.assertFalse(supported, " S12 should be supported on version >= 0x107")

        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S22)
        self.assertFalse(supported, " S22 should be supported on version >= 0x107")

    def test_should_read_firmware_supports_mode_for_newer_deviesd(self):
        driver_version, _ = pocketvna.driver_version()
        self.assertEqual(pocketvna.VERSION, driver_version, msg="Should have the same version")


    def test_should_read_firmware_supports_mode_for_newer_deviesd(self):
        driver_version, _ = pocketvna.driver_version()
        version_from_description = driver.version()

        if version_from_description <  0x107:
            print("test_should_read_firmware_supports_mode_for_newer_deviesd test is disabled. Functions get_info_* is not exposed")
            return

        self.assertTrue(version_from_description >=  0x107, "This query does not exist on elder firmware")
        # API_VERSION_SEARCH_TAG
        self.assertTrue(driver_version >= 51, "This query does not exist on elder driver")

        # works for version 0x107. It does not exist on elder driver/firmware
        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S11)
        self.assertTrue(supported, " S11 is to be supported anyway")

        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S21)
        self.assertTrue(supported, " S21 is to be supported anyway")

        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S12)
        self.assertTrue(supported, " S12 should be supported on version >= 0x107")

        supported = driver.get_info_param_supported(pocketvna.NetworkParams.S22)
        self.assertTrue(supported, " S22 should be supported on version >= 0x107")

    def test_should_get_temperature(self):
        driver_version, _ = pocketvna.driver_version()
        version_from_description = driver.version()

        if version_from_description <  0x107:
            print("test_should_get_temperature test is disabled. Functions get_info_* is not exposed")
            return

        self.assertTrue(version_from_description >=  0x107, "This query does not exist on elder firmware")
        self.assertTrue(driver_version > 40, "This query does not exist on elder driver")

        if version_from_description > 0x200:
            kalvin_temperature = driver.get_info_device_temperature()
            self.assertTrue(kalvin_temperature > 0.0, "It is positively warmer than 0K" + str(kalvin_temperature))

            self.assertTrue(kalvin_temperature > 200,  "~ -70*C is very rare temperature on enhabited earth " + str(kalvin_temperature))
            self.assertTrue(kalvin_temperature < 400, " Hard to imagine that device is hotter than boiling water " + str(kalvin_temperature))            
        else:
            with self.assertRaises(pocketvna.PocketVnaAPIError, msg="Elder device <=2.00") as error:
                kalvin_temperature = driver.get_info_device_temperature()
            self.assertEqual(pocketvna.Result.DEV_UnknownMode, error.exception.code(), msg="Elder device <=2.00. Request is not implemented")
 

class Data:
    class Meas:
        l_raw11   = [ 1.+4e-05j,           1.+3e-05j,          1.+2.0E-5j         ]
        l_raw21   = [-2270.0-1010.0j,     -3480.0-770.0j,      -2933.0+648.0j     ]
        l_raw12   = [ -1380.0-1690.0j,     -730.0 -1570.0j,     -2100.0+1180.0j    ]
        l_raw22   = [ 1.+1.0e-05j,         1. - 2e-06j,          1.-2e-05j        ]

    class Cali:
        l_shrt11 = [ 495607.8+158961.6j,  422794.4-77247.0j,  258956.2-256262.0j ]
        l_open11  = [-103507.6+103030.2j, -39050.0 +151186.0j, 46518.4 +163327.2j ]
        l_load11  = [ 107190.6+185938.2j,  159541.2+128062.6j, 180890.8+43653.8j  ]

        l_open21  = [ 1159.6-750.4j,       2114.4-68.2j,        2046.2+443.4j     ]
        l_thru21  = [ 445712.4+139863.0j,  313045.6-210936.8j, -11186.6-337464.8j ]

        l_open12  = [  34.2-1773.4j,        477.6-1705.4j,       1910.0-1296.2j    ]
        l_thru12  = [  289138.6-141807.0j,  21247.0-283341.0j,  -174717.8-157904.2j]

        l_shrt22  = [ 361065.2-215336.2j,  147570.4-341318.8j,  -68243.4-341182.2j]
        l_open22  = [ 16711.4+108657.4j,   74518.6+90616.0j,     110157.8+35605.4j]
        l_load22  = [ 191258.4+32263.0j,   157767.8-61217.8j,    84613.4-131882.6j]


    class Exp:
        exp11    = [ (0.606576756035065+0.762588073517888j),   (0.513267531550349+0.9791358538146341j), (0.235892205955221+1.0616400454600028j)  ]
        exp21    = [-0.007180986213496086+0.0016874101047902755j, -0.011275636438731433-0.009904048451696977j, -2.8395798205189582e-05-0.014736475042388703j]
        exp12 = [ (-0.004075270223455314-0.00168546296895949j), (-0.000792659613743921-0.004229355008451727j), (0.005751344808592438-0.019118771834241523j) ]
        exp22    = [ (0.8069678649875225+0.7892394729459603j), (0.6180166034864449+0.852233905016351j), (0.5742805835193814+0.7886191880642951j) ]


class TestRfMathCalibration(unittest.TestCase):
    def _assertComplexNear(self, c1, cexp, msg):
        cs1 = str(c1)
        exs = str(cexp)
        vs  = cs1 + " vs " + exs
        self.assertAlmostEqual(c1.real, cexp.real, msg= "(real)" + vs + msg)
        self.assertAlmostEqual(c1.imag, cexp.imag, msg= "(imag)" + vs + msg)

    def _assertComplexArrayNear(self, c1, cexp, msg):
        self.assertEqual(len(c1), len(cexp), msg="Arrays should be of the same size. " + msg)
        for idx in range(0, len(cexp)):
            self._assertComplexNear(c1[idx], cexp[idx], " Complex numbers are different At index " + str(idx))

    # ************** No NUMPY ******************

    def test_calibrate_reflection_without_numpy_s11(self):
        dut11 = pocketvna.calibrate_reflection_no_numpy(raw_meas_mm = Data.Meas.l_raw11,
            short_mm = Data.Cali.l_shrt11,
            open_mm  = Data.Cali.l_open11,
            load_mm  = Data.Cali.l_load11, z0 = 50.0)

        self._assertComplexArrayNear(Data.Exp.exp11, dut11, "reflection s11 calibration (no numpy)")

    def test_calibrate_reflection_without_numpy_s22(self):
        dut22 = pocketvna.calibrate_reflection_no_numpy(raw_meas_mm = Data.Meas.l_raw22,
            short_mm = Data.Cali.l_shrt22,
            open_mm  = Data.Cali.l_open22,
            load_mm  = Data.Cali.l_load22, z0 = 50.0)

        self._assertComplexArrayNear(Data.Exp.exp22, dut22, "reflection s22 calibration (no numpy)")

    def test_calibrate_transmission_expected__without_numpy_S21(self):
        dut_21 = pocketvna.calibrate_transmission_no_numpy(raw_meas_mn = Data.Meas.l_raw21,
            open_mn = Data.Cali.l_open21, thru_mn = Data.Cali.l_thru21)

        self._assertComplexArrayNear(Data.Exp.exp21, dut_21, "transmission s21 calibration")


    def test_calibrate_transmission_expected___without_numpy_S12(self):
        dut_12 = pocketvna.calibrate_transmission_no_numpy(raw_meas_mn = Data.Meas.l_raw12,
            open_mn = Data.Cali.l_open12, thru_mn = Data.Cali.l_thru12)

        self._assertComplexArrayNear(Data.Exp.exp12, dut_12, "transmission s12 calibration")

    # ************** NUMPY version ******************************

    def test_calibrate_reflection_expected_s11(self):
        raw_11   = numpy.array(Data.Meas.l_raw11,    dtype=numpy.complex128)

        short_11 = numpy.array(Data.Cali.l_shrt11,   dtype=numpy.complex128)
        open_11  = numpy.array(Data.Cali.l_open11,   dtype=numpy.complex128)
        load_11  = numpy.array(Data.Cali.l_load11,   dtype=numpy.complex128)

        dut11 = pocketvna.calibrate_reflection_numpy(raw_meas_mm = raw_11,
            short_mm = short_11, open_mm = open_11, load_mm = load_11, z0 = 50.0)

        self._assertComplexArrayNear(Data.Exp.exp11, dut11, "reflection s11 calibration")

    def test_calibrate_reflection_expected_s22(self):
        meas_22 = numpy.array(Data.Meas.l_raw22,    dtype=numpy.complex128)

        shrt_22 = numpy.array(Data.Cali.l_shrt22,   dtype=numpy.complex128)
        open_22 = numpy.array(Data.Cali.l_open22,   dtype=numpy.complex128)
        load_22 = numpy.array(Data.Cali.l_load22,   dtype=numpy.complex128)

        dut22 = pocketvna.calibrate_reflection_numpy(raw_meas_mm = meas_22,
            short_mm = shrt_22, open_mm = open_22, load_mm = load_22, z0 = 50.0)

        self._assertComplexArrayNear(Data.Exp.exp22, dut22, "reflection s22 calibration")


    def test_calibrate_transmission_expected__S21(self):
        meas_21 = numpy.array(Data.Meas.l_raw21,   dtype=numpy.complex128)

        open_21 = numpy.array(Data.Cali.l_open21,  dtype=numpy.complex128)
        thru_21 = numpy.array(Data.Cali.l_thru21,  dtype=numpy.complex128)

        dut_21 = pocketvna.calibrate_transmission_numpy(raw_meas_mn = meas_21, open_mn = open_21, thru_mn = thru_21)

        self._assertComplexArrayNear(Data.Exp.exp21, dut_21, "transmission s21 calibration")


    def test_calibrate_transmission_expected__S12(self):
        meas_12 = numpy.array(Data.Meas.l_raw12,   dtype=numpy.complex128)

        open_12 = numpy.array(Data.Cali.l_open12,  dtype=numpy.complex128)
        thru_12 = numpy.array(Data.Cali.l_thru12,  dtype=numpy.complex128)

        dut_12 = pocketvna.calibrate_transmission_numpy(raw_meas_mn = meas_12, open_mn = open_12, thru_mn = thru_12)

        self._assertComplexArrayNear(Data.Exp.exp12, dut_12, "transmission s12 calibration")

class TestSimulatorWithFullNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simulation_device = pocketvna.open_simulation_device()

    @classmethod
    def tearDownClass(cls):
        pocketvna.release_handler(cls.simulation_device)
        cls.simulation_device = None
        #cls.driver = None
        #cls.count_driver = 0

    def _device(self):
        return self.__class__.simulation_device

    def _check(self, frequencies, V_nprm, V_p1, V_p2):
        matrix_for = pocketvna.scan_frequencies_4Port(self._device(), frequencies, AVERAGE, V_nprm )
        self.assertEqual((4,4,len(frequencies)), matrix_for.shape)

        for p1 in range(0,4):
            for p2 in range(0,4):
                v = matrix_for[p1,p2,:]
                self.assertEqual( len(frequencies), len(v) )
                if ( p1 == V_p1 and p2 == V_p2 ):
                    self.assertTrue( numpy.all( v != 0.0j )  )
                else:
                    self.assertTrue( numpy.all( v == 0.0j )  )

    def test_each_parameters(self):
        frequencies = [ 1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000 ]

        self._check(frequencies,  pocketvna.NetworkParams.S11, 0, 0)
        self._check(frequencies,  pocketvna.NetworkParams.S12, 0, 1)
        self._check(frequencies,  pocketvna.NetworkParams.S13, 0, 2)
        self._check(frequencies,  pocketvna.NetworkParams.S14, 0, 3)

        self._check(frequencies,  pocketvna.NetworkParams.S21, 1, 0)
        self._check(frequencies,  pocketvna.NetworkParams.S22, 1, 1)
        self._check(frequencies,  pocketvna.NetworkParams.S23, 1, 2)
        self._check(frequencies,  pocketvna.NetworkParams.S24, 1, 3)

        self._check(frequencies,  pocketvna.NetworkParams.S31, 2, 0)
        self._check(frequencies,  pocketvna.NetworkParams.S32, 2, 1)
        self._check(frequencies,  pocketvna.NetworkParams.S33, 2, 2)
        self._check(frequencies,  pocketvna.NetworkParams.S34, 2, 3)

        self._check(frequencies,  pocketvna.NetworkParams.S41, 3, 0)
        self._check(frequencies,  pocketvna.NetworkParams.S42, 3, 1)
        self._check(frequencies,  pocketvna.NetworkParams.S43, 3, 2)
        self._check(frequencies,  pocketvna.NetworkParams.S44, 3, 3)

    def test_all_parameters(self):
        frequencies = [ 1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000 ]
        matrix_for = pocketvna.scan_frequencies_4Port(self._device(), frequencies, AVERAGE, pocketvna.NetworkParams.Util4Port.ALL, None )
        self.assertEqual( (4,4,len(frequencies)), matrix_for.shape )

        for p1 in range(0,4):
            for p2 in range(0,4):
                v = matrix_for[p1,p2,:]
                self.assertEqual( len(frequencies), len(v) )
                self.assertTrue(  numpy.all( v != 0.0j )   )

    def test_all_parameters_range(self):
        frequenyFrom, frequenyTo, steps = pocketvna.MHz(1), pocketvna.MHz(10), 10

        matrix_for = pocketvna.scan_frequencyRange_4Port(self._device(), 
                frequenyFrom, frequenyTo, steps, pocketvna.Distributions.Linear, 
                AVERAGE, pocketvna.NetworkParams.Util4Port.ALL, None)
        self.assertEqual( (4,4,steps), matrix_for.shape )

        for p1 in range(0,4):
            for p2 in range(0,4):
                v = matrix_for[p1,p2,:]
                self.assertEqual( steps, len(v) )
                self.assertTrue(  numpy.all( v != 0.0j )   )

    def test_if_supported(self):
        params = [
            pocketvna.NetworkParams.S11,  pocketvna.NetworkParams.S12,  pocketvna.NetworkParams.S13, pocketvna.NetworkParams.S14,
            pocketvna.NetworkParams.S21,  pocketvna.NetworkParams.S22,  pocketvna.NetworkParams.S23, pocketvna.NetworkParams.S24,
            pocketvna.NetworkParams.S31,  pocketvna.NetworkParams.S32,  pocketvna.NetworkParams.S33, pocketvna.NetworkParams.S34,
            pocketvna.NetworkParams.S41,  pocketvna.NetworkParams.S42,  pocketvna.NetworkParams.S43, pocketvna.NetworkParams.S44
        ]
        for p in params:
            self.assertTrue(  pocketvna.info_get_param_supported(self._device(), p)   )
            self.assertTrue(  pocketvna.supports_network_parameter(self._device(), p)   )



if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        print("Close driver ")
        driver.close()
        pocketvna.close_api()
        print("DONE!")
