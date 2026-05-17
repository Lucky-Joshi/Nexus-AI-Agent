import json
import os
from pathlib import Path
from typing import Any


class Config:
    """Centralized configuration management for NEXUS."""

    _instance = None
    _config: dict = {}
    _config_path: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config:
            self._load_config()

    def _load_config(self):
        config_path = Path(__file__).parent.parent / "config" / "settings.json"
        self._config_path = str(config_path)

        if config_path.exists():
            with open(config_path, "r") as f:
                self._config = json.load(f)
        else:
            self._config = self._default_config()
            self.save()

    def _default_config(self) -> dict:
        return {
            "app": {"name": "NEXUS", "version": "2.0.0", "debug": False},
            "terminal": {
                "theme": "nexus",
                "typing_speed": 0.01,
                "show_header": True,
                "show_sidebar": True,
                "show_status_bar": True,
                "auto_complete": True,
            },
            "llm": {
                "provider": "ollama",
                "use_in_agents": True,
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama3",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
                "openai": {
                    "api_key": "",
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
            },
            "ui": {
                "theme": "dark",
                "window_width": 1400,
                "window_height": 900,
                "font_family": "Segoe UI",
                "font_size": 14,
                "accent_color": "#00D4FF",
                "glass_effect": True,
            },
            "database": {"path": "data/nexus.db", "auto_backup": True},
            "memory": {
                "max_context_length": 50,
                "save_conversations": True,
                "save_preferences": True,
            },
            "agents": {
                "file_agent": {"enabled": True, "watch_downloads": True},
                "web_agent": {
                    "enabled": True,
                    "default_search_engine": "duckduckgo",
                    "user_agent": "NEXUS-WebAgent/1.0",
                },
                "automation_agent": {
                    "enabled": True,
                    "safety_delay": 0.5,
                    "confirm_destructive": True,
                },
                "coding_agent": {"enabled": True, "default_language": "python", "workspace_path": ""},
                "memory_agent": {"enabled": True, "auto_save": True},
                "vision_agent": {
                    "enabled": True,
                    "screenshot_dir": "data/screenshots",
                    "ocr_languages": ["en"],
                    "use_gpu": False,
                    "monitor_interval": 2.0,
                },
                "notification_agent": {
                    "enabled": True,
                    "max_queue_size": 100,
                    "max_history": 500,
                    "focus_mode": {
                        "enabled": False,
                        "allow_critical": True,
                        "quiet_hours_start": "22:00",
                        "quiet_hours_end": "08:00",
                        "quiet_hours_enabled": False,
                    },
                },
                "knowledge_agent": {
                    "enabled": True,
                    "embedding_model": "all-MiniLM-L6-v2",
                    "vector_store_path": "data/knowledge_vectors",
                    "auto_index": True,
                    "max_search_results": 20,
                },
                "terminal_agent": {
                    "enabled": True,
                    "strict_mode": True,
                    "default_timeout": 30,
                    "script_timeout": 120,
                    "max_output_size": 50000,
                    "allowed_extensions": [".py", ".bat", ".cmd", ".ps1", ".sh", ".js"],
                },
                "personality_agent": {
                    "enabled": True,
                    "default_preset": "default",
                    "auto_adapt_tone": True,
                    "emotion_decay_rate": 0.05,
                    "max_tone_history": 50,
                },
                "workflow_agent": {
                    "enabled": True,
                    "auto_deactivate_on_switch": True,
                    "default_timer_duration": 25,
                    "max_concurrent_modes": 1,
                },
                "plugin_agent": {
                    "enabled": True,
                    "plugins_dir": "agents/plugin_agent/plugins",
                    "registry_path": "data/plugins/registry.json",
                    "auto_load_enabled": True,
                    "sandbox_enabled": True,
                    "max_execution_time": 10,
                },
                "security_agent": {
                    "enabled": True,
                    "auto_block_critical": True,
                    "max_risk_level": "medium",
                    "monitoring_enabled": True,
                    "monitoring_interval": 30,
                    "audit_enabled": True,
                    "safe_execution_mode": True,
                },
                "workflow_chain_agent": {
                    "enabled": True,
                    "default_timeout": 300,
                    "max_concurrent_steps": 3,
                    "auto_save_executions": True,
                    "checkpoint_enabled": True,
                },
                "analytics_agent": {
                    "enabled": True,
                    "auto_track": True,
                    "resource_monitoring_interval": 60,
                    "retention_days": 90,
                    "dashboard_refresh_interval": 30,
                },
                "context_awareness_agent": {
                    "enabled": True,
                    "monitoring_enabled": False,
                    "monitoring_interval": 10,
                    "privacy_mode": False,
                    "retention_days": 30,
                    "auto_suggest_workflows": True,
                },
                "communication_bus_agent": {
                    "enabled": True,
                    "max_workers": 8,
                    "max_queue_size": 10000,
                    "default_ttl": 300,
                    "max_retries": 3,
                    "retry_delay": 1.0,
                    "max_memory_logs": 5000,
                    "log_retention_days": 7,
                    "auto_cleanup_hours": 24,
                },
                "planner_agent": {
                    "enabled": True,
                    "max_parallel_tasks": 3,
                    "default_timeout": 300,
                    "max_retries": 1,
                    "auto_plan": True,
                    "plan_retention_days": 30,
                },
                "marketplace_agent": {
                    "enabled": True,
                    "install_dir": "agents/marketplace_agent/installed_agents",
                    "auto_verify": True,
                    "sandbox_install": True,
                    "auto_update_check": True,
                    "review_retention_days": 365,
                },
            },
            "logging": {"level": "INFO", "file": "logs/nexus.log", "max_size_mb": 10, "backup_count": 5},
        }

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        with open(self._config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    @property
    def config(self) -> dict:
        return self._config.copy()
