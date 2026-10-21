import unittest

from pydantic import ValidationError

from app.schemas import TelemetryPayload, ThresholdUpdate


VALID_PAYLOAD = {
    "schema_version": 2,
    "device_id": "tank-001",
    "timestamp": "2026-10-19T01:00:00Z",
    "sequence": 1,
    "temperature_c": 27.4,
    "ph": 7.2,
    "turbidity_pct": 18.0,
    "signal_strength_dbm": -61,
    "sensor_status": "normal",
}


class TelemetryPayloadTests(unittest.TestCase):
    def test_accepts_valid_payload(self):
        self.assertEqual(TelemetryPayload.model_validate(VALID_PAYLOAD).ph, 7.2)

    def test_partial_failure_keeps_other_measurements(self):
        payload = TelemetryPayload.model_validate({**VALID_PAYLOAD, "ph": None, "sensor_status": "error"})
        self.assertIsNone(payload.ph)
        self.assertEqual(payload.temperature_c, 27.4)

    def test_rejects_inconsistent_sensor_status(self):
        for changes in ({"sensor_status": "error"}, {"ph": None}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                TelemetryPayload.model_validate({**VALID_PAYLOAD, **changes})

    def test_rejects_invalid_values(self):
        for changes in (
            {"ph": -1}, {"ph": 14.1}, {"temperature_c": -127},
            {"temperature_c": 126}, {"turbidity_pct": 101},
            {"ph": float("nan")}, {"temperature_c": float("inf")},
            {"schema_version": 1}, {"timestamp": "2026-10-19T01:00:00"},
            {"water_level_cm": 10}, {"device_id": "../tank"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                TelemetryPayload.model_validate({**VALID_PAYLOAD, **changes})

    def test_threshold_validation(self):
        self.assertEqual(ThresholdUpdate().ph_min, 6.5)
        for changes in (
            {"ph_min": 9, "ph_max": 8},
            {"temperature_min_c": 30, "temperature_max_c": 30},
            {"turbidity_warning_pct": 90, "turbidity_critical_pct": 80},
            {"ph_max": float("nan")}, {"water_warning_cm": 50},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                ThresholdUpdate(**changes)


if __name__ == "__main__":
    unittest.main()
