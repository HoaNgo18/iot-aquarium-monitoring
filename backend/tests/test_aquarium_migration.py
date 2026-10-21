import importlib.util
from pathlib import Path
import unittest

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

from app.database import Base


class AquariumMigrationTests(unittest.TestCase):
    def test_adds_tables_without_modifying_legacy_records(self):
        path = Path(__file__).resolve().parents[1] / "alembic/versions/0002_aquarium_monitoring.py"
        spec = importlib.util.spec_from_file_location("aquarium_migration", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        engine = create_engine("sqlite://")
        with engine.begin() as connection:
            # Minimal representatives of the existing v1 tables, including historical values.
            connection.execute(text("CREATE TABLE devices (id VARCHAR(64) PRIMARY KEY)"))
            connection.execute(text("CREATE TABLE telemetry (id INTEGER PRIMARY KEY, water_level_cm FLOAT)"))
            connection.execute(text("CREATE TABLE thresholds (device_id VARCHAR(64) PRIMARY KEY)"))
            connection.execute(text("CREATE TABLE alerts (id INTEGER PRIMARY KEY, message TEXT)"))
            connection.execute(text("INSERT INTO telemetry VALUES (1, 75.5)"))
            connection.execute(text("INSERT INTO alerts VALUES (1, 'Historical flood alert')"))
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                module.upgrade()
            self.assertEqual(connection.scalar(text("SELECT water_level_cm FROM telemetry WHERE id=1")), 75.5)
            self.assertEqual(connection.scalar(text("SELECT message FROM alerts WHERE id=1")), "Historical flood alert")
            inspector = inspect(connection)
            for table in ("aquarium_telemetry", "aquarium_thresholds", "aquarium_alerts"):
                self.assertIn(table, inspector.get_table_names())
                columns = {c["name"] for c in inspector.get_columns(table)}
                self.assertEqual(columns, set(Base.metadata.tables[table].columns.keys()))
            connection.execute(text("INSERT INTO devices VALUES ('tank-test')"))
            connection.execute(text(
                "INSERT INTO aquarium_telemetry "
                "(device_id, sequence, measured_at, temperature_c, ph, turbidity_pct, signal_strength_dbm, sensor_status) "
                "VALUES ('tank-test', 1, CURRENT_TIMESTAMP, 27, 7, 20, -55, 'normal')"
            ))
            self.assertEqual(connection.scalar(text("SELECT ph FROM aquarium_telemetry")), 7)
        engine.dispose()


if __name__ == "__main__":
    unittest.main()
