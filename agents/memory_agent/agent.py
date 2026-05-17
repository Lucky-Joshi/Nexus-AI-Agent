"""
Memory Agent for NEXUS.
Thin orchestrator that delegates to specialized service classes:
- MemoryService: episodic/semantic/procedural memory
- PreferenceService: user preferences
- WorkflowService: saved workflows
- ContextManager: conversation context
"""

import re
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import MemoryType, MemoryCategory, Workflow
from .services import MemoryService, PreferenceService, WorkflowService, ContextManager
from .storage import SQLiteStorage, JSONStorage, VectorStorage


class MemoryAgent(BaseAgent):
    """
    Persistent memory agent for NEXUS.
    Handles memory storage/retrieval, preferences, workflows, and context management.
    """

    def __init__(self):
        super().__init__("memory_agent", "Persistent memory, preferences, workflows, and context management")
        self.logger = Logger().get_logger("MemoryAgent")
        self.config = Config()

        sqlite = SQLiteStorage()
        json_store = JSONStorage()
        vector = VectorStorage()

        self._memory_service = MemoryService(sqlite_storage=sqlite, vector_storage=vector)
        self._preference_service = PreferenceService(json_storage=json_store, sqlite_storage=sqlite)
        self._workflow_service = WorkflowService(sqlite_storage=sqlite, json_storage=json_store)
        self._context_manager = ContextManager(
            max_size=self.config.get("memory.max_context_length", 50),
        )

        self.logger.info("MemoryAgent initialized with all services")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["what do you know", "what do you remember", "recall", "retrieve", "search memory"]):
                return self._handle_recall(command)

            elif self._matches(cmd, ["save workflow", "create workflow"]):
                return self._handle_save_workflow(command)

            elif self._matches(cmd, ["load workflow", "run workflow", "execute workflow"]):
                return self._handle_load_workflow(command)

            elif self._matches(cmd, ["list workflows", "show workflows", "all workflows"]):
                return self._handle_list_workflows()

            elif self._matches(cmd, ["list preferences", "show preferences", "all preferences"]):
                return self._handle_list_preferences()

            elif self._matches(cmd, ["list memories", "show memories", "all memories"]):
                return self._handle_list_memories(command)

            elif self._matches(cmd, ["memory", "stats", "status"]):
                return self._handle_stats()

            elif self._matches(cmd, ["clear", "delete", "forget"]) and self._matches(cmd, ["memory", "memories", "all", "context", "preferences", "workflows"]):
                return self._handle_clear_memory(command)

            elif self._matches(cmd, ["delete memory", "forget memory", "remove memory"]):
                return self._handle_delete_memory(command)

            elif self._matches(cmd, ["preference", "setting"]) and self._matches(cmd, ["set", "save", "change"]):
                return self._handle_set_preference(command)

            elif self._matches(cmd, ["preference", "setting"]) and self._matches(cmd, ["get", "show", "what is"]):
                return self._handle_get_preference(command)

            elif self._matches(cmd, ["context", "history", "recent", "conversation"]):
                return self._handle_context(command)

            elif self._matches(cmd, ["remember", "save", "store", "note"]):
                return self._handle_remember(command)

            else:
                return self._handle_remember(command)

        except Exception as e:
            self.logger.error(f"MemoryAgent error: {e}")
            return {
                "success": False,
                "response": f"Memory error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "remember",
            "recall",
            "search_memories",
            "save_preference",
            "get_preference",
            "list_preferences",
            "save_workflow",
            "load_workflow",
            "list_workflows",
            "get_context",
            "list_memories",
            "delete_memory",
            "clear_memory",
            "memory_stats",
        ]

    def _handle_remember(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, [
            "remember ", "save ", "store ", "note ",
            "remember that ", "save that ", "store that ",
        ])

        if not content:
            return {"success": False, "response": "Please provide something to remember."}

        memory_type = self._detect_memory_type(content)
        category = self._detect_category(content)
        tags = self._extract_tags(content)
        importance = self._compute_importance(content)

        entry = self._memory_service.save(
            content=content,
            memory_type=memory_type,
            category=category,
            tags=tags,
            importance=importance,
        )

        return {
            "success": True,
            "response": f"I've remembered that: {content}",
            "data": entry.to_dict(),
        }

    def _handle_recall(self, command: str) -> Dict[str, Any]:
        query = self._extract_content(command, [
            "recall ", "retrieve ", "search memory for ",
            "what do you know about ", "what do you remember about ",
            "find ", "search ",
        ])

        if not query:
            return {"success": False, "response": "Please provide a topic to search for."}

        memories = self._memory_service.search(query, top_k=10)

        if not memories:
            return {
                "success": True,
                "response": f"I don't have any memories related to '{query}'.",
                "data": [],
            }

        lines = [f"Found {len(memories)} memories related to '{query}':\n"]
        for i, m in enumerate(memories, 1):
            score = m.to_dict().get("retrieval_score", "?")
            lines.append(f"{i}. [{m.memory_type}] {m.content[:120]}")
            if m.tags:
                lines.append(f"   Tags: {', '.join(m.tags)}")
            lines.append(f"   Score: {score} | Accessed: {m.access_count} times\n")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [m.to_dict() for m in memories],
        }

    def _handle_set_preference(self, command: str) -> Dict[str, Any]:
        if "=" in command:
            parts = command.split("=", 1)
            key = self._extract_content(parts[0], [
                "set preference ", "set setting ", "preference ", "setting ",
            ]).strip().lower()
            value = parts[1].strip()
        else:
            key = self._extract_content(command, [
                "set preference ", "set setting ", "preference ", "setting ",
            ]).strip().lower()
            value = ""

        if not key:
            return {"success": False, "response": "Please specify a preference key."}

        self._preference_service.set(key, value)
        return {
            "success": True,
            "response": f"Preference saved: {key} = {value}",
        }

    def _handle_get_preference(self, command: str) -> Dict[str, Any]:
        key = self._extract_content(command, [
            "get preference ", "get setting ", "what is preference ",
            "what is setting ", "preference ", "setting ",
        ]).strip().lower()

        if not key:
            return {"success": False, "response": "Please specify a preference key."}

        value = self._preference_service.get(key)
        if value is not None:
            return {
                "success": True,
                "response": f"Preference: {key} = {value}",
                "data": {"key": key, "value": value},
            }
        return {
            "success": True,
            "response": f"No preference found for: {key}",
        }

    def _handle_list_preferences(self) -> Dict[str, Any]:
        prefs = self._preference_service.get_all()
        if not prefs:
            return {"success": True, "response": "No preferences stored."}

        lines = ["Stored preferences:\n"]
        for key, value in sorted(prefs.items()):
            lines.append(f"  {key} = {value}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": prefs,
        }

    def _handle_save_workflow(self, command: str) -> Dict[str, Any]:
        name = self._extract_content(command, [
            "save workflow ", "create workflow ", "workflow save ",
            "save workflow named ", "create workflow named ",
        ])

        if not name:
            return {"success": False, "response": "Please provide a workflow name."}

        existing = self._workflow_service.load_by_name(name)
        if existing:
            return {
                "success": False,
                "response": f"Workflow '{name}' already exists (ID: {existing.id}). Use 'load workflow {name}' to use it.",
            }

        workflow = self._workflow_service.create(name=name, description=f"User-created workflow: {name}")
        workflow_id = self._workflow_service.save(workflow)

        return {
            "success": True,
            "response": f"Workflow '{name}' created (ID: {workflow_id}). Add steps using the automation agent.",
            "data": {"id": workflow_id, "name": name},
        }

    def _handle_load_workflow(self, command: str) -> Dict[str, Any]:
        name = self._extract_content(command, [
            "load workflow ", "run workflow ", "execute workflow ",
            "workflow load ", "workflow run ", "workflow execute ",
        ])

        if not name:
            return {"success": False, "response": "Please provide a workflow name."}

        workflow = self._workflow_service.load_by_name(name)
        if not workflow:
            return {
                "success": False,
                "response": f"Workflow '{name}' not found.",
            }

        self._workflow_service.record_execution(workflow.id)
        plan = self._workflow_service.get_execution_plan(workflow)

        lines = [f"Workflow: {workflow.name}", f"Steps: {len(plan)}\n"]
        for step in plan:
            lines.append(f"  {step['step']}. [{step['agent']}] {step['command']}")
            if step.get("description"):
                lines.append(f"     {step['description']}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"workflow": workflow.to_dict(), "plan": plan},
        }

    def _handle_list_workflows(self) -> Dict[str, Any]:
        workflows = self._workflow_service.list_workflows()
        if not workflows:
            return {"success": True, "response": "No workflows saved."}

        lines = ["Saved workflows:\n"]
        for wf in workflows:
            lines.append(f"  - {wf.name} ({len(wf.steps)} steps, used {wf.usage_count} times)")
            lines.append(f"    ID: {wf.id}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [wf.to_dict() for wf in workflows],
        }

    def _handle_context(self, command: str) -> Dict[str, Any]:
        session_id = self.config.get("app.session_id", "default")
        context = self._context_manager.get_context(session_id)

        if not context:
            active = self._context_manager.get_active_sessions()
            if active:
                lines = [f"No context for session '{session_id}'. Active sessions: {', '.join(active)}"]
                for sid in active:
                    msgs = self._context_manager.get_context(sid)
                    lines.append(f"\nSession '{sid}' ({len(msgs)} messages):")
                    for msg in msgs[-5:]:
                        lines.append(f"  [{msg['role']}] {msg['content'][:80]}")
                return {
                    "success": True,
                    "response": "\n".join(lines),
                    "data": {"active_sessions": active},
                }
            return {"success": True, "response": "No conversation context available."}

        lines = [f"Recent context ({len(context)} messages):\n"]
        for msg in context[-10:]:
            preview = msg["content"][:100]
            lines.append(f"  [{msg['role']}] {preview}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": context,
        }

    def _handle_list_memories(self, command: str) -> Dict[str, Any]:
        memory_type = None
        if "episodic" in command.lower():
            memory_type = MemoryType.EPISODIC.value
        elif "semantic" in command.lower():
            memory_type = MemoryType.SEMANTIC.value
        elif "procedural" in command.lower():
            memory_type = MemoryType.PROCEDURAL.value

        memories = self._memory_service.list_memories(memory_type=memory_type, limit=30)
        if not memories:
            return {"success": True, "response": "No memories stored."}

        lines = [f"Stored memories ({len(memories)}):\n"]
        for m in memories:
            lines.append(f"  [{m.memory_type}] {m.content[:100]}")
            lines.append(f"    Tags: {', '.join(m.tags) if m.tags else 'none'} | Importance: {m.importance:.2f}\n")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [m.to_dict() for m in memories],
        }

    def _handle_stats(self) -> Dict[str, Any]:
        mem_stats = self._memory_service.get_stats()
        ctx_stats = self._context_manager.get_stats()
        workflows = self._workflow_service.list_workflows()
        prefs = self._preference_service.get_all()

        lines = [
            "Memory Agent Statistics:",
            f"  Total memories: {mem_stats['total_memories']}",
            f"  By type: {mem_stats['by_type']}",
            f"  Vector index: {mem_stats['vector_index_size']} entries",
            f"  Active sessions: {ctx_stats['active_sessions']}",
            f"  Total context messages: {ctx_stats['total_messages']}",
            f"  Saved workflows: {len(workflows)}",
            f"  Stored preferences: {len(prefs)}",
        ]

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"memory": mem_stats, "context": ctx_stats},
        }

    def _handle_clear_memory(self, command: str) -> Dict[str, Any]:
        if "context" in command.lower():
            session_id = self.config.get("app.session_id", "default")
            self._context_manager.clear_session(session_id)
            return {"success": True, "response": "Context cleared."}

        if "preferences" in command.lower():
            self._preference_service.clear_all()
            return {"success": True, "response": "All preferences cleared."}

        if "workflows" in command.lower():
            for wf in self._workflow_service.list_workflows():
                self._workflow_service.delete(wf.id)
            return {"success": True, "response": "All workflows cleared."}

        memories = self._memory_service.list_memories(limit=1000)
        for m in memories:
            self._memory_service.delete(m.id)
        self._context_manager.clear_all()

        return {"success": True, "response": "All memories and context cleared."}

    def _handle_delete_memory(self, command: str) -> Dict[str, Any]:
        memory_id = self._extract_id(command)
        if not memory_id:
            return {"success": False, "response": "Please specify a memory ID to delete."}

        entry = self._memory_service.recall(memory_id)
        if not entry:
            return {"success": False, "response": f"Memory not found: {memory_id}"}

        self._memory_service.delete(memory_id)
        return {
            "success": True,
            "response": f"Memory deleted: {memory_id}",
        }

    def add_message_to_context(self, session_id: str, role: str, content: str,
                                agent: str = "", importance: float = 0.5):
        """Add a message to the context window (called by AI Manager)."""
        self._context_manager.add_message(session_id, role, content, agent, importance)

    def get_context_for_session(self, session_id: str, limit: int = None) -> List[Dict[str, str]]:
        """Get context messages for a session (called by AI Manager)."""
        return self._context_manager.get_context(session_id, limit)

    def build_llm_context(self, session_id: str, system_prompt: str = None,
                           max_messages: int = 20) -> List[Dict[str, str]]:
        """Build context for LLM API calls (called by AI Manager)."""
        return self._context_manager.build_llm_context(session_id, system_prompt, max_messages)

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: List[str]) -> str:
        cmd_lower = command.lower()
        for prefix in prefixes:
            if cmd_lower.startswith(prefix):
                return command[len(prefix):].strip()
        return ""

    @staticmethod
    def _extract_id(command: str) -> Optional[str]:
        match = re.search(r"[a-f0-9]{8}", command.lower())
        return match.group(0) if match else None

    def _detect_memory_type(self, content: str) -> str:
        cmd = content.lower()
        if any(kw in cmd for kw in ["i did", "i went", "i visited", "happened", "event"]):
            return MemoryType.EPISODIC.value
        if any(kw in cmd for kw in ["is a", "are", "means", "definition", "fact"]):
            return MemoryType.SEMANTIC.value
        if any(kw in cmd for kw in ["how to", "steps", "procedure", "method"]):
            return MemoryType.PROCEDURAL.value
        return MemoryType.USER_MEMORY.value

    def _detect_category(self, content: str) -> str:
        cmd = content.lower()
        if any(kw in cmd for kw in ["like", "prefer", "favorite", "want"]):
            return MemoryCategory.PREFERENCE.value
        if any(kw in cmd for kw in ["workflow", "steps", "process"]):
            return MemoryCategory.WORKFLOW.value
        if any(kw in cmd for kw in ["fact", "is a", "definition"]):
            return MemoryCategory.FACT.value
        return MemoryCategory.USER_DATA.value

    def _extract_tags(self, content: str) -> List[str]:
        tags = []
        words = re.findall(r"\b[a-z]{4,}\b", content.lower())
        stop_words = {"this", "that", "with", "have", "from", "they", "been", "will", "would", "could", "should"}
        for w in words:
            if w not in stop_words and w not in tags:
                tags.append(w)
                if len(tags) >= 5:
                    break
        return tags

    def _compute_importance(self, content: str) -> float:
        score = 0.5
        if any(kw in content.lower() for kw in ["important", "remember", "always", "never", "must"]):
            score += 0.2
        if len(content.split()) > 20:
            score += 0.1
        return min(1.0, score)
