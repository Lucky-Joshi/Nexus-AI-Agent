"""
File Agent for NEXUS.
Orchestrates FileService, AppService, SystemService, and DownloadService.
Handles command parsing and delegates to the appropriate service.
"""

from typing import Any, Dict, Optional
from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from .services import FileService, AppService, SystemService, DownloadService
from .utils import PathResolver, extract_filename


class FileAgent(BaseAgent):
    """
    File and system operations agent for NEXUS.
    Thin orchestrator that delegates to specialized service classes.
    """

    def __init__(self):
        super().__init__("file_agent", "File operations, app management, and system monitoring")
        self.logger = Logger().get_logger("FileAgent")

        self._path_resolver = PathResolver()
        self._file_service = FileService(self._path_resolver)
        self._app_service = AppService()
        self._system_service = SystemService()
        self._download_service = DownloadService(self._path_resolver)

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route command to the appropriate service handler."""
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["open", "launch", "run", "start"]):
                if any(kw in cmd for kw in ["desktop", "downloads", "documents", "pictures", "videos", "onedrive"]):
                    return self._handle_open_folder(command)
                elif any(kw in cmd for kw in ["pdf"]):
                    return self._handle_open_pdf(command)
                elif any(kw in cmd for kw in ["media", "video", "music", "mp4", "mp3"]):
                    return self._handle_open_media(command)
                elif any(kw in cmd for kw in ["file", "document", "pdf", "image", "video", "audio"]):
                    return self._handle_open_file(command)
                return self._handle_open_app(command)

            elif self._matches(cmd, ["create file", "make file", "new file"]):
                return self._handle_create_file(command)

            elif self._matches(cmd, ["create folder", "make folder", "new folder", "create directory", "make directory", "new directory"]):
                return self._handle_create_folder(command)

            elif self._matches(cmd, ["create", "make", "new"]) and self._matches(cmd, ["folder", "directory"]):
                return self._handle_create_folder(command)

            elif self._matches(cmd, ["create", "make", "new"]) and self._matches(cmd, ["file"]):
                return self._handle_create_file(command)

            elif self._matches(cmd, ["delete", "remove", "trash"]):
                return self._handle_delete(command)

            elif "rename" in cmd:
                return self._handle_rename(command)

            elif "move" in cmd:
                return self._handle_move(command)

            elif "copy" in cmd:
                return self._handle_copy(command)

            elif self._matches(cmd, ["search", "find"]) and self._matches(cmd, ["file", "folder"]):
                return self._handle_search(command)

            elif self._matches(cmd, ["read", "show", "display", "view", "cat", "type"]) and self._matches(cmd, ["file"]):
                return self._handle_read_file(command)

            elif self._matches(cmd, ["list", "ls", "dir"]) or (self._matches(cmd, ["show", "display"]) and self._matches(cmd, ["folder", "directory", "contents"])):
                return self._handle_list_dir(command)

            elif self._matches(cmd, ["organize"]) and self._matches(cmd, ["download"]):
                return self._handle_organize_downloads()

            elif self._matches(cmd, ["download", "stats"]) and not self._matches(cmd, ["organize"]):
                return self._handle_download_stats()

            elif self._matches(cmd, ["open"]) and self._matches(cmd, ["folder", "desktop", "downloads", "documents", "pictures", "videos", "onedrive"]):
                return self._handle_open_folder(command)

            elif self._matches(cmd, ["open", "find"]) and self._matches(cmd, ["pdf"]):
                return self._handle_open_pdf(command)

            elif self._matches(cmd, ["open", "find", "play"]) and self._matches(cmd, ["media", "video", "music", "mp4", "mp3"]):
                return self._handle_open_media(command)

            elif self._matches(cmd, ["system", "status", "info"]):
                return self._handle_system_info()

            elif self._matches(cmd, ["cpu"]):
                return self._handle_cpu_info()

            elif self._matches(cmd, ["ram", "memory"]) and not self._matches(cmd, ["system"]):
                return self._handle_memory_info()

            elif self._matches(cmd, ["disk", "storage", "drive"]):
                return self._handle_disk_info()

            elif self._matches(cmd, ["network", "net", "internet"]):
                return self._handle_network_info()

            elif self._matches(cmd, ["process", "task", "running"]):
                return self._handle_processes(command)

            elif self._matches(cmd, ["kill", "stop", "terminate"]):
                return self._handle_kill_process(command)

            else:
                return self._handle_open_app(command)

        except Exception as e:
            self.logger.error(f"FileAgent error: {e}")
            return {
                "success": False,
                "response": f"File operation error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "open_application",
            "open_file",
            "open_folder",
            "open_pdf",
            "open_media",
            "create_file",
            "create_folder",
            "delete",
            "rename",
            "move",
            "copy",
            "search_files",
            "read_file",
            "list_directory",
            "system_info",
            "cpu_info",
            "memory_info",
            "disk_info",
            "network_info",
            "processes",
            "kill_process",
            "organize_downloads",
            "download_stats",
        ]

    def _handle_open_app(self, command: str) -> Dict[str, Any]:
        app_name = command.lower()
        for prefix in ["open ", "launch ", "run ", "start "]:
            if app_name.startswith(prefix):
                app_name = app_name[len(prefix):]
                break
        app_name = app_name.strip()

        if not app_name:
            return {"success": False, "response": "Please specify an application to open."}

        return self._app_service.open_app(app_name)

    def _handle_open_file(self, command: str) -> Dict[str, Any]:
        file_path = extract_filename(
            command,
            prefixes=["open file ", "open document ", "launch file ", "run file ", "open "],
            suffixes=[" file", " document", " pdf", " image"],
        )

        if not file_path:
            return {"success": False, "response": "Please specify a file to open."}

        return self._file_service.open_file(file_path)

    def _handle_create_file(self, command: str) -> Dict[str, Any]:
        name, parent = self._extract_name_and_dir(command, [
            "create file ", "make file ", "new file ",
            "create ", "make ", "new ",
        ])

        if not name:
            return {"success": False, "response": "Please specify a file name. Example: 'create file notes.txt in C:\\Users\\lucky\\Documents'"}

        return self._file_service.create_file(name, parent=parent)

    def _handle_create_folder(self, command: str) -> Dict[str, Any]:
        name, parent = self._extract_name_and_dir(command, [
            "create folder ", "make folder ", "new folder ",
            "create directory ", "make directory ", "new directory ",
            "create ", "make ", "new ",
        ])

        if not name:
            return {"success": False, "response": "Please specify a folder name. Example: 'create folder projects in D:\\work'"}

        return self._file_service.create_folder(name, parent=parent)

    def _handle_delete(self, command: str) -> Dict[str, Any]:
        path_str = extract_filename(
            command,
            prefixes=["delete ", "remove ", "trash "],
            suffixes=[],
        )

        if not path_str:
            return {"success": False, "response": "Please specify what to delete."}

        return self._file_service.delete(path_str)

    def _handle_rename(self, command: str) -> Dict[str, Any]:
        parts = command.lower().split(" to ")
        if len(parts) != 2:
            return {"success": False, "response": "Usage: rename [source] to [new_name]"}

        source = parts[0].replace("rename", "").strip()
        new_name = parts[1].strip()

        return self._file_service.rename(source, new_name)

    def _handle_move(self, command: str) -> Dict[str, Any]:
        parts = command.lower().split(" to ")
        if len(parts) != 2:
            return {"success": False, "response": "Usage: move [source] to [destination]"}

        source = parts[0].replace("move", "").strip()
        dest = parts[1].strip()

        return self._file_service.move(source, dest)

    def _handle_copy(self, command: str) -> Dict[str, Any]:
        parts = command.lower().split(" to ")
        if len(parts) != 2:
            return {"success": False, "response": "Usage: copy [source] to [destination]"}

        source = parts[0].replace("copy", "").strip()
        dest = parts[1].strip()

        return self._file_service.copy(source, dest)

    def _handle_search(self, command: str) -> Dict[str, Any]:
        query = extract_filename(
            command,
            prefixes=["search ", "find ", "search files ", "find files ", "search for "],
            suffixes=[" files", " folders", " file", " folder"],
        )

        if not query:
            return {"success": False, "response": "Please specify a search query."}

        return self._file_service.search(query)

    def _handle_read_file(self, command: str) -> Dict[str, Any]:
        file_path = extract_filename(
            command,
            prefixes=["read ", "show ", "display ", "view ", "read file ", "show file ", "cat ", "type "],
            suffixes=[" file"],
        )

        if not file_path:
            return {"success": False, "response": "Please specify a file to read."}

        return self._file_service.read_file(file_path)

    def _handle_list_dir(self, command: str) -> Dict[str, Any]:
        path_str = extract_filename(
            command,
            prefixes=["list folder ", "list directory ", "ls folder ", "dir folder ", "show folder ", "show directory ", "list ", "ls ", "dir ", "show ", "display "],
            suffixes=[" directory", " folder", " contents"],
        )

        if not path_str:
            path_str = "."

        return self._file_service.list_directory(path_str)

    def _handle_system_info(self) -> Dict[str, Any]:
        return self._system_service.get_system_info()

    def _handle_cpu_info(self) -> Dict[str, Any]:
        return self._system_service.get_cpu_info()

    def _handle_memory_info(self) -> Dict[str, Any]:
        return self._system_service.get_memory_info()

    def _handle_disk_info(self) -> Dict[str, Any]:
        return self._system_service.get_disk_info()

    def _handle_network_info(self) -> Dict[str, Any]:
        return self._system_service.get_network_info()

    def _handle_processes(self, command: str) -> Dict[str, Any]:
        limit = 15
        for word in command.lower().split():
            if word.isdigit():
                limit = int(word)
                break
        return self._app_service.get_running_processes(limit)

    def _handle_kill_process(self, command: str) -> Dict[str, Any]:
        target = extract_filename(
            command,
            prefixes=["kill ", "stop ", "terminate ", "kill process ", "stop process "],
            suffixes=[],
        )

        if not target:
            return {"success": False, "response": "Please specify a process PID or name to kill."}

        return self._app_service.kill_process(target)

    def _handle_organize_downloads(self) -> Dict[str, Any]:
        return self._download_service.organize()

    def _handle_download_stats(self) -> Dict[str, Any]:
        return self._download_service.get_stats()

    def _handle_open_folder(self, command: str) -> Dict[str, Any]:
        folder_name = extract_filename(
            command,
            prefixes=["open ", "open folder ", "go to ", "navigate to "],
            suffixes=[" folder"],
        )

        if not folder_name:
            return {"success": False, "response": "Please specify a folder to open."}

        return self._file_service.open_folder(folder_name)

    def _handle_open_pdf(self, command: str) -> Dict[str, Any]:
        folder = extract_filename(
            command,
            prefixes=["open pdf ", "find pdf ", "open pdf in ", "find pdf in "],
            suffixes=[],
        )

        if not folder:
            return self._file_service.open_pdf()

        return self._file_service.open_pdf(folder)

    def _handle_open_media(self, command: str) -> Dict[str, Any]:
        folder = extract_filename(
            command,
            prefixes=["open media ", "play media ", "open video ", "play music ", "open media in "],
            suffixes=[],
        )

        if not folder:
            return self._file_service.open_media()

        return self._file_service.open_media(folder)

    def _extract_name_and_dir(self, command: str, prefixes: list) -> tuple:
        """Extract item name and optional parent directory from command.
        Supports: 'create file X', 'create file X in Y', 'create file X inside Y', 'create file X at Y'
        """
        cmd_lower = command.lower()
        content = None
        for prefix in prefixes:
            if cmd_lower.startswith(prefix):
                content = command[len(prefix):].strip()
                break

        if not content:
            return None, None

        dir_markers = [" in ", " inside ", " at ", " under ", " within ", " into "]
        for marker in dir_markers:
            idx = content.lower().find(marker)
            if idx > 0:
                name = content[:idx].strip().strip('"').strip("'")
                parent = content[idx + len(marker):].strip().strip('"').strip("'")
                return name, parent

        name = content.strip().strip('"').strip("'")
        return name, None

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        """Check if any keyword exists in text."""
        return any(kw in text for kw in keywords)
