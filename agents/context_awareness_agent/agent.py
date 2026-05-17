"""
Context Awareness Agent
Continuously understands the user's current context and intelligently
adapts system behavior. Detects activities, suggests workflows, and
triggers adaptive automation.
"""

import time
import threading
from typing import Dict, Any, Optional, List

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import (
    ActivityType, ContextConfidence, FocusLevel, TriggerAction,
    UserContext, AdaptiveTrigger,
)
from .storage import ContextStorage
from .services import ContextDetector, WorkflowDetector, AdaptiveTriggerSystem, ContextHistory


class ContextAwarenessAgent(BaseAgent):
    """Context awareness and adaptive behavior agent for NEXUS."""

    def __init__(self):
        super().__init__("context_awareness_agent", "Context awareness, activity detection, and adaptive system behavior")

        self.logger = Logger().get_logger("ContextAwarenessAgent")
        self.config = Config()

        self._storage = ContextStorage()
        self._detector = ContextDetector(self._storage)
        self._workflow_detector = WorkflowDetector(self._storage)
        self._trigger_system = AdaptiveTriggerSystem(self._storage)
        self._history = ContextHistory(self._storage)

        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_interval = 10
        self._last_context: Optional[UserContext] = None
        self._ai_manager = None

        self._detector.on_context_change(self._on_context_change)
        self._history.start_session()

        self.logger.info("ContextAwarenessAgent initialized")

    def set_ai_manager(self, manager):
        self._ai_manager = manager

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["current context", "what am i doing", "what context", "my context", "detect context"]):
                return self._handle_current_context(command)
            elif self._matches(cmd, ["active window", "current window", "focused window", "what window"]):
                return self._handle_active_window(command)
            elif self._matches(cmd, ["running apps", "open apps", "what apps", "list apps", "app list"]):
                return self._handle_running_apps(command)
            elif self._matches(cmd, ["activity type", "what activity", "my activity", "detect activity"]):
                return self._handle_activity_type(command)
            elif self._matches(cmd, ["focus level", "my focus", "am i focused", "focus status"]):
                return self._handle_focus_level(command)
            elif self._matches(cmd, ["system load", "system status", "resource load", "cpu load"]):
                return self._handle_system_load(command)
            elif self._matches(cmd, ["suggest workflow", "workflow suggestion", "what mode", "suggest mode"]):
                return self._handle_suggest_workflow(command)
            elif self._matches(cmd, ["suggest actions", "what should i do", "recommendations", "context suggestions"]):
                return self._handle_suggest_actions(command)
            elif self._matches(cmd, ["start monitoring", "enable monitoring", "start context monitor", "monitor start"]):
                return self._handle_start_monitoring(command)
            elif self._matches(cmd, ["stop monitoring", "disable monitoring", "stop context monitor", "monitor stop"]):
                return self._handle_stop_monitoring(command)
            elif self._matches(cmd, ["workflow patterns", "detect workflows", "workflow detection", "pattern list"]):
                return self._handle_workflow_patterns(command)
            elif self._matches(cmd, ["detect workflow", "what workflow", "current workflow"]):
                return self._handle_detect_workflow(command)
            elif self._matches(cmd, ["triggers", "adaptive triggers", "list triggers", "trigger list"]):
                return self._handle_list_triggers(command)
            elif self._matches(cmd, ["add trigger", "new trigger", "create trigger"]):
                return self._handle_add_trigger(command)
            elif self._matches(cmd, ["toggle trigger", "enable trigger", "disable trigger"]):
                return self._handle_toggle_trigger(command)
            elif self._matches(cmd, ["context history", "context log", "past context", "context timeline"]):
                return self._handle_context_history(command)
            elif self._matches(cmd, ["activity summary", "activity stats", "usage summary", "activity report"]):
                return self._handle_activity_summary(command)
            elif self._matches(cmd, ["session start", "start session", "new session"]):
                return self._handle_session_start(command)
            elif self._matches(cmd, ["session end", "end session", "close session"]):
                return self._handle_session_end(command)
            elif self._matches(cmd, ["context rules", "list rules", "show rules"]):
                return self._handle_context_rules(command)
            elif self._matches(cmd, ["add rule", "new rule", "create rule"]):
                return self._handle_add_rule(command)
            elif self._matches(cmd, ["delete rule", "remove rule"]):
                return self._handle_delete_rule(command)
            elif self._matches(cmd, ["cleanup", "clean context", "purge context"]):
                return self._handle_cleanup(command)
            elif self._matches(cmd, ["context", "context agent", "context help"]):
                return self._handle_help(command)
            else:
                return self._handle_current_context(command)
        except Exception as e:
            return {"success": False, "response": f"Error: {e}", "error": str(e)}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "current_context",
            "active_window",
            "running_apps",
            "activity_type",
            "focus_level",
            "system_load",
            "suggest_workflow",
            "suggest_actions",
            "start_monitoring",
            "stop_monitoring",
            "workflow_patterns",
            "detect_workflow",
            "list_triggers",
            "add_trigger",
            "toggle_trigger",
            "context_history",
            "activity_summary",
            "session_start",
            "session_end",
            "context_rules",
            "add_rule",
            "delete_rule",
            "cleanup",
        ]

    def get_current_context(self) -> Optional[UserContext]:
        return self._last_context or self._detector.detect_context()

    def get_activity_type(self) -> str:
        ctx = self.get_current_context()
        return ctx.activity.value if ctx else "unknown"

    def get_focus_level(self) -> str:
        ctx = self.get_current_context()
        return ctx.focus_level.value if ctx else "idle"

    def should_suggest_mode(self) -> Optional[str]:
        ctx = self.get_current_context()
        if ctx and ctx.suggested_workflow:
            return ctx.suggested_workflow
        return None

    def _on_context_change(self, context: UserContext):
        self._last_context = context
        self._history.update_session(context)

        triggers = self._trigger_system.evaluate(context)
        for trigger in triggers:
            self._execute_trigger(trigger, context)

    def _execute_trigger(self, trigger: Dict[str, Any], context: UserContext):
        action = trigger.get("action", "")
        target = trigger.get("target", "")

        if action == "suggest_workflow" and self._ai_manager:
            self.logger.info(f"Context suggestion: activate {target}")
        elif action == "silence_notifications" and self._ai_manager:
            self.logger.info(f"Context action: silence notifications")
        elif action == "save_context":
            self._history.end_session()
            self._history.start_session()

    def _monitor_loop(self):
        while self._monitoring:
            try:
                self._detector.detect_context()
            except Exception as e:
                self.logger.error(f"Context monitoring error: {e}")
            time.sleep(self._monitor_interval)

    def _handle_current_context(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        self._last_context = context

        lines = [
            "Current Context:",
            "=" * 40,
            f"Activity: {context.activity.value} ({context.activity_confidence.value} confidence)",
            f"Focus Level: {context.focus_level.value}",
            f"Session Type: {context.session_type}",
            f"Session Duration: {self._detector.get_session_duration():.1f} minutes",
        ]

        if context.active_window:
            lines.append(f"\nActive Window:")
            lines.append(f"  Title: {context.active_window.title[:80]}")
            lines.append(f"  Process: {context.active_window.process_name}")
            lines.append(f"  Duration: {context.active_window.duration_seconds:.0f}s")

        if context.system_load:
            lines.append(f"\nSystem Load: {context.system_load.level}")
            lines.append(f"  CPU: {context.system_load.cpu_percent:.1f}%")
            lines.append(f"  Memory: {context.system_load.memory_percent:.1f}%")

        if context.time_context:
            lines.append(f"\nTime Context: {context.time_context.period}")
            lines.append(f"  Work Hours: {'Yes' if context.time_context.is_work_hours else 'No'}")
            lines.append(f"  Weekday: {'Yes' if context.time_context.is_weekday else 'No'}")

        if context.context_signals:
            lines.append(f"\nSignals:")
            for signal in context.context_signals[:5]:
                lines.append(f"  - {signal}")

        if context.suggested_workflow:
            lines.append(f"\nSuggested Workflow: {context.suggested_workflow}")

        if context.suggested_actions:
            lines.append(f"\nSuggestions:")
            for action in context.suggested_actions:
                lines.append(f"  - {action}")

        return {"success": True, "response": "\n".join(lines), "data": context.to_dict()}

    def _handle_active_window(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        if not context.active_window:
            return {"success": True, "response": "No active window detected."}

        w = context.active_window
        lines = [
            "Active Window:",
            f"  Title: {w.title}",
            f"  Process: {w.process_name}",
            f"  PID: {w.pid}",
            f"  Minimized: {'Yes' if w.is_minimized else 'No'}",
            f"  Visible: {'Yes' if w.is_visible else 'No'}",
            f"  Duration: {w.duration_seconds:.0f}s",
            f"  Window Switches: {w.switch_count}",
        ]

        return {"success": True, "response": "\n".join(lines), "data": w.to_dict()}

    def _handle_running_apps(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        apps = context.running_apps

        if not apps:
            return {"success": True, "response": "No running apps detected."}

        category_filter = self._extract_content(command, ["category", "type", "filter"])
        if category_filter:
            apps = [a for a in apps if a.category == category_filter.lower()]

        lines = [f"Running Applications ({len(apps)}):\n"]
        categories = {}
        for app in apps[:20]:
            if app.category not in categories:
                categories[app.category] = []
            categories[app.category].append(app)

        for cat, cat_apps in sorted(categories.items()):
            lines.append(f"  {cat.upper()} ({len(cat_apps)}):")
            for app in cat_apps[:5]:
                lines.append(f"    {app.name} (PID: {app.pid}, RAM: {app.memory_mb:.0f}MB)")
            if len(cat_apps) > 5:
                lines.append(f"    ... and {len(cat_apps) - 5} more")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [a.to_dict() for a in apps[:20]]}

    def _handle_activity_type(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        lines = [
            f"Current Activity: {context.activity.value}",
            f"Confidence: {context.activity_confidence.value}",
            f"Session Type: {context.session_type}",
        ]
        if context.context_signals:
            lines.append("\nDetection Signals:")
            for signal in context.context_signals:
                lines.append(f"  - {signal}")

        return {"success": True, "response": "\n".join(lines), "data": context.to_dict()}

    def _handle_focus_level(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        focus_descriptions = {
            "deep": "Deep focus - single task, minimal distractions",
            "focused": "Focused - primary task with occasional context switches",
            "moderate": "Moderate - multiple tasks, regular switching",
            "distracted": "Distracted - browsing, media, or entertainment",
            "idle": "Idle - no active window detected",
        }

        lines = [
            f"Focus Level: {context.focus_level.value}",
            f"Description: {focus_descriptions.get(context.focus_level.value, '')}",
            f"Activity: {context.activity.value}",
            f"Window Switches: {context.active_window.switch_count if context.active_window else 0}",
            f"Session Duration: {self._detector.get_session_duration():.1f} minutes",
        ]

        return {"success": True, "response": "\n".join(lines), "data": context.to_dict()}

    def _handle_system_load(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        if not context.system_load:
            return {"success": False, "response": "Unable to get system load."}

        sl = context.system_load
        lines = [
            f"System Load: {sl.level}",
            f"CPU: {sl.cpu_percent:.1f}%",
            f"Memory: {sl.memory_percent:.1f}% ({sl.memory_used_gb:.1f}GB used)",
            f"Disk: {sl.disk_percent:.1f}%",
            f"Processes: {sl.process_count}",
            f"Network Connections: {sl.network_connections}",
        ]

        return {"success": True, "response": "\n".join(lines), "data": sl.to_dict()}

    def _handle_suggest_workflow(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        workflows = self._workflow_detector.detect_workflow(context)

        if not workflows:
            lines = [
                f"Current Activity: {context.activity.value}",
                "No specific workflow patterns matched.",
            ]
            if context.suggested_workflow:
                lines.append(f"Suggested: {context.suggested_workflow}")
        else:
            lines = [f"Detected Workflows ({len(workflows)}):\n"]
            for w in workflows:
                lines.append(f"  {w['pattern']} ({w['confidence']:.0%} confidence)")
                lines.append(f"    Suggested: {w['suggested_workflow']}")
                lines.append(f"    Description: {w['description']}")
                lines.append(f"    Matching apps: {', '.join(w['matching_apps'])}")
                lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": workflows}

    def _handle_suggest_actions(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        actions = context.suggested_actions

        if not actions:
            return {"success": True, "response": "No specific suggestions for current context."}

        lines = [f"Context Suggestions ({len(actions)}):\n"]
        for action in actions:
            lines.append(f"  - {action}")

        return {"success": True, "response": "\n".join(lines), "data": {"actions": actions}}

    def _handle_start_monitoring(self, command: str) -> Dict[str, Any]:
        if self._monitoring:
            return {"success": False, "response": "Context monitoring already active."}

        interval = self._extract_number(command, default=10)
        self._monitor_interval = max(interval, 5)
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        return {"success": True, "response": f"Context monitoring started (interval: {self._monitor_interval}s)"}

    def _handle_stop_monitoring(self, command: str) -> Dict[str, Any]:
        if not self._monitoring:
            return {"success": False, "response": "Context monitoring not active."}

        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

        return {"success": True, "response": "Context monitoring stopped."}

    def _handle_workflow_patterns(self, command: str) -> Dict[str, Any]:
        patterns = self._workflow_detector.get_patterns()

        if not patterns:
            return {"success": True, "response": "No workflow patterns defined."}

        lines = [f"Workflow Patterns ({len(patterns)}):\n"]
        for p in patterns:
            lines.append(f"  {p['name']}")
            lines.append(f"    Activity: {p['activity_type']}")
            lines.append(f"    Required apps: {', '.join(p['required_apps'])}")
            lines.append(f"    Detections: {p['detection_count']}")
            if p.get("description"):
                lines.append(f"    {p['description']}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": patterns}

    def _handle_detect_workflow(self, command: str) -> Dict[str, Any]:
        context = self._detector.detect_context()
        workflows = self._workflow_detector.detect_workflow(context)

        if not workflows:
            return {"success": True, "response": f"No specific workflow detected. Current activity: {context.activity.value}"}

        best = workflows[0]
        lines = [
            f"Detected Workflow: {best['pattern']}",
            f"Confidence: {best['confidence']:.0%}",
            f"Suggested Mode: {best['suggested_workflow']}",
            f"Description: {best['description']}",
            f"Matching Apps: {', '.join(best['matching_apps'])}",
        ]

        return {"success": True, "response": "\n".join(lines), "data": best}

    def _handle_list_triggers(self, command: str) -> Dict[str, Any]:
        triggers = self._trigger_system.list_triggers()

        if not triggers:
            return {"success": True, "response": "No adaptive triggers defined."}

        lines = [f"Adaptive Triggers ({len(triggers)}):\n"]
        for t in triggers:
            status = "ENABLED" if t.enabled else "DISABLED"
            lines.append(f"  [{status}] {t.name}")
            lines.append(f"    Action: {t.action.value} -> {t.action_target}")
            if t.condition_activity:
                lines.append(f"    Condition: activity={t.condition_activity.value}")
            if t.condition_apps:
                lines.append(f"    Condition: apps={', '.join(t.condition_apps)}")
            if t.condition_time:
                lines.append(f"    Condition: time={t.condition_time}")
            lines.append(f"    Fired: {t.trigger_count} times")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [t.to_dict() for t in triggers]}

    def _handle_add_trigger(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["add trigger", "new trigger", "create trigger"])
        if not content:
            return {
                "success": False,
                "response": "Usage: 'add trigger <name> when <activity> then <action> <target>'",
            }

        trigger = AdaptiveTrigger(
            name=content[:50],
            description=f"Custom trigger: {content}",
        )
        self._trigger_system.add_trigger(trigger)

        return {"success": True, "response": f"Trigger '{trigger.name}' added. Configure conditions via context rules."}

    def _handle_toggle_trigger(self, command: str) -> Dict[str, Any]:
        trigger_id = self._extract_id(command)
        if not trigger_id:
            return {"success": False, "response": "Please provide a trigger ID."}

        success = self._trigger_system.toggle_trigger(trigger_id)
        if success:
            return {"success": True, "response": f"Trigger {trigger_id} toggled."}
        return {"success": False, "response": f"Trigger {trigger_id} not found."}

    def _handle_context_history(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=20)
        snapshots = self._history.get_recent_context(limit=limit)

        if not snapshots:
            return {"success": True, "response": "No context history available."}

        lines = [f"Context History ({len(snapshots)} snapshots):\n"]
        for s in snapshots[:10]:
            lines.append(f"  [{s['timestamp'][:19]}] {s['activity']} - Focus: {s['focus_level']}")
            if s.get("active_window_title"):
                lines.append(f"    Window: {s['active_window_title'][:60]}")
            lines.append(f"    CPU: {s['cpu_percent']:.1f}%, Apps: {s['app_count']}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": snapshots}

    def _handle_activity_summary(self, command: str) -> Dict[str, Any]:
        days = self._extract_number(command, default=7)
        summary = self._history.get_activity_summary(days=days)

        if not summary.get("activities"):
            return {"success": True, "response": "No activity data available. Start monitoring to collect data."}

        lines = [
            f"Activity Summary (Last {days} days)",
            "=" * 40,
            f"Total Sessions: {summary['total_sessions']}",
            f"Avg Focus Score: {summary['avg_focus_score']:.1f}/5",
            "",
            "Activities:",
        ]

        activities = summary.get("activities", {})
        for activity, data in sorted(activities.items(), key=lambda x: x[1]["count"], reverse=True):
            lines.append(f"  {activity}: {data['count']} sessions, Avg {data['avg_duration']:.0f}s, Total {data['total_duration']:.0f}s")

        return {"success": True, "response": "\n".join(lines), "data": summary}

    def _handle_session_start(self, command: str) -> Dict[str, Any]:
        session_type = self._extract_content(command, ["session start", "start session", "new session"])
        if not session_type or session_type.lower() in ("session", "start", "new"):
            session_type = "general"

        self._history.end_session()
        self._history.start_session(session_type)

        return {"success": True, "response": f"Context session started (type: {session_type})"}

    def _handle_session_end(self, command: str) -> Dict[str, Any]:
        self._history.end_session()
        self._history.start_session()
        return {"success": True, "response": "Context session ended and new one started."}

    def _handle_context_rules(self, command: str) -> Dict[str, Any]:
        rules = self._storage.get_rules()

        if not rules:
            return {"success": True, "response": "No context rules defined. Use 'add rule' to create one."}

        lines = [f"Context Rules ({len(rules)}):\n"]
        for r in rules:
            status = "ENABLED" if r.get("enabled") else "DISABLED"
            lines.append(f"  [{status}] {r['name']}")
            lines.append(f"    Type: {r['rule_type']}")
            lines.append(f"    Condition: {r['condition']}")
            lines.append(f"    Action: {r['action']}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": rules}

    def _handle_add_rule(self, command: str) -> Dict[str, Any]:
        content = self._extract_content(command, ["add rule", "new rule", "create rule"])
        if not content:
            return {
                "success": False,
                "response": "Usage: 'add rule <name> when <condition> then <action>'",
            }

        import uuid
        rule_id = str(uuid.uuid4())[:8]
        rule = {
            "id": rule_id,
            "name": content[:50],
            "rule_type": "custom",
            "condition": content,
            "action": "notify",
            "enabled": True,
        }
        self._storage.save_rule(rule)

        return {"success": True, "response": f"Context rule '{rule['name']}' added (ID: {rule_id})"}

    def _handle_delete_rule(self, command: str) -> Dict[str, Any]:
        rule_id = self._extract_id(command)
        if not rule_id:
            return {"success": False, "response": "Please provide a rule ID."}

        success = self._storage.delete_rule(rule_id)
        if success:
            return {"success": True, "response": f"Rule {rule_id} deleted."}
        return {"success": False, "response": f"Rule {rule_id} not found."}

    def _handle_cleanup(self, command: str) -> Dict[str, Any]:
        days = self._extract_number(command, default=30)
        deleted = self._history.cleanup(days)
        return {"success": True, "response": f"Cleaned up {deleted} old context records."}

    def _handle_help(self, command: str) -> Dict[str, Any]:
        lines = [
            "Context Awareness Agent Commands:",
            "",
            "Context Detection:",
            "  current context         - Show full context snapshot",
            "  active window           - Show current active window",
            "  running apps [category] - List running applications",
            "  activity type           - Show detected activity type",
            "  focus level             - Show current focus level",
            "  system load             - Show system resource load",
            "",
            "Suggestions:",
            "  suggest workflow        - Suggest workflow mode based on context",
            "  suggest actions         - Show contextual suggestions",
            "  detect workflow         - Detect current workflow pattern",
            "  workflow patterns       - List all workflow patterns",
            "",
            "Monitoring:",
            "  start monitoring [sec]  - Start continuous context monitoring",
            "  stop monitoring         - Stop context monitoring",
            "",
            "Triggers:",
            "  triggers                - List adaptive triggers",
            "  add trigger <name>      - Add a new trigger",
            "  toggle trigger <id>     - Enable/disable a trigger",
            "",
            "History & Sessions:",
            "  context history         - Show context history",
            "  activity summary [days] - Show activity summary",
            "  session start [type]    - Start a new context session",
            "  session end             - End current session",
            "",
            "Rules:",
            "  context rules           - List context rules",
            "  add rule <definition>   - Add a context rule",
            "  delete rule <id>        - Delete a context rule",
            "",
            "Maintenance:",
            "  cleanup [days]          - Clean up old context records",
        ]

        return {"success": True, "response": "\n".join(lines)}

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

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        import re
        match = re.search(r'\b(\d+)\b', command)
        return int(match.group(1)) if match else default
