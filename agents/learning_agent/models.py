"""
Learning Agent Models
Data structures for behavior tracking, pattern learning, and recommendations.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class PatternType(Enum):
    SEQUENCE = "sequence"
    FREQUENCY = "frequency"
    TIME_BASED = "time_based"
    CONTEXTUAL = "contextual"
    CONDITIONAL = "conditional"
    HABIT = "habit"


class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RecommendationType(Enum):
    WORKFLOW = "workflow"
    AUTOMATION = "automation"
    APP_SUGGESTION = "app_suggestion"
    OPTIMIZATION = "optimization"
    HABIT = "habit"
    CLEANUP = "cleanup"
    MODE = "mode"


class LearningStatus(Enum):
    OBSERVING = "observing"
    LEARNING = "learning"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


@dataclass
class BehaviorRecord:
    """A single observed user behavior."""
    action: str
    agent: str = ""
    context: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    hour: int = 0
    day_of_week: int = 0
    is_weekday: bool = True
    preceding_actions: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    success: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __post_init__(self):
        if not self.hour:
            self.hour = datetime.now().hour
        if not self.day_of_week:
            self.day_of_week = datetime.now().weekday()
        self.is_weekday = self.day_of_week < 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "agent": self.agent,
            "context": self.context,
            "timestamp": self.timestamp,
            "hour": self.hour,
            "day_of_week": self.day_of_week,
            "is_weekday": self.is_weekday,
            "preceding_actions": self.preceding_actions,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BehaviorRecord":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            action=data.get("action", ""),
            agent=data.get("agent", ""),
            context=data.get("context", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            hour=data.get("hour", datetime.now().hour),
            day_of_week=data.get("day_of_week", datetime.now().weekday()),
            is_weekday=data.get("is_weekday", True),
            preceding_actions=data.get("preceding_actions", []),
            duration_seconds=data.get("duration_seconds", 0.0),
            success=data.get("success", True),
        )


@dataclass
class LearnedPattern:
    """A pattern learned from user behavior."""
    name: str
    pattern_type: PatternType
    description: str = ""
    actions: List[str] = field(default_factory=list)
    frequency: int = 0
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    confidence_score: float = 0.0
    typical_time: str = ""
    typical_day: str = ""
    context_triggers: List[str] = field(default_factory=list)
    average_duration: float = 0.0
    success_rate: float = 0.0
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    status: LearningStatus = LearningStatus.OBSERVING
    automation_suggestion: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "pattern_type": self.pattern_type.value,
            "description": self.description,
            "actions": self.actions,
            "frequency": self.frequency,
            "confidence": self.confidence.value,
            "confidence_score": round(self.confidence_score, 3),
            "typical_time": self.typical_time,
            "typical_day": self.typical_day,
            "context_triggers": self.context_triggers,
            "average_duration": round(self.average_duration, 1),
            "success_rate": round(self.success_rate, 2),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "status": self.status.value,
            "automation_suggestion": self.automation_suggestion,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearnedPattern":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            pattern_type=PatternType(data.get("pattern_type", "frequency")),
            description=data.get("description", ""),
            actions=data.get("actions", []),
            frequency=data.get("frequency", 0),
            confidence=ConfidenceLevel(data.get("confidence", "low")),
            confidence_score=data.get("confidence_score", 0.0),
            typical_time=data.get("typical_time", ""),
            typical_day=data.get("typical_day", ""),
            context_triggers=data.get("context_triggers", []),
            average_duration=data.get("average_duration", 0.0),
            success_rate=data.get("success_rate", 0.0),
            first_seen=data.get("first_seen", datetime.now().isoformat()),
            last_seen=data.get("last_seen", datetime.now().isoformat()),
            status=LearningStatus(data.get("status", "observing")),
            automation_suggestion=data.get("automation_suggestion", ""),
        )

    def update(self, success: bool = True, duration: float = 0.0):
        self.frequency += 1
        self.last_seen = datetime.now().isoformat()
        if duration > 0:
            total = self.average_duration * (self.frequency - 1) + duration
            self.average_duration = total / self.frequency
        if self.frequency > 0:
            total_success = self.success_rate * (self.frequency - 1) + (1.0 if success else 0.0)
            self.success_rate = total_success / self.frequency
        self._update_confidence()

    def _update_confidence(self):
        score = 0.0
        if self.frequency >= 3:
            score += 0.2
        if self.frequency >= 5:
            score += 0.1
        if self.frequency >= 10:
            score += 0.1
        if self.success_rate > 0.8:
            score += 0.2
        if self.success_rate > 0.95:
            score += 0.1
        if self.average_duration > 0:
            score += 0.1
        if self.context_triggers:
            score += 0.1
        if self.typical_time:
            score += 0.1

        self.confidence_score = min(score, 1.0)
        if self.confidence_score >= 0.8:
            self.confidence = ConfidenceLevel.VERY_HIGH
            if self.status == LearningStatus.LEARNING:
                self.status = LearningStatus.CONFIRMED
        elif self.confidence_score >= 0.6:
            self.confidence = ConfidenceLevel.HIGH
            if self.status == LearningStatus.OBSERVING:
                self.status = LearningStatus.LEARNING
        elif self.confidence_score >= 0.3:
            self.confidence = ConfidenceLevel.MEDIUM
            if self.status == LearningStatus.OBSERVING:
                self.status = LearningStatus.LEARNING
        else:
            self.confidence = ConfidenceLevel.LOW


@dataclass
class Recommendation:
    """A recommendation generated by the learning engine."""
    rec_type: RecommendationType
    title: str
    description: str
    confidence: float = 0.0
    pattern_id: str = ""
    suggested_action: str = ""
    suggested_params: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    dismissed: bool = False
    accepted: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rec_type": self.rec_type.value,
            "title": self.title,
            "description": self.description,
            "confidence": round(self.confidence, 3),
            "pattern_id": self.pattern_id,
            "suggested_action": self.suggested_action,
            "suggested_params": self.suggested_params,
            "reason": self.reason,
            "dismissed": self.dismissed,
            "accepted": self.accepted,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recommendation":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            rec_type=RecommendationType(data.get("rec_type", "workflow")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            confidence=data.get("confidence", 0.0),
            pattern_id=data.get("pattern_id", ""),
            suggested_action=data.get("suggested_action", ""),
            suggested_params=data.get("suggested_params", {}),
            reason=data.get("reason", ""),
            dismissed=data.get("dismissed", False),
            accepted=data.get("accepted", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )

    def accept(self):
        self.accepted = True
        self.dismissed = False

    def dismiss(self):
        self.dismissed = True
        self.accepted = False


@dataclass
class UserHabit:
    """A detected user habit."""
    name: str
    description: str = ""
    actions: List[str] = field(default_factory=list)
    typical_time: str = ""
    typical_days: List[str] = field(default_factory=list)
    frequency_per_week: float = 0.0
    consistency: float = 0.0
    duration_minutes: float = 0.0
    context: str = ""
    automation_potential: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "actions": self.actions,
            "typical_time": self.typical_time,
            "typical_days": self.typical_days,
            "frequency_per_week": round(self.frequency_per_week, 1),
            "consistency": round(self.consistency, 2),
            "duration_minutes": round(self.duration_minutes, 1),
            "context": self.context,
            "automation_potential": round(self.automation_potential, 2),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserHabit":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            actions=data.get("actions", []),
            typical_time=data.get("typical_time", ""),
            typical_days=data.get("typical_days", []),
            frequency_per_week=data.get("frequency_per_week", 0.0),
            consistency=data.get("consistency", 0.0),
            duration_minutes=data.get("duration_minutes", 0.0),
            context=data.get("context", ""),
            automation_potential=data.get("automation_potential", 0.0),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


@dataclass
class Prediction:
    """A predicted next action based on learned patterns."""
    predicted_action: str
    predicted_agent: str = ""
    confidence: float = 0.0
    reason: str = ""
    pattern_match: str = ""
    time_relevance: float = 0.0
    context_relevance: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "predicted_action": self.predicted_action,
            "predicted_agent": self.predicted_agent,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "pattern_match": self.pattern_match,
            "time_relevance": round(self.time_relevance, 3),
            "context_relevance": round(self.context_relevance, 3),
        }


@dataclass
class LearningStats:
    """Aggregate learning statistics."""
    total_behaviors_recorded: int = 0
    patterns_learned: int = 0
    confirmed_patterns: int = 0
    habits_detected: int = 0
    recommendations_made: int = 0
    recommendations_accepted: int = 0
    predictions_made: int = 0
    predictions_correct: int = 0
    learning_days: int = 0
    most_common_action: str = ""
    most_active_hour: int = 0
    most_active_day: str = ""
    top_patterns: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_behaviors_recorded": self.total_behaviors_recorded,
            "patterns_learned": self.patterns_learned,
            "confirmed_patterns": self.confirmed_patterns,
            "habits_detected": self.habits_detected,
            "recommendations_made": self.recommendations_made,
            "recommendations_accepted": self.recommendations_accepted,
            "predictions_made": self.predictions_made,
            "predictions_correct": self.predictions_correct,
            "learning_days": self.learning_days,
            "most_common_action": self.most_common_action,
            "most_active_hour": self.most_active_hour,
            "most_active_day": self.most_active_day,
            "top_patterns": self.top_patterns,
        }
