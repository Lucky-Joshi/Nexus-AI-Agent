"""
Workflow Chain Agent
Multi-agent task chaining and autonomous workflow execution.
Chains multiple agents, passes outputs between them, manages dependencies,
and supports conditional logic workflows.
"""

import json
import uuid
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import (
    ChainStep, ChainDefinition, ChainExecution, ExecutionContext,
    StepCondition, ConditionType, ActionType, FailureStrategy,
    StepStatus, ChainStatus, ChainTemplate,
)
from .storage import ChainStorage
from .services import ChainEngine, DependencyGraph, ConditionEvaluator, RecoveryManager


class WorkflowChainAgent(BaseAgent):
    """Orchestrates multi-agent workflow chains with dependency management."""

    def __init__(self):
        super().__init__("workflow_chain_agent", "Multi-agent task chaining and autonomous workflow execution")

        self.logger = Logger().get_logger("WorkflowChainAgent")
        self.config = Config()

        self._storage = ChainStorage()
        self._engine = ChainEngine(self._storage)
        self._ai_manager = None

        self._active_executions: Dict[str, ChainExecution] = {}
        self._templates: Dict[str, ChainTemplate] = {}

        self._load_builtin_templates()
        self.logger.info("WorkflowChainAgent initialized")

    def set_ai_manager(self, manager):
        self._ai_manager = manager
        self._engine.set_agent_executor(self._execute_agent)

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["run chain", "execute chain", "start chain", "run workflow", "execute workflow"]):
                return self._handle_run_chain(command)
            elif self._matches(cmd, ["run async", "execute async", "start async"]):
                return self._handle_run_async(command)
            elif self._matches(cmd, ["cancel chain", "stop chain", "cancel workflow", "stop workflow"]):
                return self._handle_cancel(command)
            elif self._matches(cmd, ["chain status", "workflow status", "execution status", "chain progress"]):
                return self._handle_status(command)
            elif self._matches(cmd, ["list chains", "show chains", "all chains", "available chains"]):
                return self._handle_list_chains(command)
            elif self._matches(cmd, ["chain info", "workflow info", "chain details", "show chain"]):
                return self._handle_chain_info(command)
            elif self._matches(cmd, ["create chain", "new chain", "add chain", "define chain"]):
                return self._handle_create_chain(command)
            elif self._matches(cmd, ["delete chain", "remove chain"]):
                return self._handle_delete_chain(command)
            elif self._matches(cmd, ["list templates", "show templates", "available templates", "template list"]):
                return self._handle_list_templates(command)
            elif self._matches(cmd, ["run template", "execute template", "use template"]):
                return self._handle_run_template(command)
            elif self._matches(cmd, ["execution history", "chain history", "run history", "past executions"]):
                return self._handle_history(command)
            elif self._matches(cmd, ["chain stats", "workflow stats", "statistics"]):
                return self._handle_stats(command)
            elif self._matches(cmd, ["resume chain", "resume execution", "continue chain"]):
                return self._handle_resume(command)
            elif self._matches(cmd, ["prepare coding workspace", "setup coding", "coding setup"]):
                return self._handle_preset_coding_workspace(command)
            elif self._matches(cmd, ["research and summarize", "research topic", "research and report"]):
                return self._handle_preset_research(command)
            elif self._matches(cmd, ["analyze system", "system analysis", "full system scan"]):
                return self._handle_preset_system_analysis(command)
            elif self._matches(cmd, ["workflow chain", "chain agent", "chain help"]):
                return self._handle_help(command)
            else:
                return self._handle_run_chain(command)
        except Exception as e:
            return {"success": False, "response": f"Error: {e}", "error": str(e)}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "run_chain",
            "run_async",
            "cancel_chain",
            "chain_status",
            "list_chains",
            "chain_info",
            "create_chain",
            "delete_chain",
            "list_templates",
            "run_template",
            "execution_history",
            "chain_stats",
            "resume_chain",
            "preset_coding_workspace",
            "preset_research",
            "preset_system_analysis",
        ]

    def run_chain(self, chain: ChainDefinition,
                  variables: Optional[Dict[str, Any]] = None,
                  async_mode: bool = False) -> ChainExecution:
        execution = self._engine.execute_chain(chain, variables, async_mode)
        if not async_mode:
            self._active_executions[execution.id] = execution
        return execution

    def cancel_chain(self, execution_id: str) -> bool:
        self._engine.cancel_execution(execution_id)
        if execution_id in self._active_executions:
            exec_obj = self._active_executions[execution_id]
            exec_obj.mark_cancelled()
            self._storage.save_execution(exec_obj.to_dict())
        return True

    def _execute_agent(self, agent_name: str, command: str) -> Dict[str, Any]:
        if self._ai_manager and agent_name in self._ai_manager.agents:
            agent = self._ai_manager.agents[agent_name]
            try:
                result = agent.execute(command)
                return {
                    "success": result.get("success", False),
                    "response": result.get("response", ""),
                    "data": result.get("data"),
                }
            except Exception as e:
                return {"success": False, "response": f"Agent error: {e}"}
        return {"success": False, "response": f"Agent '{agent_name}' not found"}

    def _load_builtin_templates(self):
        templates = self._get_builtin_templates()
        for t in templates:
            self._templates[t.id] = t
            self._storage.save_template(t.to_dict())
        self.logger.info(f"Loaded {len(templates)} builtin chain templates")

    def _get_builtin_templates(self) -> List[ChainTemplate]:
        return [
            ChainTemplate(
                id="coding_workspace",
                name="Prepare Coding Workspace",
                description="Open VS Code, GitHub, terminal, and load recent project",
                category="development",
                tags=["coding", "workspace", "setup", "development"],
                chain=ChainDefinition(
                    id="coding_workspace",
                    name="Prepare Coding Workspace",
                    description="Set up a complete coding environment",
                    category="development",
                    tags=["coding", "workspace"],
                    steps=[
                        ChainStep(id="open_vscode", name="Open VS Code", agent="file_agent",
                                  command="open vscode", output_variable="vscode_status"),
                        ChainStep(id="open_github", name="Open GitHub", agent="file_agent",
                                  command="open github", depends_on=["open_vscode"]),
                        ChainStep(id="open_terminal", name="Open Terminal", agent="terminal_agent",
                                  command="new session", depends_on=["open_vscode"]),
                        ChainStep(id="load_project", name="Load Recent Project", agent="file_agent",
                                  command="open recent project", depends_on=["open_terminal"]),
                    ],
                ),
            ),
            ChainTemplate(
                id="research_summarize",
                name="Research and Summarize",
                description="Search web, analyze results, and generate summary",
                category="research",
                tags=["research", "web", "summarize", "analysis"],
                chain=ChainDefinition(
                    id="research_summarize",
                    name="Research and Summarize",
                    description="Multi-step research workflow",
                    category="research",
                    steps=[
                        ChainStep(id="search", name="Web Search", agent="web_agent",
                                  command="search web for {{topic}}", output_variable="search_results"),
                        ChainStep(id="analyze", name="Analyze Results", agent="knowledge_agent",
                                  command="analyze {{search.output}}", depends_on=["search"],
                                  output_variable="analysis"),
                        ChainStep(id="summarize", name="Generate Summary", agent="coding_agent",
                                  command="summarize: {{analyze.output}}", depends_on=["analyze"],
                                  output_variable="final_summary"),
                    ],
                ),
            ),
            ChainTemplate(
                id="system_analysis",
                name="Full System Analysis",
                description="Check system health, scan processes, and generate security report",
                category="security",
                tags=["security", "system", "analysis", "health"],
                chain=ChainDefinition(
                    id="system_analysis",
                    name="Full System Analysis",
                    description="Comprehensive system security analysis",
                    category="security",
                    steps=[
                        ChainStep(id="health", name="System Health", agent="security_agent",
                                  command="system health", output_variable="health_report"),
                        ChainStep(id="scan", name="Process Scan", agent="security_agent",
                                  command="process scan", depends_on=["health"],
                                  output_variable="scan_results"),
                        ChainStep(id="stats", name="Security Stats", agent="security_agent",
                                  command="stats", depends_on=["health"]),
                        ChainStep(id="report", name="Generate Report", agent="coding_agent",
                                  command="generate report from {{health.output}} and {{scan.output}}",
                                  depends_on=["scan", "stats"], output_variable="final_report"),
                    ],
                ),
            ),
            ChainTemplate(
                id="deep_clean",
                name="System Cleanup",
                description="Check disk, clean temp files, and optimize",
                category="maintenance",
                tags=["cleanup", "maintenance", "disk", "optimization"],
                chain=ChainDefinition(
                    id="deep_clean",
                    name="System Cleanup",
                    description="Automated system cleanup workflow",
                    category="maintenance",
                    steps=[
                        ChainStep(id="check_disk", name="Check Disk Usage", agent="file_agent",
                                  command="disk usage", output_variable="disk_info"),
                        ChainStep(id="check_temp", name="Check Temp Files", agent="file_agent",
                                  command="check temp files", output_variable="temp_info"),
                        ChainStep(id="clean", name="Clean Temp Files", agent="file_agent",
                                  command="clean temp files", depends_on=["check_temp"],
                                  condition=StepCondition(ConditionType.OUTPUT_CONTAINS,
                                                          target_step="check_temp", pattern="temp")),
                        ChainStep(id="verify", name="Verify Cleanup", agent="file_agent",
                                  command="disk usage", depends_on=["clean"]),
                    ],
                ),
            ),
        ]

    def _handle_run_chain(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["run chain", "execute chain", "start chain", "run workflow", "execute workflow"])
        if not content:
            return self._handle_help(command)

        chain = self._storage.get_chain_by_name(content)
        if not chain:
            for tid, template in self._templates.items():
                if content.lower() in template.name.lower() or content.lower() in template.id.lower():
                    chain = template.chain
                    break

        if not chain:
            return {
                "success": False,
                "response": f"Chain '{content}' not found. Use 'list chains' to see available chains.",
            }

        chain_def = ChainDefinition.from_dict({**chain, "steps": chain.get("steps", [])})
        execution = self._engine.execute_chain(chain_def)
        self._active_executions[execution.id] = execution

        summary = self._engine.get_chain_summary(execution)
        return {"success": True, "response": summary, "data": execution.to_dict()}

    def _handle_run_async(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["run async", "execute async", "start async"])
        if not content:
            return {"success": False, "response": "Please specify a chain name. Example: 'run async research_summarize'"}

        chain = self._storage.get_chain_by_name(content)
        if not chain:
            return {"success": False, "response": f"Chain '{content}' not found."}

        chain_def = ChainDefinition.from_dict({**chain, "steps": chain.get("steps", [])})
        execution = self._engine.execute_chain(chain_def, async_mode=True)
        self._active_executions[execution.id] = execution

        return {
            "success": True,
            "response": f"Chain '{content}' started asynchronously. Execution ID: {execution.id}\nUse 'chain status {execution.id}' to check progress.",
            "data": {"execution_id": execution.id},
        }

    def _handle_cancel(self, command: str) -> Dict[str, Any]:
        exec_id = self._extract_id(command)
        if not exec_id:
            running = self._engine.get_running_executions()
            if running:
                exec_id = running[0]
            else:
                return {"success": False, "response": "No running chains to cancel."}

        self.cancel_chain(exec_id)
        return {"success": True, "response": f"Chain execution {exec_id} cancelled."}

    def _handle_status(self, command: str) -> Dict[str, Any]:
        exec_id = self._extract_id(command)
        if exec_id and exec_id in self._active_executions:
            execution = self._active_executions[exec_id]
            stored = self._storage.get_execution(exec_id)
            if stored:
                execution = ChainExecution.from_dict(stored)
            summary = self._engine.get_chain_summary(execution)
            return {"success": True, "response": summary, "data": execution.to_dict()}

        running = self._engine.get_running_executions()
        if running:
            lines = [f"Running Executions ({len(running)}):\n"]
            for eid in running:
                exec_obj = self._active_executions.get(eid)
                if exec_obj:
                    lines.append(f"  {eid}: {exec_obj.chain_name} - {exec_obj.completed_steps}/{exec_obj.total_steps} steps")
            return {"success": True, "response": "\n".join(lines)}

        return {"success": True, "response": "No active chain executions."}

    def _handle_list_chains(self, command: str) -> Dict[str, Any]:
        chains = self._storage.get_chains()
        templates = list(self._templates.values())

        lines = ["Available Workflow Chains:\n"]

        if chains:
            lines.append("Saved Chains:")
            for c in chains:
                step_count = len(c.get("steps", []))
                lines.append(f"  {c['name']} ({step_count} steps, {c['category']})")
                if c.get("description"):
                    lines.append(f"    {c['description']}")
            lines.append("")

        if templates:
            lines.append("Templates:")
            for t in templates:
                step_count = len(t.chain.steps) if t.chain else 0
                lines.append(f"  {t.name} ({step_count} steps, {t.category})")
                lines.append(f"    {t.description}")
            lines.append("")

        if not chains and not templates:
            lines.append("No chains or templates available. Use 'create chain' to define one.")

        return {"success": True, "response": "\n".join(lines)}

    def _handle_chain_info(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["chain info", "workflow info", "chain details", "show chain"])
        if not content:
            return {"success": False, "response": "Please specify a chain name."}

        chain = self._storage.get_chain_by_name(content)
        if not chain:
            for t in self._templates.values():
                if content.lower() in t.name.lower() or content.lower() in t.id.lower():
                    chain = t.chain.to_dict() if t.chain else None
                    break

        if not chain:
            return {"success": False, "response": f"Chain '{content}' not found."}

        steps = chain.get("steps", [])
        lines = [
            f"Chain: {chain['name']}",
            f"Description: {chain.get('description', 'N/A')}",
            f"Category: {chain.get('category', 'general')}",
            f"Steps: {len(steps)}",
            f"Timeout: {chain.get('timeout', 300)}s",
            f"On Failure: {chain.get('on_failure', 'abort')}",
            "",
            "Steps:",
        ]

        for i, step in enumerate(steps, 1):
            deps = f" (depends on: {', '.join(step.get('depends_on', []))})" if step.get("depends_on") else ""
            lines.append(f"  {i}. {step.get('name', step['id'])} -> {step.get('agent', '?')}: {step.get('command', '')[:60]}{deps}")

        return {"success": True, "response": "\n".join(lines), "data": chain}

    def _handle_create_chain(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["create chain", "new chain", "add chain", "define chain"])
        if not content:
            return {
                "success": False,
                "response": "Usage: 'create chain <name> with steps: step1 -> agent1: command1, step2 -> agent2: command2'",
            }

        try:
            chain_id = str(uuid.uuid4())[:8]
            steps = self._parse_chain_steps(content)
            if not steps:
                return {"success": False, "response": "Could not parse chain steps. Use format: 'step_name -> agent: command'"}

            chain_def = ChainDefinition(
                id=chain_id,
                name=steps[0].get("chain_name", content.split(" with ")[0].strip()),
                description=f"Custom chain: {content[:80]}",
                steps=[ChainStep(**s) for s in steps[0].get("steps", [])],
            )
            self._storage.save_chain(chain_def.to_dict())

            return {
                "success": True,
                "response": f"Chain '{chain_def.name}' created with {len(chain_def.steps)} steps (ID: {chain_id})",
                "data": chain_def.to_dict(),
            }
        except Exception as e:
            return {"success": False, "response": f"Failed to create chain: {e}"}

    def _handle_delete_chain(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["delete chain", "remove chain"])
        if not content:
            return {"success": False, "response": "Please specify a chain name or ID."}

        chain = self._storage.get_chain_by_name(content)
        if chain:
            self._storage.delete_chain(chain["id"])
            return {"success": True, "response": f"Chain '{content}' deleted."}

        return {"success": False, "response": f"Chain '{content}' not found."}

    def _handle_list_templates(self, command: str) -> Dict[str, Any]:
        templates = self._storage.get_templates()
        if not templates:
            templates = [t.to_dict() for t in self._templates.values()]

        lines = ["Workflow Chain Templates:\n"]
        for t in templates:
            lines.append(f"  {t['name']} ({t['category']})")
            lines.append(f"    {t['description']}")
            lines.append(f"    Tags: {', '.join(t.get('tags', []))}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines)}

    def _handle_run_template(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["run template", "execute template", "use template"])
        if not content:
            return {"success": False, "response": "Please specify a template name."}

        template = None
        for t in self._templates.values():
            if content.lower() in t.name.lower() or content.lower() in t.id.lower():
                template = t
                break

        if not template:
            stored = self._storage.get_template(content)
            if stored:
                template = ChainTemplate(
                    id=stored["id"],
                    name=stored["name"],
                    description=stored["description"],
                    category=stored["category"],
                    tags=stored.get("tags", []),
                    initial_variables=stored.get("initial_variables", {}),
                    chain=ChainDefinition.from_dict(stored.get("definition", {})) if stored.get("definition") else None,
                )

        if not template or not template.chain:
            return {"success": False, "response": f"Template '{content}' not found."}

        execution = self._engine.execute_chain(template.chain, template.initial_variables)
        self._active_executions[execution.id] = execution

        summary = self._engine.get_chain_summary(execution)
        return {"success": True, "response": summary, "data": execution.to_dict()}

    def _handle_history(self, command: str) -> Dict[str, Any]:
        executions = self._storage.get_executions(limit=20)

        if not executions:
            return {"success": True, "response": "No execution history."}

        lines = [f"Execution History ({len(executions)}):\n"]
        for e in executions[:10]:
            status = e["status"].upper()
            lines.append(f"  [{status}] {e['chain_name']} (ID: {e['id']})")
            lines.append(f"    {e['completed_steps']}/{e['total_steps']} steps, {e['duration']:.1f}s")
            lines.append(f"    Started: {e['started_at'][:19]}")
            if e.get("error"):
                lines.append(f"    Error: {e['error'][:80]}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": {"executions": executions}}

    def _handle_stats(self, command: str) -> Dict[str, Any]:
        stats = self._storage.get_stats()

        lines = [
            "Workflow Chain Statistics:",
            f"Total Chains: {stats['total_chains']}",
            f"Total Executions: {stats['total_executions']}",
            f"Completed: {stats['completed_executions']}",
            f"Failed: {stats['failed_executions']}",
            f"Running: {stats['running_executions']}",
            f"Templates: {stats['total_templates']}",
            f"Avg Duration: {stats['avg_duration_seconds']}s",
            f"Success Rate: {stats['success_rate']}%",
        ]

        return {"success": True, "response": "\n".join(lines), "data": stats}

    def _handle_resume(self, command: str) -> Dict[str, Any]:
        exec_id = self._extract_id(command)
        if not exec_id:
            return {"success": False, "response": "Please provide an execution ID to resume."}

        checkpoint = self._engine._recovery.get_recovery_point(exec_id)
        if not checkpoint:
            return {"success": False, "response": f"No recovery point found for execution {exec_id}."}

        stored = self._storage.get_execution(exec_id)
        if not stored:
            return {"success": False, "response": f"Execution {exec_id} not found."}

        execution = ChainExecution.from_dict(stored)
        success = self._recovery.restore_from_checkpoint(execution, checkpoint)
        if not success:
            return {"success": False, "response": "Failed to restore from checkpoint."}

        chain = self._storage.get_chain(execution.chain_id)
        if not chain:
            return {"success": False, "response": "Chain definition not found for execution."}

        chain_def = ChainDefinition.from_dict({**chain, "steps": chain.get("steps", [])})
        execution = self._engine.execute_chain(chain_def)
        self._active_executions[execution.id] = execution

        summary = self._engine.get_chain_summary(execution)
        return {"success": True, "response": f"Resumed from checkpoint:\n{summary}", "data": execution.to_dict()}

    def _handle_preset_coding_workspace(self, command: str) -> Dict[str, Any]:
        template = self._templates.get("coding_workspace")
        if not template or not template.chain:
            return {"success": False, "response": "Coding workspace template not available."}

        execution = self._engine.execute_chain(template.chain)
        self._active_executions[execution.id] = execution
        summary = self._engine.get_chain_summary(execution)
        return {"success": True, "response": f"Coding Workspace Setup:\n{summary}", "data": execution.to_dict()}

    def _handle_preset_research(self, command: str) -> Dict[str, Any]:
        topic = self._extract_content(command, ["research and summarize", "research topic", "research and report"])
        if not topic:
            topic = "latest technology trends"

        template = self._templates.get("research_summarize")
        if not template or not template.chain:
            return {"success": False, "response": "Research template not available."}

        variables = {"topic": topic}
        execution = self._engine.execute_chain(template.chain, variables)
        self._active_executions[execution.id] = execution
        summary = self._engine.get_chain_summary(execution)
        return {"success": True, "response": f"Research: {topic}\n{summary}", "data": execution.to_dict()}

    def _handle_preset_system_analysis(self, command: str) -> Dict[str, Any]:
        template = self._templates.get("system_analysis")
        if not template or not template.chain:
            return {"success": False, "response": "System analysis template not available."}

        execution = self._engine.execute_chain(template.chain)
        self._active_executions[execution.id] = execution
        summary = self._engine.get_chain_summary(execution)
        return {"success": True, "response": f"System Analysis:\n{summary}", "data": execution.to_dict()}

    def _handle_help(self, command: str) -> Dict[str, Any]:
        lines = [
            "Workflow Chain Agent Commands:",
            "",
            "Execution:",
            "  run chain <name>          - Execute a workflow chain",
            "  run async <name>          - Execute chain asynchronously",
            "  cancel chain [id]         - Cancel a running chain",
            "  chain status [id]         - Check chain execution status",
            "  resume chain <id>         - Resume from checkpoint",
            "",
            "Management:",
            "  list chains               - List available chains",
            "  chain info <name>         - Show chain details",
            "  create chain <definition> - Create a new chain",
            "  delete chain <name>       - Delete a chain",
            "",
            "Templates:",
            "  list templates            - List chain templates",
            "  run template <name>       - Execute a template",
            "",
            "Presets:",
            "  prepare coding workspace  - Open VS Code, GitHub, terminal",
            "  research and summarize    - Search, analyze, summarize topic",
            "  analyze system            - Health check, scan, security report",
            "",
            "History & Stats:",
            "  execution history         - View past executions",
            "  chain stats               - Show statistics",
            "",
            "Chain Definition Format:",
            "  'create chain MyChain with steps:",
            "   step1 -> file_agent: open vscode,",
            "   step2 -> terminal_agent: new session (depends on: step1),",
            "   step3 -> web_agent: search web for {{step2.output}} (depends on: step2)'",
        ]

        return {"success": True, "response": "\n".join(lines)}

    @staticmethod
    def _parse_chain_steps(content: str) -> List[Dict[str, Any]]:
        steps = []
        parts = content.split(",")
        for i, part in enumerate(parts):
            part = part.strip()
            if "->" in part:
                name, rest = part.split("->", 1)
                name = name.strip()
                rest = rest.strip()

                if ":" in rest:
                    agent, command = rest.split(":", 1)
                    agent = agent.strip()
                    command = command.strip()
                else:
                    agent = "file_agent"
                    command = rest

                depends_on = []
                if "(depends on:" in command:
                    match = command.split("(depends on:")[1].split(")")[0]
                    depends_on = [d.strip() for d in match.split(",")]
                    command = command.split("(depends on:")[0].strip()

                step_id = f"step_{i + 1}"
                steps.append({
                    "id": step_id,
                    "name": name,
                    "agent": agent,
                    "command": command,
                    "depends_on": depends_on,
                })

        if steps:
            return [{"chain_name": content.split(" with ")[0].strip(), "steps": steps}]
        return []

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: list) -> str:
        lower = command.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                return command[len(prefix):].strip()
            idx = lower.find(prefix)
            if idx >= 0:
                return command[idx + len(prefix):].strip()
        return command.strip()

    @staticmethod
    def _extract_id(command: str) -> str:
        import re
        match = re.search(r'\b([a-f0-9]{8})\b', command)
        return match.group(1) if match else ""
