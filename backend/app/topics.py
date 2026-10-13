import re


TOPIC_PATTERN = re.compile(
    r"^flood-monitoring/devices/(?P<device_id>[A-Za-z0-9][A-Za-z0-9_-]{0,63})/"
    r"(?P<kind>telemetry|status)$"
)
