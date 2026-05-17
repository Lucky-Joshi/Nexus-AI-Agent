"""
Business logic services for the Personality Agent.
Handles personality engine, tone management, conversation style adaptation,
emotion simulation, and response transformation.
"""

import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.logger import Logger
from core.config import Config
from core.llm_provider import LLMProvider

from .models import (
    PersonalityProfile, PersonalityPreset, ToneState, EmotionState,
    ConversationStyle, SessionContext, ToneType, Emotion,
)
from .storage import PersonalityStorage, PresetStorage


BUILTIN_PRESETS = {
    "default": PersonalityPreset(
        name="Default",
        description="Balanced, helpful AI assistant",
        big_five={"openness": 0.7, "conscientiousness": 0.8, "extraversion": 0.6, "agreeableness": 0.75, "neuroticism": 0.2},
        default_tone=ToneType.FRIENDLY,
        humor_level=0.3, formality_level=0.5, verbosity=0.6,
        empathy_level=0.7, creativity=0.6, confidence=0.7,
        greeting_style="warm", signoff_style="helpful",
        emoji_usage=0.2, slang_tolerance=0.3,
    ),
    "professional": PersonalityPreset(
        name="Professional",
        description="Formal, precise, and business-oriented",
        big_five={"openness": 0.5, "conscientiousness": 0.95, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.1},
        default_tone=ToneType.PROFESSIONAL,
        humor_level=0.05, formality_level=0.9, verbosity=0.5,
        empathy_level=0.4, creativity=0.3, confidence=0.85,
        greeting_style="formal", signoff_style="professional",
        emoji_usage=0.0, slang_tolerance=0.0,
    ),
    "friendly": PersonalityPreset(
        name="Friendly",
        description="Warm, approachable, and conversational",
        big_five={"openness": 0.75, "conscientiousness": 0.6, "extraversion": 0.85, "agreeableness": 0.9, "neuroticism": 0.15},
        default_tone=ToneType.FRIENDLY,
        humor_level=0.5, formality_level=0.3, verbosity=0.7,
        empathy_level=0.9, creativity=0.6, confidence=0.7,
        greeting_style="warm", signoff_style="friendly",
        emoji_usage=0.4, slang_tolerance=0.5,
    ),
    "humorous": PersonalityPreset(
        name="Humorous",
        description="Witty, playful, and entertaining",
        big_five={"openness": 0.9, "conscientiousness": 0.5, "extraversion": 0.95, "agreeableness": 0.7, "neuroticism": 0.1},
        default_tone=ToneType.HUMOROUS,
        humor_level=0.9, formality_level=0.2, verbosity=0.8,
        empathy_level=0.6, creativity=0.9, confidence=0.8,
        catchphrases=["Great question!", "Let me think about that...", "Here's the fun part:"],
        greeting_style="playful", signoff_style="witty",
        emoji_usage=0.6, slang_tolerance=0.7,
    ),
    "empathetic": PersonalityPreset(
        name="Empathetic",
        description="Understanding, supportive, and caring",
        big_five={"openness": 0.8, "conscientiousness": 0.7, "extraversion": 0.5, "agreeableness": 0.95, "neuroticism": 0.3},
        default_tone=ToneType.EMPATHETIC,
        humor_level=0.15, formality_level=0.4, verbosity=0.7,
        empathy_level=0.95, creativity=0.5, confidence=0.6,
        greeting_style="gentle", signoff_style="supportive",
        emoji_usage=0.3, slang_tolerance=0.2,
    ),
    "concise": PersonalityPreset(
        name="Concise",
        description="Direct, efficient, no-nonsense",
        big_five={"openness": 0.4, "conscientiousness": 0.9, "extraversion": 0.3, "agreeableness": 0.5, "neuroticism": 0.1},
        default_tone=ToneType.DIRECT,
        humor_level=0.0, formality_level=0.6, verbosity=0.2,
        empathy_level=0.3, creativity=0.2, confidence=0.9,
        greeting_style="brief", signoff_style="minimal",
        emoji_usage=0.0, slang_tolerance=0.0,
    ),
    "enthusiastic": PersonalityPreset(
        name="Enthusiastic",
        description="Energetic, optimistic, and excited",
        big_five={"openness": 0.85, "conscientiousness": 0.6, "extraversion": 0.95, "agreeableness": 0.8, "neuroticism": 0.05},
        default_tone=ToneType.ENTHUSIASTIC,
        humor_level=0.6, formality_level=0.2, verbosity=0.8,
        empathy_level=0.7, creativity=0.8, confidence=0.85,
        catchphrases=["Awesome!", "Let's dive in!", "This is exciting!"],
        greeting_style="energetic", signoff_style="upbeat",
        emoji_usage=0.7, slang_tolerance=0.5,
    ),
    "sarcastic": PersonalityPreset(
        name="Sarcastic",
        description="Dry wit, clever, slightly irreverent",
        big_five={"openness": 0.85, "conscientiousness": 0.5, "extraversion": 0.6, "agreeableness": 0.3, "neuroticism": 0.2},
        default_tone=ToneType.SARCASTIC,
        humor_level=0.85, formality_level=0.3, verbosity=0.6,
        empathy_level=0.4, creativity=0.8, confidence=0.9,
        greeting_style="dry", signoff_style="snarky",
        emoji_usage=0.3, slang_tolerance=0.6,
    ),
}


class PersonalityEngine:
    """Core personality management: profiles, presets, and trait application."""

    def __init__(self, storage: PersonalityStorage, preset_storage: PresetStorage):
        self.logger = Logger().get_logger("PersonalityEngine")
        self._storage = storage
        self._preset_storage = preset_storage
        self._active_profile: Optional[PersonalityProfile] = None
        self._load_active_profile()

    def _load_active_profile(self):
        profile = self._storage.get_active_profile()
        if profile:
            self._active_profile = profile
        else:
            self._active_profile = PersonalityProfile()
            self._storage.save_profile(self._active_profile, active=True)
        self.logger.info(f"Active personality: {self._active_profile.name}")

    @property
    def active_profile(self) -> PersonalityProfile:
        return self._active_profile

    def apply_preset(self, preset_name: str) -> Dict[str, Any]:
        preset = BUILTIN_PRESETS.get(preset_name.lower())
        if not preset:
            preset_data = self._preset_storage.load_preset(preset_name)
            if preset_data:
                preset = PersonalityPreset(**preset_data)

        if not preset:
            available = ", ".join(BUILTIN_PRESETS.keys())
            return {"success": False, "response": f"Preset '{preset_name}' not found. Available: {available}"}

        self._active_profile.apply_preset(preset)
        self._active_profile.updated_at = datetime.now().isoformat()
        self._storage.save_profile(self._active_profile, active=True)
        self.logger.info(f"Preset applied: {preset_name}")
        return {"success": True, "response": f"Personality set to: {preset.name}\n{preset.description}"}

    def create_custom_profile(self, name: str, traits: Dict[str, Any]) -> Dict[str, Any]:
        profile = PersonalityProfile(name=name)
        for key, value in traits.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.now().isoformat()
        self._storage.save_profile(profile, active=True)
        self._active_profile = profile
        return {"success": True, "response": f"Custom profile created: {name}"}

    def list_profiles(self) -> List[PersonalityProfile]:
        return self._storage.get_all_profiles()

    def switch_profile(self, profile_id: str) -> Dict[str, Any]:
        profile = self._storage.get_profile(profile_id)
        if not profile:
            return {"success": False, "response": f"Profile {profile_id} not found."}
        self._storage.save_profile(profile, active=True)
        self._active_profile = profile
        return {"success": True, "response": f"Switched to profile: {profile.name}"}

    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        if self._active_profile and self._active_profile.id == profile_id:
            return {"success": False, "response": "Cannot delete active profile."}
        success = self._storage.delete_profile(profile_id)
        if success:
            return {"success": True, "response": f"Profile {profile_id} deleted."}
        return {"success": False, "response": f"Profile {profile_id} not found."}

    def set_trait(self, trait: str, value: float) -> Dict[str, Any]:
        valid_traits = ["humor_level", "formality_level", "verbosity", "empathy_level",
                       "creativity", "confidence", "emoji_usage", "slang_tolerance"]
        if trait not in valid_traits:
            return {"success": False, "response": f"Unknown trait: {trait}. Valid: {', '.join(valid_traits)}"}
        if not 0 <= value <= 1:
            return {"success": False, "response": "Trait value must be between 0 and 1."}
        setattr(self._active_profile, trait, value)
        self._active_profile.updated_at = datetime.now().isoformat()
        self._storage.save_profile(self._active_profile, active=True)
        return {"success": True, "response": f"{trait} set to {value:.2f}"}

    def get_profile_summary(self) -> Dict[str, Any]:
        p = self._active_profile
        lines = [
            f"Personality: {p.name}",
            f"  {p.description}",
            f"  Tone: {p.default_tone.value}",
            f"  Humor: {p.humor_level:.2f} | Formality: {p.formality_level:.2f}",
            f"  Verbosity: {p.verbosity:.2f} | Empathy: {p.empathy_level:.2f}",
            f"  Creativity: {p.creativity:.2f} | Confidence: {p.confidence:.2f}",
            f"  Emoji: {p.emoji_usage:.2f} | Slang: {p.slang_tolerance:.2f}",
        ]
        if p.catchphrases:
            lines.append(f"  Catchphrases: {', '.join(p.catchphrases[:3])}")
        return {"success": True, "response": "\n".join(lines), "data": p.to_dict()}


class ToneManager:
    """Manages conversation tone: detection, adaptation, and application."""

    def __init__(self, profile: PersonalityProfile, llm_provider: Optional[LLMProvider] = None):
        self.logger = Logger().get_logger("ToneManager")
        self._profile = profile
        self._llm = llm_provider
        self._tone_state = ToneState()

    @property
    def tone_state(self) -> ToneState:
        return self._tone_state

    def detect_user_tone(self, message: str) -> ToneType:
        """Detect the tone of the user's message."""
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["please", "thank", "appreciate", "wonderful", "great", "love"]):
            return ToneType.FRIENDLY
        if any(w in msg_lower for w in ["urgent", "asap", "immediately", "need this now", "critical"]):
            return ToneType.DIRECT
        if any(w in msg_lower for w in ["haha", "lol", "funny", "joke", "lmao", "rofl"]):
            return ToneType.HUMOROUS
        if any(w in msg_lower for w in ["sad", "upset", "worried", "stressed", "anxious", "help me"]):
            return ToneType.EMPATHETIC
        if any(w in msg_lower for w in ["wow", "amazing", "awesome", "incredible", "excited"]):
            return ToneType.ENTHUSIASTIC
        if any(w in msg_lower for w in ["formal", "professional", "business", "report", "document"]):
            return ToneType.PROFESSIONAL
        if any(w in msg_lower for w in ["whatever", "yeah right", "sure", "ok fine"]):
            return ToneType.SARCASTIC
        if any(w in msg_lower for w in ["calm", "relax", "peaceful", "quiet", "meditat"]):
            return ToneType.CALM

        return self._profile.default_tone

    def adapt_tone(self, user_tone: ToneType, context: Optional[SessionContext] = None):
        """Adapt NEXUS tone based on user's detected tone and personality profile."""
        mapping = {
            ToneType.FRIENDLY: (ToneType.FRIENDLY, 0.6),
            ToneType.DIRECT: (ToneType.PROFESSIONAL, 0.7),
            ToneType.HUMOROUS: (ToneType.HUMOROUS, min(1.0, self._profile.humor_level + 0.3)),
            ToneType.EMPATHETIC: (ToneType.EMPATHETIC, 0.8),
            ToneType.ENTHUSIASTIC: (ToneType.ENTHUSIASTIC, 0.7),
            ToneType.PROFESSIONAL: (ToneType.PROFESSIONAL, 0.8),
            ToneType.SARCASTIC: (ToneType.CASUAL, 0.4),
            ToneType.CALM: (ToneType.CALM, 0.6),
        }

        target_tone, intensity = mapping.get(user_tone, (self._profile.default_tone, 0.5))

        if self._profile.formality_level > 0.7:
            target_tone = ToneType.PROFESSIONAL
            intensity = min(1.0, intensity + 0.2)

        if self._profile.humor_level > 0.7 and user_tone != ToneType.EMPATHETIC:
            target_tone = ToneType.HUMOROUS
            intensity = min(1.0, intensity + 0.2)

        self._tone_state.adjust(target_tone, intensity)
        if context:
            context.tone_adaptations += 1

    def apply_tone(self, response: str) -> str:
        """Apply current tone styling to a response."""
        tone = self._tone_state.current_tone
        intensity = self._tone_state.intensity

        if tone == ToneType.HUMOROUS and intensity > 0.5 and random.random() < self._profile.humor_level:
            response = self._add_humor(response)

        if tone == ToneType.EMPATHETIC and intensity > 0.5:
            response = self._add_empathy(response)

        if tone == ToneType.PROFESSIONAL and intensity > 0.5:
            response = self._add_formality(response)

        if tone == ToneType.ENTHUSIASTIC and intensity > 0.5:
            response = self._add_enthusiasm(response)

        if tone == ToneType.CALM:
            response = self._add_calm(response)

        if self._profile.emoji_usage > 0.3 and random.random() < self._profile.emoji_usage:
            response = self._add_emoji(response)

        return response

    def _add_humor(self, text: str) -> str:
        humor_additions = [
            "\n\n(That's my two cents, for what it's worth!)",
            "\n\n(Just trying to be helpful here!)",
            "\n\n(No charge for the advice, but tips are appreciated.)",
            "\n\n(I promise I'm not making this up... mostly.)",
        ]
        if self._profile.catchphrases:
            humor_additions.extend(self._profile.catchphrases)
        return text + random.choice(humor_additions)

    def _add_empathy(self, text: str) -> str:
        empathy_additions = [
            "I understand this might be challenging. ",
            "I'm here to help you through this. ",
            "Take your time, I'm not going anywhere. ",
        ]
        if not text.startswith(("I understand", "I'm here", "Take your")):
            return random.choice(empathy_additions) + text
        return text

    def _add_formality(self, text: str) -> str:
        if not text.startswith(("Certainly", "Indeed", "Regarding", "Please note")):
            return "Certainly. " + text
        return text

    def _add_enthusiasm(self, text: str) -> str:
        enthusiasm_additions = [
            "Great news! ",
            "Here's what I found: ",
            "Let me share this with you: ",
        ]
        if not text.startswith(("Great", "Here's", "Let me")):
            return random.choice(enthusiasm_additions) + text
        return text

    def _add_calm(self, text: str) -> str:
        if not text.startswith(("Take a moment", "Let's look at", "Here's a calm breakdown")):
            return "Let's look at this step by step. " + text
        return text

    def _add_emoji(self, text: str) -> str:
        emojis = ["✨", "💡", "👍", "🎯", "📌", "🔍", "💬", "🌟"]
        if random.random() < self._profile.emoji_usage:
            return text + " " + random.choice(emojis)
        return text


class StyleAdapter:
    """Adapts conversation style based on user preferences and session context."""

    def __init__(self, profile: PersonalityProfile):
        self.logger = Logger().get_logger("StyleAdapter")
        self._profile = profile
        self._styles: Dict[str, ConversationStyle] = {}

    def get_style(self, session_id: str) -> ConversationStyle:
        if session_id not in self._styles:
            self._styles[session_id] = ConversationStyle()
        return self._styles[session_id]

    def adapt_to_user(self, session_id: str, user_messages: List[str]) -> ConversationStyle:
        """Adapt style based on observed user communication patterns."""
        style = self.get_style(session_id)

        if not user_messages:
            return style

        avg_length = sum(len(m) for m in user_messages) / len(user_messages)
        if avg_length < 50:
            style.response_length = "short"
        elif avg_length > 300:
            style.response_length = "long"
        else:
            style.response_length = "medium"

        technical_terms = sum(1 for m in user_messages if re.search(r"\b(api|function|class|import|deploy|config|server|database|query)\b", m.lower()))
        style.technical_depth = min(1.0, technical_terms / max(len(user_messages), 1) * 2)

        questions = sum(1 for m in user_messages if "?" in m)
        style.question_frequency = min(1.0, questions / max(len(user_messages), 1) * 1.5)

        slang_count = sum(1 for m in user_messages if re.search(r"\b(lol|lmao|btw|imo|tbh|gonna|wanna|gotta)\b", m.lower()))
        if slang_count > len(user_messages) * 0.3:
            style.user_preferences["uses_slang"] = True

        return style

    def generate_system_prompt(self, style: ConversationStyle) -> str:
        """Generate a system prompt that encodes personality and style."""
        p = self._profile
        parts = [
            f"You are NEXUS, an AI assistant with the following personality:",
            f"- Tone: {p.default_tone.value}",
            f"- Humor level: {p.humor_level:.0%}",
            f"- Formality: {p.formality_level:.0%}",
            f"- Verbosity: {p.verbosity:.0%}",
            f"- Empathy: {p.empathy_level:.0%}",
            f"- Creativity: {p.creativity:.0%}",
            f"- Confidence: {p.confidence:.0%}",
        ]

        if style.user_name:
            parts.append(f"- The user's name is {style.user_name}. Address them naturally.")

        if style.response_length == "short":
            parts.append("- Keep responses brief and direct.")
        elif style.response_length == "long":
            parts.append("- Provide detailed, thorough responses.")

        if style.technical_depth > 0.7:
            parts.append("- Use technical language and assume expertise.")
        elif style.technical_depth < 0.3:
            parts.append("- Explain concepts simply, avoid jargon.")

        if style.use_examples:
            parts.append("- Include examples when helpful.")
        if style.use_analogies:
            parts.append("- Use analogies to explain complex concepts.")

        if p.forbidden_topics:
            parts.append(f"- Avoid these topics: {', '.join(p.forbidden_topics)}")

        return "\n".join(parts)


class EmotionSimulator:
    """Simulates emotional responses based on conversation context."""

    EMOTION_TRIGGERS = {
        Emotion.HAPPY: ["great", "awesome", "amazing", "wonderful", "fantastic", "excellent", "perfect", "love", "happy"],
        Emotion.CURIOUS: ["how", "why", "what if", "explain", "tell me", "wonder", "curious"],
        Emotion.CONCERNED: ["error", "problem", "issue", "broken", "fail", "crash", "bug", "worried", "help"],
        Emotion.EXCITED: ["wow", "incredible", "unbelievable", "mind-blown", "holy", "yes", "finally"],
        Emotion.THOUGHTFUL: ["think", "consider", "analyze", "compare", "evaluate", "assess", "ponder"],
        Emotion.PLAYFUL: ["joke", "fun", "game", "play", "trick", "riddle", "guess"],
        Emotion.SERIOUS: ["important", "critical", "urgent", "essential", "must", "require"],
        Emotion.SUPPORTIVE: ["thank", "appreciate", "grateful", "help", "support", "thanks"],
        Emotion.CONFUSED: ["confused", "don't understand", "unclear", "lost", "what does", "huh"],
    }

    def __init__(self):
        self.logger = Logger().get_logger("EmotionSimulator")
        self._states: Dict[str, EmotionState] = {}

    def get_state(self, session_id: str) -> EmotionState:
        if session_id not in self._states:
            self._states[session_id] = EmotionState()
        return self._states[session_id]

    def detect_emotion(self, message: str) -> Tuple[Emotion, float]:
        """Detect emotion from user message."""
        msg_lower = message.lower()
        scores = {}

        for emotion, triggers in self.EMOTION_TRIGGERS.items():
            count = sum(1 for t in triggers if t in msg_lower)
            if count > 0:
                scores[emotion] = min(1.0, count * 0.3)

        if not scores:
            return Emotion.NEUTRAL, 0.0

        best_emotion = max(scores, key=scores.get)
        return best_emotion, scores[best_emotion]

    def update_emotion(self, session_id: str, message: str) -> EmotionState:
        """Update emotional state based on message."""
        state = self.get_state(session_id)
        emotion, intensity = self.detect_emotion(message)

        if emotion != Emotion.NEUTRAL and intensity > state.intensity:
            state.set_emotion(emotion, intensity, trigger=message[:50])
        else:
            state.decay(rate=0.05)

        return state

    def get_emotional_response(self, session_id: str) -> str:
        """Get an emotional prefix/suffix based on current state."""
        state = self.get_state(session_id)
        if state.current_emotion == Emotion.NEUTRAL or state.intensity < 0.2:
            return ""

        responses = {
            Emotion.HAPPY: ["I'm glad to hear that! ", "That's wonderful! "],
            Emotion.CURIOUS: ["Interesting question! ", "Let me think about that... "],
            Emotion.CONCERNED: ["I understand your concern. ", "Let me help you with that. "],
            Emotion.EXCITED: ["That's exciting! ", "I love the energy! "],
            Emotion.THOUGHTFUL: ["That's a thoughtful question. ", "Let me consider this carefully. "],
            Emotion.PLAYFUL: ["Oh, I like where this is going! ", "Fun question! "],
            Emotion.SERIOUS: ["I take this seriously. ", "Understood. "],
            Emotion.SUPPORTIVE: ["You're welcome! ", "Happy to help! "],
            Emotion.CONFUSED: ["Let me clarify that for you. ", "Good question, let me explain. "],
        }

        options = responses.get(state.current_emotion, [""])
        return random.choice(options) if random.random() < state.intensity else ""


class ResponseTransformer:
    """Transforms raw responses through personality filters."""

    def __init__(self, profile: PersonalityProfile, tone_manager: ToneManager,
                 emotion_simulator: EmotionSimulator):
        self.logger = Logger().get_logger("ResponseTransformer")
        self._profile = profile
        self._tone_manager = tone_manager
        self._emotion_simulator = emotion_simulator

    def transform(self, response: str, session_id: str = "",
                  user_message: str = "") -> str:
        """Apply all personality transformations to a response."""
        if not response:
            return response

        emotional_prefix = ""
        if session_id and user_message:
            self._emotion_simulator.update_emotion(session_id, user_message)
            emotional_prefix = self._emotion_simulator.get_emotional_response(session_id)

        response = self._tone_manager.apply_tone(response)
        response = self._adjust_length(response)
        response = self._apply_catchphrases(response)

        if emotional_prefix:
            response = emotional_prefix + response

        return response

    def _adjust_length(self, text: str) -> str:
        verbosity = self._profile.verbosity
        if verbosity < 0.3 and len(text) > 200:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            return " ".join(sentences[:3]) + "..."
        elif verbosity > 0.8 and len(text) < 100:
            return text + "\n\nLet me know if you need more details on any part of this."
        return text

    def _apply_catchphrases(self, text: str) -> str:
        if not self._profile.catchphrases:
            return text
        if random.random() < 0.15:
            return random.choice(self._profile.catchphrases) + "\n\n" + text
        return text

    def generate_greeting(self, session_id: str = "") -> str:
        """Generate a personality-appropriate greeting."""
        style = self._profile.greeting_style
        greetings = {
            "warm": ["Hey there! ", "Hello! Good to see you. ", "Hi! How can I help today? "],
            "formal": ["Greetings. ", "Good day. How may I assist you? ", "Hello. "],
            "playful": ["Well hello there! ", "Look who it is! ", "What's shaking? "],
            "gentle": ["Hello, how are you doing? ", "Hi there, take your time. ", "Welcome. "],
            "energetic": ["Hey! Ready to get things done? ", "Hi! Let's make today awesome! "],
            "brief": ["Hi. ", "Hello. ", "Ready. "],
            "dry": ["Oh, it's you. ", "Back again? ", "What do you need? "],
        }
        options = greetings.get(style, greetings["warm"])
        return random.choice(options)

    def generate_signoff(self, session_id: str = "") -> str:
        """Generate a personality-appropriate signoff."""
        style = self._profile.signoff_style
        signoffs = {
            "helpful": ["Let me know if you need anything else!", "Happy to help anytime!", "Just ask if you have more questions."],
            "professional": ["Best regards.", "Regards.", "At your service."],
            "friendly": ["Take care!", "See you later!", "Catch you next time!"],
            "witty": ["I'll be here, plotting my next response.", "Until next time, stay curious!", "That's all, folks... for now."],
            "supportive": ["I'm always here for you.", "You've got this!", "Remember, I'm just a message away."],
            "minimal": ["Done.", "OK.", "Bye."],
            "upbeat": ["Have an amazing day!", "Keep being awesome!", "Let's do it again soon!"],
            "snarky": ["Try not to miss me too much.", "I'll try to survive without you.", "Until the next crisis..."],
        }
        options = signoffs.get(style, signoffs["helpful"])
        return "\n\n" + random.choice(options)
