"""
Example: System Info Plugin
Provides system monitoring commands for NEXUS.
"""

import psutil
from datetime import datetime

from agents.plugin_agent.plugin_api import CommandPlugin
from agents.plugin_agent.models import PluginMetadata, PluginCapability, PluginType, SecurityLevel


class SystemInfoPlugin(CommandPlugin):
    """Plugin that provides system monitoring and info commands."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="System Info",
            version="1.0.0",
            description="System monitoring and information plugin",
            author="NEXUS",
            plugin_type=PluginType.COMMAND,
            security_level=SecurityLevel.SANDBOXED,
            min_nexus_version="1.0.0",
            tags=["system", "monitoring", "info", "hardware"],
            capabilities=[
                PluginCapability(
                    name="sysinfo",
                    description="Get system information",
                    command_prefix="sysinfo",
                    permissions=["read_system"],
                ),
                PluginCapability(
                    name="meminfo",
                    description="Get memory usage",
                    command_prefix="meminfo",
                    permissions=["read_system"],
                ),
                PluginCapability(
                    name="diskinfo",
                    description="Get disk usage",
                    command_prefix="diskinfo",
                    permissions=["read_system"],
                ),
            ],
        )

    def _get_command_handlers(self):
        return {
            "sysinfo": self._handle_sysinfo,
            "meminfo": self._handle_meminfo,
            "diskinfo": self._handle_diskinfo,
        }

    def _handle_sysinfo(self, command, params):
        import platform
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        lines = [
            f"System: {platform.system()} {platform.release()}",
            f"CPU: {psutil.cpu_count(logical=False)} cores @ {cpu:.1f}%",
            f"RAM: {mem.percent}% used ({mem.used / 1024**3:.1f}GB / {mem.total / 1024**3:.1f}GB)",
            f"Uptime: {datetime.now().timestamp() - psutil.boot_time():.0f}s",
        ]
        return "\n".join(lines)

    def _handle_meminfo(self, command, params):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        lines = [
            f"Memory: {mem.percent}% used",
            f"  Total: {mem.total / 1024**3:.1f}GB",
            f"  Available: {mem.available / 1024**3:.1f}GB",
            f"  Used: {mem.used / 1024**3:.1f}GB",
            f"Swap: {swap.percent}% used ({swap.used / 1024**3:.1f}GB)",
        ]
        return "\n".join(lines)

    def _handle_diskinfo(self, command, params):
        lines = ["Disk Usage:"]
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                lines.append(f"  {part.mountpoint}: {usage.percent}% ({usage.used / 1024**3:.1f}GB / {usage.total / 1024**3:.1f}GB)")
            except PermissionError:
                continue
        return "\n".join(lines)
