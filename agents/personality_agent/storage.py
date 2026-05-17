"""
Storage backend for the Personality Agent.
Provides SQLite for personality state and JSON for profile/preset persistence.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import Logger
from core.config import Config

from .models import PersonalityProfile, ConversationStyle, EmotionState, SessionContext


class PersonalityStorage:
    """SQLite storage for personality state, profiles, and session context."""

    def __init__(self, db_path: Optional[str] = None):
        self.logger = Logger().get_logger("PersonalityStorage")
        if db_path is None:
            config = Config()
            db_path = config.get("database.path", "data/nexus.db")
        self._db_path = str(Path(__file__).parent.parent.parent / db_path)
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._initialize()

    def _initialize(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS personality_profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    big_five TEXT DEFAULT '{}',
                    default_tone TEXT DEFAULT 'friendly',
                    humor_level REAL DEFAULT 0.3,
                    formality_level REAL DEFAULT 0.5,
                    verbosity REAL DEFAULT 0.6,
                    empathy_level REAL DEFAULT 0.7,
                    creativity REAL DEFAULT 0.6,
                    confidence REAL DEFAULT 0.7,
                    catchphrases TEXT DEFAULT '[]',
                    response_patterns TEXT DEFAULT '{}',
                    forbidden_topics TEXT DEFAULT '[]',
                    greeting_style TEXT DEFAULT 'warm',
                    signoff_style TEXT DEFAULT 'helpful',
                    emoji_usage REAL DEFAULT 0.2,
                    slang_tolerance REAL DEFAULT 0.3,
                    created_at TEXT,
                    updated_at TEXT,
                    is_active INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS conversation_styles (
                    session_id TEXT PRIMARY KEY,
                    response_length TEXT DEFAULT 'medium',
                    use_examples INTEGER DEFAULT 1,
                    use_analogies INTEGER DEFAULT 1,
                    technical_depth REAL DEFAULT 0.5,
                    humor_frequency REAL DEFAULT 0.1,
                    question_frequency REAL DEFAULT 0.2,
                    personalization_level REAL DEFAULT 0.5,
                    user_name TEXT DEFAULT '',
                    user_preferences TEXT DEFAULT '{}',
                    created_at TEXT
                );

                CREATE TABLE IF NOT EXISTS emotion_states (
                    session_id TEXT PRIMARY KEY,
                    current_emotion TEXT DEFAULT 'neutral',
                    intensity REAL DEFAULT 0.3,
                    trigger TEXT DEFAULT '',
                    emotion_log TEXT DEFAULT '[]',
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS session_contexts (
                    session_id TEXT PRIMARY KEY,
                    started_at TEXT,
                    last_active TEXT,
                    message_count INTEGER DEFAULT 0,
                    dominant_emotion TEXT DEFAULT 'neutral',
                    tone_adaptations INTEGER DEFAULT 0,
                    user_mood_detected TEXT DEFAULT '',
                    interaction_quality REAL DEFAULT 0.5
                );

                CREATE TABLE IF NOT EXISTS personality_history (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    event_type TEXT,
                    details TEXT DEFAULT '{}',
                    timestamp TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_personality_active ON personality_profiles(is_active);
                CREATE INDEX IF NOT EXISTS idx_personality_history_session ON personality_history(session_id);
                CREATE INDEX IF NOT EXISTS idx_personality_history_type ON personality_history(event_type);
            """)
        self.logger.info("Personality storage initialized")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_profile(self, profile: PersonalityProfile, active: bool = False) -> bool:
        with self._get_connection() as conn:
            if active:
                conn.execute("UPDATE personality_profiles SET is_active = 0")
            conn.execute("""
                INSERT OR REPLACE INTO personality_profiles
                (id, name, description, big_five, default_tone, humor_level,
                 formality_level, verbosity, empathy_level, creativity, confidence,
                 catchphrases, response_patterns, forbidden_topics, greeting_style,
                 signoff_style, emoji_usage, slang_tolerance, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.id, profile.name, profile.description,
                json.dumps(profile.big_five), profile.default_tone.value,
                profile.humor_level, profile.formality_level, profile.verbosity,
                profile.empathy_level, profile.creativity, profile.confidence,
                json.dumps(profile.catchphrases), json.dumps(profile.response_patterns),
                json.dumps(profile.forbidden_topics),
                profile.greeting_style, profile.signoff_style,
                profile.emoji_usage, profile.slang_tolerance,
                profile.created_at, profile.updated_at, int(active),
            ))
        return True

    def get_active_profile(self) -> Optional[PersonalityProfile]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM personality_profiles WHERE is_active = 1"
            ).fetchone()
        if not row:
            return None
        return self._row_to_profile(row)

    def get_profile(self, profile_id: str) -> Optional[PersonalityProfile]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM personality_profiles WHERE id = ?", (profile_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_profile(row)

    def get_all_profiles(self) -> List[PersonalityProfile]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM personality_profiles ORDER BY updated_at DESC"
            ).fetchall()
        return [self._row_to_profile(r) for r in rows]

    def delete_profile(self, profile_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM personality_profiles WHERE id = ?", (profile_id,)
            )
        return cursor.rowcount > 0

    def save_conversation_style(self, session_id: str, style: ConversationStyle) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversation_styles
                (session_id, response_length, use_examples, use_analogies,
                 technical_depth, humor_frequency, question_frequency,
                 personalization_level, user_name, user_preferences, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, style.response_length, int(style.use_examples),
                int(style.use_analogies), style.technical_depth,
                style.humor_frequency, style.question_frequency,
                style.personalization_level, style.user_name,
                json.dumps(style.user_preferences),
                datetime.now().isoformat(),
            ))
        return True

    def get_conversation_style(self, session_id: str) -> Optional[ConversationStyle]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM conversation_styles WHERE session_id = ?", (session_id,)
            ).fetchone()
        if not row:
            return None
        return ConversationStyle(
            response_length=row["response_length"],
            use_examples=bool(row["use_examples"]),
            use_analogies=bool(row["use_analogies"]),
            technical_depth=row["technical_depth"],
            humor_frequency=row["humor_frequency"],
            question_frequency=row["question_frequency"],
            personalization_level=row["personalization_level"],
            user_name=row["user_name"],
            user_preferences=json.loads(row["user_preferences"]),
        )

    def save_emotion_state(self, session_id: str, state: EmotionState) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO emotion_states
                (session_id, current_emotion, intensity, trigger, emotion_log, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id, state.current_emotion.value, state.intensity,
                state.trigger, json.dumps(state.emotion_log),
                datetime.now().isoformat(),
            ))
        return True

    def get_emotion_state(self, session_id: str) -> Optional[EmotionState]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM emotion_states WHERE session_id = ?", (session_id,)
            ).fetchone()
        if not row:
            return None
        from .models import Emotion
        return EmotionState(
            current_emotion=Emotion(row["current_emotion"]),
            intensity=row["intensity"],
            trigger=row["trigger"],
            emotion_log=json.loads(row["emotion_log"]),
        )

    def save_session_context(self, session_id: str, context: SessionContext) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO session_contexts
                (session_id, started_at, last_active, message_count, dominant_emotion,
                 tone_adaptations, user_mood_detected, interaction_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, context.started_at, context.last_active,
                context.message_count, context.dominant_emotion.value,
                context.tone_adaptations, context.user_mood_detected,
                context.interaction_quality,
            ))
        return True

    def get_session_context(self, session_id: str) -> Optional[SessionContext]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM session_contexts WHERE session_id = ?", (session_id,)
            ).fetchone()
        if not row:
            return None
        from .models import Emotion
        return SessionContext(
            session_id=row["session_id"],
            started_at=row["started_at"],
            last_active=row["last_active"],
            message_count=row["message_count"],
            dominant_emotion=Emotion(row["dominant_emotion"]),
            tone_adaptations=row["tone_adaptations"],
            user_mood_detected=row["user_mood_detected"],
            interaction_quality=row["interaction_quality"],
        )

    def log_event(self, session_id: str, event_type: str, details: Dict[str, Any]) -> bool:
        import uuid
        from datetime import datetime
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO personality_history (id, session_id, event_type, details, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4())[:8], session_id, event_type,
                json.dumps(details), datetime.now().isoformat(),
            ))
        return True

    def get_history(self, session_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if session_id:
                rows = conn.execute(
                    "SELECT * FROM personality_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (session_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM personality_history ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [{
            "id": r["id"],
            "session_id": r["session_id"],
            "event_type": r["event_type"],
            "details": json.loads(r["details"]),
            "timestamp": r["timestamp"],
        } for r in rows]

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_profiles = conn.execute("SELECT COUNT(*) FROM personality_profiles").fetchone()[0]
            active_profile = conn.execute("SELECT name FROM personality_profiles WHERE is_active = 1").fetchone()
            total_sessions = conn.execute("SELECT COUNT(*) FROM session_contexts").fetchone()[0]
            total_events = conn.execute("SELECT COUNT(*) FROM personality_history").fetchone()[0]

        return {
            "total_profiles": total_profiles,
            "active_profile": active_profile[0] if active_profile else None,
            "total_sessions": total_sessions,
            "total_events": total_events,
        }

    def _row_to_profile(self, row) -> PersonalityProfile:
        return PersonalityProfile(
            id=row["id"], name=row["name"], description=row["description"],
            big_five=json.loads(row["big_five"]),
            default_tone=__import__("agents.personality_agent.models", fromlist=["ToneType"]).ToneType(row["default_tone"]),
            humor_level=row["humor_level"], formality_level=row["formality_level"],
            verbosity=row["verbosity"], empathy_level=row["empathy_level"],
            creativity=row["creativity"], confidence=row["confidence"],
            catchphrases=json.loads(row["catchphrases"]),
            response_patterns=json.loads(row["response_patterns"]),
            forbidden_topics=json.loads(row["forbidden_topics"]),
            greeting_style=row["greeting_style"], signoff_style=row["signoff_style"],
            emoji_usage=row["emoji_usage"], slang_tolerance=row["slang_tolerance"],
            created_at=row["created_at"], updated_at=row["updated_at"],
        )


class PresetStorage:
    """JSON-based storage for personality presets."""

    def __init__(self, presets_dir: Optional[str] = None):
        self.logger = Logger().get_logger("PresetStorage")
        if presets_dir is None:
            presets_dir = str(Path(__file__).parent / "presets")
        self._presets_dir = Path(presets_dir)
        os.makedirs(self._presets_dir, exist_ok=True)

    def save_preset(self, name: str, data: Dict[str, Any]) -> str:
        path = self._presets_dir / f"{name.lower().replace(' ', '_')}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Preset saved: {path}")
        return str(path)

    def load_preset(self, name: str) -> Optional[Dict[str, Any]]:
        path = self._presets_dir / f"{name.lower().replace(' ', '_')}.json"
        if not path.exists():
            return None
        with open(path, "r") as f:
            return json.load(f)

    def list_presets(self) -> List[str]:
        return [p.stem.replace("_", " ").title() for p in self._presets_dir.glob("*.json")]

    def delete_preset(self, name: str) -> bool:
        path = self._presets_dir / f"{name.lower().replace(' ', '_')}.json"
        if path.exists():
            path.unlink()
            return True
        return False


from datetime import datetime
