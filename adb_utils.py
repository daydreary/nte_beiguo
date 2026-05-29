import os
import shlex
import shutil
import sys


def _module_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _bundled_adb_executable() -> str:
    base = _module_dir()
    if sys.platform == "darwin":
        return os.path.join(base, "platform-tools-mac", "adb")
    return os.path.join(base, "platform-tools", "adb.exe")


def get_adb_executable() -> str:
    """优先使用 PATH 中的 adb，否则使用项目内 platform-tools。"""
    path_adb = shutil.which("adb")
    if path_adb:
        return path_adb
    return _bundled_adb_executable()


def adb_prefix(serial: str = "") -> str:
    """返回 adb 命令前缀，可选附带设备序列号。"""
    adb = get_adb_executable()
    if serial.strip():
        return f"{adb} -s {shlex.quote(serial.strip())}"
    return adb
