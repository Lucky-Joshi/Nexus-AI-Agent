"""
NEXUS - Autonomous Planner Agent
Goal decomposition system that breaks high-level goals into executable tasks
using LLM-powered analysis, rule-based templates, and pattern matching.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from core.logger import Logger
from core.config import Config
from .models import Plan, PlanTask, TaskPriority, GoalType, GoalTemplate


class GoalDecomposer:
    """
    Decomposes high-level goals into structured, executable task plans.
    Uses a hybrid approach: template matching -> rule-based decomposition -> LLM fallback.
    """

    def __init__(self, llm_provider=None):
        self.logger = Logger().get_logger("GoalDecomposer")
        self.config = Config()
        self.llm = llm_provider
        self._templates: List[GoalTemplate] = []
        self._load_builtin_templates()

    def _load_builtin_templates(self):
        """Load predefined goal templates for common scenarios."""
        self._templates = [
            GoalTemplate(
                name="exam_preparation",
                description="Prepare for an exam by organizing study materials and creating a study plan",
                trigger_keywords=["exam", "study", "test", "revision", "prepare for exam", "exam prep"],
                task_blueprint=[
                    {"title": "Open study notes", "agent": "file_agent", "command": "open notes", "priority": 1},
                    {"title": "Create revision checklist", "agent": "coding_agent", "command": "generate a revision checklist in markdown", "priority": 1},
                    {"title": "Search for study resources", "agent": "web_agent", "command": "search web for study resources and exam tips", "priority": 2},
                    {"title": "Start study timer", "agent": "workflow_agent", "command": "start study mode", "priority": 2},
                    {"title": "Silence notifications", "agent": "notification_agent", "command": "enable focus mode", "priority": 0},
                    {"title": "Summarize key topics", "agent": "knowledge_agent", "command": "search knowledge base for key topics", "priority": 3},
                ],
            ),
            GoalTemplate(
                name="coding_project",
                description="Set up and start a coding project",
                trigger_keywords=["coding project", "start coding", "new project", "create project", "build app", "write code"],
                task_blueprint=[
                    {"title": "Create project directory", "agent": "file_agent", "command": "create folder for project", "priority": 0},
                    {"title": "Initialize version control", "agent": "coding_agent", "command": "initialize git repository", "priority": 0},
                    {"title": "Set up development environment", "agent": "terminal_agent", "command": "check python version and installed packages", "priority": 1},
                    {"title": "Generate project structure", "agent": "coding_agent", "command": "generate a standard python project structure", "priority": 1},
                    {"title": "Open code editor", "agent": "file_agent", "command": "open vscode", "priority": 2},
                ],
            ),
            GoalTemplate(
                name="meeting_prep",
                description="Prepare for a meeting",
                trigger_keywords=["meeting", "prepare meeting", "meeting prep", "presentation", "briefing"],
                task_blueprint=[
                    {"title": "Check calendar", "agent": "file_agent", "command": "open calendar", "priority": 0},
                    {"title": "Gather meeting notes", "agent": "knowledge_agent", "command": "search for recent meeting notes", "priority": 1},
                    {"title": "Prepare agenda", "agent": "coding_agent", "command": "generate a meeting agenda template", "priority": 1},
                    {"title": "Open presentation tools", "agent": "file_agent", "command": "open powerpoint", "priority": 2},
                    {"title": "Enable focus mode", "agent": "notification_agent", "command": "enable focus mode for meeting", "priority": 0},
                ],
            ),
            GoalTemplate(
                name="system_cleanup",
                description="Clean up and optimize the system",
                trigger_keywords=["cleanup", "clean system", "optimize", "free space", "system maintenance"],
                task_blueprint=[
                    {"title": "Check disk space", "agent": "file_agent", "command": "show disk space", "priority": 0},
                    {"title": "Scan for large files", "agent": "file_agent", "command": "search for large files", "priority": 1},
                    {"title": "Check running processes", "agent": "file_agent", "command": "show system info", "priority": 1},
                    {"title": "Clean temporary files", "agent": "terminal_agent", "command": "run disk cleanup", "priority": 2},
                    {"title": "Generate cleanup report", "agent": "coding_agent", "command": "generate a system cleanup summary", "priority": 3},
                ],
            ),
            GoalTemplate(
                name="research_task",
                description="Research a topic thoroughly",
                trigger_keywords=["research", "learn about", "investigate", "look into", "find information"],
                task_blueprint=[
                    {"title": "Search web for topic", "agent": "web_agent", "command": "search web for the topic", "priority": 0},
                    {"title": "Summarize findings", "agent": "web_agent", "command": "summarize the search results", "priority": 1},
                    {"title": "Check knowledge base", "agent": "knowledge_agent", "command": "search knowledge base for related info", "priority": 1},
                    {"title": "Save research notes", "agent": "memory_agent", "command": "save the research findings", "priority": 2},
                    {"title": "Generate report", "agent": "coding_agent", "command": "generate a research summary document", "priority": 3},
                ],
            ),
            GoalTemplate(
                name="writing_session",
                description="Set up an optimized writing environment",
                trigger_keywords=["write", "writing", "draft", "essay", "article", "blog post", "document"],
                task_blueprint=[
                    {"title": "Open writing application", "agent": "file_agent", "command": "open notepad", "priority": 0},
                    {"title": "Enable focus mode", "agent": "notification_agent", "command": "enable focus mode", "priority": 0},
                    {"title": "Start writing timer", "agent": "workflow_agent", "command": "start deep work mode", "priority": 1},
                    {"title": "Gather reference materials", "agent": "knowledge_agent", "command": "search for related reference materials", "priority": 2},
                ],
            ),
        ]
        self.logger.info(f"Loaded {len(self._templates)} goal templates")

    def decompose(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Plan:
        """
        Decompose a goal into a structured plan.
        Strategy: template match -> rule-based -> LLM fallback.
        """
        context = context or {}

        template = self._find_matching_template(goal)
        if template:
            self.logger.info(f"Matched template: {template.name}")
            plan = self._build_plan_from_template(goal, template, context)
            template.usage_count += 1
            return plan

        plan = self._rule_based_decomposition(goal, context)
        if plan.tasks:
            self.logger.info(f"Rule-based decomposition created {len(plan.tasks)} tasks")
            return plan

        if self.llm and self.llm.is_available():
            plan = self._llm_decomposition(goal, context)
            if plan.tasks:
                self.logger.info(f"LLM decomposition created {len(plan.tasks)} tasks")
                return plan

        self.logger.warning(f"Could not decompose goal: {goal}")
        plan = Plan(goal=goal, description="Could not decompose into tasks", goal_type=GoalType.SIMPLE)
        plan.add_task(PlanTask(
            title=f"Execute: {goal}",
            description=goal,
            command=goal,
            priority=TaskPriority.NORMAL,
        ))
        return plan

    def _find_matching_template(self, goal: str) -> Optional[GoalTemplate]:
        """Find the best matching goal template."""
        goal_lower = goal.lower()
        best_match = None
        best_score = 0

        for template in self._templates:
            if not template.is_active:
                continue
            score = sum(1 for kw in template.trigger_keywords if kw in goal_lower)
            if score > best_score:
                best_score = score
                best_match = template

        return best_match if best_score > 0 else None

    def _build_plan_from_template(self, goal: str, template: GoalTemplate, context: Dict[str, Any]) -> Plan:
        """Build a plan from a matched template, customizing with context."""
        plan = Plan(
            goal=goal,
            description=template.description,
            goal_type=GoalType.MULTI_STEP,
            context=context,
        )

        for i, bp in enumerate(template.task_blueprint):
            task = PlanTask(
                title=self._substitute_variables(bp.get("title", ""), context),
                description=goal,
                agent_name=bp.get("agent", ""),
                command=self._substitute_variables(bp.get("command", ""), context),
                priority=TaskPriority(bp.get("priority", 2)),
                params=bp.get("params", {}),
                dependencies=bp.get("dependencies", []),
                max_retries=bp.get("max_retries", 1),
            )

            if i > 0:
                prev_task = plan.tasks[-1]
                if bp.get("depends_on_previous", True):
                    task.dependencies.append(prev_task.id)

            plan.add_task(task)

        return plan

    def _rule_based_decomposition(self, goal: str, context: Dict[str, Any]) -> Plan:
        """Decompose using rule-based heuristics."""
        goal_lower = goal.lower()
        plan = Plan(goal=goal, goal_type=GoalType.MULTI_STEP, context=context)

        actions = self._extract_actions(goal_lower)

        if not actions:
            return plan

        agent_map = self._map_actions_to_agents(actions, goal_lower)

        for i, (action, agent_name, command) in enumerate(agent_map):
            task = PlanTask(
                title=action.title(),
                description=f"Action: {action}",
                agent_name=agent_name,
                command=command,
                priority=self._infer_priority(action, goal_lower),
            )

            if i > 0 and self._needs_sequential(action, goal_lower):
                task.dependencies.append(plan.tasks[-1].id)

            plan.add_task(task)

        return plan

    def _extract_actions(self, goal: str) -> List[str]:
        """Extract actionable verbs/phrases from the goal."""
        action_patterns = [
            (r'(?:open|launch|start)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "open"),
            (r'(?:create|make|generate|build)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "create"),
            (r'(?:search|find|look\s+for|research)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "search"),
            (r'(?:save|store|remember)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "save"),
            (r'(?:send|email|message)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "send"),
            (r'(?:set|enable|disable|turn\s+on|turn\s+off)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "configure"),
            (r'(?:run|execute|perform)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "execute"),
            (r'(?:check|verify|monitor|show)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "check"),
            (r'(?:clean|clear|delete|remove)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "cleanup"),
            (r'(?:summarize|analyze|review)\s+([\w\s]+?)(?:\s+(?:and|then|also|to)|$)', "analyze"),
        ]

        actions = []
        for pattern, action_type in action_patterns:
            matches = re.findall(pattern, goal)
            for match in matches:
                actions.append(f"{action_type}: {match.strip()}")

        if not actions:
            actions = [goal]

        return actions

    def _map_actions_to_agents(self, actions: List[str], goal: str) -> List[Tuple[str, str, str]]:
        """Map extracted actions to appropriate agents."""
        mappings = []
        goal_lower = goal.lower()

        for action in actions:
            action_lower = action.lower()
            agent, command = self._infer_agent_and_command(action_lower, goal_lower)
            mappings.append((action, agent, command))

        return mappings

    def _infer_agent_and_command(self, action: str, goal: str) -> Tuple[str, str]:
        """Infer which agent should handle an action and what command to use."""
        file_keywords = ["open", "launch", "create folder", "create file", "delete file",
                         "rename", "search files", "disk space", "system info", "downloads"]
        web_keywords = ["search web", "research", "find information", "scrape", "summarize url",
                        "look up", "browse"]
        coding_keywords = ["generate code", "write code", "debug", "explain code", "git",
                           "create project", "project structure"]
        memory_keywords = ["save", "remember", "recall", "store", "preference"]
        notification_keywords = ["notification", "focus mode", "silent", "mute", "reminder", "alert"]
        workflow_keywords = ["workflow", "mode", "timer", "pomodoro", "study mode", "deep work"]
        knowledge_keywords = ["knowledge", "search knowledge", "knowledge base", "document"]
        terminal_keywords = ["run command", "execute", "terminal", "script", "batch", "powershell"]
        vision_keywords = ["screenshot", "screen", "capture", "ocr", "image"]
        automation_keywords = ["automate", "click", "type", "mouse", "keyboard"]

        for keyword in file_keywords:
            if keyword in action:
                return "file_agent", action
        for keyword in web_keywords:
            if keyword in action:
                return "web_agent", action
        for keyword in coding_keywords:
            if keyword in action:
                return "coding_agent", action
        for keyword in memory_keywords:
            if keyword in action:
                return "memory_agent", action
        for keyword in notification_keywords:
            if keyword in action:
                return "notification_agent", action
        for keyword in workflow_keywords:
            if keyword in action:
                return "workflow_agent", action
        for keyword in knowledge_keywords:
            if keyword in action:
                return "knowledge_agent", action
        for keyword in terminal_keywords:
            if keyword in action:
                return "terminal_agent", action
        for keyword in vision_keywords:
            if keyword in action:
                return "vision_agent", action
        for keyword in automation_keywords:
            if keyword in action:
                return "automation_agent", action

        return "file_agent", action

    def _infer_priority(self, action: str, goal: str) -> TaskPriority:
        """Infer task priority from action type."""
        high_keywords = ["open", "launch", "enable focus", "silence", "mute", "setup"]
        low_keywords = ["summarize", "report", "generate summary", "analyze"]

        for kw in high_keywords:
            if kw in action.lower():
                return TaskPriority.HIGH
        for kw in low_keywords:
            if kw in action.lower():
                return TaskPriority.LOW

        return TaskPriority.NORMAL

    def _needs_sequential(self, action: str, goal: str) -> bool:
        """Determine if an action should depend on the previous one."""
        sequential_indicators = ["then", "after", "next", "once", "when", "and then"]
        return any(ind in goal for ind in sequential_indicators)

    def _llm_decomposition(self, goal: str, context: Dict[str, Any]) -> Plan:
        """Use LLM to decompose a complex goal."""
        system_prompt = (
            "You are a planning assistant for NEXUS, an AI desktop ecosystem. "
            "Break down the user's goal into a sequence of executable tasks. "
            "Each task should be assigned to one of these agents: "
            "file_agent, web_agent, coding_agent, memory_agent, notification_agent, "
            "workflow_agent, knowledge_agent, terminal_agent, vision_agent, automation_agent. "
            "Return ONLY a JSON array of tasks with: title, agent, command, priority (0-4), "
            "and dependencies (list of task indices, empty for first task). "
            "Do not include any explanation."
        )

        user_prompt = f"Goal: {goal}\nContext: {json.dumps(context)}\n\nReturn tasks as JSON array."

        try:
            response = self.llm.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ])

            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            tasks_data = json.loads(response)
            plan = Plan(goal=goal, goal_type=GoalType.MULTI_STEP, context=context)

            task_ids = []
            for task_data in tasks_data:
                task = PlanTask(
                    title=task_data.get("title", ""),
                    description=goal,
                    agent_name=task_data.get("agent", "file_agent"),
                    command=task_data.get("command", ""),
                    priority=TaskPriority(min(task_data.get("priority", 2), 4)),
                    dependencies=[task_ids[i] for i in task_data.get("dependencies", []) if i < len(task_ids)],
                )
                plan.add_task(task)
                task_ids.append(task.id)

            return plan

        except Exception as e:
            self.logger.error(f"LLM decomposition failed: {e}")
            return Plan(goal=goal, goal_type=GoalType.SIMPLE)

    def _substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Replace {{variable}} placeholders with context values."""
        for key, value in context.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        return text

    def add_template(self, template: GoalTemplate):
        """Add a custom goal template."""
        self._templates.append(template)
        self.logger.info(f"Added goal template: {template.name}")

    def get_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates."""
        return [t.to_dict() for t in self._templates]
