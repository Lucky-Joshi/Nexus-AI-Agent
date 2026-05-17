"""
Learning Agent Services
Core services for behavior tracking, pattern learning, recommendation generation,
pattern analysis, and adaptive workflow generation.
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from core.logger import Logger
from core.config import Config

from .models import (
    BehaviorRecord, LearnedPattern, Recommendation, UserHabit, Prediction,
    LearningStats, PatternType, ConfidenceLevel, RecommendationType, LearningStatus,
)
from .storage import LearningStorage


class BehaviorTracker:
    """Tracks and records user behaviors for learning."""

    def __init__(self, storage: LearningStorage):
        self.logger = Logger().get_logger("BehaviorTracker")
        self._storage = storage
        self._recent_actions: List[str] = []
        self._max_history = 20
        self._session_actions: List[BehaviorRecord] = []
        self._lock = threading.Lock()

    def record_behavior(self, action: str, agent: str = "", context: str = "",
                        duration: float = 0.0, success: bool = True):
        record = BehaviorRecord(
            action=action,
            agent=agent,
            context=context,
            duration_seconds=duration,
            success=success,
            preceding_actions=self._recent_actions[-5:].copy(),
        )
        self._storage.save_behavior(record.to_dict())

        with self._lock:
            self._recent_actions.append(action)
            if len(self._recent_actions) > self._max_history:
                self._recent_actions = self._recent_actions[-self._max_history:]
            self._session_actions.append(record)

        self.logger.debug(f"Behavior recorded: {action} (agent: {agent})")
        return record

    def get_recent_actions(self, limit: int = 10) -> List[str]:
        with self._lock:
            return self._recent_actions[-limit:]

    def get_session_actions(self) -> List[BehaviorRecord]:
        with self._lock:
            return self._session_actions.copy()

    def clear_session(self):
        with self._lock:
            self._session_actions.clear()

    def get_action_frequency(self, days: int = 7) -> Dict[str, int]:
        start = (datetime.now() - timedelta(days=days)).isoformat()
        behaviors = self._storage.get_behaviors(limit=1000, start_time=start)
        return Counter(b["action"] for b in behaviors)

    def get_hourly_pattern(self, days: int = 14) -> Dict[int, int]:
        start = (datetime.now() - timedelta(days=days)).isoformat()
        behaviors = self._storage.get_behaviors(limit=2000, start_time=start)
        return Counter(b["hour"] for b in behaviors)

    def get_daily_pattern(self, days: int = 14) -> Dict[int, int]:
        start = (datetime.now() - timedelta(days=days)).isoformat()
        behaviors = self._storage.get_behaviors(limit=2000, start_time=start)
        return Counter(b["day_of_week"] for b in behaviors)


class PatternAnalyzer:
    """Analyzes behavior data to detect patterns and habits."""

    def __init__(self, storage: LearningStorage, tracker: BehaviorTracker):
        self.logger = Logger().get_logger("PatternAnalyzer")
        self._storage = storage
        self._tracker = tracker
        self._patterns: Dict[str, LearnedPattern] = {}
        self._load_patterns()

    def _load_patterns(self):
        stored = self._storage.get_patterns()
        for p in stored:
            pattern = LearnedPattern.from_dict(p)
            self._patterns[pattern.id] = pattern
        self.logger.info(f"Loaded {len(self._patterns)} learned patterns")

    def analyze_and_learn(self) -> List[LearnedPattern]:
        """Run pattern analysis and update learned patterns."""
        new_patterns = []
        new_patterns.extend(self._detect_frequency_patterns())
        new_patterns.extend(self._detect_sequence_patterns())
        new_patterns.extend(self._detect_time_patterns())
        new_patterns.extend(self._detect_contextual_patterns())

        for pattern in new_patterns:
            self._patterns[pattern.id] = pattern
            self._storage.save_pattern(pattern.to_dict())

        self._update_existing_patterns()
        return new_patterns

    def _detect_frequency_patterns(self) -> List[LearnedPattern]:
        """Detect frequently repeated actions."""
        freq = self._tracker.get_action_frequency(days=14)
        new_patterns = []

        for action, count in freq.items():
            if count < 3:
                continue

            existing = self._find_pattern_by_action(action)
            if existing:
                continue

            behaviors = self._storage.get_behaviors(limit=100, action=action)
            if not behaviors:
                continue

            hours = [b["hour"] for b in behaviors]
            days = [b["day_of_week"] for b in behaviors]
            durations = [b["duration_seconds"] for b in behaviors if b["duration_seconds"] > 0]

            most_common_hour = Counter(hours).most_common(1)[0][0] if hours else 0
            most_common_day = Counter(days).most_common(1)[0][0] if days else 0
            avg_duration = sum(durations) / len(durations) if durations else 0

            hour_str = f"{most_common_hour:02d}:00"
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_str = day_names[most_common_day] if most_common_day < 7 else ""

            pattern = LearnedPattern(
                name=f"Frequent: {action}",
                pattern_type=PatternType.FREQUENCY,
                description=f"Action '{action}' performed {count} times in 14 days",
                actions=[action],
                frequency=count,
                typical_time=hour_str,
                typical_day=day_str,
                average_duration=avg_duration,
                context_triggers=list(set(b["context"] for b in behaviors if b.get("context"))),
            )
            pattern.update(success=True, duration=avg_duration)
            new_patterns.append(pattern)

        return new_patterns

    def _detect_sequence_patterns(self) -> List[LearnedPattern]:
        """Detect repeated action sequences."""
        behaviors = self._storage.get_behaviors(limit=500)
        if len(behaviors) < 10:
            return []

        sequences = defaultdict(int)
        for b in behaviors:
            preceding = tuple(b.get("preceding_actions", []))
            if preceding:
                seq_key = preceding + (b["action"],)
                sequences[seq_key] += 1

        new_patterns = []
        for seq, count in sequences.items():
            if count < 3:
                continue

            seq_name = " -> ".join(seq[-3:])
            existing = self._find_pattern_by_name(seq_name)
            if existing:
                existing.frequency = count
                existing.last_seen = datetime.now().isoformat()
                existing._update_confidence()
                self._storage.save_pattern(existing.to_dict())
                continue

            pattern = LearnedPattern(
                name=f"Sequence: {seq_name}",
                pattern_type=PatternType.SEQUENCE,
                description=f"Action sequence repeated {count} times",
                actions=list(seq),
                frequency=count,
            )
            pattern.update()
            new_patterns.append(pattern)

        return new_patterns

    def _detect_time_patterns(self) -> List[LearnedPattern]:
        """Detect time-based patterns."""
        hourly = self._tracker.get_hourly_pattern(days=14)
        daily = self._tracker.get_daily_pattern(days=14)
        new_patterns = []

        for hour, count in hourly.items():
            if count < 5:
                continue

            pattern_name = f"Hourly Pattern: {hour:02d}:00"
            existing = self._find_pattern_by_name(pattern_name)
            if existing:
                continue

            pattern = LearnedPattern(
                name=pattern_name,
                pattern_type=PatternType.TIME_BASED,
                description=f"Peak activity at {hour:02d}:00 ({count} actions)",
                frequency=count,
                typical_time=f"{hour:02d}:00",
            )
            pattern.update()
            new_patterns.append(pattern)

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, count in daily.items():
            if count < 10:
                continue

            pattern_name = f"Daily Pattern: {day_names[day]}"
            existing = self._find_pattern_by_name(pattern_name)
            if existing:
                continue

            pattern = LearnedPattern(
                name=pattern_name,
                pattern_type=PatternType.TIME_BASED,
                description=f"Peak activity on {day_names[day]} ({count} actions)",
                frequency=count,
                typical_day=day_names[day],
            )
            pattern.update()
            new_patterns.append(pattern)

        return new_patterns

    def _detect_contextual_patterns(self) -> List[LearnedPattern]:
        """Detect context-triggered patterns."""
        behaviors = self._storage.get_behaviors(limit=500)
        context_actions = defaultdict(lambda: defaultdict(int))

        for b in behaviors:
            ctx = b.get("context", "")
            if ctx:
                context_actions[ctx][b["action"]] += 1

        new_patterns = []
        for ctx, actions in context_actions.items():
            for action, count in actions.items():
                if count < 2:
                    continue

                pattern_name = f"Context: {ctx} -> {action}"
                existing = self._find_pattern_by_name(pattern_name)
                if existing:
                    continue

                pattern = LearnedPattern(
                    name=pattern_name,
                    pattern_type=PatternType.CONTEXTUAL,
                    description=f"When context is '{ctx}', action '{action}' follows ({count} times)",
                    actions=[action],
                    frequency=count,
                    context_triggers=[ctx],
                )
                pattern.update()
                new_patterns.append(pattern)

        return new_patterns

    def _update_existing_patterns(self):
        """Update confidence and status of existing patterns."""
        for pattern in self._patterns.values():
            if pattern.status == LearningStatus.DEPRECATED:
                continue
            pattern._update_confidence()
            self._storage.save_pattern(pattern.to_dict())

    def _find_pattern_by_action(self, action: str) -> Optional[LearnedPattern]:
        for p in self._patterns.values():
            if action in p.actions and p.pattern_type == PatternType.FREQUENCY:
                return p
        return None

    def _find_pattern_by_name(self, name: str) -> Optional[LearnedPattern]:
        for p in self._patterns.values():
            if p.name == name:
                return p
        return None

    def get_patterns(self, pattern_type: Optional[str] = None,
                     status: Optional[str] = None,
                     min_confidence: float = 0.0) -> List[LearnedPattern]:
        stored = self._storage.get_patterns(
            pattern_type=pattern_type,
            status=status,
            min_confidence=min_confidence,
        )
        return [LearnedPattern.from_dict(p) for p in stored]

    def detect_habits(self) -> List[UserHabit]:
        """Detect user habits from patterns."""
        patterns = self._storage.get_patterns(min_confidence=0.3)
        habits = []

        time_patterns = [p for p in patterns if p["pattern_type"] == PatternType.TIME_BASED.value]
        freq_patterns = [p for p in patterns if p["pattern_type"] == PatternType.FREQUENCY.value]

        for fp in freq_patterns:
            if fp["frequency"] < 5:
                continue

            matching_time = None
            for tp in time_patterns:
                if tp["typical_time"]:
                    matching_time = tp["typical_time"]
                    break

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            consistency = fp["confidence_score"]
            automation_potential = min(consistency * 1.5, 1.0) if fp["success_rate"] > 0.8 else 0.0

            habit = UserHabit(
                name=f"Habit: {fp['actions'][0]}",
                description=f"Regularly performs {fp['actions'][0]} ({fp['frequency']} times)",
                actions=fp["actions"],
                typical_time=matching_time or "",
                typical_days=days if fp.get("typical_day", "") in days else [],
                frequency_per_week=fp["frequency"] / 2.0,
                consistency=consistency,
                duration_minutes=fp["average_duration"] / 60.0,
                automation_potential=automation_potential,
            )
            habits.append(habit)
            self._storage.save_habit(habit.to_dict())

        return habits

    def get_habits(self) -> List[UserHabit]:
        stored = self._storage.get_habits()
        return [UserHabit.from_dict(h) for h in stored]


class RecommendationEngine:
    """Generates recommendations based on learned patterns."""

    def __init__(self, storage: LearningStorage, analyzer: PatternAnalyzer):
        self.logger = Logger().get_logger("RecommendationEngine")
        self._storage = storage
        self._analyzer = analyzer

    def generate_recommendations(self, current_context: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate recommendations based on learned patterns."""
        recs = []
        recs.extend(self._recommend_workflows())
        recs.extend(self._recommend_automations())
        recs.extend(self._recommend_optimizations())
        recs.extend(self._recommend_habits())
        recs.extend(self._recommend_apps(current_context))

        for rec in recs:
            self._storage.save_recommendation(rec.to_dict())

        return recs

    def _recommend_workflows(self) -> List[Recommendation]:
        """Recommend workflow chains based on patterns."""
        recs = []
        patterns = self._storage.get_patterns(pattern_type="sequence", min_confidence=0.4)

        for p in patterns:
            if len(p.get("actions", [])) >= 2:
                rec = Recommendation(
                    rec_type=RecommendationType.WORKFLOW,
                    title=f"Create workflow for: {' -> '.join(p['actions'][:3])}",
                    description=f"This action sequence has been repeated {p['frequency']} times. Consider creating a workflow chain.",
                    confidence=p["confidence_score"],
                    pattern_id=p["id"],
                    suggested_action="create_chain",
                    suggested_params={"actions": p["actions"], "name": p["name"]},
                    reason=f"Repeated {p['frequency']} times with {p['success_rate']:.0%} success rate",
                )
                recs.append(rec)

        return recs

    def _recommend_automations(self) -> List[Recommendation]:
        """Recommend automations for frequent actions."""
        recs = []
        patterns = self._storage.get_patterns(pattern_type="frequency", min_confidence=0.5)

        for p in patterns:
            if p["frequency"] >= 5 and p.get("automation_suggestion"):
                rec = Recommendation(
                    rec_type=RecommendationType.AUTOMATION,
                    title=f"Automate: {p['actions'][0]}",
                    description=p["automation_suggestion"],
                    confidence=p["confidence_score"],
                    pattern_id=p["id"],
                    suggested_action="create_automation",
                    suggested_params={"action": p["actions"][0], "pattern": p["name"]},
                    reason=f"Performed {p['frequency']} times, avg {p['average_duration']:.0f}s each",
                )
                recs.append(rec)

        return recs

    def _recommend_optimizations(self) -> List[Recommendation]:
        """Recommend optimizations based on patterns."""
        recs = []
        patterns = self._storage.get_patterns(min_confidence=0.3)

        slow_patterns = [p for p in patterns if p.get("average_duration", 0) > 60 and p["frequency"] >= 3]
        for p in slow_patterns:
            rec = Recommendation(
                rec_type=RecommendationType.OPTIMIZATION,
                title=f"Optimize: {p['name']}",
                description=f"This action averages {p['average_duration']:.0f}s. Consider batching or pre-loading.",
                confidence=p["confidence_score"] * 0.8,
                pattern_id=p["id"],
                suggested_action="optimize",
                suggested_params={"action": p["actions"][0], "duration": p["average_duration"]},
                reason=f"Slow action ({p['average_duration']:.0f}s) repeated {p['frequency']} times",
            )
            recs.append(rec)

        return recs

    def _recommend_habits(self) -> List[Recommendation]:
        """Recommend habit-based automations."""
        recs = []
        habits = self._storage.get_habits()

        for h in habits:
            if h.get("automation_potential", 0) > 0.5:
                rec = Recommendation(
                    rec_type=RecommendationType.HABIT,
                    title=f"Automate habit: {h['name']}",
                    description=f"You do this {h['frequency_per_week']:.1f} times/week at {h.get('typical_time', 'various times')}. Automate it?",
                    confidence=h["consistency"],
                    suggested_action="create_habit_automation",
                    suggested_params={"habit": h["name"], "time": h.get("typical_time", "")},
                    reason=f"Consistent habit ({h['consistency']:.0%}) with high automation potential",
                )
                recs.append(rec)

        return recs

    def _recommend_apps(self, context: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Recommend apps based on time and context."""
        recs = []
        if not context:
            return recs

        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()

        hourly = self._tracker.get_hourly_pattern(days=14)
        if current_hour in hourly and hourly[current_hour] > 5:
            behaviors = self._storage.get_behaviors(limit=50, hour=current_hour)
            common_actions = Counter(b["action"] for b in behaviors).most_common(3)

            for action, count in common_actions:
                rec = Recommendation(
                    rec_type=RecommendationType.APP_SUGGESTION,
                    title=f"You usually do '{action}' at this time",
                    description=f"At {current_hour:02d}:00, you typically perform '{action}' ({count} times observed).",
                    confidence=min(count / 10.0, 1.0),
                    suggested_action=action,
                    reason=f"Time-based pattern: {count} occurrences at {current_hour:02d}:00",
                )
                recs.append(rec)

        return recs

    def get_recommendations(self, rec_type: Optional[str] = None,
                            active_only: bool = True, limit: int = 20) -> List[Recommendation]:
        stored = self._storage.get_recommendations(
            rec_type=rec_type,
            active_only=active_only,
            limit=limit,
        )
        return [Recommendation.from_dict(r) for r in stored]

    def accept_recommendation(self, rec_id: str) -> bool:
        return self._storage.update_recommendation(rec_id, {"accepted": True})

    def dismiss_recommendation(self, rec_id: str) -> bool:
        return self._storage.update_recommendation(rec_id, {"dismissed": True})


class AdaptiveWorkflowGenerator:
    """Generates adaptive workflows based on learned patterns."""

    def __init__(self, storage: LearningStorage, analyzer: PatternAnalyzer):
        self.logger = Logger().get_logger("AdaptiveWorkflowGenerator")
        self._storage = storage
        self._analyzer = analyzer

    def generate_from_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Generate a workflow definition from a learned pattern."""
        pattern = self._storage.get_pattern(pattern_id)
        if not pattern:
            return None

        actions = pattern.get("actions", [])
        if len(actions) < 2:
            return None

        steps = []
        for i, action in enumerate(actions):
            step_id = f"step_{i + 1}"
            agent = self._infer_agent(action)
            steps.append({
                "id": step_id,
                "name": action,
                "agent": agent,
                "command": action,
                "depends_on": [f"step_{i}"] if i > 0 else [],
            })

        workflow = {
            "name": f"Learned: {pattern['name']}",
            "description": f"Auto-generated from pattern (frequency: {pattern['frequency']}, confidence: {pattern['confidence_score']:.2f})",
            "category": "learned",
            "steps": steps,
            "confidence": pattern["confidence_score"],
            "pattern_id": pattern_id,
        }

        return workflow

    def generate_daily_routine(self) -> Optional[Dict[str, Any]]:
        """Generate a daily routine workflow from morning patterns."""
        morning_behaviors = self._storage.get_behaviors(limit=50, hour=9)
        if len(morning_behaviors) < 3:
            return None

        common_actions = Counter(b["action"] for b in morning_behaviors).most_common(5)
        if not common_actions:
            return None

        steps = []
        for i, (action, count) in enumerate(common_actions):
            step_id = f"step_{i + 1}"
            agent = self._infer_agent(action)
            steps.append({
                "id": step_id,
                "name": action,
                "agent": agent,
                "command": action,
                "depends_on": [f"step_{i}"] if i > 0 else [],
            })

        return {
            "name": "Daily Morning Routine",
            "description": f"Auto-generated from {len(morning_behaviors)} morning observations",
            "category": "routine",
            "steps": steps,
        }

    def predict_next_action(self, recent_actions: List[str],
                           current_hour: Optional[int] = None,
                           current_context: Optional[str] = None) -> List[Prediction]:
        """Predict the next likely action based on recent behavior."""
        predictions = []

        if len(recent_actions) < 2:
            return predictions

        recent_tuple = tuple(recent_actions[-3:])
        behaviors = self._storage.get_behaviors(limit=500)

        sequence_follows = defaultdict(int)
        for b in behaviors:
            preceding = tuple(b.get("preceding_actions", [])[-3:])
            if preceding == recent_tuple or preceding[-2:] == recent_tuple[-2:]:
                sequence_follows[b["action"]] += 1

        for action, count in sequence_follows.most_common(3):
            confidence = min(count / 5.0, 1.0)
            if confidence < 0.2:
                continue

            agent = self._infer_agent(action)
            time_relevance = self._calculate_time_relevance(action, current_hour)
            context_relevance = self._calculate_context_relevance(action, current_context)

            predictions.append(Prediction(
                predicted_action=action,
                predicted_agent=agent,
                confidence=confidence,
                reason=f"Follows sequence {recent_tuple} ({count} occurrences)",
                pattern_match="sequence",
                time_relevance=time_relevance,
                context_relevance=context_relevance,
            ))

        if current_hour is not None and not predictions:
            hourly_behaviors = self._storage.get_behaviors(limit=50, hour=current_hour)
            if hourly_behaviors:
                common = Counter(b["action"] for b in hourly_behaviors).most_common(2)
                for action, count in common:
                    agent = self._infer_agent(action)
                    predictions.append(Prediction(
                        predicted_action=action,
                        predicted_agent=agent,
                        confidence=min(count / 10.0, 0.8),
                        reason=f"Common at {current_hour:02d}:00 ({count} occurrences)",
                        pattern_match="time",
                        time_relevance=0.8,
                        context_relevance=0.0,
                    ))

        return predictions

    def _infer_agent(self, action: str) -> str:
        agent_map = {
            "open": "file_agent",
            "search": "web_agent",
            "screenshot": "vision_agent",
            "run": "terminal_agent",
            "analyze": "security_agent",
            "code": "coding_agent",
            "remember": "memory_agent",
            "notify": "notification_agent",
            "schedule": "scheduler_agent",
            "chain": "workflow_chain_agent",
            "dashboard": "analytics_agent",
            "context": "context_awareness_agent",
        }
        for keyword, agent in agent_map.items():
            if keyword in action.lower():
                return agent
        return "file_agent"

    def _calculate_time_relevance(self, action: str, hour: Optional[int]) -> float:
        if hour is None:
            return 0.0
        behaviors = self._storage.get_behaviors(limit=100, action=action)
        if not behaviors:
            return 0.0
        hour_matches = sum(1 for b in behaviors if b["hour"] == hour)
        return hour_matches / len(behaviors)

    def _calculate_context_relevance(self, action: str, context: Optional[str]) -> float:
        if not context:
            return 0.0
        behaviors = self._storage.get_behaviors(limit=100, action=action)
        if not behaviors:
            return 0.0
        context_matches = sum(1 for b in behaviors if b.get("context") == context)
        return context_matches / len(behaviors)

    def log_prediction(self, prediction: Prediction, actual_action: str = ""):
        was_correct = prediction.predicted_action == actual_action if actual_action else False
        self._storage.save_prediction({
            "id": prediction.id,
            "predicted_action": prediction.predicted_action,
            "predicted_agent": prediction.predicted_agent,
            "confidence": prediction.confidence,
            "actual_action": actual_action,
            "was_correct": was_correct,
            "timestamp": datetime.now().isoformat(),
        })


class LearningEngine:
    """Central engine coordinating all learning services."""

    def __init__(self, storage: LearningStorage):
        self.logger = Logger().get_logger("LearningEngine")
        self._storage = storage
        self._tracker = BehaviorTracker(storage)
        self._analyzer = PatternAnalyzer(storage, self._tracker)
        self._recommender = RecommendationEngine(storage, self._analyzer)
        self._workflow_gen = AdaptiveWorkflowGenerator(storage, self._analyzer)

        self._learning_thread: Optional[threading.Thread] = None
        self._learning_active = False
        self._learning_interval = 300

    @property
    def tracker(self) -> BehaviorTracker:
        return self._tracker

    @property
    def analyzer(self) -> PatternAnalyzer:
        return self._analyzer

    @property
    def recommender(self) -> RecommendationEngine:
        return self._recommender

    @property
    def workflow_generator(self) -> AdaptiveWorkflowGenerator:
        return self._workflow_gen

    def start_learning(self, interval: int = 300):
        if self._learning_active:
            return
        self._learning_interval = interval
        self._learning_active = True
        self._learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self._learning_thread.start()
        self.logger.info(f"Learning engine started (interval: {interval}s)")

    def stop_learning(self):
        self._learning_active = False
        if self._learning_thread:
            self._learning_thread.join(timeout=5)
        self.logger.info("Learning engine stopped")

    def _learning_loop(self):
        while self._learning_active:
            try:
                self._analyzer.analyze_and_learn()
                self._recommender.generate_recommendations()
                self._analyzer.detect_habits()
            except Exception as e:
                self.logger.error(f"Learning loop error: {e}")
            time.sleep(self._learning_interval)

    def get_stats(self) -> LearningStats:
        stats_data = self._storage.get_stats()
        prediction_accuracy = self._storage.get_prediction_accuracy()

        patterns = self._storage.get_patterns(min_confidence=0.5)
        top_patterns = [
            {"name": p["name"], "frequency": p["frequency"], "confidence": p["confidence_score"]}
            for p in patterns[:5]
        ]

        return LearningStats(
            total_behaviors_recorded=stats_data["total_behaviors_recorded"],
            patterns_learned=stats_data["patterns_learned"],
            confirmed_patterns=stats_data["confirmed_patterns"],
            habits_detected=stats_data["habits_detected"],
            recommendations_made=stats_data["recommendations_made"],
            recommendations_accepted=stats_data["recommendations_accepted"],
            predictions_made=prediction_accuracy["total"],
            predictions_correct=prediction_accuracy["correct"],
            learning_days=stats_data["learning_days"],
            most_common_action=stats_data["most_common_action"],
            most_active_hour=stats_data["most_active_hour"],
            most_active_day=stats_data["most_active_day"],
            top_patterns=top_patterns,
        )

    def cleanup(self, days: int = 90):
        return self._storage.cleanup_old_records(days)
