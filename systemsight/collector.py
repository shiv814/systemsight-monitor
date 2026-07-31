from __future__ import annotations

from datetime import datetime, timezone
import os
import platform
import socket
import time
from typing import Any

import psutil


def bytes_to_gib(value: int | float) -> float:
    return round(float(value) / (1024 ** 3), 2)


def _safe_temperatures() -> dict[str, list[float]]:
    if not hasattr(psutil, "sensors_temperatures"):
        return {}
    try:
        return {
            group: [round(float(entry.current), 1) for entry in entries if entry.current is not None]
            for group, entries in psutil.sensors_temperatures().items()
        }
    except (AttributeError, OSError, RuntimeError):
        return {}


def _top_processes(limit: int) -> list[dict[str, Any]]:
    processes: list[dict[str, Any]] = []
    for process in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent", "status"]):
        try:
            info = process.info
            processes.append(
                {
                    "pid": int(info["pid"]),
                    "name": info.get("name") or "unknown",
                    "username": info.get("username") or "unknown",
                    "cpu_percent": round(float(info.get("cpu_percent") or 0.0), 2),
                    "memory_percent": round(float(info.get("memory_percent") or 0.0), 2),
                    "status": info.get("status") or "unknown",
                }
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    processes.sort(key=lambda item: (item["cpu_percent"] + item["memory_percent"]), reverse=True)
    return processes[: max(0, int(limit))]


def collect_snapshot(*, disk_path: str = "/", process_limit: int = 5, sample_interval: float = 0.05) -> dict[str, Any]:
    """Collect one portable system-health snapshot.

    The collector is deliberately free of policy decisions: it reports facts while
    the analyzer decides whether those facts are healthy, warning, or critical.
    """

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage(disk_path)
    disk_io = psutil.disk_io_counters()
    network = psutil.net_io_counters()
    boot_time = float(psutil.boot_time())
    now = time.time()
    try:
        load = [round(float(value), 2) for value in os.getloadavg()]
    except (AttributeError, OSError):
        load = []
    cpu_times = psutil.cpu_times_percent(interval=max(0.0, sample_interval), percpu=False)
    cpu_percent = max(0.0, 100.0 - float(getattr(cpu_times, "idle", 0.0)))
    logical_cores = psutil.cpu_count(logical=True) or 1
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epoch": now,
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "uptime_seconds": round(now - boot_time, 1),
        "cpu": {
            "percent": round(cpu_percent, 2),
            "logical_cores": logical_cores,
            "physical_cores": psutil.cpu_count(logical=False),
            "per_cpu_percent": [round(float(value), 2) for value in psutil.cpu_percent(interval=None, percpu=True)],
            "load_average": load,
            "load_per_core": round(load[0] / logical_cores, 3) if load else None,
        },
        "memory": {
            "percent": round(float(memory.percent), 2),
            "used_gib": bytes_to_gib(memory.used),
            "available_gib": bytes_to_gib(memory.available),
            "total_gib": bytes_to_gib(memory.total),
            "swap_percent": round(float(swap.percent), 2),
            "swap_used_gib": bytes_to_gib(swap.used),
        },
        "disk": {
            "path": disk_path,
            "percent": round(float(disk.percent), 2),
            "free_gib": bytes_to_gib(disk.free),
            "used_gib": bytes_to_gib(disk.used),
            "total_gib": bytes_to_gib(disk.total),
            "read_bytes": int(disk_io.read_bytes) if disk_io else 0,
            "write_bytes": int(disk_io.write_bytes) if disk_io else 0,
        },
        "network": {
            "bytes_sent": int(network.bytes_sent),
            "bytes_received": int(network.bytes_recv),
            "packets_sent": int(network.packets_sent),
            "packets_received": int(network.packets_recv),
            "errors_in": int(network.errin),
            "errors_out": int(network.errout),
        },
        "processes": {
            "count": len(psutil.pids()),
            "top": _top_processes(process_limit),
        },
        "temperatures_c": _safe_temperatures(),
    }
