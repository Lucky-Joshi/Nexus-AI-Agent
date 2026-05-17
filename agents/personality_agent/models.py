"""
Data models for the Personality Agent.
Defines personality profiles, tone states, conversation styles, and emotion tracking.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class PersonalityDimension(Enum):
    """Big Five personality dimensions."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class ToneType(Enum):
    """Conversation tone types."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    EMPATHETIC = "empathetic"
    DIRECT = "direct"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    SARCASTIC = "sarcastic"
    FORMAL = "formal"


class Emotion(Enum):
    """Simulated emotional states."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    SUPPORTIVE = "supportive"
    CONFUSED = "confused"


@dataclass
class PersonalityProfile:
    """Core personality configuration for NEXUS."""
    name: str = "NEXUS Default"
    description: str = "Balanced, helpful AI assistant"
    big_five: Dict[str, float] = field(default_factory=lambda: {
        "openness": 0.7,
        "conscientiousness": 0.8,
        "extraversion": 0.6,
        "agreeableness": 0.75,
        "neuroticism": 0.2,
    })
    default_tone: ToneType = ToneType.FRIENDLY
    humor_level: float = 0.3
    formality_level: float = 0.5
    verbosity: float = 0.6
    empathy_level: float = 0.7
    creativity: float = 0.6
    confidence: float = 0.7
    catchphrases: List[str] = field(default_factory=list)
    response_patterns: Dict[str, str] = field(default_factory=dict)
    forbidden_topics: List[str] = field(default_factory=list)
    greeting_style: str = "warm"
    signoff_style: str = "helpful"
    emoji_usage: float = 0.2
    slang_tolerance: float = 0.3
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "big_five": self.big_five,
            "default_tone": self.default_tone.value,
            "humor_level": self.humor_level,
            "formality_level": self.formality_level,
            "verbosity": self.verbosity,
            "empathy_level": self.empathy_level,
            "creativity": self.creativity,
            "confidence": self.confidence,
            "catchphrases": self.catchphrases,
            "response_patterns": self.response_patterns,
            "forbidden_topics": self.forbidden_topics,
            "greeting_style": self.greeting_style,
            "signoff_style": self.signoff_style,
            "emoji_usage": self.emoji_usage,
            "slang_tolerance": self.slang_tolerance,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonalityProfile":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "NEXUS Default"),
            description=data.get("description", ""),
            big_five=data.get("big_five", cls().big_five),
            default_tone=ToneType(data.get("default_tone", "friendly")),
            humor_level=data.get("humor_level", 0.3),
            formality_level=data.get("formality_level", 0.5),
            verbosity=data.get("verbosity", 0.6),
            empathy_level=data.get("empathy_level", 0.7),
            creativity=data.get("creativity", 0.6),
            confidence=data.get("confidence", 0.7),
            catchphrases=data.get("catchphrases", []),
            response_patterns=data.get("response_patterns", {}),
            forbidden_topics=data.get("forbidden_topics", []),
            greeting_style=data.get("greeting_style", "warm"),
            signoff_style=data.get("signoff_style", "helpful"),
            emoji_usage=data.get("emoji_usage", 0.2),
            slang_tolerance=data.get("slang_tolerance", 0.3),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )

    def apply_preset(self, preset: "PersonalityPreset"):
        """Apply a preset configuration to this profile."""
        self.name = preset.name
        self.description = preset.description
        self.big_five.update(preset.big_five)
        self.default_tone = preset.default_tone
        self.humor_level = preset.humor_level
        self.formality_level = preset.formality_level
        self.verbosity = preset.verbosity
        self.empathy_level = preset.empathy_level
        self.creativity = preset.creativity
        self.confidence = preset.confidence
        self.catchphrases = preset.catchphrases.copy()
        self.response_patterns.update(preset.response_patterns)
        self.forbidden_topics = preset.forbidden_topics.copy()
        self.greeting_style = preset.greeting_style
        self.signoff_style = preset.signoff_style
        self.emoji_usage = preset.emoji_usage
        self.slang_tolerance = preset.slang_tolerance
        self.updated_at = datetime.now().isoformat()


@dataclass
class PersonalityPreset:
    """Predefined personality configurations."""
    name: str
    description: str
    big_five: Dict[str, float]
    default_tone: ToneType
    humor_level: float = 0.3
    formality_level: float = 0.5
    verbosity: float = 0.6
    empathy_level: float = 0.7
    creativity: float = 0.6
    confidence: float = 0.7
    catchphrases: List[str] = field(default_factory=list)
    response_patterns: Dict[str, str] = field(default_factory=dict)
    forbidden_topics: List[str] = field(default_factory=list)
    greeting_style: str = "warm"
    signoff_style: str = "helpful"
    emoji_usage: float = 0.2
    slang_tolerance: float = 0.3


@dataclass
class ToneState:
    """Current tone state for a conversation."""
    current_tone: ToneType = ToneType.FRIENDLY
    intensity: float = 0.5
    adapted_to_user: bool = False
    last_adjustment: str = field(default_factory=lambda: datetime.now().isoformat())
    tone_history: List[Dict[str, Any]] = field(default_factory=list)

    def adjust(self, new_tone: ToneType, intensity: float = 0.5):
        old = self.current_tone
        self.current_tone = new_tone
        self.intensity = intensity
        self.adapted_to_user = True
        self.last_adjustment = datetime.now().isoformat()
        self.tone_history.append({
            "from": old.value,
            "to": new_tone.value,
            "intensity": intensity,
            "timestamp": self.last_adjustment,
        })
        if len(self.tone_history) > 50:
            self.tone_history = self.tone_history[-50:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_tone": self.current_tone.value,
            "intensity": self.intensity,
            "adapted_to_user": self.adapted_to_user,
            "last_adjustment": self.last_adjustment,
            "tone_history": self.tone_history[-10:],
        }


@dataclass
class EmotionState:
    """Simulated emotional state tracking."""
    current_emotion: Emotion = Emotion.NEUTRAL
    intensity: float = 0.3
    trigger: str = ""
    duration_seconds: float = 0.0
    emotion_log: List[Dict[str, Any]] = field(default_factory=list)

    def set_emotion(self, emotion: Emotion, intensity: float = 0.3, trigger: str = ""):
        self.current_emotion = emotion
        self.intensity = intensity
        self.trigger = trigger
        self.emotion_log.append({
            "emotion": emotion.value,
            "intensity": intensity,
            "trigger": trigger,
            "timestamp": datetime.now().isoformat(),
        })
        if len(self.emotion_log) > 100:
            self.emotion_log = self.emotion_log[-100:]

    def decay(self, rate: float = 0.1):
        """Gradually return to neutral."""
        if self.intensity > 0:
            self.intensity = max(0, self.intensity - rate)
            if self.intensity < 0.05:
                self.current_emotion = Emotion.NEUTRAL
                self.trigger = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_emotion": self.current_emotion.value,
            "intensity": self.intensity,
            "trigger": self.trigger,
            "emotion_log": self.emotion_log[-10:],
        }


@dataclass
class ConversationStyle:
    """Adaptive conversation style preferences."""
    response_length: str = "medium"
    use_examples: bool = True
    use_analogies: bool = True
    technical_depth: float = 0.5
    humor_frequency: float = 0.1
    question_frequency: float = 0.2
    personalization_level: float = 0.5
    greeting_used: bool = False
    signoff_used: bool = False
    user_name: str = ""
    user_preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response_length": self.response_length,
            "use_examples": self.use_examples,
            "use_analogies": self.use_analogies,
            "technical_depth": self.technical_depth,
            "humor_frequency": self.humor_frequency,
            "question_frequency": self.question_frequency,
            "personalization_level": self.personalization_level,
            "user_name": self.user_name,
            "user_preferences": self.user_preferences,
        }


@dataclass
class SessionContext:
    """Session-level personality context."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())
    message_count: int = 0
    dominant_emotion: Emotion = Emotion.NEUTRAL
    tone_adaptations: int = 0
    user_mood_detected: str = ""
    interaction_quality: float = 0.5

    def touch(self):
        self.last_active = datetime.now().isoformat()
        self.message_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_active": self.last_active,
            "message_count": self.message_count,
            "dominant_emotion": self.dominant_emotion.value,
            "tone_adaptations": self.tone_adaptations,
            "user_mood_detected": self.user_mood_detected,
            "interaction_quality": self.interaction_quality,
        }
