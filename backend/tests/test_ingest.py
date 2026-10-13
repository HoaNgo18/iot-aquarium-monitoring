from datetime import datetime, timezone
import json
import unittest

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.ingest import IngestResult, ingest_message
from app.models import Device, Telemetry


class IngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine, expire_on_commit=False)

    def tearDown(self) -> None:
        self.engine.dispose()

    def telemetry(self) -> bytes:
        return json.dumps(
            {
                "schema_version": 1,
                "device_id": "node-test",
                "timestamp": "2026-10-13T01:00:00Z",
                "sequence": 1,
                "water_level_cm": 22.5,
                "rainfall_mm": 1.2,
                "signal_strength_dbm": -55,
                "sensor_status": "normal",
            }
        ).encode()

    def test_stores_telemetry_and_updates_device(self) -> None:
        result = ingest_message(
            "flood-monitoring/devices/node-test/telemetry", self.telemetry(), self.sessions
        )
        with self.sessions() as session:
            device = session.get(Device, "node-test")
            count = session.scalar(select(func.count()).select_from(Telemetry))

        self.assertEqual(result, IngestResult.STORED)
        self.assertEqual(count, 1)
        self.assertEqual(device.connectivity, "online")

    def test_duplicate_is_not_stored_twice(self) -> None:
        topic = "flood-monitoring/devices/node-test/telemetry"
        ingest_message(topic, self.telemetry(), self.sessions)
        result = ingest_message(topic, self.telemetry(), self.sessions)
        with self.sessions() as session:
            count = session.scalar(select(func.count()).select_from(Telemetry))

        self.assertEqual(result, IngestResult.DUPLICATE)
        self.assertEqual(count, 1)

    def test_rejects_device_id_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            ingest_message(
                "flood-monitoring/devices/another-node/telemetry",
                self.telemetry(),
                self.sessions,
            )

    def test_updates_offline_status(self) -> None:
        status = json.dumps(
            {
                "schema_version": 1,
                "device_id": "node-test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "connectivity": "offline",
            }
        ).encode()
        ingest_message("flood-monitoring/devices/node-test/status", status, self.sessions)
        with self.sessions() as session:
            device = session.get(Device, "node-test")
        self.assertEqual(device.connectivity, "offline")


if __name__ == "__main__":
    unittest.main()
