import unittest

from app.capture import demo_packets
from app.stats import calculate_stats


class TrafficStatsTest(unittest.TestCase):
    def test_total_packets(self):
        stats = calculate_stats(demo_packets())
        self.assertEqual(stats.total_packets, 7)

    def test_total_bytes(self):
        stats = calculate_stats(demo_packets())
        # 76 + 120 + 1500 + 60 + 84 + 66 + 1400 = 3306
        self.assertEqual(stats.total_bytes, 3306)

    def test_packets_by_protocol(self):
        stats = calculate_stats(demo_packets())
        protocol_dict = dict(stats.packets_by_protocol)
        self.assertEqual(protocol_dict["TCP"], 4)
        self.assertEqual(protocol_dict["UDP"], 2)
        self.assertEqual(protocol_dict["ICMP"], 1)

    def test_top_sources_sorted_by_bytes(self):
        stats = calculate_stats(demo_packets())
        # 10.0.0.11 = 1500 + 1400 = 2900 bytes (maior)
        # 10.0.0.10 = 76 + 120 + 84 = 280 bytes
        self.assertEqual(stats.top_sources[0][0], "10.0.0.11")
        self.assertEqual(stats.top_sources[0][2], 2900)
        self.assertEqual(stats.top_sources[1][0], "10.0.0.10")
        self.assertEqual(stats.top_sources[1][2], 280)

    def test_top_sources_include_packet_count(self):
        stats = calculate_stats(demo_packets())
        # 10.0.0.11 tem 2 pacotes
        self.assertEqual(stats.top_sources[0][1], 2)
        # 10.0.0.10 tem 3 pacotes
        self.assertEqual(stats.top_sources[1][1], 3)

    def test_top_destinations_sorted_by_bytes(self):
        stats = calculate_stats(demo_packets())
        # 172.217.29.14 = 1500 + 60 = 1560 bytes
        # 10.0.0.1 = 66 + 1400 = 1466 bytes
        self.assertEqual(stats.top_destinations[0][0], "172.217.29.14")
        self.assertEqual(stats.top_destinations[0][2], 1560)
        self.assertEqual(stats.top_destinations[1][0], "10.0.0.1")
        self.assertEqual(stats.top_destinations[1][2], 1466)

    def test_top_limited_to_5(self):
        stats = calculate_stats(demo_packets())
        self.assertLessEqual(len(stats.top_sources), 5)
        self.assertLessEqual(len(stats.top_destinations), 5)

    def test_empty_packets(self):
        stats = calculate_stats([])
        self.assertEqual(stats.total_packets, 0)
        self.assertEqual(stats.total_bytes, 0)
        self.assertEqual(stats.packets_by_protocol, [])
        self.assertEqual(stats.top_sources, [])
        self.assertEqual(stats.top_destinations, [])


if __name__ == "__main__":
    unittest.main()
