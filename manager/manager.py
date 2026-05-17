import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from core.logger import Logger
from core.database import Database
from core.base_agent import BaseAgent, AgentStatus
from core.config import Config
from core.llm_provider import LLMProvider
from manager.router import Router
from manager.dispatcher import TaskDispatcher


class AIManager:
    """
    Central orchestrator for NEXUS.
    Receives commands, detects intent, routes to agents, manages task execution,
    and returns structured responses.
    """

    def __init__(self):
        self.logger = Logger().get_logger("AIManager")
        self.config = Config()
        self.db = Database()
        self.dispatcher = TaskDispatcher(max_workers=4)
        self._agents: Dict[str, BaseAgent] = {}
        self._session_id = str(uuid.uuid4())[:8]
        self._running = True
        self._chat_history: List[Dict[str, str]] = []

        self._use_llm = self.config.get("llm.use_in_agents", True)
        self._llm = None
        if self._use_llm:
            try:
                self._llm = LLMProvider(self.config)
                self.logger.info(f"LLM provider initialized: {self._llm.get_provider_name()} ({self._llm.get_model()})")
            except Exception as e:
                self.logger.warning(f"LLM not available: {e}")
                self._use_llm = False

        self.router = Router(use_llm=self._use_llm, llm_provider=self._llm)

        self.logger.info(f"AIManager initialized (session: {self._session_id})")

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the manager."""
        self._agents[agent.name] = agent
        self.logger.info(f"Agent registered: {agent.name}")

    def unregister_agent(self, agent_name: str):
        """Unregister an agent."""
        if agent_name in self._agents:
            del self._agents[agent_name]
            self.logger.info(f"Agent unregistered: {agent_name}")

    def process_command(self, command: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point. Process a user command through the full pipeline:
        1. Detect intent via Router
        2. Route to appropriate agent
        3. Execute task
        4. Save conversation to memory
        5. Return structured response
        """
        sid = session_id or self._session_id
        self.logger.info(f"Processing command (session {sid}): {command}")

        self._save_conversation(sid, "user", command)

        routing = self.router.detect_intent(command)
        agent_name = routing["agent"]
        intent = routing["intent"]

        if agent_name == "manager":
            if intent == "conversation":
                response = self._handle_conversation(command)
            else:
                response = self._handle_manager_command(intent, command, routing["params"])
        elif agent_name in self._agents:
            response = self._dispatch_to_agent(agent_name, command, routing)
        elif agent_name == "unknown" and self._use_llm and self._llm:
            response = self._handle_conversation(command)
        else:
            response = {
                "success": False,
                "response": f"No agent found for: {agent_name}",
                "agent": None,
                "intent": intent,
                "task_id": None,
            }

        self._save_conversation(sid, "assistant", response.get("response", ""))
        return response

    def _dispatch_to_agent(self, agent_name: str, command: str, routing: Dict) -> Dict[str, Any]:
        """Dispatch command to the appropriate agent."""
        agent = self._agents[agent_name]

        if not agent.is_available():
            return {
                "success": False,
                "response": f"{agent_name} is currently busy. Please wait.",
                "agent": agent_name,
                "intent": routing["intent"],
                "task_id": None,
            }

        task_id = self.dispatcher.submit_task(agent, command, routing["params"])
        start_time = datetime.now()
        result = self.dispatcher.execute_task(task_id, agent, command, routing["params"])
        duration = (datetime.now() - start_time).total_seconds()

        analytics_agent = self._agents.get("analytics_agent")
        if analytics_agent and hasattr(analytics_agent, "track_execution"):
            try:
                analytics_agent.track_execution(agent_name, command, result, duration, sid)
            except Exception as e:
                self.logger.debug(f"Analytics tracking error: {e}")

        response_text = result.get("response", result.get("error", "No response"))
        return {
            "success": result.get("success", False),
            "response": response_text,
            "agent": agent_name,
            "intent": routing["intent"],
            "task_id": task_id,
            "data": result.get("data"),
        }

    def _handle_manager_command(self, intent: str, command: str, params: Dict) -> Dict[str, Any]:
        """Handle manager-level commands (help, status, clear, etc.)."""
        if intent == "help":
            return {
                "success": True,
                "response": self._get_help_text(),
                "agent": "manager",
                "intent": "help",
                "task_id": None,
            }

        if intent == "status":
            status = self.get_agent_status()
            status_lines = [f"  {name}: {info['status']}" for name, info in status.items()]
            return {
                "success": True,
                "response": "Agent Status:\n" + "\n".join(status_lines),
                "agent": "manager",
                "intent": "status",
                "task_id": None,
                "data": status,
            }

        if intent == "clear":
            return {
                "success": True,
                "response": "Conversation cleared.",
                "agent": "manager",
                "intent": "clear",
                "task_id": None,
            }

        return {
            "success": False,
            "response": f"Unknown manager command: {command}",
            "agent": "manager",
            "intent": intent,
            "task_id": None,
        }

    def execute_workflow(self, steps: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Execute a multi-step workflow across agents.
        Each step: {"agent": "agent_name", "command": "command text"}
        """
        self.logger.info(f"Executing workflow with {len(steps)} steps")
        results = []

        for i, step in enumerate(steps):
            agent_name = step.get("agent")
            command = step.get("command", "")

            if agent_name not in self._agents:
                results.append({
                    "step": i + 1,
                    "success": False,
                    "error": f"Agent not found: {agent_name}",
                })
                continue

            agent = self._agents[agent_name]
            task_id = self.dispatcher.submit_task(agent, command, {})
            result = self.dispatcher.execute_task(task_id, agent, command, {})

            results.append({
                "step": i + 1,
                "agent": agent_name,
                "command": command,
                "success": result.get("success", False),
                "response": result.get("response", ""),
                "task_id": task_id,
            })

            if not result.get("success", False):
                self.logger.warning(f"Workflow step {i + 1} failed, continuing...")

        return results

    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents."""
        return {
            name: {
                "status": agent.status.value,
                "description": agent.description,
                "capabilities": agent.get_capabilities(),
            }
            for name, agent in self._agents.items()
        }

    def get_task_history(self, limit: int = 20) -> list:
        """Get recent task history from database."""
        rows = self.db.fetchall(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in rows]

    def get_conversation_history(self, session_id: Optional[str] = None, limit: int = 50) -> list:
        """Get conversation history."""
        if session_id:
            rows = self.db.fetchall(
                "SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit),
            )
        else:
            rows = self.db.fetchall(
                "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
        return [dict(row) for row in rows]

    def _handle_conversation(self, command: str) -> Dict[str, Any]:
        """Handle general conversation using LLM."""
        self._chat_history.append({"role": "user", "content": command})

        context_messages = [
            {"role": "system", "content": (
                "You are NEXUS, a helpful AI assistant that can control the user's computer. "
                "You have access to file operations, web search, automation, coding, and memory capabilities. "
                "Keep responses concise and helpful. If the user asks you to do something on their computer, "
                "explain that they should use specific commands like 'open [app]', 'search web for [query]', "
                "'generate code for [description]', etc."
            )}
        ]

        recent = self._chat_history[-10:]
        context_messages.extend(recent)

        if self._llm and self._llm.is_available():
            response_text = self._llm.chat(context_messages)
        else:
            response_text = (
                "I'm NEXUS, your AI assistant. I can help with:\n"
                "- File operations: 'open [app]', 'search files [query]'\n"
                "- Web research: 'search web for [query]', 'research [topic]'\n"
                "- Automation: 'take screenshot', 'run workflow [name]'\n"
                "- Coding: 'generate code for [description]', 'explain code'\n"
                "- Memory: 'remember [fact]', 'what do you remember about [topic]'\n\n"
                "Type 'help' for full command list."
            )

        self._chat_history.append({"role": "assistant", "content": response_text})

        return {
            "success": True,
            "response": response_text,
            "agent": "nexus_llm",
            "intent": "conversation",
            "task_id": None,
        }

    def _save_conversation(self, session_id: str, role: str, content: str):
        """Save a conversation turn to the database."""
        self.db.execute(
            "INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )

    def _get_help_text(self) -> str:
        return """NEXUS AI Manager - Available Commands:

File Operations:
  - "Open [application]" - Launch an application
  - "Create file [path]" - Create a new file
  - "Search files [query]" - Search for files
  - "System status" - Check CPU, RAM, disk usage

Web Operations:
  - "Search web for [query]" - Search the internet
  - "Summarize [url]" - Summarize a webpage
  - "Research [topic]" - Multi-page research

Automation:
  - "Take screenshot" - Capture screen
  - "Run workflow [name]" - Execute a preset workflow

Coding:
  - "Generate code for [description]" - Generate code
  - "Explain this code: [code]" - Explain code
  - "Git [command]" - Git operations

Memory:
  - "Remember [fact]" - Save to memory
  - "What do you remember about [topic]?" - Recall memory
  - "Set preference [key] = [value]" - Save preference

Manager:
  - "help" - Show this help
  - "status" - Show agent status
  - "clear" - Clear conversation"""

    def shutdown(self):
        """Graceful shutdown of the manager and all components."""
        self.logger.info("Shutting down AIManager...")
        self._running = False
        self.dispatcher.shutdown(wait=True)
        for name, agent in self._agents.items():
            agent.status = AgentStatus.OFFLINE
            self.logger.info(f"Agent offline: {name}")
        self.logger.info("AIManager shutdown complete")

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def agents(self) -> Dict[str, BaseAgent]:
        return self._agents.copy()

    @property
    def is_running(self) -> bool:
        return self._running
