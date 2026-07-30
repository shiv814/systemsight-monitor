from __future__ import annotations

from datetime import datetime, timezone
import platform
import socket
from typing import Any

import psutil


def bytes_to_gib(value: int) -> float:
    return round(value / (1024 ** 3), 2)


def collect_snapshot() -> dict[str, Any]:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()
    temperatures = {}
    if hasattr(psutil, "sensors_temperatures"):
        try:
            temperatures = {
                group: [round(entry.current, 1) for entry in entries]
                for group, entries in psutil.sensors_temperatures().items()
            }
        except (AttributeError, OSError):
            temperatures = {}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "cpu": {
            "percent": psutil.cpu_percent(interval=0.1),
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
        },
        "memory": {
            "percent": memory.percent,
            "used_gib": bytes_to_gib(memory.used),
            "total_gib": bytes_to_gib(memory.total),
        },
        "disk": {
            "percent": disk.percent,
            "used_gib": bytes_to_gib(disk.used),
            "total_gib": bytes_to_gib(disk.total),
        },
        "network": {
            "bytes_sent": network.bytes_sent,
            "bytes_received": network.bytes_recv,
        },
        "temperatures_c": temperatures,
    }
