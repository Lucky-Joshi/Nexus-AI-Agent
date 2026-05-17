"""
Learning Agent
Learns from user behavior and improves over time. Detects patterns, habits,
predicts actions, recommends automations, and generates adaptive workflows.
"""

from typing import Dict, Any, Optional, List

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import RecommendationType
from .storage import LearningStorage
from .services import LearningEngine


class LearningAgent(BaseAgent):
    """Learning and behavior analysis agent for NEXUS."""

    def __init__(self):
        super().__init__("learning_agent", "Behavior learning, pattern detection, and adaptive recommendations")

        self.logger = Logger().get_logger("LearningAgent")
        self.config = Config()

        self._storage = LearningStorage()
        self._engine = LearningEngine(self._storage)

        self._ai_manager = None
        self.logger.info("LearningAgent initialized")

    def set_ai_manager(self, manager):
        self._ai_manager = manager

    def track_action(self, action: str, agent: str = "", context: str = "",
                     duration: float = 0.0, success: bool = True):
        self._engine.tracker.record_behavior(action, agent, context, duration, success)

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["learn", "start learning", "enable learning", "learning on"]):
                return self._handle_start_learning(command)
            elif self._matches(cmd, ["stop learning", "disable learning", "learning off"]):
                return self._handle_stop_learning(command)
            elif self._matches(cmd, ["analyze", "analyze patterns", "run analysis", "learn now"]):
                return self._handle_analyze(command)
            elif self._matches(cmd, ["patterns", "learned patterns", "show patterns", "list patterns"]):
                return self._handle_patterns(command)
            elif self._matches(cmd, ["habits", "my habits", "detected habits", "habit list"]):
                return self._handle_habits(command)
            elif self._matches(cmd, ["recommendations", "recommendations for me", "suggestions", "what should i do"]):
                return self._handle_recommendations(command)
            elif self._matches(cmd, ["accept recommendation", "accept suggestion", "apply recommendation"]):
                return self._handle_accept_recommendation(command)
            elif self._matches(cmd, ["dismiss recommendation", "dismiss suggestion", "ignore recommendation"]):
                return self._handle_dismiss_recommendation(command)
            elif self._matches(cmd, ["predict", "predict next", "what next", "next action"]):
                return self._handle_predict(command)
            elif self._matches(cmd, ["behavior history", "my behaviors", "behavior log", "action history"]):
                return self._handle_behavior_history(command)
            elif self._matches(cmd, ["learning stats", "learning statistics", "learning status", "how much learned"]):
                return self._handle_stats(command)
            elif self._matches(cmd, ["generate workflow", "create workflow", "workflow from pattern", "auto workflow"]):
                return self._handle_generate_workflow(command)
            elif self._matches(cmd, ["daily routine", "morning routine", "generate routine", "my routine"]):
                return self._handle_daily_routine(command)
            elif self._matches(cmd, ["most common", "frequent actions", "top actions", "common actions"]):
                return self._handle_most_common(command)
            elif self._matches(cmd, ["hourly pattern", "activity by hour", "when am i active"]):
                return self._handle_hourly_pattern(command)
            elif self._matches(cmd, ["daily pattern", "activity by day", "which day active"]):
                return self._handle_daily_pattern(command)
            elif self._matches(cmd, ["prediction accuracy", "how accurate", "prediction stats"]):
                return self._handle_prediction_accuracy(command)
            elif self._matches(cmd, ["cleanup", "clean learning data", "purge old data"]):
                return self._handle_cleanup(command)
            elif self._matches(cmd, ["learning", "learning agent", "learning help"]):
                return self._handle_help(command)
            else:
                return self._handle_stats(command)
        except Exception as e:
            return {"success": False, "response": f"Error: {e}", "error": str(e)}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "start_learning",
            "stop_learning",
            "analyze_patterns",
            "list_patterns",
            "list_habits",
            "get_recommendations",
            "accept_recommendation",
            "dismiss_recommendation",
            "predict_next_action",
            "behavior_history",
            "learning_stats",
            "generate_workflow",
            "daily_routine",
            "most_common_actions",
            "hourly_pattern",
            "daily_pattern",
            "prediction_accuracy",
            "cleanup",
        ]

    def _handle_start_learning(self, command: str) -> Dict[str, Any]:
        interval = self._extract_number(command, default=300)
        self._engine.start_learning(interval)
        return {"success": True, "response": f"Learning engine started (interval: {interval}s). NEXUS will now learn from your behavior."}

    def _handle_stop_learning(self, command: str) -> Dict[str, Any]:
        self._engine.stop_learning()
        return {"success": True, "response": "Learning engine stopped. Existing knowledge is preserved."}

    def _handle_analyze(self, command: str) -> Dict[str, Any]:
        new_patterns = self._engine.analyzer.analyze_and_learn()
        habits = self._engine.analyzer.detect_habits()
        recs = self._engine.recommender.generate_recommendations()

        lines = ["Analysis Complete:", "=" * 40]
        lines.append(f"New patterns detected: {len(new_patterns)}")
        lines.append(f"Habits identified: {len(habits)}")
        lines.append(f"Recommendations generated: {len(recs)}")

        if new_patterns:
            lines.append("\nNew Patterns:")
            for p in new_patterns[:5]:
                lines.append(f"  - {p.name} (confidence: {p.confidence.value})")

        if recs:
            lines.append("\nTop Recommendations:")
            for r in recs[:3]:
                lines.append(f"  - {r.title}")

        return {"success": True, "response": "\n".join(lines), "data": {
            "new_patterns": len(new_patterns),
            "habits": len(habits),
            "recommendations": len(recs),
        }}

    def _handle_patterns(self, command: str) -> Dict[str, Any]:
        pattern_type = None
        if "frequency" in command.lower():
            pattern_type = "frequency"
        elif "sequence" in command.lower():
            pattern_type = "sequence"
        elif "time" in command.lower():
            pattern_type = "time_based"
        elif "context" in command.lower():
            pattern_type = "contextual"

        patterns = self._engine.analyzer.get_patterns(pattern_type=pattern_type, min_confidence=0.2)

        if not patterns:
            return {"success": True, "response": "No patterns learned yet. Use 'learn' to start tracking."}

        lines = [f"Learned Patterns ({len(patterns)}):\n"]
        for p in patterns[:15]:
            status_icon = {"observing": "OBS", "learning": "LRN", "confirmed": "CONF", "active": "ACT"}.get(p.status.value, "???")
            lines.append(f"  [{status_icon}] [{p.confidence.value}] {p.name}")
            lines.append(f"    Type: {p.pattern_type.value}, Frequency: {p.frequency}")
            if p.typical_time:
                lines.append(f"    Typical time: {p.typical_time}")
            if p.typical_day:
                lines.append(f"    Typical day: {p.typical_day}")
            if p.automation_suggestion:
                lines.append(f"    Suggestion: {p.automation_suggestion}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [p.to_dict() for p in patterns]}

    def _handle_habits(self, command: str) -> Dict[str, Any]:
        habits = self._engine.analyzer.get_habits()

        if not habits:
            return {"success": True, "response": "No habits detected yet. Keep using NEXUS to build patterns."}

        lines = [f"Detected Habits ({len(habits)}):\n"]
        for h in habits[:10]:
            lines.append(f"  {h.name}")
            lines.append(f"    Frequency: {h.frequency_per_week:.1f} times/week")
            lines.append(f"    Consistency: {h.consistency:.0%}")
            if h.typical_time:
                lines.append(f"    Typical time: {h.typical_time}")
            if h.typical_days:
                lines.append(f"    Typical days: {', '.join(h.typical_days)}")
            lines.append(f"    Automation potential: {h.automation_potential:.0%}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [h.to_dict() for h in habits]}

    def _handle_recommendations(self, command: str) -> Dict[str, Any]:
        rec_type = None
        if "workflow" in command.lower():
            rec_type = "workflow"
        elif "automation" in command.lower():
            rec_type = "automation"
        elif "habit" in command.lower():
            rec_type = "habit"
        elif "app" in command.lower():
            rec_type = "app_suggestion"

        recs = self._engine.recommender.get_recommendations(rec_type=rec_type, active_only=True, limit=15)

        if not recs:
            return {"success": True, "response": "No recommendations yet. Use 'analyze' to generate some."}

        lines = [f"Recommendations ({len(recs)}):\n"]
        for r in recs[:10]:
            lines.append(f"  [{r.rec_type.value}] {r.title}")
            lines.append(f"    {r.description}")
            lines.append(f"    Confidence: {r.confidence:.0%}")
            lines.append(f"    Reason: {r.reason}")
            lines.append(f"    (accept/dismiss with ID: {r.id})")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [r.to_dict() for r in recs]}

    def _handle_accept_recommendation(self, command: str) -> Dict[str, Any]:
        rec_id = self._extract_id(command)
        if not rec_id:
            return {"success": False, "response": "Please provide a recommendation ID."}

        self._engine.recommender.accept_recommendation(rec_id)
        return {"success": True, "response": f"Recommendation {rec_id} accepted."}

    def _handle_dismiss_recommendation(self, command: str) -> Dict[str, Any]:
        rec_id = self._extract_id(command)
        if not rec_id:
            return {"success": False, "response": "Please provide a recommendation ID."}

        self._engine.recommender.dismiss_recommendation(rec_id)
        return {"success": True, "response": f"Recommendation {rec_id} dismissed."}

    def _handle_predict(self, command: str) -> Dict[str, Any]:
        recent = self._engine.tracker.get_recent_actions(limit=5)
        if len(recent) < 2:
            return {"success": True, "response": "Not enough recent actions to predict. Use NEXUS more to build patterns."}

        predictions = self._engine.workflow_generator.predict_next_action(
            recent_actions=recent,
            current_hour=datetime.now().hour,
        )

        if not predictions:
            return {"success": True, "response": f"Recent actions: {', '.join(recent)}. No strong prediction available yet."}

        lines = [f"Predicted Next Actions (based on: {', '.join(recent[-3:])}):\n"]
        for p in predictions[:3]:
            lines.append(f"  {p.predicted_action} ({p.confidence:.0%} confidence)")
            lines.append(f"    Agent: {p.predicted_agent}")
            lines.append(f"    Reason: {p.reason}")
            lines.append(f"    Time relevance: {p.time_relevance:.0%}, Context relevance: {p.context_relevance:.0%}")
            lines.append("")

        self._engine.workflow_generator.log_prediction(predictions[0])

        return {"success": True, "response": "\n".join(lines), "data": [p.to_dict() for p in predictions]}

    def _handle_behavior_history(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=20)
        behaviors = self._storage.get_behaviors(limit=limit)

        if not behaviors:
            return {"success": True, "response": "No behavior history recorded yet."}

        lines = [f"Behavior History ({len(behaviors)}):\n"]
        for b in behaviors[:15]:
            status = "OK" if b.get("success") else "FAIL"
            lines.append(f"  [{b['timestamp'][:19]}] [{status}] {b['agent']}: {b['action']}")
            if b.get("preceding_actions"):
                lines.append(f"    After: {' -> '.join(b['preceding_actions'][-3:])}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": behaviors}

    def _handle_stats(self, command: str) -> Dict[str, Any]:
        stats = self._engine.get_stats()

        lines = [
            "Learning Statistics",
            "=" * 40,
            f"Learning Days: {stats.learning_days}",
            f"Behaviors Recorded: {stats.total_behaviors_recorded}",
            f"Patterns Learned: {stats.patterns_learned}",
            f"Confirmed Patterns: {stats.confirmed_patterns}",
            f"Habits Detected: {stats.habits_detected}",
            f"Recommendations Made: {stats.recommendations_made}",
            f"Recommendations Accepted: {stats.recommendations_accepted}",
            f"Predictions Made: {stats.predictions_made}",
            f"Predictions Correct: {stats.predictions_correct}",
            f"Most Common Action: {stats.most_common_action or 'None'}",
            f"Most Active Hour: {stats.most_active_hour:02d}:00",
            f"Most Active Day: {stats.most_active_day or 'None'}",
        ]

        if stats.top_patterns:
            lines.append("\nTop Patterns:")
            for p in stats.top_patterns:
                lines.append(f"  {p['name']} (freq: {p['frequency']}, conf: {p['confidence']:.2f})")

        return {"success": True, "response": "\n".join(lines), "data": stats.to_dict()}

    def _handle_generate_workflow(self, command: str) -> Dict[str, Any]:
        pattern_id = self._extract_id(command)
        if not pattern_id:
            patterns = self._storage.get_patterns(pattern_type="sequence", min_confidence=0.4)
            if not patterns:
                return {"success": True, "response": "No sequence patterns found to generate workflows from."}

            lines = ["Available patterns for workflow generation:\n"]
            for p in patterns[:5]:
                lines.append(f"  {p['id']}: {p['name']} (confidence: {p['confidence_score']:.2f})")
                lines.append(f"    Actions: {' -> '.join(p['actions'])}")
                lines.append("")
            lines.append("Use 'generate workflow <pattern_id>' to create one.")
            return {"success": True, "response": "\n".join(lines)}

        workflow = self._engine.workflow_generator.generate_from_pattern(pattern_id)
        if not workflow:
            return {"success": False, "response": f"Pattern {pattern_id} not found or insufficient actions."}

        lines = [
            f"Generated Workflow: {workflow['name']}",
            f"Description: {workflow['description']}",
            f"Confidence: {workflow['confidence']:.2f}",
            "",
            "Steps:",
        ]
        for step in workflow["steps"]:
            deps = f" (after {', '.join(step['depends_on'])})" if step["depends_on"] else ""
            lines.append(f"  {step['id']}: {step['name']} -> {step['agent']}{deps}")

        return {"success": True, "response": "\n".join(lines), "data": workflow}

    def _handle_daily_routine(self, command: str) -> Dict[str, Any]:
        routine = self._engine.workflow_generator.generate_daily_routine()
        if not routine:
            return {"success": True, "response": "Not enough morning data to generate a routine. Use NEXUS in the morning to build patterns."}

        lines = [
            f"Daily Routine: {routine['name']}",
            f"Description: {routine['description']}",
            "",
            "Steps:",
        ]
        for step in routine["steps"]:
            lines.append(f"  {step['id']}: {step['name']} -> {step['agent']}")

        return {"success": True, "response": "\n".join(lines), "data": routine}

    def _handle_most_common(self, command: str) -> Dict[str, Any]:
        freq = self._engine.tracker.get_action_frequency(days=14)
        if not freq:
            return {"success": True, "response": "No action data recorded yet."}

        lines = ["Most Common Actions (Last 14 days):\n"]
        for action, count in freq.most_common(10):
            lines.append(f"  {action}: {count} times")

        return {"success": True, "response": "\n".join(lines), "data": dict(freq.most_common(10))}

    def _handle_hourly_pattern(self, command: str) -> Dict[str, Any]:
        hourly = self._engine.tracker.get_hourly_pattern(days=14)
        if not hourly:
            return {"success": True, "response": "No hourly data recorded yet."}

        max_count = max(hourly.values()) if hourly else 1
        lines = ["Hourly Activity Pattern (Last 14 days):\n"]
        for hour in range(24):
            count = hourly.get(hour, 0)
            bar = "#" * int(count / max(max_count, 1) * 30)
            lines.append(f"  {hour:02d}:00  {count:4d}  {bar}")

        return {"success": True, "response": "\n".join(lines), "data": dict(hourly)}

    def _handle_daily_pattern(self, command: str) -> Dict[str, Any]:
        daily = self._engine.tracker.get_daily_pattern(days=14)
        if not daily:
            return {"success": True, "response": "No daily data recorded yet."}

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        max_count = max(daily.values()) if daily else 1
        lines = ["Daily Activity Pattern (Last 14 days):\n"]
        for day in range(7):
            count = daily.get(day, 0)
            bar = "#" * int(count / max(max_count, 1) * 30)
            lines.append(f"  {day_names[day]:12s}  {count:4d}  {bar}")

        return {"success": True, "response": "\n".join(lines), "data": dict(daily)}

    def _handle_prediction_accuracy(self, command: str) -> Dict[str, Any]:
        days = self._extract_number(command, default=7)
        accuracy = self._storage.get_prediction_accuracy(days=days)

        lines = [
            f"Prediction Accuracy (Last {days} days)",
            "=" * 40,
            f"Total Predictions: {accuracy['total']}",
            f"Correct Predictions: {accuracy['correct']}",
            f"Accuracy: {accuracy['accuracy']}%",
        ]

        return {"success": True, "response": "\n".join(lines), "data": accuracy}

    def _handle_cleanup(self, command: str) -> Dict[str, Any]:
        days = self._extract_number(command, default=90)
        deleted = self._engine.cleanup(days)
        return {"success": True, "response": f"Cleaned up {deleted} old behavior records."}

    def _handle_help(self, command: str) -> Dict[str, Any]:
        lines = [
            "Learning Agent Commands:",
            "",
            "Learning Control:",
            "  learn / start learning  - Start automatic learning",
            "  stop learning           - Stop learning engine",
            "  analyze                 - Run pattern analysis now",
            "",
            "Patterns & Habits:",
            "  patterns [type]         - Show learned patterns",
            "  habits                  - Show detected habits",
            "  most common             - Show most frequent actions",
            "  hourly pattern          - Show activity by hour",
            "  daily pattern           - Show activity by day",
            "",
            "Recommendations:",
            "  recommendations [type]  - Show recommendations",
            "  accept recommendation   - Accept a recommendation",
            "  dismiss recommendation  - Dismiss a recommendation",
            "",
            "Predictions:",
            "  predict / what next     - Predict next action",
            "  prediction accuracy     - Show prediction accuracy",
            "",
            "Workflows:",
            "  generate workflow [id]  - Generate workflow from pattern",
            "  daily routine           - Generate daily routine",
            "",
            "History & Stats:",
            "  behavior history        - Show behavior history",
            "  learning stats          - Show learning statistics",
            "",
            "Maintenance:",
            "  cleanup [days]          - Clean up old data",
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
