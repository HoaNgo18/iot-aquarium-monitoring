from datetime import datetime, timedelta, timezone
import json
import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.ingest import ingest_message
from app.models import Alert


class AlertRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.device_id = "node-alert-test"
        self.base_time = datetime(2026, 10, 13, 1, 0, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        self.engine.dispose()

    def send_telemetry(
        self,
        sequence: int,
        seconds: int,
        water: float | None,
        rain: float = 0.0,
        sensor_status: str = "normal",
    ) -> None:
        payload = {
            "schema_version": 1,
            "device_id": self.device_id,
            "timestamp": (self.base_time + timedelta(seconds=seconds)).isoformat(),
            "sequence": sequence,
            "water_level_cm": water,
            "rainfall_mm": rain,
            "signal_strength_dbm": -55,
            "sensor_status": sensor_status,
        }
        ingest_message(
            f"flood-monitoring/devices/{self.device_id}/telemetry",
            json.dumps(payload).encode(),
            self.sessions,
        )

    def send_status(self, connectivity: str, seconds: int) -> None:
        payload = {
            "schema_version": 1,
            "device_id": self.device_id,
            "timestamp": (self.base_time + timedelta(seconds=seconds)).isoformat(),
            "connectivity": connectivity,
        }
        ingest_message(
            f"flood-monitoring/devices/{self.device_id}/status",
            json.dumps(payload).encode(),
            self.sessions,
        )

    def active_alert(self, alert_type: str) -> Alert | None:
        with self.sessions() as session:
            return session.scalar(
                select(Alert).where(
                    Alert.alert_type == alert_type,
                    Alert.ended_at.is_(None),
                )
            )

    def test_flood_opens_water_and_rain_alerts(self) -> None:
        self.send_telemetry(1, 0, water=75.0, rain=25.0)

        self.assertEqual(self.active_alert("water_level").severity, "critical")
        self.assertIsNotNone(self.active_alert("heavy_rain"))

    def test_normal_sample_closes_water_and_rain_alerts(self) -> None:
        self.send_telemetry(1, 0, water=75.0, rain=25.0)
        self.send_telemetry(2, 60, water=20.0, rain=0.0)

        self.assertIsNone(self.active_alert("water_level"))
        self.assertIsNone(self.active_alert("heavy_rain"))

    def test_sensor_error_opens_and_normal_sample_closes_alert(self) -> None:
        self.send_telemetry(1, 0, water=None, sensor_status="error")
        self.assertIsNotNone(self.active_alert("sensor_error"))

        self.send_telemetry(2, 60, water=20.0)
        self.assertIsNone(self.active_alert("sensor_error"))

    def test_rapid_rise_opens_alert(self) -> None:
        self.send_telemetry(1, 0, water=10.0)
        self.send_telemetry(2, 60, water=25.0)

        self.assertEqual(self.active_alert("rapid_rise").severity, "warning")

    def test_offline_opens_and_online_closes_alert(self) -> None:
        self.send_status("offline", 0)
        self.assertIsNotNone(self.active_alert("offline"))

        self.send_status("online", 60)
        self.assertIsNone(self.active_alert("offline"))


if __name__ == "__main__":
    unittest.main()
