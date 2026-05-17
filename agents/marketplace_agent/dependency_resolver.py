"""
NEXUS - Agent Marketplace System
Dependency resolver for marketplace agents with version compatibility checking,
conflict detection, and installation order resolution.
"""

import re
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple

from core.logger import Logger
from .models import MarketplaceAgent, MarketplaceDependency, DependencyType, InstallRecord


class DependencyResolver:
    """
    Resolves agent dependencies, detects conflicts, and determines
    the correct installation order.
    """

    def __init__(self):
        self.logger = Logger().get_logger("DependencyResolver")
        self._installed_agents: Dict[str, InstallRecord] = {}
        self._catalog: Dict[str, MarketplaceAgent] = {}

    def set_installed_agents(self, agents: Dict[str, InstallRecord]):
        """Set the currently installed agents."""
        self._installed_agents = agents

    def set_catalog(self, catalog: Dict[str, MarketplaceAgent]):
        """Set the marketplace catalog."""
        self._catalog = catalog

    def resolve_dependencies(self, agent: MarketplaceAgent) -> Tuple[bool, List[str], List[str]]:
        """
        Resolve all dependencies for an agent.
        Returns (success, install_order, issues).
        """
        issues = []
        to_install = []
        visited = set()

        success = self._resolve_recursive(agent, to_install, visited, issues)

        if success:
            install_order = self._topological_sort(to_install)
            return True, install_order, []
        else:
            return False, [], issues

    def _resolve_recursive(self, agent: MarketplaceAgent, to_install: List[str],
                           visited: Set[str], issues: List[str]) -> bool:
        """Recursively resolve dependencies."""
        if agent.name in visited:
            return True
        visited.add(agent.name)

        for dep in agent.dependencies:
            if dep.dep_type == DependencyType.CONFLICTS:
                if dep.name in self._installed_agents:
                    record = self._installed_agents[dep.name]
                    if record.status.value == "installed":
                        issues.append(f"Conflict: {agent.name} conflicts with installed {dep.name}")
                        return False
                continue

            if dep.dep_type == DependencyType.OPTIONAL:
                continue

            dep_agent = self._catalog.get(dep.name)
            if not dep_agent:
                issues.append(f"Dependency not found in marketplace: {dep.name}")
                return False

            if not self._version_compatible(dep_agent.version, dep.min_version, dep.max_version):
                issues.append(
                    f"Version incompatibility: {dep.name} {dep_agent.version} "
                    f"(requires {dep.min_version} - {dep.max_version})"
                )
                return False

            if dep.name not in self._installed_agents or \
               self._installed_agents[dep.name].status.value != "installed":
                if not self._resolve_recursive(dep_agent, to_install, visited, issues):
                    return False
                if dep.name not in to_install:
                    to_install.append(dep.name)

        if agent.name not in to_install:
            to_install.append(agent.name)

        return True

    def _version_compatible(self, version: str, min_ver: str, max_ver: str) -> bool:
        """Check if a version is within the required range."""
        if not self._version_gte(version, min_ver):
            return False
        if max_ver != "*" and not self._version_lte(version, max_ver):
            return False
        return True

    def _topological_sort(self, agents: List[str]) -> List[str]:
        """Sort agents in dependency-respecting installation order."""
        in_degree = defaultdict(int)
        graph = defaultdict(list)

        for name in agents:
            agent = self._catalog.get(name)
            if agent:
                for dep in agent.dependencies:
                    if dep.name in agents and dep.dep_type == DependencyType.REQUIRED:
                        graph[dep.name].append(name)
                        in_degree[name] += 1
            if name not in in_degree:
                in_degree[name] = 0

        queue = deque([n for n in agents if in_degree[n] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(agents):
            self.logger.warning("Circular dependency detected, using original order")
            return agents

        return result

    def check_update(self, agent_name: str, current_version: str) -> Optional[str]:
        """Check if an update is available for an installed agent."""
        catalog_agent = self._catalog.get(agent_name)
        if not catalog_agent:
            return None

        if self._version_gt(catalog_agent.version, current_version):
            return catalog_agent.version
        return None

    def check_all_updates(self) -> List[Dict[str, Any]]:
        """Check for updates for all installed agents."""
        updates = []
        for name, record in self._installed_agents.items():
            if record.status.value != "installed":
                continue
            new_version = self.check_update(name, record.version)
            if new_version:
                updates.append({
                    "agent_name": name,
                    "current_version": record.version,
                    "available_version": new_version,
                })
        return updates

    def get_dependency_tree(self, agent: MarketplaceAgent, depth: int = 0,
                            visited: Optional[Set[str]] = None) -> Dict[str, Any]:
        """Get a visual dependency tree for an agent."""
        if visited is None:
            visited = set()

        if agent.name in visited:
            return {"name": agent.name, "version": agent.version, "circular": True}

        visited.add(agent.name)

        tree = {
            "name": agent.name,
            "version": agent.version,
            "installed": agent.name in self._installed_agents,
            "dependencies": [],
        }

        for dep in agent.dependencies:
            dep_agent = self._catalog.get(dep.name)
            if dep_agent:
                dep_tree = self.get_dependency_tree(dep_agent, depth + 1, visited)
                dep_tree["dep_type"] = dep.dep_type.value
                dep_tree["version_required"] = f"{dep.min_version} - {dep.max_version}"
                tree["dependencies"].append(dep_tree)

        return tree

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

    @staticmethod
    def _version_gt(v1: str, v2: str) -> bool:
        p1 = [int(x) for x in re.findall(r"\d+", v1)]
        p2 = [int(x) for x in re.findall(r"\d+", v2)]
        return p1 > p2
