"""
NEXUS - Agent Marketplace System
MarketplaceAgent: BaseAgent wrapper that integrates the marketplace API,
agent installer, verification system, dependency resolver, and review system
with the AI Manager.
"""

import re
import time
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import (
    MarketplaceAgent, InstallRecord, InstallStatus, AgentReview,
    VerificationReport, VerificationStatus, AgentCategory,
    ReviewSort, MarketplaceStats, MarketplaceDependency, DependencyType,
)
from .storage import MarketplaceStorage
from .marketplace_api import MarketplaceAPI
from .verification import AgentVerifier
from .dependency_resolver import DependencyResolver
from .agent_installer import AgentInstaller


class MarketplaceAgent(BaseAgent):
    """
    Agent Marketplace System for NEXUS.
    Allows browsing, installing, updating, and managing community-built agents
    with verification, dependency resolution, and review system.
    """

    def __init__(self):
        super().__init__(
            name="marketplace_agent",
            description="Browse, install, and manage community-built agents with verification and dependency resolution",
        )
        self.logger = Logger().get_logger("MarketplaceAgent")
        self.config = Config()

        self._storage = MarketplaceStorage()
        self._api = MarketplaceAPI(storage=self._storage)
        self._verifier = AgentVerifier()
        self._resolver = DependencyResolver()
        self._installer = AgentInstaller(
            storage=self._storage,
            verifier=self._verifier,
            resolver=self._resolver,
        )

        self._ai_manager = None
        self._user_id = "local_user"

        self._register_handlers()
        self._load_installed_agents()
        self.logger.info("MarketplaceAgent initialized")

    def set_ai_manager(self, manager):
        """Set reference to the AI Manager."""
        self._ai_manager = manager
        self.logger.info("MarketplaceAgent connected to AIManager")

    def _register_handlers(self):
        self._handlers = {
            "browse": self._handle_browse,
            "search": self._handle_search,
            "featured": self._handle_featured,
            "categories": self._handle_categories,
            "agent info": self._handle_agent_info,
            "install": self._handle_install,
            "uninstall": self._handle_uninstall,
            "update": self._handle_update,
            "check updates": self._handle_check_updates,
            "installed": self._handle_installed,
            "enable": self._handle_enable,
            "disable": self._handle_disable,
            "review": self._handle_review,
            "reviews": self._handle_reviews,
            "verify": self._handle_verify,
            "dependency tree": self._handle_dependency_tree,
            "stats": self._handle_stats,
            "help": self._handle_help,
        }

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a marketplace command."""
        self.status = AgentStatus.BUSY
        start_time = time.time()

        try:
            cmd = command.strip().lower()
            handler = self._find_handler(cmd, command)

            if handler:
                result = handler(params or {})
            else:
                result = self._handle_fallback(command, params or {})

            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(f"Command '{command}' executed in {duration_ms:.0f}ms")
            return result

        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "agent": self.name,
            }
        finally:
            self.status = AgentStatus.IDLE

    def _find_handler(self, cmd: str, original: str) -> Optional:
        if cmd in self._handlers:
            return self._handlers[cmd]
        for key, handler in self._handlers.items():
            if cmd.startswith(key):
                return handler
        return None

    def _handle_browse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Browse the marketplace catalog."""
        category = params.get("category")
        verified_only = params.get("verified_only", False)
        limit = params.get("limit", 20)

        agents = self._api.browse(category=category, verified_only=verified_only, limit=limit)

        if not agents:
            return {"success": True, "response": "No agents found in marketplace."}

        lines = [f"Marketplace Agents ({len(agents)}):\n"]
        for a in agents:
            verified_icon = "[V]" if a.verification_status == VerificationStatus.VERIFIED else "[ ]"
            official_icon = "[OFFICIAL]" if a.is_official else ""
            featured_icon = "[FEATURED]" if a.is_featured else ""
            installed = self._installer.get_install_record(a.name)
            installed_icon = "[INSTALLED]" if installed and installed.status == InstallStatus.INSTALLED else ""

            lines.append(
                f"  {verified_icon} {official_icon} {featured_icon} {installed_icon} "
                f"{a.display_name} v{a.version}"
            )
            lines.append(f"      {a.description}")
            lines.append(f"      Category: {a.category.value} | Rating: {a.rating:.1f}/5 ({a.rating_count}) | Installs: {a.install_count}")
            lines.append(f"      Author: {a.author} | License: {a.license}")
            lines.append("")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"agents": [a.to_dict() for a in agents]},
        }

    def _handle_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search the marketplace."""
        query = params.get("query", "")
        if not query:
            return {"success": False, "response": "Search query is required"}

        agents = self._api.search(query)
        if not agents:
            return {"success": True, "response": f"No agents found for '{query}'."}

        lines = [f"Search results for '{query}' ({len(agents)}):\n"]
        for a in agents:
            lines.append(f"  {a.display_name} v{a.version} - {a.description}")
            lines.append(f"      Rating: {a.rating:.1f}/5 | Installs: {a.install_count} | Category: {a.category.value}")
            lines.append("")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"agents": [a.to_dict() for a in agents]},
        }

    def _handle_featured(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get featured agents."""
        agents = self._api.get_featured()
        if not agents:
            return {"success": True, "response": "No featured agents."}

        lines = ["Featured Agents:\n"]
        for a in agents:
            lines.append(f"  [FEATURED] {a.display_name} v{a.version}")
            lines.append(f"      {a.description}")
            lines.append(f"      Rating: {a.rating:.1f}/5 ({a.rating_count} reviews) | Installs: {a.install_count}")
            lines.append("")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"agents": [a.to_dict() for a in agents]},
        }

    def _handle_categories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent categories."""
        categories = self._api.get_categories()
        lines = ["Agent Categories:\n"]
        for cat, count in sorted(categories.items()):
            lines.append(f"  {cat}: {count} agents")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"categories": categories},
        }

    def _handle_agent_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed info about an agent."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        agent = self._api.get_agent(agent_name=name)
        if not agent:
            return {"success": False, "response": f"Agent not found: {name}"}

        installed = self._installer.get_install_record(name)
        quick = self._verifier.quick_verify(agent)

        lines = [
            f"Agent: {agent.display_name} v{agent.version}",
            f"  {agent.description}",
            f"  Author: {agent.author}",
            f"  Category: {agent.category.value}",
            f"  License: {agent.license}",
            f"  Verified: {agent.verification_status.value}",
            f"  Official: {'Yes' if agent.is_official else 'No'}",
            f"  Featured: {'Yes' if agent.is_featured else 'No'}",
            f"  Rating: {agent.rating:.1f}/5 ({agent.rating_count} reviews)",
            f"  Installs: {agent.install_count} | Downloads: {agent.download_count}",
            f"  Size: {agent.file_size / 1024:.1f} KB",
            f"",
            f"  Capabilities: {', '.join(agent.capabilities)}",
            f"  Permissions: {', '.join(agent.permissions)}",
        ]

        if agent.dependencies:
            lines.append(f"  Dependencies:")
            for dep in agent.dependencies:
                lines.append(f"    - {dep.name} ({dep.dep_type.value}, >= {dep.min_version})")

        if agent.python_dependencies:
            lines.append(f"  Python packages: {', '.join(agent.python_dependencies)}")

        if installed:
            lines.append(f"  Installed: {installed.status.value} (v{installed.version})")
            if installed.available_update:
                lines.append(f"  Update available: v{installed.available_update}")

        lines.append(f"  Trust score: {'Trusted' if quick['trusted'] else 'Unverified'}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": agent.to_dict(),
        }

    def _handle_install(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Install a marketplace agent."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        agent = self._api.get_agent(agent_name=name)
        if not agent:
            return {"success": False, "response": f"Agent not found: {name}"}

        existing = self._installer.get_install_record(name)
        if existing and existing.status == InstallStatus.INSTALLED:
            return {"success": False, "response": f"Already installed: {name} v{existing.version}"}

        self._api.increment_download(name)

        source_code = params.get("source_code", "")
        record = self._installer.install_agent(agent, source_code=source_code)

        if record.status == InstallStatus.INSTALLED:
            return {
                "success": True,
                "response": f"Installed: {agent.display_name} v{agent.version}\nPath: {record.install_path}",
                "data": record.to_dict(),
            }
        else:
            return {
                "success": False,
                "response": f"Installation failed: {record.error_message}\nLog: {'; '.join(record.install_log[-3:])}",
                "data": record.to_dict(),
            }

    def _handle_uninstall(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Uninstall an agent."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        success = self._installer.uninstall_agent(name)
        return {
            "success": success,
            "response": f"Uninstalled: {name}" if success else f"Agent not found: {name}",
        }

    def _handle_update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an installed agent."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        agent = self._api.get_agent(agent_name=name)
        if not agent:
            return {"success": False, "response": f"Agent not found: {name}"}

        source_code = params.get("source_code", "")
        record = self._installer.update_agent(agent, source_code)

        if record.status == InstallStatus.INSTALLED:
            return {
                "success": True,
                "response": f"Updated: {name} to v{agent.version}",
                "data": record.to_dict(),
            }
        return {
            "success": False,
            "response": f"Update failed: {record.error_message}",
        }

    def _handle_check_updates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check for available updates."""
        updates = self._installer.check_updates()
        if not updates:
            return {"success": True, "response": "All agents are up to date."}

        lines = ["Available updates:\n"]
        for u in updates:
            lines.append(f"  {u['agent_name']}: {u['current_version']} -> {u['available_version']}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"updates": updates},
        }

    def _handle_installed(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List installed agents."""
        installed = self._installer.get_installed_agents()
        if not installed:
            return {"success": True, "response": "No agents installed."}

        lines = [f"Installed Agents ({len(installed)}):\n"]
        for r in installed:
            status_icon = {
                InstallStatus.INSTALLED: "[OK]",
                InstallStatus.FAILED: "[ERR]",
                InstallStatus.DISABLED: "[OFF]",
                InstallStatus.UPDATING: "[UPD]",
            }.get(r.status, "[??]")

            lines.append(f"  {status_icon} {r.agent_name} v{r.version}")
            if r.available_update:
                lines.append(f"      Update available: v{r.available_update}")
            if r.error_message:
                lines.append(f"      Error: {r.error_message}")
            lines.append(f"      Path: {r.install_path}")
            lines.append("")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"installed": [r.to_dict() for r in installed]},
        }

    def _handle_enable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable an installed agent."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        record = self._installer.get_install_record(name)
        if not record:
            return {"success": False, "response": f"Agent not installed: {name}"}

        record.enabled = True
        self._storage.save_install_record(record.to_dict())
        return {"success": True, "response": f"Enabled: {name}"}

    def _handle_disable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable an installed agent."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        record = self._installer.get_install_record(name)
        if not record:
            return {"success": False, "response": f"Agent not installed: {name}"}

        record.enabled = False
        self._storage.save_install_record(record.to_dict())
        return {"success": True, "response": f"Disabled: {name}"}

    def _handle_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a review for an agent."""
        agent_name = params.get("agent_name", "")
        rating = params.get("rating", 0)
        content = params.get("content", "")
        title = params.get("title", "")

        if not agent_name:
            return {"success": False, "response": "Agent name is required"}
        if not (1 <= rating <= 5):
            return {"success": False, "response": "Rating must be 1-5"}

        agent = self._api.get_agent(agent_name=agent_name)
        if not agent:
            return {"success": False, "response": f"Agent not found: {agent_name}"}

        review = AgentReview(
            agent_id=agent.id,
            agent_name=agent_name,
            user_id=self._user_id,
            username="local_user",
            rating=rating,
            title=title,
            content=content,
            is_verified_purchase=True,
        )

        self._storage.save_review(review.to_dict())
        return {
            "success": True,
            "response": f"Review submitted for {agent_name}: {rating}/5 stars",
            "data": review.to_dict(),
        }

    def _handle_reviews(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get reviews for an agent."""
        agent_name = params.get("agent_name", "")
        if not agent_name:
            return {"success": False, "response": "Agent name is required"}

        agent = self._api.get_agent(agent_name=agent_name)
        if not agent:
            return {"success": False, "response": f"Agent not found: {agent_name}"}

        sort = params.get("sort", "newest")
        reviews_data = self._storage.get_reviews(agent.id, limit=20, sort=sort)

        if not reviews_data:
            return {"success": True, "response": f"No reviews for {agent_name}."}

        lines = [f"Reviews for {agent.display_name} ({agent.rating:.1f}/5, {agent.rating_count} reviews):\n"]
        for r in reviews_data:
            stars = "*" * r["rating"] + "." * (5 - r["rating"])
            lines.append(f"  [{stars}] {r['title']}")
            lines.append(f"      {r['content']}")
            lines.append(f"      by {r['username']} on {r['created_at'][:10]}")
            lines.append("")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"reviews": reviews_data},
        }

    def _handle_verify(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify an agent's security."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        agent = self._api.get_agent(agent_name=name)
        if not agent:
            return {"success": False, "response": f"Agent not found: {name}"}

        source_code = params.get("source_code", "")
        report = self._verifier.verify_agent(agent, source_code)
        self._storage.save_verification_report(report.to_dict())

        lines = [
            f"Verification Report: {agent.display_name} v{agent.version}",
            f"  Status: {report.status.value}",
            f"  Checksum: {'Valid' if report.checksum_valid else 'Invalid/Not set'}",
            f"  Signature: {'Valid' if report.signature_valid else 'Not verified'}",
            f"  Security Scan: {'Passed' if report.security_scan_passed else 'Failed'}",
            f"  Dependencies: {'Passed' if report.dependency_check_passed else 'Failed'}",
            f"  Compatibility: {'Passed' if report.compatibility_check_passed else 'Failed'}",
            f"  Sandbox Test: {'Passed' if report.sandbox_test_passed else 'Failed'}",
        ]

        if report.issues:
            lines.append(f"\n  Issues ({len(report.issues)}):")
            for issue in report.issues:
                lines.append(f"    - {issue}")

        if report.warnings:
            lines.append(f"\n  Warnings ({len(report.warnings)}):")
            for warning in report.warnings:
                lines.append(f"    - {warning}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": report.to_dict(),
        }

    def _handle_dependency_tree(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show dependency tree for an agent."""
        name = params.get("name", "")
        if not name:
            return {"success": False, "response": "Agent name is required"}

        agent = self._api.get_agent(agent_name=name)
        if not agent:
            return {"success": False, "response": f"Agent not found: {name}"}

        tree = self._resolver.get_dependency_tree(agent)
        lines = [f"Dependency tree for {agent.display_name}:\n"]
        self._print_tree(tree, lines, indent=0)

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"tree": tree},
        }

    def _print_tree(self, node: Dict, lines: List[str], indent: int = 0):
        """Recursively print dependency tree."""
        prefix = "  " * indent + ("+-- " if indent > 0 else "")
        installed = "[installed]" if node.get("installed") else ""
        circular = "[CIRCULAR]" if node.get("circular") else ""
        dep_type = f"({node.get('dep_type', 'required')})" if node.get("dep_type") else ""

        lines.append(f"{prefix}{node['name']} v{node['version']} {installed} {dep_type} {circular}")

        for dep in node.get("dependencies", []):
            self._print_tree(dep, lines, indent + 1)

    def _handle_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get marketplace statistics."""
        stats = self._api.get_stats()
        lines = [
            "Marketplace Statistics:",
            f"  Total agents: {stats.total_agents}",
            f"  Installed: {stats.installed_agents}",
            f"  Featured: {stats.featured_agents}",
            f"  Official: {stats.official_agents}",
            f"  Verified: {stats.verified_agents}",
            f"  Total downloads: {stats.total_downloads}",
            f"  Total reviews: {stats.total_reviews}",
            f"  Average rating: {stats.avg_rating:.1f}/5",
            f"  Updates available: {stats.updates_available}",
        ]
        if stats.categories:
            lines.append(f"\n  By category:")
            for cat, count in sorted(stats.categories.items()):
                lines.append(f"    {cat}: {count}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": stats.to_dict(),
        }

    def _handle_fallback(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unrecognized commands."""
        cmd_lower = command.lower()

        if any(kw in cmd_lower for kw in ["browse", "catalog", "marketplace", "store"]):
            return self._handle_browse(params)
        if any(kw in cmd_lower for kw in ["search", "find"]):
            query = self._extract_query(command)
            return self._handle_search({"query": query})
        if any(kw in cmd_lower for kw in ["install", "get", "add"]):
            name = self._extract_name(command)
            return self._handle_install({"name": name})
        if any(kw in cmd_lower for kw in ["uninstall", "remove", "delete"]):
            name = self._extract_name(command)
            return self._handle_uninstall({"name": name})
        if any(kw in cmd_lower for kw in ["update", "upgrade"]):
            name = self._extract_name(command)
            if name:
                return self._handle_update({"name": name})
            return self._handle_check_updates(params)
        if any(kw in cmd_lower for kw in ["installed", "my agents"]):
            return self._handle_installed(params)
        if any(kw in cmd_lower for kw in ["featured", "popular"]):
            return self._handle_featured(params)
        if any(kw in cmd_lower for kw in ["stats", "statistics"]):
            return self._handle_stats(params)

        return {
            "success": False,
            "response": f"Unknown marketplace command: {command}. Type 'help' for available commands.",
        }

    def _handle_help(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show available commands."""
        return {
            "success": True,
            "response": """Marketplace Agent - Available Commands:

BROWSE & SEARCH:
  browse [category]        - Browse marketplace catalog
  search <query>           - Search for agents
  featured                 - Show featured agents
  categories               - List agent categories
  agent info <name>        - Get detailed agent info

INSTALL & MANAGE:
  install <name>           - Install an agent
  uninstall <name>         - Remove an agent
  update <name>            - Update an agent
  check updates            - Check for available updates
  installed                - List installed agents
  enable <name>            - Enable an installed agent
  disable <name>           - Disable an installed agent

REVIEWS & VERIFICATION:
  review <name> <rating>   - Submit a review (1-5 stars)
  reviews <name>           - Read agent reviews
  verify <name>            - Verify agent security

DEPENDENCIES:
  dependency tree <name>   - Show dependency tree

STATISTICS:
  stats                    - Get marketplace statistics""",
        }

    def _load_installed_agents(self):
        """Load installed agents into the resolver."""
        installed = self._installer.get_installed_agents()
        for record in installed:
            self._resolver._installed_agents[record.agent_name] = record

    def _extract_name(self, command: str) -> str:
        match = re.search(r"(?:install|uninstall|update|info|review|verify|enable|disable)\s+(?:agent\s+)?([a-zA-Z0-9_-]+)", command, re.IGNORECASE)
        return match.group(1) if match else ""

    def _extract_query(self, command: str) -> str:
        match = re.search(r"(?:search|find)\s+(?:for\s+)?(.+)", command, re.IGNORECASE)
        return match.group(1).strip() if match else command

    def get_capabilities(self) -> list:
        """Return list of capabilities."""
        return [
            "browse", "search", "featured", "categories", "agent info",
            "install", "uninstall", "update", "check updates", "installed",
            "enable", "disable", "review", "reviews", "verify",
            "dependency tree", "stats",
        ]

    def browse_agents(self, category: str = None, limit: int = 50) -> List[MarketplaceAgent]:
        """Programmatic API: Browse marketplace agents."""
        return self._api.browse(category=category, limit=limit)

    def install_agent_programmatic(self, agent_name: str, source_code: str = "") -> InstallRecord:
        """Programmatic API: Install an agent."""
        agent = self._api.get_agent(agent_name=agent_name)
        if not agent:
            return InstallRecord(status=InstallStatus.FAILED, error_message="Agent not found")
        return self._installer.install_agent(agent, source_code=source_code)

    def get_installed_agents(self) -> List[InstallRecord]:
        """Programmatic API: Get installed agents."""
        return self._installer.get_installed_agents()

    def shutdown(self):
        """Shutdown the marketplace agent."""
        self.logger.info("Shutting down MarketplaceAgent...")
        self.status = AgentStatus.OFFLINE
        self.logger.info("MarketplaceAgent shutdown complete")
