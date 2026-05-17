"""
Service classes for the File Agent.
Each service handles a specific domain: files, apps, system, downloads.
"""

import os
import shutil
import subprocess
import platform
import psutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from core.logger import Logger
from .utils import PathResolver, format_size, get_file_type, get_platform, get_default_browser


class FileService:
    """Handles all file and folder operations."""

    def __init__(self, path_resolver: PathResolver):
        self.logger = Logger().get_logger("FileService")
        self.resolver = path_resolver

    def create_file(self, name: str, parent: Optional[str] = None) -> Dict[str, Any]:
        """Create a new file."""
        if parent:
            base = self.resolver.resolve(parent) or Path(parent)
        else:
            base = self.resolver.home

        target = base / name

        if target.exists():
            return {
                "success": False,
                "response": f"File already exists: {target}",
            }

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.touch()
            self.logger.info(f"Created file: {target}")
            return {
                "success": True,
                "response": f"Created file: {target}",
                "data": {"path": str(target), "type": "file"},
            }
        except Exception as e:
            self.logger.error(f"Create file failed: {e}")
            return {"success": False, "response": f"Could not create file: {str(e)}", "error": str(e)}

    def create_folder(self, name: str, parent: Optional[str] = None) -> Dict[str, Any]:
        """Create a new folder."""
        if parent:
            base = self.resolver.resolve(parent) or Path(parent)
        else:
            base = self.resolver.home

        target = base / name

        try:
            target.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created folder: {target}")
            return {
                "success": True,
                "response": f"Created folder: {target}",
                "data": {"path": str(target), "type": "folder"},
            }
        except Exception as e:
            self.logger.error(f"Create folder failed: {e}")
            return {"success": False, "response": f"Could not create folder: {str(e)}", "error": str(e)}

    def delete(self, path_str: str) -> Dict[str, Any]:
        """Delete a file or folder."""
        target = self.resolver.resolve(path_str)
        if not target or not target.exists():
            return {"success": False, "response": f"Path not found: {path_str}"}

        try:
            if target.is_file():
                target.unlink()
                self.logger.info(f"Deleted file: {target}")
                return {"success": True, "response": f"Deleted file: {target}"}
            elif target.is_dir():
                shutil.rmtree(target)
                self.logger.info(f"Deleted folder: {target}")
                return {"success": True, "response": f"Deleted folder: {target}"}
        except PermissionError:
            return {"success": False, "response": f"Permission denied: {target}"}
        except Exception as e:
            self.logger.error(f"Delete failed: {e}")
            return {"success": False, "response": f"Could not delete: {str(e)}", "error": str(e)}

    def rename(self, source_str: str, new_name: str) -> Dict[str, Any]:
        """Rename a file or folder."""
        source = self.resolver.resolve(source_str)
        if not source or not source.exists():
            return {"success": False, "response": f"Source not found: {source_str}"}

        try:
            dest = source.parent / new_name
            source.rename(dest)
            self.logger.info(f"Renamed {source} to {dest}")
            return {"success": True, "response": f"Renamed to: {dest}"}
        except Exception as e:
            self.logger.error(f"Rename failed: {e}")
            return {"success": False, "response": f"Rename failed: {str(e)}", "error": str(e)}

    def move(self, source_str: str, dest_str: str) -> Dict[str, Any]:
        """Move a file or folder."""
        source = self.resolver.resolve(source_str)
        dest = self.resolver.resolve(dest_str)

        if not source or not source.exists():
            return {"success": False, "response": f"Source not found: {source_str}"}

        try:
            shutil.move(str(source), str(dest))
            self.logger.info(f"Moved {source} to {dest}")
            return {"success": True, "response": f"Moved to: {dest}"}
        except Exception as e:
            self.logger.error(f"Move failed: {e}")
            return {"success": False, "response": f"Move failed: {str(e)}", "error": str(e)}

    def copy(self, source_str: str, dest_str: str) -> Dict[str, Any]:
        """Copy a file or folder."""
        source = self.resolver.resolve(source_str)
        dest = self.resolver.resolve(dest_str)

        if not source or not source.exists():
            return {"success": False, "response": f"Source not found: {source_str}"}

        try:
            if source.is_file():
                shutil.copy2(str(source), str(dest))
            else:
                shutil.copytree(str(source), str(dest))
            self.logger.info(f"Copied {source} to {dest}")
            return {"success": True, "response": f"Copied to: {dest}"}
        except Exception as e:
            self.logger.error(f"Copy failed: {e}")
            return {"success": False, "response": f"Copy failed: {str(e)}", "error": str(e)}

    def search(self, query: str, max_results: int = 20, search_root: Optional[Path] = None) -> Dict[str, Any]:
        """Search for files and folders by name."""
        root = search_root or self.resolver.home
        results = []
        skipped = 0

        skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "Windows", "Program Files"}

        try:
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in skip_dirs]

                for name in filenames + dirnames:
                    if query.lower() in name.lower():
                        results.append(os.path.join(dirpath, name))
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break
        except PermissionError:
            skipped += 1
        except Exception as e:
            self.logger.warning(f"Search error in {root}: {e}")

        if not results:
            return {
                "success": True,
                "response": f"No files found matching '{query}' in {root}",
                "data": [],
            }

        lines = [f"Found {len(results)} results for '{query}':"]
        for r in results[:10]:
            lines.append(f"  - {r}")
        if len(results) > 10:
            lines.append(f"  ... and {len(results) - 10} more")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"query": query, "results": results, "root": str(root)},
        }

    def list_directory(self, path_str: str) -> Dict[str, Any]:
        """List contents of a directory."""
        target = self.resolver.resolve(path_str)
        if not target or not target.exists():
            return {"success": False, "response": f"Path not found: {path_str}"}
        if not target.is_dir():
            return {"success": False, "response": f"Not a directory: {target}"}

        try:
            items = list(target.iterdir())
            dirs = sorted([i for i in items if i.is_dir()], key=lambda x: x.name.lower())
            files = sorted([i for i in items if i.is_file()], key=lambda x: x.name.lower())

            lines = [f"Contents of {target}:"]
            lines.append(f"\n  Folders ({len(dirs)}):")
            for d in dirs:
                lines.append(f"    [DIR]  {d.name}/")

            lines.append(f"\n  Files ({len(files)}):")
            for f in files:
                try:
                    size = f.stat().st_size
                    lines.append(f"    {format_size(size):>8}  {f.name}")
                except OSError:
                    lines.append(f"     ?      {f.name}")

            return {
                "success": True,
                "response": "\n".join(lines),
                "data": {"path": str(target), "dirs": len(dirs), "files": len(files)},
            }
        except PermissionError:
            return {"success": False, "response": f"Permission denied: {target}"}
        except Exception as e:
            self.logger.error(f"List directory failed: {e}")
            return {"success": False, "response": f"Could not list directory: {str(e)}", "error": str(e)}

    def open_file(self, path_str: str) -> Dict[str, Any]:
        """Open a file or folder with the default system application."""
        target = self.resolver.resolve(path_str)
        if not target or not target.exists():
            return {"success": False, "response": f"File not found: {path_str}"}
        if target.is_dir():
            return self.list_directory(path_str)

        try:
            plat = get_platform()
            if plat == "windows":
                os.startfile(str(target))
            elif plat == "macos":
                subprocess.run(["open", str(target)])
            else:
                subprocess.run(["xdg-open", str(target)])

            self.logger.info(f"Opened file: {target}")
            return {
                "success": True,
                "response": f"Opened file: {target}",
                "data": {"path": str(target), "type": get_file_type(target)},
            }
        except Exception as e:
            self.logger.error(f"Open file failed: {e}")
            return {"success": False, "response": f"Could not open file: {str(e)}", "error": str(e)}

    def open_folder(self, folder_name: str) -> Dict[str, Any]:
        """Open a common user folder by name."""
        target = self.resolver.get_folder_path(folder_name)
        if not target:
            available = ", ".join(["desktop", "downloads", "documents", "pictures", "videos", "onedrive"])
            return {"success": False, "response": f"Unknown folder. Available: {available}"}

        try:
            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)

            plat = get_platform()
            if plat == "windows":
                os.startfile(str(target))
            elif plat == "macos":
                subprocess.run(["open", str(target)])
            else:
                subprocess.run(["xdg-open", str(target)])

            return {
                "success": True,
                "response": f"Opened {folder_name}: {target}",
                "data": {"folder": folder_name, "path": str(target)},
            }
        except Exception as e:
            return {"success": False, "response": f"Could not open folder: {str(e)}", "error": str(e)}

    def find_and_open(self, folder_path: str, extension: str) -> Dict[str, Any]:
        """Find first file matching extension in folder and open it."""
        target = self.resolver.resolve(folder_path)
        if not target or not target.is_dir():
            return {"success": False, "response": f"Invalid folder: {folder_path}"}

        files = list(target.rglob(f"*{extension}"))
        if not files:
            return {"success": False, "response": f"No {extension} files found in {target}"}

        try:
            plat = get_platform()
            if plat == "windows":
                os.startfile(str(files[0]))
            elif plat == "macos":
                subprocess.run(["open", str(files[0])])
            else:
                subprocess.run(["xdg-open", str(files[0])])

            return {
                "success": True,
                "response": f"Opened: {files[0]}",
                "data": {"path": str(files[0]), "total_found": len(files)},
            }
        except Exception as e:
            return {"success": False, "response": f"Could not open: {str(e)}", "error": str(e)}

    def open_pdf(self, folder_path: str = None) -> Dict[str, Any]:
        """Find and open the first PDF in a folder."""
        folder = folder_path or str(self.resolver.documents)
        return self.find_and_open(folder, ".pdf")

    def open_media(self, folder_path: str = None) -> Dict[str, Any]:
        """Find and open the first media file in a folder."""
        folder = folder_path or str(self.resolver.videos)
        target = self.resolver.resolve(folder)
        if not target or not target.is_dir():
            return {"success": False, "response": f"Invalid folder: {folder}"}

        for ext in (".mp4", ".mp3", ".mkv", ".avi", ".wav", ".flac"):
            files = list(target.glob(f"*{ext}"))
            if files:
                return self.find_and_open(folder, ext)

        return {"success": False, "response": f"No media files found in {target}"}

    def read_file(self, path_str: str, max_lines: int = 100) -> Dict[str, Any]:
        """Read file contents."""
        target = self.resolver.resolve(path_str)
        if not target or not target.exists():
            return {"success": False, "response": f"File not found: {path_str}"}
        if target.is_dir():
            return {"success": False, "response": f"Is a directory: {target}"}

        try:
            content = target.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            total_lines = len(lines)
            display_lines = lines[:max_lines]

            numbered = "\n".join(f"  {i+1}: {line}" for i, line in enumerate(display_lines))
            suffix = f"\n  ... ({total_lines - max_lines} more lines)" if total_lines > max_lines else ""

            return {
                "success": True,
                "response": f"Contents of {target} ({total_lines} lines):\n\n{numbered}{suffix}",
                "data": {"path": str(target), "lines": total_lines, "size": format_size(target.stat().st_size)},
            }
        except UnicodeDecodeError:
            return {"success": False, "response": f"Binary file, cannot read as text: {target}"}
        except Exception as e:
            self.logger.error(f"Read file failed: {e}")
            return {"success": False, "response": f"Could not read file: {str(e)}", "error": str(e)}


class AppService:
    """Handles application launching and process management."""

    def __init__(self):
        self.logger = Logger().get_logger("AppService")
        self._app_map = self._build_app_map()

    def _build_app_map(self) -> Dict[str, str]:
        """Build platform-specific application mappings."""
        plat = get_platform()

        if plat == "windows":
            return {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "settings": "ms-settings:",
                "explorer": "explorer.exe",
                "file explorer": "explorer.exe",
                "browser": get_default_browser(),
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "terminal": "wt.exe",
                "windows terminal": "wt.exe",
                "cmd": "cmd.exe",
                "command prompt": "cmd.exe",
                "powershell": "pwsh.exe",
                "vscode": "code.exe",
                "code": "code.exe",
                "visual studio code": "code.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "outlook": "outlook.exe",
                "teams": "teams.exe",
                "spotify": "spotify.exe",
                "discord": "Discord.exe",
                "slack": "slack.exe",
                "steam": "steam.exe",
                "task manager": "taskmgr.exe",
                "control panel": "control.exe",
                "regedit": "regedit.exe",
                "paint": "mspaint.exe",
                "snipping tool": "SnippingTool.exe",
                "camera": "microsoft.windows.camera:",
                "photos": "ms-photos:",
                "weather": "bingweather:",
                "store": "ms-windows-store:",
                "xbox": "xbox:",
                "clock": "alarms:",
                "maps": "bingmaps:",
                "mail": "outlookmail:",
                "calendar": "outlookcal:",
                "phone": "ms-phone:",
            }
        elif plat == "macos":
            return {
                "finder": "/System/Library/CoreServices/Finder.app",
                "safari": "/Applications/Safari.app",
                "chrome": "/Applications/Google Chrome.app",
                "terminal": "/Applications/Utilities/Terminal.app",
                "vscode": "/Applications/Visual Studio Code.app",
                "calculator": "/Applications/Calculator.app",
                "notes": "/Applications/Notes.app",
                "textedit": "/Applications/TextEdit.app",
            }
        else:
            return {
                "terminal": "gnome-terminal",
                "browser": "firefox",
                "firefox": "firefox",
                "chrome": "google-chrome",
                "vscode": "code",
                "editor": "gedit",
                "calculator": "gnome-calculator",
                "files": "nautilus",
            }

    def open_app(self, app_name: str) -> Dict[str, Any]:
        """Launch an application by name using multiple resolution strategies."""
        app_lower = app_name.lower().strip()

        # Strategy 1: Check if it's a URL - open in browser
        if app_lower.startswith(("http://", "https://", "www.")):
            import webbrowser
            url = app_lower if app_lower.startswith("http") else "https://" + app_lower
            webbrowser.open(url)
            return {
                "success": True,
                "response": f"Opened URL: {url}",
                "data": {"type": "url", "url": url},
            }

        # Strategy 2: Check app map for known apps
        app_cmd = self._app_map.get(app_lower)

        if not app_cmd:
            for key in self._app_map:
                if key in app_lower:
                    app_cmd = self._app_map[key]
                    break

        # Strategy 3: Use shutil.which() to find in PATH
        if not app_cmd:
            found = shutil.which(app_lower)
            if found:
                app_cmd = found

        # Strategy 4: Try as a direct file path
        if not app_cmd:
            from pathlib import Path
            p = Path(app_lower)
            if p.exists():
                app_cmd = str(p)

        if not app_cmd:
            app_cmd = app_lower

        plat = get_platform()

        if plat == "windows":
            # Check if it's a URI scheme (ms-settings:, microsoft.windows.camera:, etc.)
            if ":" in app_cmd and not app_cmd.startswith("C:") and not app_cmd.startswith("D:"):
                try:
                    os.startfile(app_cmd)
                    self.logger.info(f"Launched URI: {app_cmd}")
                    return {
                        "success": True,
                        "response": f"Opened {app_name}",
                        "data": {"app": app_cmd, "type": "uri"},
                    }
                except Exception as e:
                    self.logger.warning(f"URI launch failed, trying shell: {e}")

            # Primary: os.startfile works with exe names, paths, and folders
            try:
                os.startfile(app_cmd)
                self.logger.info(f"Launched application: {app_cmd}")
                return {
                    "success": True,
                    "response": f"Opened {app_name}",
                    "data": {"app": app_cmd, "type": "file"},
                }
            except FileNotFoundError:
                # Fallback: try shell execution
                try:
                    subprocess.Popen(f'start "" "{app_cmd}"', shell=True)
                    self.logger.info(f"Launched via shell: {app_cmd}")
                    return {
                        "success": True,
                        "response": f"Opened {app_name}",
                        "data": {"app": app_cmd, "type": "shell"},
                    }
                except Exception as e2:
                    return {
                        "success": False,
                        "response": f"Application not found: {app_name}\nAvailable apps: {', '.join(list(self._app_map.keys())[:15])}...",
                    }
            except Exception as e:
                self.logger.error(f"Launch app failed: {e}")
                return {"success": False, "response": f"Could not open {app_name}: {str(e)}", "error": str(e)}
        else:
            try:
                if plat == "macos":
                    subprocess.Popen(["open", app_cmd])
                else:
                    subprocess.Popen(["xdg-open", app_cmd])
                self.logger.info(f"Launched application: {app_cmd}")
                return {
                    "success": True,
                    "response": f"Opened {app_name}",
                    "data": {"app": app_cmd, "command": app_cmd},
                }
            except FileNotFoundError:
                return {
                    "success": False,
                    "response": f"Application not found: {app_name}\nAvailable apps: {', '.join(list(self._app_map.keys())[:15])}...",
                }
            except Exception as e:
                self.logger.error(f"Launch app failed: {e}")
                return {"success": False, "response": f"Could not open {app_name}: {str(e)}", "error": str(e)}

    def get_running_processes(self, limit: int = 15) -> Dict[str, Any]:
        """Get list of running processes."""
        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    info = proc.info
                    processes.append({
                        "pid": info["pid"],
                        "name": info["name"],
                        "cpu": info["cpu_percent"] or 0,
                        "memory": info["memory_percent"] or 0,
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            processes.sort(key=lambda x: x["memory"], reverse=True)
            top = processes[:limit]

            lines = [f"Top {limit} processes by memory:"]
            for p in top:
                lines.append(f"  PID {p['pid']:<6} {p['memory']:>5.1f}% RAM  {p['cpu']:>5.1f}% CPU  {p['name']}")

            return {
                "success": True,
                "response": "\n".join(lines),
                "data": {"processes": top, "total": len(processes)},
            }
        except Exception as e:
            self.logger.error(f"Get processes failed: {e}")
            return {"success": False, "response": f"Could not get processes: {str(e)}", "error": str(e)}

    def kill_process(self, pid_or_name: str) -> Dict[str, Any]:
        """Kill a process by PID or name."""
        try:
            pid = int(pid_or_name)
            proc = psutil.Process(pid)
            proc.kill()
            self.logger.info(f"Killed process {pid}")
            return {"success": True, "response": f"Killed process {pid} ({proc.name()})"}
        except ValueError:
            killed = []
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if pid_or_name.lower() in proc.info["name"].lower():
                        proc.kill()
                        killed.append(proc.info["name"])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if killed:
                return {"success": True, "response": f"Killed: {', '.join(set(killed))}"}
            return {"success": False, "response": f"No process found matching: {pid_or_name}"}
        except Exception as e:
            self.logger.error(f"Kill process failed: {e}")
            return {"success": False, "response": f"Could not kill process: {str(e)}", "error": str(e)}


class SystemService:
    """Handles system monitoring and utilities."""

    def __init__(self):
        self.logger = Logger().get_logger("SystemService")

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        disk_partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                })
            except PermissionError:
                continue

        net_io = psutil.net_io_counters()
        net = psutil.net_if_stats()

        info = {
            "os": f"{platform.system()} {platform.release()}",
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu": {
                "percent": cpu_percent,
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "frequency_mhz": round(cpu_freq.current, 0) if cpu_freq else None,
            },
            "memory": {
                "total_gb": round(memory.total / (1024 ** 3), 2),
                "used_gb": round(memory.used / (1024 ** 3), 2),
                "available_gb": round(memory.available / (1024 ** 3), 2),
                "percent": memory.percent,
            },
            "swap": {
                "total_gb": round(swap.total / (1024 ** 3), 2),
                "used_gb": round(swap.used / (1024 ** 3), 2),
                "percent": swap.percent,
            },
            "disks": disk_partitions,
            "network": {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024 ** 2), 1),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024 ** 2), 1),
            },
            "uptime": str(uptime).split(".")[0],
            "boot_time": boot_time.isoformat(),
        }

        lines = [
            "System Status:",
            f"  OS: {info['os']} ({info['machine']})",
            f"  CPU: {info['cpu']['percent']}% | {info['cpu']['cores_physical']} cores @ {info['cpu']['frequency_mhz']}MHz",
            f"  RAM: {info['memory']['used_gb']}GB / {info['memory']['total_gb']}GB ({info['memory']['percent']}%)",
            f"  Swap: {info['swap']['used_gb']}GB / {info['swap']['total_gb']}GB ({info['swap']['percent']}%)",
        ]

        for disk in disk_partitions:
            lines.append(
                f"  Disk {disk['mountpoint']}: {format_size(disk['used'])} / {format_size(disk['total'])} ({disk['percent']}%)"
            )

        lines.append(f"  Network: ↑{info['network']['bytes_sent_mb']}MB  ↓{info['network']['bytes_recv_mb']}MB")
        lines.append(f"  Uptime: {info['uptime']}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": info,
        }

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information."""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()

        lines = [
            "CPU Information:",
            f"  Physical cores: {psutil.cpu_count(logical=False)}",
            f"  Logical cores: {psutil.cpu_count(logical=True)}",
            f"  Frequency: {cpu_freq.current:.0f}MHz (min: {cpu_freq.min:.0f}, max: {cpu_freq.max:.0f})" if cpu_freq else "  Frequency: N/A",
            f"  Overall usage: {sum(cpu_percent) / len(cpu_percent):.1f}%",
            "",
            "  Per-core usage:",
        ]

        for i, usage in enumerate(cpu_percent):
            bar = "█" * int(usage / 5) + "░" * (20 - int(usage / 5))
            lines.append(f"    Core {i:>2}: [{bar}] {usage:5.1f}%")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"cores": len(cpu_percent), "usage_per_core": cpu_percent},
        }

    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information."""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        lines = [
            "Memory Information:",
            f"  Total: {format_size(memory.total)}",
            f"  Used: {format_size(memory.used)} ({memory.percent}%)",
            f"  Available: {format_size(memory.available)}",
            f"  Swap Total: {format_size(swap.total)}",
            f"  Swap Used: {format_size(swap.used)} ({swap.percent}%)",
        ]

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"memory": dict(memory._asdict()), "swap": dict(swap._asdict())},
        }

    def get_disk_info(self) -> Dict[str, Any]:
        """Get detailed disk information."""
        lines = ["Disk Information:"]

        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                bar = "█" * int(usage.percent / 5) + "░" * (20 - int(usage.percent / 5))
                lines.append(f"  {part.mountpoint} ({part.fstype})")
                lines.append(f"    [{bar}] {usage.percent}%")
                lines.append(f"    Total: {format_size(usage.total)} | Used: {format_size(usage.used)} | Free: {format_size(usage.free)}")
                lines.append("")
            except PermissionError:
                continue

        return {
            "success": True,
            "response": "\n".join(lines),
        }

    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information."""
        lines = ["Network Information:"]
        net_io = psutil.net_io_counters()

        lines.append(f"  Total sent: {format_size(net_io.bytes_sent)}")
        lines.append(f"  Total received: {format_size(net_io.bytes_recv)}")
        lines.append(f"  Packets sent: {net_io.packets_sent:,}")
        lines.append(f"  Packets received: {net_io.packets_recv:,}")
        lines.append("")

        for name, stats in psutil.net_if_stats().items():
            lines.append(f"  {name}: {'UP' if stats.isup else 'DOWN'} ({stats.speed}Mbps)")

        return {
            "success": True,
            "response": "\n".join(lines),
        }


class DownloadService:
    """Handles download folder organization and management."""

    def __init__(self, path_resolver: PathResolver):
        self.logger = Logger().get_logger("DownloadService")
        self.resolver = path_resolver
        self._categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".rtf", ".csv"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
            "Installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
            "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".java", ".cpp", ".c", ".h"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        }

    def organize(self) -> Dict[str, Any]:
        """Organize downloads folder by file type."""
        downloads = self.resolver.downloads
        if not downloads.exists():
            return {"success": False, "response": "Downloads folder not found."}

        organized = {cat: 0 for cat in self._categories}
        organized["Other"] = 0
        errors = []

        for item in downloads.iterdir():
            if not item.is_file():
                continue

            ext = item.suffix.lower()
            moved = False

            for category, extensions in self._categories.items():
                if ext in extensions:
                    dest = downloads / category
                    try:
                        dest.mkdir(exist_ok=True)
                        target = dest / item.name
                        if target.exists():
                            target = dest / f"{item.stem}_{int(item.stat().st_mtime)}{item.suffix}"
                        shutil.move(str(item), str(target))
                        organized[category] += 1
                        moved = True
                    except Exception as e:
                        errors.append(f"{item.name}: {str(e)}")
                    break

            if not moved:
                organized["Other"] += 1

        total = sum(organized.values())
        lines = [f"Downloads organized ({total} files):"]
        for cat, count in organized.items():
            if count > 0:
                lines.append(f"  {cat}: {count} files")

        if errors:
            lines.append(f"\nErrors ({len(errors)}):")
            for err in errors[:5]:
                lines.append(f"  - {err}")

        self.logger.info(f"Organized downloads: {total} files")
        return {
            "success": True,
            "response": "\n".join(lines),
            "data": organized,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get download folder statistics."""
        downloads = self.resolver.downloads
        if not downloads.exists():
            return {"success": False, "response": "Downloads folder not found."}

        by_type = {}
        total_size = 0
        total_files = 0

        for item in downloads.iterdir():
            if item.is_file():
                ext = item.suffix.lower() or "no extension"
                by_type[ext] = by_type.get(ext, 0) + 1
                total_files += 1
                try:
                    total_size += item.stat().st_size
                except OSError:
                    pass

        lines = [f"Downloads folder ({total_files} files, {format_size(total_size)}):"]
        for ext, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:15]:
            lines.append(f"  {ext}: {count} files")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"files": total_files, "size": total_size, "by_type": by_type},
        }

    def cleanup(self, days_old: int = 30) -> Dict[str, Any]:
        """Remove files older than specified days."""
        import time

        downloads = self.resolver.downloads
        if not downloads.exists():
            return {"success": False, "response": "Downloads folder not found."}

        cutoff = time.time() - (days_old * 86400)
        removed = []

        for item in downloads.iterdir():
            if item.is_file():
                try:
                    if item.stat().st_mtime < cutoff:
                        item.unlink()
                        removed.append(item.name)
                except OSError:
                    continue

        return {
            "success": True,
            "response": f"Cleaned up {len(removed)} files older than {days_old} days",
            "data": {"removed": removed, "count": len(removed)},
        }
