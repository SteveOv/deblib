""" Unit tests for the Mission base class and sub classes. """
import unittest

from deblib.mission import Mission, Tess, Kepler

# pylint: disable=too-many-public-methods, line-too-long
class TestMission(unittest.TestCase):
    """ Unit tests for the Mission base class and sub classes. """
    _all_missions = [Tess, Kepler]

    #
    # Tests Mission.get_instance(mission_name: str) -> Mission:
    #
    def test_mission_get_instance_unknown_missions(self):
        """ Tests the Mission get_instance() function with unknown missions. """
        self.assertRaises(KeyError, Mission.get_instance, "Test")
        self.assertRaises(KeyError, Mission.get_instance, "Mission-Impossible")
        self.assertRaises(KeyError, Mission.get_instance, "Mission-Critical")

    def test_mission_get_instance_known_missions(self):
        """ Tests the Mission get_instance() function with valid variations of known missions. """
        for mission_name, mission_type in [("Tess", Tess),
                                           ("tess", Tess),
                                           ("Kepler", Kepler),
                                           ("KEPLER  ", Kepler)]:
            mission = Mission.get_instance(mission_name)
            self.assertIsInstance(mission, mission_type)

    def test_mission_get_instance_assert_caching(self):
        """ Tests the Mission get_instance() to assert caching of instances """
        # Currently uses a simple lru_cache decorator
        # so it's dependent on consistent naming
        instance1 = Mission.get_instance("Tess")
        instance2 = Mission.get_instance("Tess")
        self.assertEqual(instance1, instance2)


    #
    # Tests base/sub-class get_response_function()
    #
    def test_tess_get_response_function(self):
        """ Tests the TESS get_response_function(). """
        rf = Tess.get_response_function()
        self.assertIsNotNone(rf)
        self.assertEqual(rf[rf["lambda"]==800]["coefficient"], 0.777)
        self.assertEqual(len(rf[(rf["lambda"]>=600) & (rf["lambda"]<=1000)]), 201)

    def test_kepler_get_response_function(self):
        """ Tests the Kepler get_response_function(). """
        rf = Kepler.get_response_function()
        self.assertIsNotNone(rf)
        self.assertEqual(rf[rf["lambda"]==500]["coefficient"], 6.239e-1)
        self.assertEqual(len(rf[(rf["lambda"]>=400) & (rf["lambda"]<=900)]), 501)

    def test_mission_get_response_function(self):
        """ Tests polymorphic use of Mission get_response_function(). """
        for (mission, exp_coeff) in zip([Tess, Kepler],
                                        [0.768, 0.6159]):
            rf = mission.get_response_function()
            self.assertIsNotNone(rf)
            self.assertEqual(rf[rf["lambda"]==700]["coefficient"], exp_coeff)

    def test_mission_get_response_function_response_caching(self):
        """ Tests Mission subclass get_response_function() response caching. """
        for mission in self._all_missions:
            rf1 = mission.get_response_function()
            rf2 = mission.get_response_function()
            self.assertTrue(rf2 is rf1, f"{mission} failed test of rf2 is rf1")


    #
    # Tests default_bandpass -> (u.nm, u.nm)
    #
    def test_default_bandpass(self):
        """ Tests default_bandpass property returns correct bandpass. """
        bandpass = Tess.get_default_bandpass()
        self.assertEqual(bandpass, (600, 1000))

        bandpass = Kepler.get_default_bandpass()
        self.assertEqual(bandpass, (420, 900))


    #
    # Tests expected_brightness_ratio(t_eff_1, t_eff_1, bandpass)
    #
    def test_expected_expected_brightness_ratio_known_systems(self):
        """ Tests that expected_brightness_ratio(known dEBs) gives an appropriate result """
        bandpass = Tess.get_default_bandpass()
        for (target,        t_eff_1,    t_eff_2,    exp_ratio,  round_dp) in [
            ("CW Eri",      6830,       6561,       0.9262,     1), # OverallSouthworth24obsR17
            ("V1022 Cas",   6450,       6590,       1.0391,     1), # Southworth21obsR3
            ("psi Cen",     10450,      8800,       0.688,      1), # BrunttSouthworth+06aa
            ("V454 Aur",    5890,       6170,       1.2059,     1), # Southworth24obsR19
        ]:
            ratio = Tess.expected_brightness_ratio(t_eff_1, t_eff_2, bandpass)
            print(f"{target}: calculated ratio is {ratio:.4f}, expected is {exp_ratio:.4f}")
            self.assertAlmostEqual(ratio, exp_ratio, round_dp, f"{target}: calculated ratio {ratio:.4f} !~ {exp_ratio:.4f}")

if __name__ == "__main__":
    unittest.main()
