from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from telemetry import SCENARIOS, TelemetryGenerator, status_payload

FIXED_TIME = "2026-10-19T00:00:00.000Z"


class TelemetryGeneratorTests(unittest.TestCase):
    def create(self, scenario):
        return TelemetryGenerator("tank-test", scenario, seed=42, clock=lambda: FIXED_TIME)

    def test_normal_payload_and_reproducibility(self):
        a, b = self.create("normal"), self.create("normal")
        for sequence in range(1, 6):
            payload = a.next_payload()
            self.assertEqual(payload, b.next_payload())
            self.assertEqual(payload["schema_version"], 2)
            self.assertEqual(payload["sequence"], sequence)
            self.assertEqual(payload["timestamp"], FIXED_TIME)
            self.assertTrue(26 <= payload["temperature_c"] <= 28)
            self.assertTrue(6.8 <= payload["ph"] <= 7.4)
            self.assertTrue(10 <= payload["turbidity_pct"] <= 25)

    def test_scenarios_cross_demo_thresholds(self):
        for scenario, field, predicate in (
            ("temperature-low", "temperature_c", lambda v: v < 22),
            ("temperature-high", "temperature_c", lambda v: v > 30),
            ("ph-low", "ph", lambda v: v < 6.5),
            ("ph-high", "ph", lambda v: v > 8.5),
            ("turbidity-high", "turbidity_pct", lambda v: v >= 80),
        ):
            with self.subTest(scenario=scenario):
                self.assertTrue(predicate(self.create(scenario).next_payload()[field]))

    def test_sensor_error_rotates_partial_failures(self):
        generator = self.create("sensor-error")
        rows = [generator.next_payload() for _ in range(9)]
        for index, field in ((2, "ph"), (5, "temperature_c"), (8, "turbidity_pct")):
            self.assertEqual(rows[index]["sensor_status"], "error")
            self.assertIsNone(rows[index][field])
            self.assertEqual(sum(rows[index][k] is None for k in ("ph", "temperature_c", "turbidity_pct")), 1)

    def test_status_payload(self):
        self.assertEqual(status_payload("tank-test", "offline")["schema_version"], 2)
        with self.assertRaises(ValueError):
            status_payload("tank-test", "unknown")

    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError):
            self.create("flood")


if __name__ == "__main__":
    unittest.main()
