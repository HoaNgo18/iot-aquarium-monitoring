"""Create device, telemetry, threshold and alert tables."""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("connectivity", sa.String(length=16), nullable=False),
        sa.Column("sensor_status", sa.String(length=16), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("connectivity IN ('online', 'offline')", name="ck_devices_connectivity"),
        sa.CheckConstraint("sensor_status IN ('normal', 'error')", name="ck_devices_sensor_status"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "telemetry",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("water_level_cm", sa.Float(), nullable=True),
        sa.Column("rainfall_mm", sa.Float(), nullable=False),
        sa.Column("signal_strength_dbm", sa.Integer(), nullable=False),
        sa.Column("sensor_status", sa.String(length=16), nullable=False),
        sa.CheckConstraint("rainfall_mm >= 0", name="ck_rainfall_nonnegative"),
        sa.CheckConstraint("sensor_status IN ('normal', 'error')", name="ck_telemetry_sensor_status"),
        sa.CheckConstraint("water_level_cm IS NULL OR water_level_cm >= 0", name="ck_water_level_nonnegative"),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "sequence", "measured_at", name="uq_telemetry_device_sample"),
    )
    op.create_index("ix_telemetry_device_measured", "telemetry", ["device_id", "measured_at"])
    op.create_table(
        "thresholds",
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("water_warning_cm", sa.Float(), nullable=False),
        sa.Column("water_critical_cm", sa.Float(), nullable=False),
        sa.Column("rise_rate_cm_per_min", sa.Float(), nullable=False),
        sa.Column("rainfall_warning_mm", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("water_critical_cm > water_warning_cm", name="ck_threshold_critical_gt_warning"),
        sa.CheckConstraint("water_warning_cm >= 0", name="ck_threshold_warning_nonnegative"),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("device_id"),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("alert_type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("message", sa.String(length=255), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("severity IN ('warning', 'critical')", name="ck_alerts_severity"),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_device_started", "alerts", ["device_id", "started_at"])


def downgrade() -> None:
    op.drop_index("ix_alerts_device_started", table_name="alerts")
    op.drop_table("alerts")
    op.drop_table("thresholds")
    op.drop_index("ix_telemetry_device_measured", table_name="telemetry")
    op.drop_table("telemetry")
    op.drop_table("devices")
