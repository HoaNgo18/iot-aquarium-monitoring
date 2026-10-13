from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from telemetry import TelemetryGenerator, status_payload  # noqa: E402


FIXED_TIME = "2026-10-13T00:00:00.000Z"


class TelemetryGeneratorTests(unittest.TestCase):
    def create(self, scenario: str) -> TelemetryGenerator:
        return TelemetryGenerator("node-test", scenario, seed=42, clock=lambda: FIXED_TIME)

    def test_normal_payload_matches_schema_and_safe_range(self) -> None:
        payload = self.create("normal").next_payload()

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["device_id"], "node-test")
        self.assertEqual(payload["timestamp"], FIXED_TIME)
        self.assertEqual(payload["sequence"], 1)
        self.assertEqual(payload["sensor_status"], "normal")
        self.assertGreaterEqual(payload["water_level_cm"], 12.0)
        self.assertLessEqual(payload["water_level_cm"], 25.0)

    def test_heavy_rain_raises_water_level(self) -> None:
        generator = self.create("heavy-rain")
        levels = [generator.next_payload()["water_level_cm"] for _ in range(4)]

        self.assertEqual(levels, sorted(levels))
        self.assertTrue(all(level > 28.0 for level in levels))

    def test_flood_crosses_warning_level_immediately(self) -> None:
        payload = self.create("flood").next_payload()

        self.assertGreater(payload["water_level_cm"], 70.0)
        self.assertGreaterEqual(payload["rainfall_mm"], 20.0)

    def test_sensor_error_emits_null_every_third_sample(self) -> None:
        generator = self.create("sensor-error")
        payloads = [generator.next_payload() for _ in range(3)]

        self.assertEqual(payloads[1]["sensor_status"], "normal")
        self.assertEqual(payloads[2]["sensor_status"], "error")
        self.assertIsNone(payloads[2]["water_level_cm"])

    def test_status_payload(self) -> None:
        payload = status_payload("node-test", "online")

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["connectivity"], "online")


if __name__ == "__main__":
    unittest.main()
