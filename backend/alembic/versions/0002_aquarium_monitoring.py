"""Add aquarium tables without modifying or converting historical flood data."""

from alembic import op
import sqlalchemy as sa


revision = "0002_aquarium_monitoring"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aquarium_telemetry",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.String(64), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column("temperature_c", sa.Float(), nullable=True),
        sa.Column("ph", sa.Float(), nullable=True),
        sa.Column("turbidity_pct", sa.Float(), nullable=True),
        sa.Column("signal_strength_dbm", sa.Integer(), nullable=False),
        sa.Column("sensor_status", sa.String(16), nullable=False),
        sa.UniqueConstraint("device_id", "sequence", "measured_at", name="uq_aquarium_telemetry_sample"),
        sa.CheckConstraint("sensor_status IN ('normal', 'error')", name="ck_telemetry_sensor_status"),
        sa.CheckConstraint("temperature_c IS NULL OR temperature_c BETWEEN -55 AND 125", name="ck_aquarium_temperature"),
        sa.CheckConstraint("ph IS NULL OR ph BETWEEN 0 AND 14", name="ck_aquarium_ph"),
        sa.CheckConstraint("turbidity_pct IS NULL OR turbidity_pct BETWEEN 0 AND 100", name="ck_aquarium_turbidity"),
    )
    op.create_index("ix_aquarium_telemetry_device_measured", "aquarium_telemetry", ["device_id", "measured_at"])
    op.create_table(
        "aquarium_thresholds",
        sa.Column("device_id", sa.String(64), sa.ForeignKey("devices.id"), primary_key=True),
        sa.Column("temperature_min_c", sa.Float(), nullable=False),
        sa.Column("temperature_max_c", sa.Float(), nullable=False),
        sa.Column("ph_min", sa.Float(), nullable=False),
        sa.Column("ph_max", sa.Float(), nullable=False),
        sa.Column("turbidity_warning_pct", sa.Float(), nullable=False),
        sa.Column("turbidity_critical_pct", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False),
        sa.CheckConstraint("-55 <= temperature_min_c AND temperature_min_c < temperature_max_c AND temperature_max_c <= 125", name="ck_aquarium_temp_range"),
        sa.CheckConstraint("0 <= ph_min AND ph_min < ph_max AND ph_max <= 14", name="ck_aquarium_ph_range"),
        sa.CheckConstraint("0 <= turbidity_warning_pct AND turbidity_warning_pct < turbidity_critical_pct AND turbidity_critical_pct <= 100", name="ck_aquarium_turbidity_range"),
    )
    op.create_table(
        "aquarium_alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.String(64), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("alert_type", sa.String(32), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("message", sa.String(255), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("severity IN ('warning', 'critical')", name="ck_alerts_severity"),
    )
    op.create_index("ix_aquarium_alerts_device_started", "aquarium_alerts", ["device_id", "started_at"])


def downgrade() -> None:
    # An explicit downgrade discards only aquarium records, never legacy flood tables.
    op.drop_index("ix_aquarium_alerts_device_started", table_name="aquarium_alerts")
    op.drop_table("aquarium_alerts")
    op.drop_table("aquarium_thresholds")
    op.drop_index("ix_aquarium_telemetry_device_measured", table_name="aquarium_telemetry")
    op.drop_table("aquarium_telemetry")
