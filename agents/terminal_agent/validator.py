"""
Command validator for the Terminal Agent.
Implements dangerous command filtering, safety levels, and sandbox rules.
"""

import os
import re
import platform
from enum import Enum
from typing import List, Optional, Tuple

from core.logger import Logger


class SafetyLevel(Enum):
    """Safety classification for commands."""
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"


class CommandValidator:
    """Validates terminal commands against safety rules and blocklists."""

    WINDOWS_BLOCKED = [
        "format", "diskpart", "chkdsk /f", "sfc /scannow",
        "bcdedit", "bootcfg", "fixboot", "fixmbr",
        "rd /s /q", "deltree",
        "shutdown /r /f", "shutdown /s /f",
        "taskkill /f /im csrss.exe", "taskkill /f /im wininit.exe",
        "taskkill /f /im winlogon.exe", "taskkill /f /im lsass.exe",
        "net user", "net localgroup",
        "reg delete", "reg add",
        "sc delete", "sc stop",
        "wmic process call create",
        "powershell -encodedcommand", "powershell -enc",
        "cmd /c del", "cmd /c rd",
        "attrib +h +s",
        "cipher /w",
        "takeown", "icacls",
        "fsutil",
        "bcdboot",
        "diskraid",
    ]

    UNIX_BLOCKED = [
        "rm -rf /", "rm -rf /*", "rm -rf ~",
        "mkfs", "dd if=", "fdisk", "parted",
        "shutdown -r now", "shutdown -h now", "reboot -f",
        "kill -9 1", "killall -9 init",
        "chmod 777 /", "chmod -R 777 /",
        "chown -R", "chgrp -R",
        "iptables -F", "ufw disable",
        "userdel", "groupdel",
        "passwd", "visudo",
        "> /dev/sda", "> /dev/hda",
        "wget", "curl",
        "nc -l", "netcat", "ncat",
        "base64 -d", "xxd -r",
        "eval", "exec",
        ":(){:|:&};:",
    ]

    CAUTION_COMMANDS = [
        "pip install", "npm install", "yarn add", "cargo install",
        "choco install", "winget install",
        "git push", "git reset", "git clean",
        "docker rm", "docker rmi", "docker system prune",
        "del ", "rmdir ", "remove-item",
        "move ", "rename ", "ren ",
        "net stop", "net start",
        "sc config", "sc create",
        "taskkill", "tskill",
        "reg ",
        "attrib ",
        "cipher ",
        "icacls ",
        "takeown ",
        "fsutil ",
    ]

    SAFE_COMMANDS = [
        "dir", "ls", "cd", "pwd", "echo", "cat", "type",
        "find", "grep", "where", "which", "whoami", "hostname",
        "date", "time", "uptime", "ver", "systeminfo",
        "ipconfig", "ifconfig", "ping", "tracert", "traceroute",
        "netstat", "nslookup", "dig",
        "tasklist", "ps", "top", "htop",
        "python", "python3", "node", "npm", "pip",
        "git status", "git log", "git diff", "git branch",
        "mkdir", "md", "touch", "cp", "copy", "xcopy",
        "help", "man", "info",
        "cls", "clear",
        "tree",
        "vol", "label",
        "path", "set", "env", "printenv",
        "calc", "notepad", "mspaint",
    ]

    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+\*",
        r"rm\s+-rf\s+~",
        r">\s*/dev/sd[a-z]",
        r">\s*/dev/hd[a-z]",
        r":\(\)\{:\|:&\};:",
        r"chmod\s+-?R?\s*777\s+/",
        r"kill\s+-9\s+1\b",
        r"mkfs\.",
        r"dd\s+if=",
        r"format\s+[A-Z]:",
        r"diskpart",
        r"bcdedit",
        r"shutdown\s+/-?[rsf]",
        r"taskkill\s+/f\s+/im\s+(csrss|wininit|winlogon|lsass)\.exe",
        r"powershell\s+-(?:encodedcommand|enc)\s+",
        r"(?:wget|curl)\s+.*\|\s*(?:sh|bash|powershell|cmd)",
        r"eval\s+",
        r"exec\s*\(",
        r"base64\s+-d",
        r"xxd\s+-r",
        r"net\s+user\s+\S+\s+\S+\s+/add",
        r"net\s+localgroup\s+\S+\s+\S+\s+/add",
        r"reg\s+delete\s+",
        r"sc\s+delete\s+",
        r"wmic\s+process\s+call\s+create",
    ]

    def __init__(self, strict_mode: bool = True, allowed_dirs: Optional[List[str]] = None):
        self.logger = Logger().get_logger("CommandValidator")
        self._strict_mode = strict_mode
        self._is_windows = platform.system() == "Windows"
        self._allowed_dirs = allowed_dirs or []
        self._blocked = self.WINDOWS_BLOCKED if self._is_windows else self.UNIX_BLOCKED
        self._compile_patterns()

    def _compile_patterns(self):
        self._dangerous_regex = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS]

    def validate(self, command: str) -> Tuple[SafetyLevel, str]:
        """
        Validate a command and return safety level and reason.
        Returns: (SafetyLevel, reason)
        """
        cmd_stripped = command.strip()
        if not cmd_stripped:
            return SafetyLevel.BLOCKED, "Empty command"

        cmd_lower = cmd_stripped.lower()

        for pattern in self._dangerous_regex:
            if pattern.search(cmd_lower):
                return SafetyLevel.BLOCKED, f"Matches dangerous pattern"

        for blocked in self._blocked:
            if cmd_lower.startswith(blocked.lower()) or cmd_lower == blocked.lower():
                return SafetyLevel.BLOCKED, f"Blocked command: {blocked}"

        if "&&" in cmd_lower or "||" in cmd_lower or ";" in cmd_lower:
            parts = re.split(r"[;&|]+", cmd_lower)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                level, reason = self._check_command(part)
                if level == SafetyLevel.BLOCKED:
                    return SafetyLevel.BLOCKED, f"Chained command blocked: {reason}"
                elif level == SafetyLevel.DANGEROUS:
                    return SafetyLevel.DANGEROUS, reason
            return SafetyLevel.CAUTION, "Chained command - review all parts"

        return self._check_command(cmd_lower)

    def _check_command(self, cmd_lower: str) -> Tuple[SafetyLevel, str]:
        for caution in self.CAUTION_COMMANDS:
            if cmd_lower.startswith(caution.lower()):
                return SafetyLevel.CAUTION, f"Requires caution: {caution}"

        for safe in self.SAFE_COMMANDS:
            if cmd_lower.startswith(safe.lower()) or cmd_lower == safe.lower():
                return SafetyLevel.SAFE, "Known safe command"

        if self._is_path_traversal(cmd_lower):
            return SafetyLevel.DANGEROUS, "Path traversal detected"

        if self._is_redirect_dangerous(cmd_lower):
            return SafetyLevel.CAUTION, "Output redirection to system location"

        if self._strict_mode and not self._is_known_safe(cmd_lower):
            return SafetyLevel.CAUTION, "Unknown command - strict mode"

        return SafetyLevel.SAFE, "Command appears safe"

    def _is_path_traversal(self, cmd: str) -> bool:
        traversal_patterns = ["../", "..\\", "%2e%2e/", "%2e%2e\\"]
        return any(p in cmd for p in traversal_patterns)

    def _is_redirect_dangerous(self, cmd: str) -> bool:
        dangerous_targets = [
            "> /dev/sd", "> /dev/hd", "> /etc/", "> /boot/",
            "> C:\\Windows", "> C:\\Program Files",
            "> /usr/bin", "> /usr/sbin", "> /system32",
        ]
        return any(t in cmd for t in dangerous_targets)

    def _is_known_safe(self, cmd: str) -> bool:
        safe_prefixes = [
            "python ", "python3 ", "node ", "npm ", "pip ",
            "git ", "cargo ", "rustc ", "gcc ", "g++ ",
            "javac ", "java ", "dotnet ",
            "dir ", "ls ", "cd ", "echo ", "cat ", "type ",
            "find ", "grep ", "where ", "which ",
            "date ", "time ", "ver ", "systeminfo",
            "ipconfig", "ping ", "tracert ",
            "tasklist", "ps ", "top ",
            "mkdir ", "md ", "touch ", "cp ", "copy ",
            "help ", "cls ", "clear ", "tree",
            "path ", "set ", "env ",
            "calc", "notepad", "mspaint",
            "code ", "notepad++",
            "winget ", "choco ",
            "docker ps", "docker images", "docker logs",
            "docker inspect", "docker stats",
            "kubectl get", "kubectl describe", "kubectl logs",
        ]
        return any(cmd.startswith(p) for p in safe_prefixes)

    def is_safe(self, command: str) -> bool:
        """Quick check if command is safe to execute."""
        level, _ = self.validate(command)
        return level in (SafetyLevel.SAFE,)

    def get_safety_report(self, command: str) -> Dict:
        """Get detailed safety report for a command."""
        level, reason = self.validate(command)
        return {
            "command": command,
            "safety_level": level.value,
            "reason": reason,
            "is_safe": level == SafetyLevel.SAFE,
            "requires_confirmation": level == SafetyLevel.CAUTION,
            "is_blocked": level == SafetyLevel.BLOCKED,
        }

    def add_to_allowlist(self, command_prefix: str):
        """Add a command prefix to the safe commands list."""
        if command_prefix not in self.SAFE_COMMANDS:
            self.SAFE_COMMANDS.append(command_prefix)
            self.logger.info(f"Added to allowlist: {command_prefix}")

    def add_to_blocklist(self, command: str):
        """Add a command to the blocked list."""
        if command not in self._blocked:
            self._blocked.append(command)
            self.logger.info(f"Added to blocklist: {command}")

    @property
    def strict_mode(self) -> bool:
        return self._strict_mode

    @strict_mode.setter
    def strict_mode(self, value: bool):
        self._strict_mode = value
        self.logger.info(f"Strict mode: {value}")
