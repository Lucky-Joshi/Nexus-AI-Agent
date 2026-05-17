"""
NEXUS - Autonomous Planner Agent
Dependency graph for task ordering, cycle detection, parallel execution groups,
and topological sorting.
"""

from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple

from core.logger import Logger
from .models import PlanTask, TaskStatus, DependencyType


class DependencyGraph:
    """
    Directed acyclic graph (DAG) for task dependencies.
    Supports topological sorting, cycle detection, parallel execution levels,
    and dependency resolution.
    """

    def __init__(self):
        self.logger = Logger().get_logger("DependencyGraph")
        self._adjacency: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_adj: Dict[str, Set[str]] = defaultdict(set)
        self._nodes: Dict[str, PlanTask] = {}
        self._dependency_types: Dict[Tuple[str, str], DependencyType] = {}

    def add_task(self, task: PlanTask):
        """Add a task node to the graph."""
        self._nodes[task.id] = task

    def add_dependency(self, task_id: str, depends_on: str, dep_type: DependencyType = DependencyType.REQUIRED):
        """Add a dependency edge: task_id depends on depends_on."""
        if task_id not in self._nodes or depends_on not in self._nodes:
            self.logger.warning(f"Cannot add dependency: unknown task {task_id} or {depends_on}")
            return False

        self._adjacency[depends_on].add(task_id)
        self._reverse_adj[task_id].add(depends_on)
        self._dependency_types[(task_id, depends_on)] = dep_type
        return True

    def build_from_tasks(self, tasks: List[PlanTask]):
        """Build the graph from a list of tasks with their dependencies."""
        for task in tasks:
            self.add_task(task)
            for dep_id in task.dependencies:
                self.add_dependency(task.id, dep_id, task.dependency_type)

    def get_dependencies(self, task_id: str) -> List[str]:
        """Get all tasks that task_id depends on."""
        return list(self._reverse_adj.get(task_id, set()))

    def get_dependents(self, task_id: str) -> List[str]:
        """Get all tasks that depend on task_id."""
        return list(self._adjacency.get(task_id, set()))

    def has_cycle(self) -> bool:
        """Detect if the graph has a cycle using DFS."""
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self._adjacency.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for node in self._nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> List[str]:
        """Return tasks in topological order (dependencies first)."""
        in_degree = defaultdict(int)
        for node in self._nodes:
            if node not in in_degree:
                in_degree[node] = 0
            for dep in self._reverse_adj.get(node, set()):
                in_degree[node] += 1

        queue = deque([n for n in self._nodes if in_degree[n] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in self._adjacency.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self._nodes):
            self.logger.warning("Cycle detected in dependency graph")
            return list(self._nodes.keys())

        return result

    def get_execution_levels(self) -> List[List[str]]:
        """
        Group tasks into parallel execution levels.
        Tasks in the same level have no dependencies on each other.
        """
        in_degree = defaultdict(int)
        for node in self._nodes:
            in_degree[node] = len(self._reverse_adj.get(node, set()))

        levels = []
        remaining = set(self._nodes.keys())

        while remaining:
            level = [n for n in remaining if in_degree[n] == 0]
            if not level:
                level = list(remaining)
                self.logger.warning(f"Breaking cycle, adding remaining tasks: {level}")

            levels.append(level)

            for node in level:
                remaining.discard(node)
                for neighbor in self._adjacency.get(node, set()):
                    in_degree[neighbor] -= 1

        return levels

    def get_ready_tasks(self, completed: Set[str], failed: Set[str]) -> List[PlanTask]:
        """Get tasks whose dependencies are all satisfied."""
        ready = []
        for task_id, task in self._nodes.items():
            if task.status != TaskStatus.PENDING:
                continue
            if task_id in completed:
                continue

            deps = self._reverse_adj.get(task_id, set())
            if not deps:
                ready.append(task)
                continue

            all_satisfied = True
            for dep_id in deps:
                if dep_id in failed:
                    dep_type = self._dependency_types.get((task_id, dep_id), DependencyType.REQUIRED)
                    if dep_type == DependencyType.REQUIRED:
                        all_satisfied = False
                        break
                elif dep_id not in completed:
                    all_satisfied = False
                    break

            if all_satisfied:
                ready.append(task)

        return ready

    def get_blocked_tasks(self, completed: Set[str], failed: Set[str]) -> List[PlanTask]:
        """Get tasks that are blocked due to failed required dependencies."""
        blocked = []
        for task_id, task in self._nodes.items():
            if task.status != TaskStatus.PENDING:
                continue
            deps = self._reverse_adj.get(task_id, set())
            for dep_id in deps:
                if dep_id in failed:
                    dep_type = self._dependency_types.get((task_id, dep_id), DependencyType.REQUIRED)
                    if dep_type == DependencyType.REQUIRED:
                        blocked.append(task)
                        break
        return blocked

    def get_task_order(self) -> List[PlanTask]:
        """Get tasks in dependency-respecting order."""
        order = self.topological_sort()
        return [self._nodes[tid] for tid in order if tid in self._nodes]

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the dependency graph."""
        issues = []

        if self.has_cycle():
            issues.append("Cycle detected in dependency graph")

        for task_id, task in self._nodes.items():
            for dep_id in task.dependencies:
                if dep_id not in self._nodes:
                    issues.append(f"Task {task_id} depends on unknown task {dep_id}")

        return len(issues) == 0, issues

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        levels = self.get_execution_levels()
        max_parallel = max(len(level) for level in levels) if levels else 0

        return {
            "total_tasks": len(self._nodes),
            "total_dependencies": sum(len(deps) for deps in self._reverse_adj.values()),
            "execution_levels": len(levels),
            "max_parallel_tasks": max_parallel,
            "has_cycle": self.has_cycle(),
        }

    def clear(self):
        """Clear the graph."""
        self._adjacency.clear()
        self._reverse_adj.clear()
        self._nodes.clear()
        self._dependency_types.clear()
