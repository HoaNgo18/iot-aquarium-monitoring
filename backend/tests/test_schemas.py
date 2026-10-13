import unittest

from pydantic import ValidationError

from app.schemas import TelemetryPayload


VALID_PAYLOAD = {
    "schema_version": 1,
    "device_id": "node-001",
    "timestamp": "2026-10-13T01:00:00Z",
    "sequence": 1,
    "water_level_cm": 18.4,
    "rainfall_mm": 2.8,
    "signal_strength_dbm": -61,
    "sensor_status": "normal",
}


class TelemetryPayloadTests(unittest.TestCase):
    def test_accepts_valid_payload(self) -> None:
        payload = TelemetryPayload.model_validate(VALID_PAYLOAD)
        self.assertEqual(payload.device_id, "node-001")

    def test_error_requires_null_water_level(self) -> None:
        document = {**VALID_PAYLOAD, "sensor_status": "error"}
        with self.assertRaises(ValidationError):
            TelemetryPayload.model_validate(document)

    def test_rejects_naive_timestamp(self) -> None:
        document = {**VALID_PAYLOAD, "timestamp": "2026-10-13T01:00:00"}
        with self.assertRaises(ValidationError):
            TelemetryPayload.model_validate(document)


if __name__ == "__main__":
    unittest.main()
