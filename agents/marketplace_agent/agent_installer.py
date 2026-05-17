"""
NEXUS - Agent Marketplace System
Agent installer that handles downloading, verifying, installing, updating,
and uninstalling marketplace agents with sandboxed execution.
"""

import os
import json
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from core.logger import Logger
from core.config import Config
from .models import (
    MarketplaceAgent, InstallRecord, InstallStatus, VerificationReport,
    VerificationStatus,
)
from .storage import MarketplaceStorage
from .verification import AgentVerifier
from .dependency_resolver import DependencyResolver


class AgentInstaller:
    """
    Handles the full lifecycle of marketplace agent installation:
    download -> verify -> resolve dependencies -> install -> register.
    """

    def __init__(
        self,
        storage: Optional[MarketplaceStorage] = None,
        verifier: Optional[AgentVerifier] = None,
        resolver: Optional[DependencyResolver] = None,
        install_dir: str = "",
    ):
        self.logger = Logger().get_logger("AgentInstaller")
        self.config = Config()
        self.storage = storage or MarketplaceStorage()
        self.verifier = verifier or AgentVerifier()
        self.resolver = resolver or DependencyResolver()

        if not install_dir:
            install_dir = str(Path(__file__).parent / "installed_agents")
        self._install_dir = Path(install_dir)
        self._install_dir.mkdir(parents=True, exist_ok=True)

        self._load_installed_agents()
        self.logger.info(f"AgentInstaller initialized (install_dir: {self._install_dir})")

    def _load_installed_agents(self):
        """Load installed agent records from storage."""
        records = self.storage.get_all_install_records()
        for data in records:
            record = InstallRecord.from_dict(data)
            self.resolver._installed_agents[record.agent_name] = record

    def install_agent(self, agent: MarketplaceAgent, source_code: str = "",
                      auto_deps: bool = True, sandbox: bool = True) -> InstallRecord:
        """
        Install a marketplace agent with full verification.
        Returns an InstallRecord with the installation result.
        """
        record = InstallRecord(
            agent_id=agent.id,
            agent_name=agent.name,
            version=agent.version,
            status=InstallStatus.DOWNLOADING,
        )
        record.install_log.append(f"Starting installation of {agent.name} v{agent.version}")

        try:
            record.status = InstallStatus.VERIFYING
            record.install_log.append("Verifying agent...")

            report = self.verifier.verify_agent(agent, source_code)
            self.storage.save_verification_report(report.to_dict())

            if not report.is_verified and sandbox:
                record.status = InstallStatus.FAILED
                record.error_message = f"Verification failed: {', '.join(report.issues)}"
                record.install_log.append(f"Verification FAILED: {record.error_message}")
                self.storage.save_install_record(record.to_dict())
                return record

            record.install_log.append(f"Verification passed: {report.status.value}")

            if auto_deps:
                record.install_log.append("Resolving dependencies...")
                success, install_order, issues = self.resolver.resolve_dependencies(agent)

                if not success:
                    record.status = InstallStatus.FAILED
                    record.error_message = f"Dependency resolution failed: {'; '.join(issues)}"
                    record.install_log.append(f"Dependencies FAILED: {record.error_message}")
                    self.storage.save_install_record(record.to_dict())
                    return record

                if install_order and install_order[-1] != agent.name:
                    record.install_log.append(f"Dependencies to install: {', '.join(install_order[:-1])}")

            record.status = InstallStatus.INSTALLING
            record.install_log.append("Installing agent files...")

            agent_dir = self._install_dir / agent.name
            agent_dir.mkdir(parents=True, exist_ok=True)

            if source_code:
                main_file = agent_dir / "agent.py"
                main_file.write_text(source_code, encoding="utf-8")
                record.install_log.append(f"Source written to {main_file}")

            manifest = {
                "name": agent.name,
                "version": agent.version,
                "display_name": agent.display_name,
                "description": agent.description,
                "author": agent.author,
                "category": agent.category.value,
                "capabilities": agent.capabilities,
                "permissions": agent.permissions,
                "installed_at": datetime.now().isoformat(),
                "verification_status": report.status.value,
            }
            manifest_file = agent_dir / "manifest.json"
            manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            record.install_path = str(agent_dir)
            record.status = InstallStatus.INSTALLED
            record.installed_at = datetime.now()
            record.updated_at = datetime.now()
            record.install_log.append(f"Installation complete: {agent_dir}")

            self.storage.save_install_record(record.to_dict())
            self.resolver._installed_agents[agent.name] = record

            self.storage.update_agent_stats(agent.id, installs=1)

            self.logger.info(f"Agent installed: {agent.name} v{agent.version}")
            return record

        except Exception as e:
            record.status = InstallStatus.FAILED
            record.error_message = str(e)
            record.install_log.append(f"Installation error: {str(e)}")
            self.storage.save_install_record(record.to_dict())
            self.logger.error(f"Installation failed for {agent.name}: {e}")
            return record

    def uninstall_agent(self, agent_name: str) -> bool:
        """Uninstall an agent and remove its files."""
        record = self.resolver._installed_agents.get(agent_name)
        if not record:
            record_data = self.storage.get_install_record(agent_name=agent_name)
            if record_data:
                record = InstallRecord.from_dict(record_data)
            else:
                return False

        agent_dir = Path(record.install_path)
        if agent_dir.exists():
            try:
                shutil.rmtree(agent_dir)
                self.logger.info(f"Removed agent files: {agent_dir}")
            except Exception as e:
                self.logger.error(f"Failed to remove agent files: {e}")

        self.storage.delete_install_record(record.agent_id)
        self.resolver._installed_agents.pop(agent_name, None)

        self.logger.info(f"Agent uninstalled: {agent_name}")
        return True

    def update_agent(self, agent: MarketplaceAgent, source_code: str = "") -> InstallRecord:
        """Update an installed agent to a new version."""
        existing = self.resolver._installed_agents.get(agent.name)
        if not existing:
            return InstallRecord(
                agent_id=agent.id,
                agent_name=agent.name,
                status=InstallStatus.FAILED,
                error_message="Agent not installed",
            )

        existing.status = InstallStatus.UPDATING
        existing.install_log.append(f"Updating from v{existing.version} to v{agent.version}")
        self.storage.save_install_record(existing.to_dict())

        result = self.install_agent(agent, source_code)
        return result

    def get_installed_agents(self) -> List[InstallRecord]:
        """Get all installed agents."""
        return list(self.resolver._installed_agents.values())

    def get_install_record(self, agent_name: str) -> Optional[InstallRecord]:
        """Get install record for a specific agent."""
        return self.resolver._installed_agents.get(agent_name)

    def check_updates(self) -> List[Dict[str, Any]]:
        """Check for available updates for all installed agents."""
        return self.resolver.check_all_updates()

    def get_install_dir(self) -> str:
        """Get the installation directory path."""
        return str(self._install_dir)
