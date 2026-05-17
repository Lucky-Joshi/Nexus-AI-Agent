"""
Personality Agent for NEXUS.
Provides human-like interaction style, emotional tone, conversational consistency,
and personalization through persistent personality profiles.
"""

import re
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config
from core.llm_provider import LLMProvider

from .models import (
    PersonalityProfile, ToneType, Emotion,
    ConversationStyle, SessionContext,
)
from .storage import PersonalityStorage, PresetStorage
from .services import (
    PersonalityEngine, ToneManager, StyleAdapter,
    EmotionSimulator, ResponseTransformer, BUILTIN_PRESETS,
)


class PersonalityAgent(BaseAgent):
    """
    Personality agent for NEXUS.
    Thin orchestrator delegating to specialized service classes.
    """

    def __init__(self):
        super().__init__("personality_agent", "Personality management, tone adaptation, and conversational style")
        self.logger = Logger().get_logger("PersonalityAgent")
        self.config = Config()

        self._storage = PersonalityStorage()
        self._preset_storage = PresetStorage()

        self._engine = PersonalityEngine(
            storage=self._storage,
            preset_storage=self._preset_storage,
        )

        llm = None
        if self.config.get("llm.use_in_agents", True):
            try:
                llm = LLMProvider(self.config)
            except Exception as e:
                self.logger.warning(f"LLM not available for PersonalityAgent: {e}")

        self._tone_manager = ToneManager(
            profile=self._engine.active_profile,
            llm_provider=llm,
        )
        self._style_adapter = StyleAdapter(profile=self._engine.active_profile)
        self._emotion_simulator = EmotionSimulator()
        self._transformer = ResponseTransformer(
            profile=self._engine.active_profile,
            tone_manager=self._tone_manager,
            emotion_simulator=self._emotion_simulator,
        )

        self._sessions: Dict[str, SessionContext] = {}

        self.logger.info(f"PersonalityAgent initialized (profile: {self._engine.active_profile.name})")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["reset personality", "reset persona", "default personality"]):
                return self._handle_reset()

            elif self._matches(cmd, ["set personality", "set persona", "switch personality", "switch persona"]):
                return self._handle_set_preset(command)

            elif self._matches(cmd, ["list personalities", "list personas", "show personalities", "show personas"]):
                return self._handle_list_presets()

            elif self._matches(cmd, ["personality status", "persona status", "my personality", "current personality"]):
                return self._handle_status()

            elif self._matches(cmd, ["set tone", "change tone", "switch tone"]):
                return self._handle_set_tone(command)

            elif self._matches(cmd, ["set humor", "humor level", "be funny", "be serious"]):
                return self._handle_set_humor(command)

            elif self._matches(cmd, ["set formality", "formality level", "be formal", "be casual"]):
                return self._handle_set_formality(command)

            elif self._matches(cmd, ["set verbosity", "verbosity level", "be brief", "be detailed"]):
                return self._handle_set_verbosity(command)

            elif self._matches(cmd, ["set empathy", "empathy level", "be empathetic"]):
                return self._handle_set_empathy(command)

            elif self._matches(cmd, ["set creativity", "creativity level", "be creative"]):
                return self._handle_set_creativity(command)

            elif self._matches(cmd, ["set confidence", "confidence level"]):
                return self._handle_set_confidence(command)

            elif self._matches(cmd, ["set emoji", "emoji usage", "use emoji"]):
                return self._handle_set_emoji(command)

            elif self._matches(cmd, ["set slang", "slang tolerance", "use slang"]):
                return self._handle_set_slang(command)

            elif self._matches(cmd, ["create profile", "create personality", "new profile"]):
                return self._handle_create_profile(command)

            elif self._matches(cmd, ["list profiles", "show profiles", "all profiles"]):
                return self._handle_list_profiles()

            elif self._matches(cmd, ["switch profile", "use profile", "select profile"]):
                return self._handle_switch_profile(command)

            elif self._matches(cmd, ["delete profile", "remove profile"]):
                return self._handle_delete_profile(command)

            elif self._matches(cmd, ["set user name", "my name is", "call me"]):
                return self._handle_set_user_name(command)

            elif self._matches(cmd, ["set greeting", "greeting style"]):
                return self._handle_set_greeting(command)

            elif self._matches(cmd, ["set signoff", "signoff style"]):
                return self._handle_set_signoff(command)

            elif self._matches(cmd, ["emotion status", "current emotion", "how are you feeling"]):
                return self._handle_emotion_status(command)

            elif self._matches(cmd, ["session status", "session info", "how long talking"]):
                return self._handle_session_status(command)

            elif self._matches(cmd, ["personality stats", "persona stats"]):
                return self._handle_stats()

            elif self._matches(cmd, ["transform response", "apply personality"]):
                return self._handle_transform(command)

            elif self._matches(cmd, ["detect tone", "analyze tone", "what tone"]):
                return self._handle_detect_tone(command)

            elif self._matches(cmd, ["greet", "say hello", "greeting"]):
                return self._handle_greet(command)

            else:
                return self._handle_status()

        except Exception as e:
            self.logger.error(f"PersonalityAgent error: {e}")
            return {
                "success": False,
                "response": f"Personality error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "set_personality_preset",
            "list_presets",
            "personality_status",
            "set_tone",
            "set_humor",
            "set_formality",
            "set_verbosity",
            "set_empathy",
            "set_creativity",
            "set_confidence",
            "set_emoji",
            "set_slang",
            "create_profile",
            "list_profiles",
            "switch_profile",
            "delete_profile",
            "set_user_name",
            "set_greeting_style",
            "set_signoff_style",
            "emotion_status",
            "session_status",
            "personality_stats",
            "reset_personality",
            "transform_response",
            "detect_tone",
            "generate_greeting",
        ]

    def transform_response(self, response: str, session_id: str = "",
                           user_message: str = "") -> str:
        """Programmatic API: transform a response through personality filters."""
        return self._transformer.transform(response, session_id, user_message)

    def generate_greeting(self, session_id: str = "") -> str:
        """Programmatic API: generate a personality-appropriate greeting."""
        return self._transformer.generate_greeting(session_id)

    def generate_signoff(self, session_id: str = "") -> str:
        """Programmatic API: generate a personality-appropriate signoff."""
        return self._transformer.generate_signoff(session_id)

    def get_system_prompt(self, session_id: str = "") -> str:
        """Programmatic API: get personality-encoded system prompt for LLM."""
        style = self._style_adapter.get_style(session_id)
        return self._style_adapter.generate_system_prompt(style)

    def detect_user_tone(self, message: str) -> ToneType:
        """Programmatic API: detect user's tone from message."""
        return self._tone_manager.detect_user_tone(message)

    def adapt_session(self, session_id: str, user_messages: List[str]):
        """Programmatic API: adapt conversation style based on user history."""
        style = self._style_adapter.adapt_to_user(session_id, user_messages)
        user_tone = self._tone_manager.detect_user_tone(user_messages[-1] if user_messages else "")
        context = self._get_session_context(session_id)
        self._tone_manager.adapt_tone(user_tone, context)

    def _handle_set_preset(self, command: str) -> Dict[str, Any]:
        preset = self._extract_content(command, [
            "set personality ", "set persona ", "switch personality ", "switch persona ",
        ])
        if not preset:
            available = ", ".join(BUILTIN_PRESETS.keys())
            return {"success": False, "response": f"Please specify a preset. Available: {available}"}

        result = self._engine.apply_preset(preset)
        if result["success"]:
            self._tone_manager = ToneManager(
                profile=self._engine.active_profile,
            )
            self._style_adapter = StyleAdapter(profile=self._engine.active_profile)
            self._transformer = ResponseTransformer(
                profile=self._engine.active_profile,
                tone_manager=self._tone_manager,
                emotion_simulator=self._emotion_simulator,
            )
        return result

    def _handle_list_presets(self) -> Dict[str, Any]:
        lines = ["Available personality presets:\n"]
        for name, preset in BUILTIN_PRESETS.items():
            lines.append(f"  {name}: {preset.description}")
            lines.append(f"    Tone: {preset.default_tone.value} | Humor: {preset.humor_level:.0%} | Formality: {preset.formality_level:.0%}")
        return {"success": True, "response": "\n".join(lines)}

    def _handle_status(self) -> Dict[str, Any]:
        return self._engine.get_profile_summary()

    def _handle_set_tone(self, command: str) -> Dict[str, Any]:
        tone_str = self._extract_content(command, [
            "set tone ", "change tone ", "switch tone ",
        ])
        if not tone_str:
            return {"success": False, "response": "Please specify a tone. Available: " + ", ".join(t.value for t in ToneType)}

        try:
            tone = ToneType(tone_str.lower())
        except ValueError:
            return {"success": False, "response": f"Unknown tone: {tone_str}. Available: {', '.join(t.value for t in ToneType)}"}

        self._tone_manager.tone_state.adjust(tone, 0.7)
        return {"success": True, "response": f"Tone set to: {tone.value}"}

    def _handle_set_humor(self, command: str) -> Dict[str, Any]:
        if "be funny" in command.lower():
            return self._engine.set_trait("humor_level", 0.8)
        if "be serious" in command.lower():
            return self._engine.set_trait("humor_level", 0.0)
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify a humor level (0-100). Example: 'set humor 50'"}
        return self._engine.set_trait("humor_level", value / 100)

    def _handle_set_formality(self, command: str) -> Dict[str, Any]:
        if "be formal" in command.lower():
            return self._engine.set_trait("formality_level", 0.9)
        if "be casual" in command.lower():
            return self._engine.set_trait("formality_level", 0.2)
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify a formality level (0-100)."}
        return self._engine.set_trait("formality_level", value / 100)

    def _handle_set_verbosity(self, command: str) -> Dict[str, Any]:
        if "be brief" in command.lower():
            return self._engine.set_trait("verbosity", 0.2)
        if "be detailed" in command.lower():
            return self._engine.set_trait("verbosity", 0.9)
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify a verbosity level (0-100)."}
        return self._engine.set_trait("verbosity", value / 100)

    def _handle_set_empathy(self, command: str) -> Dict[str, Any]:
        if "be empathetic" in command.lower():
            return self._engine.set_trait("empathy_level", 0.9)
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify an empathy level (0-100)."}
        return self._engine.set_trait("empathy_level", value / 100)

    def _handle_set_creativity(self, command: str) -> Dict[str, Any]:
        if "be creative" in command.lower():
            return self._engine.set_trait("creativity", 0.9)
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify a creativity level (0-100)."}
        return self._engine.set_trait("creativity", value / 100)

    def _handle_set_confidence(self, command: str) -> Dict[str, Any]:
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify a confidence level (0-100)."}
        return self._engine.set_trait("confidence", value / 100)

    def _handle_set_emoji(self, command: str) -> Dict[str, Any]:
        if "use emoji" in command.lower() or "enable emoji" in command.lower():
            return self._engine.set_trait("emoji_usage", 0.6)
        if "no emoji" in command.lower() or "disable emoji" in command.lower():
            return self._engine.set_trait("emoji_usage", 0.0)
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify emoji usage (0-100)."}
        return self._engine.set_trait("emoji_usage", value / 100)

    def _handle_set_slang(self, command: str) -> Dict[str, Any]:
        if "use slang" in command.lower():
            return self._engine.set_trait("slang_tolerance", 0.7)
        value = self._extract_number(command, default=-1)
        if value < 0:
            return {"success": False, "response": "Please specify slang tolerance (0-100)."}
        return self._engine.set_trait("slang_tolerance", value / 100)

    def _handle_create_profile(self, command: str) -> Dict[str, Any]:
        name = self._extract_field(command, ["name:", "named"])
        if not name:
            return {"success": False, "response": "Please provide a profile name. Example: 'create profile name: MyBot'"}
        return self._engine.create_custom_profile(name, {})

    def _handle_list_profiles(self) -> Dict[str, Any]:
        profiles = self._engine.list_profiles()
        if not profiles:
            return {"success": True, "response": "No custom profiles."}
        lines = [f"Personality profiles ({len(profiles)}):\n"]
        for p in profiles:
            active = " (active)" if p.id == self._engine.active_profile.id else ""
            lines.append(f"  {p.id} | {p.name}{active}")
            lines.append(f"    {p.description}")
        return {"success": True, "response": "\n".join(lines)}

    def _handle_switch_profile(self, command: str) -> Dict[str, Any]:
        profile_id = self._extract_id(command)
        if not profile_id:
            return {"success": False, "response": "Please provide a profile ID."}
        result = self._engine.switch_profile(profile_id)
        if result["success"]:
            self._tone_manager = ToneManager(profile=self._engine.active_profile)
            self._transformer = ResponseTransformer(
                profile=self._engine.active_profile,
                tone_manager=self._tone_manager,
                emotion_simulator=self._emotion_simulator,
            )
        return result

    def _handle_delete_profile(self, command: str) -> Dict[str, Any]:
        profile_id = self._extract_id(command)
        if not profile_id:
            return {"success": False, "response": "Please provide a profile ID."}
        return self._engine.delete_profile(profile_id)

    def _handle_set_user_name(self, command: str) -> Dict[str, Any]:
        name = self._extract_content(command, [
            "set user name ", "my name is ", "call me ",
        ])
        if not name:
            return {"success": False, "response": "Please provide your name."}
        session_id = self._extract_id(command) or "default"
        style = self._style_adapter.get_style(session_id)
        style.user_name = name.strip()
        return {"success": True, "response": f"Got it! I'll call you {name.strip()}."}

    def _handle_set_greeting(self, command: str) -> Dict[str, Any]:
        style = self._extract_content(command, [
            "set greeting ", "greeting style ",
        ])
        valid = ["warm", "formal", "playful", "gentle", "energetic", "brief", "dry"]
        if not style or style.lower() not in valid:
            return {"success": False, "response": f"Please specify a greeting style. Available: {', '.join(valid)}"}
        self._engine.active_profile.greeting_style = style.lower()
        self._storage.save_profile(self._engine.active_profile, active=True)
        return {"success": True, "response": f"Greeting style set to: {style}"}

    def _handle_set_signoff(self, command: str) -> Dict[str, Any]:
        style = self._extract_content(command, [
            "set signoff ", "signoff style ",
        ])
        valid = ["helpful", "professional", "friendly", "witty", "supportive", "minimal", "upbeat", "snarky"]
        if not style or style.lower() not in valid:
            return {"success": False, "response": f"Please specify a signoff style. Available: {', '.join(valid)}"}
        self._engine.active_profile.signoff_style = style.lower()
        self._storage.save_profile(self._engine.active_profile, active=True)
        return {"success": True, "response": f"Signoff style set to: {style}"}

    def _handle_emotion_status(self, command: str) -> Dict[str, Any]:
        session_id = self._extract_id(command) or "default"
        state = self._emotion_simulator.get_state(session_id)
        lines = [
            f"Current emotion: {state.current_emotion.value}",
            f"Intensity: {state.intensity:.2f}",
            f"Trigger: {state.trigger or 'N/A'}",
        ]
        return {"success": True, "response": "\n".join(lines), "data": state.to_dict()}

    def _handle_session_status(self, command: str) -> Dict[str, Any]:
        session_id = self._extract_id(command) or "default"
        context = self._get_session_context(session_id)
        lines = [
            f"Session {context.session_id}",
            f"  Messages: {context.message_count}",
            f"  Started: {context.started_at[:19]}",
            f"  Tone adaptations: {context.tone_adaptations}",
            f"  Detected mood: {context.user_mood_detected or 'N/A'}",
            f"  Interaction quality: {context.interaction_quality:.2f}",
        ]
        return {"success": True, "response": "\n".join(lines), "data": context.to_dict()}

    def _handle_stats(self) -> Dict[str, Any]:
        stats = self._storage.get_stats()
        lines = [
            "Personality Agent Statistics:",
            f"  Active profile: {stats['active_profile'] or 'Default'}",
            f"  Total profiles: {stats['total_profiles']}",
            f"  Total sessions: {stats['total_sessions']}",
            f"  Total events: {stats['total_events']}",
        ]
        return {"success": True, "response": "\n".join(lines), "data": stats}

    def _handle_reset(self) -> Dict[str, Any]:
        result = self._engine.apply_preset("default")
        if result["success"]:
            self._tone_manager = ToneManager(profile=self._engine.active_profile)
            self._style_adapter = StyleAdapter(profile=self._engine.active_profile)
            self._transformer = ResponseTransformer(
                profile=self._engine.active_profile,
                tone_manager=self._tone_manager,
                emotion_simulator=self._emotion_simulator,
            )
        return result

    def _handle_transform(self, command: str) -> Dict[str, Any]:
        text = self._extract_content(command, [
            "transform response ", "apply personality ",
        ])
        if not text:
            return {"success": False, "response": "Please provide text to transform. Example: 'transform response Here is the answer'"}

        transformed = self._transformer.transform(text, session_id="test")
        return {
            "success": True,
            "response": f"Transformed:\n\n{transformed}",
        }

    def _handle_detect_tone(self, command: str) -> Dict[str, Any]:
        text = self._extract_content(command, [
            "detect tone ", "analyze tone ", "what tone ",
        ])
        if not text:
            return {"success": False, "response": "Please provide text to analyze."}

        tone = self._tone_manager.detect_user_tone(text)
        emotion, intensity = self._emotion_simulator.detect_emotion(text)
        lines = [
            f"Detected tone: {tone.value}",
            f"Detected emotion: {emotion.value} (intensity: {intensity:.2f})",
        ]
        return {"success": True, "response": "\n".join(lines)}

    def _handle_greet(self, command: str) -> Dict[str, Any]:
        session_id = self._extract_id(command) or "default"
        greeting = self._transformer.generate_greeting(session_id)
        return {"success": True, "response": greeting.strip()}

    def _get_session_context(self, session_id: str) -> SessionContext:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionContext(session_id=session_id)
        ctx = self._sessions[session_id]
        ctx.touch()
        return ctx

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: list) -> str:
        cmd_lower = command.lower()
        for prefix in prefixes:
            if cmd_lower.startswith(prefix):
                return command[len(prefix):].strip()
        return ""

    @staticmethod
    def _extract_field(command: str, prefixes: list) -> Optional[str]:
        cmd_lower = command.lower()
        for prefix in prefixes:
            idx = cmd_lower.find(prefix)
            if idx != -1:
                return command[idx + len(prefix):].strip().split("\n")[0].strip()
        return None

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        match = re.search(r"\b(\d+)\b", command)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_id(command: str) -> Optional[str]:
        match = re.search(r"\b([a-f0-9]{8})\b", command.lower())
        return match.group(1) if match else None
