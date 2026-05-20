import unittest

from plot_radiosonde_latency import parse_yyyymmddhhmm, parse_valid_time


class PlotLatencyHelpersTest(unittest.TestCase):
    def test_parse_yyyymmddhhmm(self):
        dt = parse_yyyymmddhhmm(202605201930)
        self.assertEqual((dt.year, dt.month, dt.day, dt.hour, dt.minute), (2026, 5, 20, 19, 30))

    def test_parse_yyyymmddhhmm_missing(self):
        self.assertIsNone(parse_yyyymmddhhmm(-1))

    def test_parse_valid_time(self):
        dt = parse_valid_time([2026, 5, 20, 18, 45])
        self.assertEqual((dt.year, dt.month, dt.day, dt.hour, dt.minute), (2026, 5, 20, 18, 45))

    def test_parse_valid_time_too_short(self):
        self.assertIsNone(parse_valid_time([2026, 5, 20]))


if __name__ == "__main__":
    unittest.main()
