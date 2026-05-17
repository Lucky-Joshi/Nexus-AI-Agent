"""
NEXUS - Agent Marketplace System
Security verification system for marketplace agents including checksum validation,
signature verification, sandbox testing, and security scanning.
"""

import ast
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from core.logger import Logger
from core.config import Config
from .models import (
    MarketplaceAgent, VerificationReport, VerificationStatus,
)


class AgentVerifier:
    """
    Verifies marketplace agents for security, integrity, and compatibility.
    Performs checksum validation, code analysis, sandbox testing, and
    dependency verification.
    """

    DANGEROUS_IMPORTS = [
        "ctypes", "subprocess", "os.system", "os.popen",
        "socket", "http.server", "ftplib", "telnetlib",
        "pickle", "marshal", "shelve",
        "__import__", "importlib", "exec", "eval", "compile",
    ]

    SUSPICIOUS_PATTERNS = [
        (r"os\.system\s*\(", "Direct OS command execution"),
        (r"os\.popen\s*\(", "OS pipe execution"),
        (r"subprocess\.(call|run|Popen|check_output)", "Subprocess execution"),
        (r"eval\s*\(", "Dynamic evaluation"),
        (r"exec\s*\(", "Dynamic code execution"),
        (r"__import__\s*\(", "Dynamic import"),
        (r"ctypes\.", "Direct C library access"),
        (r"socket\.", "Raw socket access"),
        (r"requests\.post\s*\(.*password", "Sending passwords over network"),
        (r"open\s*\(.*['\"].*\/etc\/", "Accessing system files"),
        (r"open\s*\(.*['\"].*windows\/system32", "Accessing system files"),
        (r"shutil\.rmtree", "Recursive directory deletion"),
        (r"shutil\.move\s*\(.*\/", "File move operations"),
        (r"globally\s*=\s*True", "Global variable modification"),
        (r"builtins\.", "Builtins modification"),
        (r"sys\.modules", "Module system manipulation"),
        (r"sys\.path\.", "Python path manipulation"),
    ]

    def __init__(self, nexus_version: str = "1.0.0"):
        self.logger = Logger().get_logger("AgentVerifier")
        self.config = Config()
        self._nexus_version = nexus_version

    def verify_agent(self, agent: MarketplaceAgent, source_code: str = "") -> VerificationReport:
        """
        Perform full verification of a marketplace agent.
        Returns a verification report with all checks.
        """
        report = VerificationReport(
            agent_id=agent.id,
            agent_name=agent.name,
            version=agent.version,
            verified_by="NEXUS Verifier",
        )

        report.checksum_valid = self._verify_checksum(agent, source_code)
        report.signature_valid = self._verify_signature(agent)
        report.security_scan_passed, security_issues, security_warnings = self._security_scan(source_code)
        report.dependency_check_passed, dep_issues = self._check_dependencies(agent)
        report.compatibility_check_passed, compat_issues = self._check_compatibility(agent)
        report.sandbox_test_passed = self._sandbox_test(agent, source_code)

        report.issues = security_issues + dep_issues + compat_issues
        report.warnings = security_warnings

        if report.checksum_valid and report.security_scan_passed and report.compatibility_check_passed:
            report.status = VerificationStatus.VERIFIED
        elif report.issues:
            report.status = VerificationStatus.REJECTED
        else:
            report.status = VerificationStatus.PENDING

        report.report_data = {
            "nexus_version": self._nexus_version,
            "checks_performed": [
                "checksum", "signature", "security_scan",
                "dependency_check", "compatibility_check", "sandbox_test",
            ],
        }

        self.logger.info(
            f"Verification for {agent.name}: {report.status.value} "
            f"(issues: {len(report.issues)}, warnings: {len(report.warnings)})"
        )
        return report

    def _verify_checksum(self, agent: MarketplaceAgent, source_code: str) -> bool:
        """Verify file checksum matches expected value."""
        if not agent.checksum or not source_code:
            return True

        content = source_code.encode("utf-8") if isinstance(source_code, str) else source_code
        computed = agent.compute_checksum(content)
        return computed == agent.checksum

    def _verify_signature(self, agent: MarketplaceAgent) -> bool:
        """Verify agent signature (simulated - in production would use cryptographic signatures)."""
        if agent.is_official:
            return True
        if agent.verification_status == VerificationStatus.VERIFIED:
            return True
        return False

    def _security_scan(self, source_code: str) -> Tuple[bool, List[str], List[str]]:
        """Scan source code for security issues."""
        issues = []
        warnings = []

        if not source_code:
            return True, [], []

        for pattern, description in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, source_code):
                if "exec" in description.lower() or "eval" in description.lower() or "ctypes" in description.lower():
                    issues.append(f"Security: {description}")
                else:
                    warnings.append(f"Warning: {description}")

        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.DANGEROUS_IMPORTS:
                            warnings.append(f"Imports dangerous module: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module in self.DANGEROUS_IMPORTS:
                        warnings.append(f"Imports from dangerous module: {node.module}")
        except SyntaxError:
            issues.append("Invalid Python syntax")

        is_clean = len(issues) == 0
        return is_clean, issues, warnings

    def _check_dependencies(self, agent: MarketplaceAgent) -> Tuple[bool, List[str]]:
        """Check if agent dependencies can be resolved."""
        issues = []

        for dep in agent.dependencies:
            if dep.dep_type.value == "required":
                issues.append(f"Missing dependency: {dep.name} (requires {dep.min_version})")

        for py_dep in agent.python_dependencies:
            try:
                import importlib
                module_name = py_dep.split("==")[0].split(">=")[0].split("<=")[0].strip()
                importlib.import_module(module_name)
            except ImportError:
                issues.append(f"Python package not installed: {py_dep}")

        return len(issues) == 0, issues

    def _check_compatibility(self, agent: MarketplaceAgent) -> Tuple[bool, List[str]]:
        """Check if agent is compatible with current NEXUS version."""
        issues = []

        min_ver = agent.min_nexus_version
        max_ver = agent.max_nexus_version

        if not self._version_gte(self._nexus_version, min_ver):
            issues.append(f"Requires NEXUS >= {min_ver}, current is {self._nexus_version}")

        if max_ver != "*" and not self._version_lte(self._nexus_version, max_ver):
            issues.append(f"Requires NEXUS <= {max_ver}, current is {self._nexus_version}")

        return len(issues) == 0, issues

    def _sandbox_test(self, agent: MarketplaceAgent, source_code: str) -> bool:
        """Simulate sandbox execution test."""
        if not source_code:
            return True

        critical_patterns = [
            r"os\.system", r"os\.popen", r"subprocess\.Popen",
            r"ctypes\.", r"socket\.socket", r"eval\s*\(", r"exec\s*\(",
        ]

        for pattern in critical_patterns:
            if re.search(pattern, source_code):
                return False

        return True

    @staticmethod
    def _version_gte(v1: str, v2: str) -> bool:
        p1 = [int(x) for x in re.findall(r"\d+", v1)]
        p2 = [int(x) for x in re.findall(r"\d+", v2)]
        return p1 >= p2

    @staticmethod
    def _version_lte(v1: str, v2: str) -> bool:
        p1 = [int(x) for x in re.findall(r"\d+", v1)]
        p2 = [int(x) for x in re.findall(r"\d+", v2)]
        return p1 <= p2

    def quick_verify(self, agent: MarketplaceAgent) -> Dict[str, Any]:
        """Quick verification without full code analysis."""
        return {
            "is_official": agent.is_official,
            "is_verified": agent.verification_status == VerificationStatus.VERIFIED,
            "is_featured": agent.is_featured,
            "has_checksum": bool(agent.checksum),
            "rating": agent.rating,
            "install_count": agent.install_count,
            "trusted": agent.is_official or agent.verification_status == VerificationStatus.VERIFIED,
        }
