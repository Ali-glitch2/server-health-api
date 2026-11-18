"""Helper functions that collect information about the machine.

This file knows nothing about web requests. It only gathers data.
main.py calls these functions and sends the results back as JSON.
"""

import os
import platform
import socket
import time

import psutil

# How many bytes are in each unit. Used to convert raw byte counts.
BYTES_PER_UNIT = {
    "B": 1,
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
}


def convert_bytes(value: int, unit: str) :
    """Convert a number of bytes into the requested unit, rounded to 2 decimals."""
    return round(value / BYTES_PER_UNIT[unit], 2)


def format_uptime(seconds: int) :
    """Turn a number of seconds into a readable string like '2d 5h 13m'."""
    days, remainder = divmod(seconds, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
    minutes, _ = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m"


def get_system_info() :
    """General facts about the machine: name, OS, Python version, uptime."""
    uptime_seconds = int(time.time() - psutil.boot_time())
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "uptime_seconds": uptime_seconds,
        "uptime_human": format_uptime(uptime_seconds),
    }


def get_cpu_info() :
    """CPU usage percentage and number of cores."""
    return {
        # interval=0.5 means: measure usage over half a second
        "usage_percent": psutil.cpu_percent(interval=0.5),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
    }


def get_memory_info(unit: str) :
    """RAM usage, converted into the requested unit."""
    memory = psutil.virtual_memory()
    return {
        "unit": unit,
        "total": convert_bytes(memory.total, unit),
        "used": convert_bytes(memory.used, unit),
        "available": convert_bytes(memory.available, unit),
        "usage_percent": memory.percent,
    }


def default_disk_path() :
    """The root of the main drive: 'C:\\' on Windows, '/' on Linux and macOS."""
    return os.path.abspath(os.sep)


def get_disk_info(path: str, unit: str) :
    """Disk usage for the drive that contains `path`.

    Raises FileNotFoundError if the path does not exist.
    """
    disk = psutil.disk_usage(path)
    return {
        "path": path,
        "unit": unit,
        "total": convert_bytes(disk.total, unit),
        "used": convert_bytes(disk.used, unit),
        "free": convert_bytes(disk.free, unit),
        "usage_percent": disk.percent,
    }
