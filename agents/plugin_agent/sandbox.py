"""
Security Sandbox for the Plugin Management Agent.
Restricts plugin execution to prevent malicious behavior.
"""

import ast
import builtins
import importlib
import os
import sys
from typing import Any, Dict, List, Optional, Set

from core.logger import Logger

from .models import SecurityLevel


class RestrictedImporter:
    """Controls what modules a plugin can import."""

    ALLOWED_MODULES = {
        "json", "re", "math", "datetime", "time", "collections",
        "itertools", "functools", "operator", "string", "textwrap",
        "pathlib", "dataclasses", "enum", "typing", "uuid",
        "hashlib", "hmac", "secrets", "base64", "urllib.parse",
        "logging", "io", "copy", "pprint", "html", "xml.etree.ElementTree",
    }

    BLOCKED_MODULES = {
        "os", "sys", "subprocess", "shutil", "ctypes", "pickle",
        "marshal", "importlib", "compileall", "site", "builtins",
        "__builtins__", "socket", "http", "ftplib", "smtplib",
        "telnetlib", "xmlrpc", "multiprocessing", "threading",
        "asyncio", "select", "signal", "mmap", "pdb", "trace",
        "inspect", "dis", "code", "codeop", "py_compile",
    }

    def __init__(self, security_level: SecurityLevel):
        self.logger = Logger().get_logger("RestrictedImporter")
        self._security_level = security_level
        self._allowed = set(self.ALLOWED_MODULES)
        self._blocked = set(self.BLOCKED_MODULES)

        if security_level == SecurityLevel.TRUSTED:
            self._blocked = set()
            self._allowed = set()
        elif security_level == SecurityLevel.RESTRICTED:
            self._allowed = {"json", "re", "math", "datetime"}
        elif security_level == SecurityLevel.BLOCKED:
            self._allowed = set()
            self._blocked = set("*")

    def is_allowed(self, module_name: str) -> bool:
        if module_name in self._blocked or module_name.startswith(tuple(m + "." for m in self._blocked)):
            return False
        if self._allowed and module_name not in self._allowed:
            parent = module_name.split(".")[0]
            if parent not in self._allowed:
                return False
        return True

    def safe_import(self, module_name: str, globals_dict: dict = None, locals_dict: dict = None,
                    fromlist: tuple = (), level: int = 0) -> Any:
        if not self.is_allowed(module_name):
            raise ImportError(f"Module '{module_name}' is not allowed in sandbox")
        return importlib.import_module(module_name)


class CodeAnalyzer:
    """Static analysis of plugin code for dangerous patterns."""

    DANGEROUS_FUNCTIONS = {
        "eval", "exec", "compile", "__import__", "getattr", "setattr",
        "delattr", "globals", "locals", "vars", "dir",
    }

    DANGEROUS_ATTRIBUTES = {
        "__builtins__", "__globals__", "__code__", "__closure__",
        "__func__", "__self__", "gi_frame", "f_locals", "f_globals",
    }

    DANGEROUS_CALLS = {
        "open", "input", "exit", "quit",
    }

    def __init__(self, security_level: SecurityLevel):
        self.logger = Logger().get_logger("CodeAnalyzer")
        self._strict = security_level in (SecurityLevel.RESTRICTED, SecurityLevel.BLOCKED)

    def analyze(self, source_code: str) -> List[str]:
        """Analyze source code and return list of security warnings."""
        warnings = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return [f"Syntax error: {e}"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in self.DANGEROUS_FUNCTIONS:
                    warnings.append(f"Dangerous function call: {func.id} at line {node.lineno}")
                if isinstance(func, ast.Name) and func.id in self.DANGEROUS_CALLS:
                    if self._strict:
                        warnings.append(f"Restricted function call: {func.id} at line {node.lineno}")

            if isinstance(node, ast.Attribute):
                if node.attr in self.DANGEROUS_ATTRIBUTES:
                    warnings.append(f"Dangerous attribute access: {node.attr} at line {node.lineno}")

            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("os", "sys", "subprocess", "ctypes"):
                        warnings.append(f"Potentially dangerous import: {alias.name} at line {node.lineno}")

            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in ("os", "sys", "subprocess", "ctypes"):
                    warnings.append(f"Potentially dangerous import from: {node.module} at line {node.lineno}")

        return warnings


class PluginSandbox:
    """Execution sandbox for plugins with restricted builtins and imports."""

    def __init__(self, security_level: SecurityLevel = SecurityLevel.SANDBOXED):
        self.logger = Logger().get_logger("PluginSandbox")
        self._security_level = security_level
        self._importer = RestrictedImporter(security_level)
        self._analyzer = CodeAnalyzer(security_level)
        self._safe_builtins = self._build_safe_builtins()

    def _build_safe_builtins(self) -> Dict[str, Any]:
        safe = {
            "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
            "bytes": bytes, "chr": chr, "dict": dict, "divmod": divmod,
            "enumerate": enumerate, "filter": filter, "float": float,
            "format": format, "frozenset": frozenset, "hash": hash,
            "hex": hex, "int": int, "isinstance": isinstance,
            "issubclass": issubclass, "iter": iter, "len": len,
            "list": list, "map": map, "max": max, "min": min,
            "next": next, "object": object, "oct": oct, "ord": ord,
            "pow": pow, "print": print, "range": range, "repr": repr,
            "reversed": reversed, "round": round, "set": set,
            "slice": slice, "sorted": sorted, "str": str, "sum": sum,
            "tuple": tuple, "type": type, "zip": zip,
            "True": True, "False": False, "None": None,
            "Exception": Exception, "ValueError": ValueError,
            "TypeError": TypeError, "KeyError": KeyError,
            "ImportError": ImportError, "RuntimeError": RuntimeError,
        }
        return safe

    def analyze_code(self, source_code: str) -> List[str]:
        return self._analyzer.analyze(source_code)

    def create_safe_globals(self, extra_globals: Dict[str, Any] = None) -> Dict[str, Any]:
        globals_dict = {"__builtins__": self._safe_builtins}
        if extra_globals:
            globals_dict.update(extra_globals)
        return globals_dict

    def execute_code(self, source_code: str, extra_globals: Dict[str, Any] = None,
                     timeout: int = 10) -> Dict[str, Any]:
        """Execute plugin code in a restricted environment."""
        warnings = self.analyze_code(source_code)
        if warnings and self._security_level != SecurityLevel.TRUSTED:
            critical = [w for w in warnings if "Dangerous" in w]
            if critical:
                return {"success": False, "error": "Code blocked: " + "; ".join(critical)}

        import threading
        result = {"success": False, "output": None, "error": None}

        def _run():
            try:
                safe_globals = self.create_safe_globals(extra_globals)
                exec(compile(source_code, "<plugin>", "exec"), safe_globals)
                result["success"] = True
                result["output"] = safe_globals.get("__result__")
            except Exception as e:
                result["error"] = str(e)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            return {"success": False, "error": f"Execution timed out after {timeout}s"}

        return result

    @property
    def security_level(self) -> SecurityLevel:
        return self._security_level
