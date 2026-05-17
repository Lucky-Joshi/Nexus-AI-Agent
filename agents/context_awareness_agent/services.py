"""
Context Awareness Agent Services
Core services for context detection, activity classification, workflow detection,
adaptive triggers, and context history management.
"""

import re
import time
import threading
import psutil
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from collections import defaultdict

from core.logger import Logger
from core.config import Config

from .models import (
    ActivityType, ContextConfidence, FocusLevel, TriggerAction,
    WindowContext, RunningApp, SystemLoad, TimeContext, UserContext,
    ContextPattern, AdaptiveTrigger, ContextSnapshot,
)
from .storage import ContextStorage


APP_CATEGORIES = {
    "coding": [
        "code.exe", "code-insiders.exe", "vscode.exe", "devenv.exe", "visualstudio.exe",
        "pycharm64.exe", "pycharm.exe", "idea64.exe", "webstorm64.exe",
        "sublime_text.exe", "notepad++.exe", "atom.exe", "vim.exe", "nvim.exe",
        "emacs.exe", "eclipse.exe", "androidstudio.exe", "clion64.exe",
        "rider64.exe", "fleet.exe", "zed.exe", "cursor.exe", "windsurf.exe",
        "terminal.exe", "wt.exe", "conhost.exe", "powershell.exe", "pwsh.exe",
        "cmd.exe", "git.exe", "githubdesktop.exe",
    ],
    "browsing": [
        "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe",
        "vivaldi.exe", "iexplore.exe", "safari.exe", "tor.exe",
    ],
    "gaming": [
        "steam.exe", "epicgameslauncher.exe", "origin.exe", "upc.exe",
        "battle.net.exe", "riotclient.exe", "minecraft.exe", "roblox.exe",
        "fortnite.exe", "valorant.exe", "league of legends.exe",
        "gog galaxy.exe", "xbox.exe", "gamebar.exe",
    ],
    "media": [
        "spotify.exe", "vlc.exe", "mpc-hc.exe", "potplayer.exe", "itunes.exe",
        "music.exe", "windowsmediaplayer.exe", "filmora.exe", "premiere.exe",
        "afterfx.exe", "davinciresolve.exe", "obs64.exe", "streamlabs.exe",
    ],
    "communication": [
        "teams.exe", "slack.exe", "discord.exe", "zoom.exe", "webex.exe",
        "skype.exe", "whatsapp.exe", "telegram.exe", "signal.exe",
        "msteams.exe", "hangouts.exe", "messenger.exe",
    ],
    "writing": [
        "winword.exe", "word.exe", "notepad.exe", "wordpad.exe",
        "onenote.exe", "evernote.exe", "obsidian.exe", "notion.exe",
        "logseq.exe", "typora.exe", "scrivener.exe",
    ],
    "design": [
        "photoshop.exe", "illustrator.exe", "figma.exe", "sketch.exe",
        "afterfx.exe", "premiere.exe", "blender.exe", "gimp.exe",
        "inkscape.exe", "krita.exe", "canva.exe",
    ],
    "file_management": [
        "explorer.exe", "totalcmd.exe", "doublecmd.exe", "files.exe",
    ],
    "system_admin": [
        "taskmgr.exe", "regedit.exe", "mmc.exe", "services.msc",
        "compmgmt.msc", "eventvwr.exe", "perfmon.exe",
    ],
}


class ActivityClassifier:
    """Classifies user activity from window and process data."""

    def __init__(self):
        self.logger = Logger().get_logger("ActivityClassifier")
        self._category_map: Dict[str, str] = {}
        self._build_category_map()

    def _build_category_map(self):
        for category, apps in APP_CATEGORIES.items():
            for app in apps:
                self._category_map[app.lower()] = category

    def classify(self, active_process: str, window_title: str = "",
                 running_apps: List[str] = None) -> tuple:
        activity = ActivityType.UNKNOWN
        confidence = ContextConfidence.LOW
        signals = []

        process_lower = active_process.lower()
        title_lower = window_title.lower() if window_title else ""

        category = self._category_map.get(process_lower)
        if category:
            activity = ActivityType(category)
            confidence = ContextConfidence.HIGH
            signals.append(f"Process '{active_process}' matches {category}")
        else:
            for app_name, cat in self._category_map.items():
                if app_name in process_lower:
                    activity = ActivityType(cat)
                    confidence = ContextConfidence.MEDIUM
                    signals.append(f"Process contains '{app_name}' -> {cat}")
                    break

        if activity == ActivityType.UNKNOWN and running_apps:
            app_categories = set()
            for app in running_apps:
                cat = self._category_map.get(app.lower())
                if not cat:
                    for app_name, c in self._category_map.items():
                        if app_name in app.lower():
                            cat = c
                            break
                if cat:
                    app_categories.add(cat)

            if len(app_categories) == 1:
                activity = ActivityType(list(app_categories)[0])
                confidence = ContextConfidence.MEDIUM
                signals.append(f"All running apps are {activity.value}")
            elif "coding" in app_categories and "communication" in app_categories:
                activity = ActivityType.CODING
                confidence = ContextConfidence.MEDIUM
                signals.append("Coding + communication -> coding session")
            elif "gaming" in app_categories:
                activity = ActivityType.GAMING
                confidence = ContextConfidence.MEDIUM
                signals.append("Gaming app detected")

        if activity == ActivityType.UNKNOWN and title_lower:
            if any(kw in title_lower for kw in ["visual studio", "intellij", "pycharm", "vs code"]):
                activity = ActivityType.CODING
                confidence = ContextConfidence.HIGH
                signals.append("IDE detected in window title")
            elif any(kw in title_lower for kw in ["youtube", "netflix", "twitch", "prime video"]):
                activity = ActivityType.MEDIA
                confidence = ContextConfidence.HIGH
                signals.append("Media site detected in window title")
            elif any(kw in title_lower for kw in ["google docs", "notion", "obsidian"]):
                activity = ActivityType.WRITING
                confidence = ContextConfidence.MEDIUM
                signals.append("Writing tool detected in window title")
            elif any(kw in title_lower for kw in ["figma", "photoshop", "illustrator"]):
                activity = ActivityType.DESIGN
                confidence = ContextConfidence.MEDIUM
                signals.append("Design tool detected in window title")

        if activity == ActivityType.UNKNOWN:
            if not active_process and not window_title:
                activity = ActivityType.IDLE
                confidence = ContextConfidence.HIGH
                signals.append("No active window detected")

        return activity, confidence, signals


class ContextDetector:
    """Main context inference engine combining all signals."""

    def __init__(self, storage: ContextStorage):
        self.logger = Logger().get_logger("ContextDetector")
        self._storage = storage
        self._classifier = ActivityClassifier()
        self._session_start = datetime.now()
        self._current_activity = ActivityType.UNKNOWN
        self._activity_duration = 0.0
        self._last_check = time.time()
        self._window_switches = 0
        self._last_active_process = ""
        self._callbacks: List[Callable] = []

    def detect_context(self) -> UserContext:
        active_window = self._get_active_window()
        running_apps = self._get_running_apps()
        system_load = self._get_system_load()
        time_ctx = self._get_time_context()

        app_names = [a.name for a in running_apps]
        activity, confidence, signals = self._classifier.classify(
            active_window.process_name if active_window else "",
            active_window.title if active_window else "",
            app_names,
        )

        focus = self._calculate_focus_level(activity, system_load, active_window)
        suggested_workflow = self._suggest_workflow(activity, app_names, time_ctx)
        suggested_actions = self._suggest_actions(activity, app_names, time_ctx, focus)

        if active_window and active_window.process_name != self._last_active_process:
            self._window_switches += 1
            self._last_active_process = active_window.process_name

        now = time.time()
        self._activity_duration += now - self._last_check
        self._last_check = now

        if activity != self._current_activity:
            self._current_activity = activity
            self._activity_duration = 0.0

        context = UserContext(
            activity=activity,
            activity_confidence=confidence,
            focus_level=focus,
            active_window=active_window,
            running_apps=running_apps[:15],
            system_load=system_load,
            time_context=time_ctx,
            session_type=self._get_session_type(activity),
            context_signals=signals,
            suggested_actions=suggested_actions,
            suggested_workflow=suggested_workflow,
        )

        self._save_snapshot(context)
        self._notify_callbacks(context)

        return context

    def on_context_change(self, callback: Callable):
        self._callbacks.append(callback)

    def _notify_callbacks(self, context: UserContext):
        for callback in self._callbacks:
            try:
                callback(context)
            except Exception as e:
                self.logger.error(f"Context callback error: {e}")

    def _get_active_window(self) -> Optional[WindowContext]:
        try:
            import pygetwindow as gw
            active = gw.getActiveWindow()
            if active and active.title:
                return WindowContext(
                    title=active.title,
                    process_name=self._get_process_for_window(active),
                    is_minimized=active.isMinimized if hasattr(active, "isMinimized") else False,
                    is_visible=active.isVisible if hasattr(active, "isVisible") else True,
                    duration_seconds=self._activity_duration,
                    switch_count=self._window_switches,
                )
        except Exception:
            pass

        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value

                    pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    process_name = ""
                    try:
                        process_name = psutil.Process(pid.value).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                    return WindowContext(
                        title=title,
                        process_name=process_name,
                        pid=pid.value,
                        duration_seconds=self._activity_duration,
                        switch_count=self._window_switches,
                    )
        except Exception:
            pass

        return None

    def _get_process_for_window(self, window) -> str:
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = getattr(window, "_hWnd", 0)
            if hwnd:
                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                return psutil.Process(pid.value).name()
        except Exception:
            pass
        return ""

    def _get_running_apps(self) -> List[RunningApp]:
        apps = []
        try:
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                try:
                    info = proc.info
                    name = info.get("name", "")
                    if not name or name.lower() in ("system", "idle", "svchost.exe", "runtimebroker.exe"):
                        continue

                    mem_mb = 0
                    if info.get("memory_info"):
                        mem_mb = info["memory_info"].rss / (1024 * 1024)

                    category = self._classifier._category_map.get(name.lower(), "unknown")
                    if category == "unknown":
                        for app_name, cat in self._classifier._category_map.items():
                            if app_name in name.lower():
                                category = cat
                                break

                    apps.append(RunningApp(
                        name=name,
                        pid=info.get("pid", 0),
                        cpu_percent=info.get("cpu_percent", 0) or 0,
                        memory_mb=round(mem_mb, 1),
                        category=category,
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass

        apps.sort(key=lambda a: a.memory_mb, reverse=True)
        return apps[:30]

    def _get_system_load(self) -> SystemLoad:
        cpu = psutil.cpu_percent(interval=0.3)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        processes = len(list(psutil.process_iter()))
        net = len(psutil.net_connections(kind="inet"))

        if cpu > 80 or memory.percent > 85:
            level = "heavy"
        elif cpu > 40 or memory.percent > 60:
            level = "moderate"
        else:
            level = "idle"

        return SystemLoad(
            cpu_percent=cpu,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            disk_percent=disk.percent,
            process_count=processes,
            network_connections=net,
            level=level,
        )

    def _get_time_context(self) -> TimeContext:
        now = datetime.now()
        hour = now.hour
        is_weekday = now.weekday() < 5
        is_work_hours = is_weekday and 9 <= hour < 18

        if 5 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"
        elif 17 <= hour < 21:
            period = "evening"
        else:
            period = "night"

        session_duration = (now - self._session_start).total_seconds() / 60

        return TimeContext(
            hour=hour,
            minute=now.minute,
            day_of_week=now.weekday(),
            is_weekday=is_weekday,
            is_work_hours=is_work_hours,
            period=period,
            session_duration_minutes=session_duration,
        )

    def _calculate_focus_level(self, activity: ActivityType,
                               system_load: SystemLoad,
                               active_window: Optional[WindowContext]) -> FocusLevel:
        if activity == ActivityType.IDLE:
            return FocusLevel.IDLE

        if activity in (ActivityType.CODING, ActivityType.WRITING, ActivityType.DESIGN):
            if active_window and active_window.switch_count < 5:
                return FocusLevel.DEEP
            return FocusLevel.FOCUSED

        if activity in (ActivityType.BROWSING, ActivityType.MEDIA):
            return FocusLevel.DISTRACTED

        if activity in (ActivityType.GAMING,):
            return FocusLevel.DEEP

        return FocusLevel.MODERATE

    def _suggest_workflow(self, activity: ActivityType,
                          app_names: List[str], time_ctx: TimeContext) -> str:
        suggestions = {
            ActivityType.CODING: "coding_mode",
            ActivityType.STUDYING: "study_mode",
            ActivityType.WRITING: "writing_mode",
            ActivityType.DESIGN: "design_mode",
            ActivityType.GAMING: "gaming_mode",
            ActivityType.MEETING: "meeting_mode",
            ActivityType.BROWSING: "research_mode",
        }

        if activity in suggestions:
            return suggestions[activity]

        if any(a in app_names for a in ["code.exe", "vscode.exe", "devenv.exe"]):
            return "coding_mode"
        if any(a in app_names for a in ["chrome.exe", "msedge.exe", "firefox.exe"]):
            if time_ctx.is_work_hours:
                return "research_mode"
        if any(a in app_names for a in ["steam.exe", "epicgameslauncher.exe"]):
            return "gaming_mode"

        return ""

    def _suggest_actions(self, activity: ActivityType, app_names: List[str],
                         time_ctx: TimeContext, focus: FocusLevel) -> List[str]:
        actions = []

        if activity == ActivityType.GAMING:
            actions.append("Silence notifications (gaming detected)")
            actions.append("Close unnecessary apps to free resources")

        if activity == ActivityType.CODING and time_ctx.period == "night":
            actions.append("Consider enabling dark theme")

        if activity == ActivityType.BROWSING and focus == FocusLevel.DISTRACTED:
            actions.append("Consider activating Deep Work mode")

        if activity == ActivityType.STUDYING:
            actions.append("Start Pomodoro timer for focused study")

        if activity == ActivityType.MEETING:
            actions.append("Mute notifications during meeting")

        if focus == FocusLevel.DEEP and time_ctx.session_duration_minutes > 60:
            actions.append("Consider taking a break (deep focus for 60+ min)")

        return actions

    def _get_session_type(self, activity: ActivityType) -> str:
        mapping = {
            ActivityType.CODING: "development",
            ActivityType.STUDYING: "learning",
            ActivityType.WRITING: "creative",
            ActivityType.DESIGN: "creative",
            ActivityType.GAMING: "entertainment",
            ActivityType.MEETING: "communication",
            ActivityType.BROWSING: "research",
            ActivityType.MEDIA: "entertainment",
            ActivityType.COMMUNICATION: "communication",
            ActivityType.IDLE: "idle",
        }
        return mapping.get(activity, "general")

    def _save_snapshot(self, context: UserContext):
        snapshot = ContextSnapshot(
            activity=context.activity.value,
            active_window_title=context.active_window.title if context.active_window else "",
            active_process=context.active_window.process_name if context.active_window else "",
            app_count=len(context.running_apps),
            focus_level=context.focus_level.value,
            cpu_percent=context.system_load.cpu_percent if context.system_load else 0,
            memory_percent=context.system_load.memory_percent if context.system_load else 0,
            duration_seconds=context.active_window.duration_seconds if context.active_window else 0,
        )
        self._storage.save_snapshot(snapshot.to_dict())

    def get_session_duration(self) -> float:
        return (datetime.now() - self._session_start).total_seconds() / 60


class WorkflowDetector:
    """Detects user workflows and suggests appropriate modes."""

    WORKFLOW_PATTERNS = [
        {
            "name": "Coding Session",
            "activity": ActivityType.CODING,
            "required_apps": ["code.exe", "vscode.exe", "terminal.exe", "git.exe"],
            "min_apps": 2,
            "suggested_workflow": "coding_mode",
            "description": "IDE + terminal or version control detected",
        },
        {
            "name": "Study Session",
            "activity": ActivityType.STUDYING,
            "required_apps": ["chrome.exe", "msedge.exe", "firefox.exe", "notepad.exe", "winword.exe"],
            "min_apps": 1,
            "suggested_workflow": "study_mode",
            "description": "Browser + document editor detected",
        },
        {
            "name": "Gaming Session",
            "activity": ActivityType.GAMING,
            "required_apps": ["steam.exe", "epicgameslauncher.exe", "battle.net.exe"],
            "min_apps": 1,
            "suggested_workflow": "gaming_mode",
            "description": "Game launcher detected",
        },
        {
            "name": "Meeting",
            "activity": ActivityType.MEETING,
            "required_apps": ["teams.exe", "zoom.exe", "webex.exe", "skype.exe", "msteams.exe"],
            "min_apps": 1,
            "suggested_workflow": "meeting_mode",
            "description": "Video conferencing app detected",
        },
        {
            "name": "Content Creation",
            "activity": ActivityType.DESIGN,
            "required_apps": ["premiere.exe", "photoshop.exe", "afterfx.exe", "obs64.exe", "figma.exe"],
            "min_apps": 1,
            "suggested_workflow": "content_creation_mode",
            "description": "Creative/design tool detected",
        },
        {
            "name": "Deep Work",
            "activity": ActivityType.CODING,
            "required_apps": ["code.exe", "vscode.exe", "devenv.exe", "notepad.exe", "winword.exe"],
            "min_apps": 1,
            "suggested_workflow": "deep_work_mode",
            "description": "Single focused app with no distractions",
        },
        {
            "name": "Research",
            "activity": ActivityType.BROWSING,
            "required_apps": ["chrome.exe", "msedge.exe", "firefox.exe"],
            "min_apps": 1,
            "suggested_workflow": "research_mode",
            "description": "Browser with research-oriented usage",
        },
    ]

    def __init__(self, storage: ContextStorage):
        self.logger = Logger().get_logger("WorkflowDetector")
        self._storage = storage
        self._load_patterns()

    def _load_patterns(self):
        stored = self._storage.get_patterns()
        if not stored:
            for p in self.WORKFLOW_PATTERNS:
                pattern = ContextPattern(
                    name=p["name"],
                    description=p["description"],
                    activity_type=p["activity"],
                    required_apps=p["required_apps"],
                    min_duration_minutes=5.0,
                )
                self._storage.save_pattern(pattern.to_dict())

    def detect_workflow(self, context: UserContext) -> List[Dict[str, Any]]:
        matches = []
        app_names = [a.name.lower() for a in context.running_apps]

        for pattern in self.WORKFLOW_PATTERNS:
            matching_apps = [app for app in pattern["required_apps"] if app.lower() in app_names]
            if len(matching_apps) >= pattern["min_apps"]:
                matches.append({
                    "pattern": pattern["name"],
                    "confidence": min(len(matching_apps) / pattern["min_apps"], 1.0),
                    "matching_apps": matching_apps,
                    "suggested_workflow": pattern["suggested_workflow"],
                    "description": pattern["description"],
                })

        matches.sort(key=lambda m: m["confidence"], reverse=True)
        return matches

    def get_patterns(self) -> List[Dict[str, Any]]:
        return self._storage.get_patterns()


class AdaptiveTriggerSystem:
    """Manages context-based adaptive triggers."""

    DEFAULT_TRIGGERS = [
        {
            "name": "Gaming Silence",
            "description": "Silence notifications when gaming",
            "condition_activity": ActivityType.GAMING,
            "action": TriggerAction.SILENCE_NOTIFICATIONS,
            "action_target": "notification_agent",
            "cooldown_seconds": 600,
        },
        {
            "name": "Coding Suggestion",
            "description": "Suggest coding mode when IDE detected",
            "condition_activity": ActivityType.CODING,
            "condition_apps": ["code.exe", "vscode.exe"],
            "action": TriggerAction.SUGGEST_WORKFLOW,
            "action_target": "coding_mode",
            "cooldown_seconds": 900,
        },
        {
            "name": "Study Mode Trigger",
            "description": "Suggest study mode when browser + docs open",
            "condition_activity": ActivityType.BROWSING,
            "condition_apps": ["chrome.exe", "msedge.exe", "firefox.exe"],
            "action": TriggerAction.SUGGEST_WORKFLOW,
            "action_target": "study_mode",
            "cooldown_seconds": 900,
        },
        {
            "name": "Meeting Focus",
            "description": "Activate focus mode during meetings",
            "condition_activity": ActivityType.MEETING,
            "action": TriggerAction.ACTIVATE_MODE,
            "action_target": "meeting_mode",
            "cooldown_seconds": 300,
        },
        {
            "name": "Deep Work Evening",
            "description": "Suggest deep work during evening coding",
            "condition_activity": ActivityType.CODING,
            "condition_time": "18-23",
            "condition_focus": FocusLevel.DEEP,
            "action": TriggerAction.SUGGEST_WORKFLOW,
            "action_target": "deep_work_mode",
            "cooldown_seconds": 1200,
        },
        {
            "name": "Idle Cleanup",
            "description": "Save context when user goes idle",
            "condition_activity": ActivityType.IDLE,
            "action": TriggerAction.SAVE_CONTEXT,
            "cooldown_seconds": 1800,
        },
    ]

    def __init__(self, storage: ContextStorage):
        self.logger = Logger().get_logger("AdaptiveTriggerSystem")
        self._storage = storage
        self._triggers: List[AdaptiveTrigger] = []
        self._last_fired: Dict[str, float] = {}
        self._load_triggers()

    def _load_triggers(self):
        stored = self._storage.get_triggers()
        if stored:
            self._triggers = [AdaptiveTrigger.from_dict(t) for t in stored]
        else:
            for t in self.DEFAULT_TRIGGERS:
                trigger = AdaptiveTrigger(
                    name=t["name"],
                    description=t.get("description", ""),
                    condition_activity=t.get("condition_activity"),
                    condition_apps=t.get("condition_apps", []),
                    condition_time=t.get("condition_time", ""),
                    condition_focus=t.get("condition_focus"),
                    action=t["action"],
                    action_target=t.get("action_target", ""),
                    cooldown_seconds=t.get("cooldown_seconds", 300),
                )
                self._triggers.append(trigger)
                self._storage.save_trigger(trigger.to_dict())
        self.logger.info(f"Loaded {len(self._triggers)} adaptive triggers")

    def evaluate(self, context: UserContext) -> List[Dict[str, Any]]:
        fired = []
        now = time.time()

        for trigger in self._triggers:
            if not trigger.enabled:
                continue

            last = self._last_fired.get(trigger.id, 0)
            if now - last < trigger.cooldown_seconds:
                continue

            if trigger.matches_context(context):
                self._last_fired[trigger.id] = now
                self._storage.update_trigger_fired(trigger.id)
                trigger.trigger_count += 1
                trigger.last_triggered = datetime.now().isoformat()

                fired.append({
                    "trigger": trigger.name,
                    "action": trigger.action.value,
                    "target": trigger.action_target,
                    "params": trigger.action_params,
                    "description": trigger.description,
                })

                self.logger.info(f"Trigger fired: {trigger.name} -> {trigger.action.value}")

        return fired

    def add_trigger(self, trigger: AdaptiveTrigger) -> bool:
        self._triggers.append(trigger)
        self._storage.save_trigger(trigger.to_dict())
        return True

    def remove_trigger(self, trigger_id: str) -> bool:
        self._triggers = [t for t in self._triggers if t.id != trigger_id]
        return True

    def list_triggers(self, enabled_only: bool = True) -> List[AdaptiveTrigger]:
        if enabled_only:
            return [t for t in self._triggers if t.enabled]
        return self._triggers

    def toggle_trigger(self, trigger_id: str) -> bool:
        for trigger in self._triggers:
            if trigger.id == trigger_id:
                trigger.enabled = not trigger.enabled
                self._storage.save_trigger(trigger.to_dict())
                return True
        return False


class ContextHistory:
    """Manages context history and pattern analysis."""

    def __init__(self, storage: ContextStorage):
        self.logger = Logger().get_logger("ContextHistory")
        self._storage = storage
        self._current_session: Optional[Dict[str, Any]] = None
        self._session_start = datetime.now()

    def start_session(self, session_type: str = "general"):
        self._current_session = {
            "id": str(datetime.now().timestamp())[:8],
            "session_type": session_type,
            "activity": "unknown",
            "started_at": datetime.now().isoformat(),
            "apps_used": [],
            "window_changes": 0,
            "focus_level": "idle",
        }

    def update_session(self, context: UserContext):
        if not self._current_session:
            return

        self._current_session["activity"] = context.activity.value
        self._current_session["focus_level"] = context.focus_level.value

        for app in context.running_apps:
            if app.name not in self._current_session["apps_used"]:
                self._current_session["apps_used"].append(app.name)

        if context.active_window:
            self._current_session["window_changes"] += 1

    def end_session(self):
        if not self._current_session:
            return

        self._current_session["ended_at"] = datetime.now().isoformat()
        duration = (datetime.now() - self._session_start).total_seconds() / 60
        self._current_session["duration_minutes"] = duration

        focus_scores = {"deep": 5, "focused": 4, "moderate": 3, "distracted": 2, "idle": 1}
        self._current_session["productivity_score"] = focus_scores.get(
            self._current_session.get("focus_level", "idle"), 1
        )

        self._storage.save_session(self._current_session)
        self._current_session = None
        self._session_start = datetime.now()

    def get_sessions(self, limit: int = 20, session_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._storage.get_sessions(limit=limit, session_type=session_type)

    def get_activity_summary(self, days: int = 7) -> Dict[str, Any]:
        return self._storage.get_activity_summary(days=days)

    def get_recent_context(self, limit: int = 50, activity: Optional[str] = None) -> List[Dict[str, Any]]:
        from datetime import timedelta
        start = (datetime.now() - timedelta(hours=24)).isoformat()
        return self._storage.get_snapshots(limit=limit, activity=activity, start_time=start)

    def cleanup(self, days: int = 30) -> int:
        return self._storage.cleanup_old_records(days)
