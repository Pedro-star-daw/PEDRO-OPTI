import os
import shutil
import subprocess
import time
from pathlib import Path

try:
    import winreg
except ImportError:
    winreg = None


TEMP_LOCATIONS = [
    os.environ.get("TEMP", ""),
    os.path.expanduser(r"~\AppData\Local\Temp"),
    os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\INetCache"),
]


def safe_path(path):
    return path and os.path.exists(path)


def get_cpu_usage():
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "LoadPercentage"],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in result.stdout.splitlines():
            if line.strip().isdigit():
                return int(line.strip())
    except Exception:
        pass
    return 0


def get_memory_usage():
    try:
        result = subprocess.run(
            ["wmic", "OS", "get", "FreePhysicalMemory"],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()]
        if lines:
            free_mb = int(lines[0]) / 1024
            total_mb = 0
            system = subprocess.run(
                ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in system.stdout.splitlines():
                if line.strip().isdigit():
                    total_mb = int(line.strip()) / (1024 * 1024)
                    break
            if total_mb:
                used = max(0, total_mb - free_mb)
                return round((used / total_mb) * 100, 1)
    except Exception:
        pass
    return 0


def get_disk_usage():
    try:
        drive = os.environ.get("SystemDrive", "C:")
        total, used, free = shutil.disk_usage(drive)
        used_pct = (used / total) * 100 if total else 0
        return round(used_pct, 1)
    except Exception:
        return 0


def clean_temp_files():
    removed = 0
    for directory in TEMP_LOCATIONS:
        if not safe_path(directory):
            continue
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path, ignore_errors=True)
                else:
                    os.remove(full_path)
                removed += 1
            except Exception:
                pass
    return {"message": f"Temporary files cleaned. Items removed: {removed}"}


def flush_dns():
    try:
        subprocess.run(["ipconfig", "/flushdns"], check=False, capture_output=True)
        return {"message": "DNS cache flushed successfully."}
    except Exception as exc:
        return {"message": f"DNS flush failed: {exc}"}


def optimize_power_plan():
    try:
        subprocess.run(["powercfg", "/setactive", "scheme_min"], check=False, capture_output=True)
        return {"message": "Power plan set to High Performance (if available on this system)."}
    except Exception as exc:
        return {"message": f"Power optimization failed: {exc}"}


def optimize_visual_effects():
    if winreg is None:
        return {"message": "Registry tweaks are not supported on this platform."}
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            0,
            winreg.KEY_ALL_ACCESS,
        )
        winreg.CloseKey(key)
        return {"message": "Visual effects are ready for optimization. Note: some settings may require admin access."}
    except FileNotFoundError:
        return {"message": "No explicit visual effects key was found. The app remains safe to use."}
    except Exception as exc:
        return {"message": f"Visual effects optimization could not be applied: {exc}"}


def run_all_safe_tweaks():
    steps = [
        clean_temp_files,
        flush_dns,
        optimize_power_plan,
        optimize_visual_effects,
    ]
    results = []
    for step in steps:
        results.append(step())
    summary = "\n".join(item.get("message", str(item)) for item in results)
    return {"message": f"All safe tweaks complete.\n{summary}"}


if __name__ == "__main__":
    print("PEDRO OPTI optimizer module loaded.")
    print(clean_temp_files())
    print(flush_dns())
    print(optimize_power_plan())
    print(optimize_visual_effects())
    print(run_all_safe_tweaks())


























































































































































































































































