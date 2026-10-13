from datetime import datetime, timedelta, timezone
import unittest

from app.domain.alert_rules import PreviousReading, ThresholdValues, calculate_rise_rate, evaluate_connectivity, evaluate_telemetry


class PureAlertRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 10, 13, 1, 0, tzinfo=timezone.utc)
        self.thresholds = ThresholdValues(50.0, 70.0, 10.0, 20.0)

    def test_critical_water_and_heavy_rain(self) -> None:
        decisions = evaluate_telemetry(
            measured_at=self.now,
            water_level_cm=75.0,
            rainfall_mm=25.0,
            sensor_status="normal",
            thresholds=self.thresholds,
            previous=None,
        )
        by_type = {decision.alert_type: decision for decision in decisions}
        self.assertEqual(by_type["water_level"].severity, "critical")
        self.assertTrue(by_type["heavy_rain"].active)

    def test_sensor_error_skips_unknown_water_level(self) -> None:
        decisions = evaluate_telemetry(
            measured_at=self.now,
            water_level_cm=None,
            rainfall_mm=0.0,
            sensor_status="error",
            thresholds=self.thresholds,
            previous=None,
        )
        by_type = {decision.alert_type: decision for decision in decisions}
        self.assertTrue(by_type["sensor_error"].active)
        self.assertNotIn("water_level", by_type)

    def test_rise_rate_uses_elapsed_time(self) -> None:
        previous = PreviousReading(self.now - timedelta(minutes=1), 10.0)
        self.assertEqual(calculate_rise_rate(self.now, 25.0, previous), 15.0)

    def test_too_short_interval_is_ignored(self) -> None:
        previous = PreviousReading(self.now - timedelta(milliseconds=500), 10.0)
        self.assertIsNone(calculate_rise_rate(self.now, 25.0, previous))

    def test_offline_decision(self) -> None:
        self.assertTrue(evaluate_connectivity("offline")[0].active)
        self.assertFalse(evaluate_connectivity("online")[0].active)


if __name__ == "__main__":
    unittest.main()
