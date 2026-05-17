"""
NEXUS - Agent Marketplace System
Simulated marketplace backend with a curated catalog of community agents,
search, filtering, and metadata management.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from core.logger import Logger
from core.config import Config
from .models import (
    MarketplaceAgent, AgentCategory, VerificationStatus, MarketplaceDependency,
    DependencyType, MarketplaceStats,
)
from .storage import MarketplaceStorage


class MarketplaceAPI:
    """
    Simulated marketplace backend that provides a catalog of community-built agents.
    In production, this would connect to a remote marketplace server.
    """

    def __init__(self, storage: Optional[MarketplaceStorage] = None):
        self.logger = Logger().get_logger("MarketplaceAPI")
        self.config = Config()
        self.storage = storage or MarketplaceStorage()
        self._catalog: Dict[str, MarketplaceAgent] = {}
        self._load_catalog()

    def _load_catalog(self):
        """Load marketplace catalog from storage or seed with built-in agents."""
        agents_data = self.storage.get_agents(limit=1000)
        if agents_data:
            for data in agents_data:
                agent = MarketplaceAgent.from_dict(data)
                self._catalog[agent.name] = agent
            self.logger.info(f"Loaded {len(self._catalog)} agents from storage")
        else:
            self._seed_catalog()
            self.logger.info(f"Seeded marketplace with {len(self._catalog)} agents")

    def _seed_catalog(self):
        """Seed the marketplace with example community agents."""
        agents = [
            MarketplaceAgent(
                id="weather_agent",
                name="weather_agent",
                display_name="Weather Agent",
                version="2.1.0",
                description="Real-time weather forecasts and alerts for your location",
                long_description="Provides current weather conditions, 7-day forecasts, severe weather alerts, and air quality data. Supports multiple locations and customizable notifications.",
                author="CommunityDev",
                author_email="dev@community.nexus",
                category=AgentCategory.UTILITIES,
                tags=["weather", "forecast", "alerts", "location"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["requests", "geopy"],
                file_size=45000,
                verification_status=VerificationStatus.VERIFIED,
                verified_by="NEXUS Team",
                verified_at=datetime.now(),
                download_count=15234,
                install_count=8901,
                rating=4.7,
                rating_count=342,
                is_featured=True,
                is_official=False,
                capabilities=["weather_forecast", "weather_alerts", "air_quality", "location_weather"],
                permissions=["internet_access", "location_access"],
            ),
            MarketplaceAgent(
                id="email_agent",
                name="email_agent",
                display_name="Email Agent",
                version="1.5.2",
                description="Send, read, and organize emails through NEXUS",
                long_description="Connect to your email accounts (Gmail, Outlook, IMAP) to read, compose, send, and organize emails. Supports templates, scheduling, and smart filtering.",
                author="MailMaster",
                author_email="mail@community.nexus",
                category=AgentCategory.COMMUNICATION,
                tags=["email", "gmail", "outlook", "communication", "imap"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["imaplib", "smtplib"],
                file_size=62000,
                verification_status=VerificationStatus.VERIFIED,
                verified_by="NEXUS Team",
                verified_at=datetime.now(),
                download_count=12045,
                install_count=6789,
                rating=4.5,
                rating_count=289,
                is_featured=True,
                is_official=False,
                capabilities=["send_email", "read_email", "search_email", "email_templates"],
                permissions=["internet_access", "email_credentials"],
            ),
            MarketplaceAgent(
                id="music_agent",
                name="music_agent",
                display_name="Music Agent",
                version="1.0.0",
                description="Control music playback and manage playlists",
                long_description="Integrate with Spotify, YouTube Music, or local media libraries. Control playback, create playlists, discover new music, and set up listening modes.",
                author="AudioPhile",
                author_email="audio@community.nexus",
                category=AgentCategory.ENTERTAINMENT,
                tags=["music", "spotify", "playlists", "media", "audio"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["spotipy", "requests"],
                file_size=38000,
                verification_status=VerificationStatus.VERIFIED,
                verified_by="NEXUS Team",
                verified_at=datetime.now(),
                download_count=9876,
                install_count=5432,
                rating=4.3,
                rating_count=198,
                is_featured=False,
                is_official=False,
                capabilities=["play_music", "create_playlist", "search_music", "now_playing"],
                permissions=["internet_access", "media_control"],
            ),
            MarketplaceAgent(
                id="git_agent",
                name="git_agent",
                display_name="Git Agent",
                version="3.0.1",
                description="Advanced Git operations with AI-powered commit messages",
                long_description="Enhanced Git management with AI-generated commit messages, branch suggestions, conflict resolution, PR summaries, and repository analytics.",
                author="CodeOps",
                author_email="git@community.nexus",
                category=AgentCategory.DEVELOPMENT,
                tags=["git", "version control", "commits", "branches", "ai"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["gitpython"],
                file_size=55000,
                verification_status=VerificationStatus.VERIFIED,
                verified_by="NEXUS Team",
                verified_at=datetime.now(),
                download_count=18234,
                install_count=11234,
                rating=4.8,
                rating_count=567,
                is_featured=True,
                is_official=True,
                capabilities=["git_status", "git_commit", "git_branch", "git_pr", "git_analytics"],
                permissions=["filesystem_access", "git_access"],
            ),
            MarketplaceAgent(
                id="calendar_agent",
                name="calendar_agent",
                display_name="Calendar Agent",
                version="1.2.0",
                description="Manage calendars, schedule meetings, and set reminders",
                long_description="Connect to Google Calendar, Outlook, or Apple Calendar. Create events, manage schedules, find meeting times, and receive smart reminders.",
                author="TimeKeeper",
                author_email="cal@community.nexus",
                category=AgentCategory.PRODUCTIVITY,
                tags=["calendar", "schedule", "meetings", "reminders", "google"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["google-api-python-client"],
                file_size=42000,
                verification_status=VerificationStatus.VERIFIED,
                verified_by="NEXUS Team",
                verified_at=datetime.now(),
                download_count=11234,
                install_count=7890,
                rating=4.6,
                rating_count=312,
                is_featured=True,
                is_official=False,
                capabilities=["create_event", "list_events", "find_time", "reminders"],
                permissions=["internet_access", "calendar_access"],
            ),
            MarketplaceAgent(
                id="docker_agent",
                name="docker_agent",
                display_name="Docker Agent",
                version="1.1.0",
                description="Manage Docker containers and images through NEXUS",
                long_description="Start, stop, monitor, and manage Docker containers. View logs, inspect images, manage networks, and deploy compose stacks.",
                author="ContainerOps",
                author_email="docker@community.nexus",
                category=AgentCategory.DEVELOPMENT,
                tags=["docker", "containers", "devops", "deployment"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["docker"],
                file_size=35000,
                verification_status=VerificationStatus.PENDING,
                download_count=5678,
                install_count=2345,
                rating=4.2,
                rating_count=89,
                is_featured=False,
                is_official=False,
                capabilities=["docker_ps", "docker_logs", "docker_start", "docker_stop", "docker_compose"],
                permissions=["docker_access", "filesystem_access"],
            ),
            MarketplaceAgent(
                id="network_agent",
                name="network_agent",
                display_name="Network Agent",
                version="1.0.3",
                description="Network diagnostics, monitoring, and management",
                long_description="Ping, traceroute, DNS lookup, port scanning, bandwidth monitoring, and network health checks. Includes WiFi analysis and speed testing.",
                author="NetOps",
                author_email="net@community.nexus",
                category=AgentCategory.SYSTEM,
                tags=["network", "diagnostics", "ping", "dns", "monitoring"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["ping3", "dnspython"],
                file_size=28000,
                verification_status=VerificationStatus.VERIFIED,
                verified_by="NEXUS Team",
                verified_at=datetime.now(),
                download_count=7890,
                install_count=4567,
                rating=4.4,
                rating_count=156,
                is_featured=False,
                is_official=False,
                capabilities=["ping", "traceroute", "dns_lookup", "port_scan", "speed_test"],
                permissions=["network_access"],
            ),
            MarketplaceAgent(
                id="translation_agent",
                name="translation_agent",
                display_name="Translation Agent",
                version="2.0.0",
                description="Real-time translation for text and documents",
                long_description="Translate text, documents, and clipboard content between 100+ languages. Supports batch translation, language detection, and glossary management.",
                author="LinguaBot",
                author_email="translate@community.nexus",
                category=AgentCategory.UTILITIES,
                tags=["translation", "language", "documents", "multilingual"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["deep-translator", "langdetect"],
                file_size=32000,
                verification_status=VerificationStatus.VERIFIED,
                verified_by="NEXUS Team",
                verified_at=datetime.now(),
                download_count=13456,
                install_count=8901,
                rating=4.6,
                rating_count=423,
                is_featured=True,
                is_official=False,
                capabilities=["translate_text", "translate_file", "detect_language", "batch_translate"],
                permissions=["filesystem_access", "clipboard_access"],
            ),
            MarketplaceAgent(
                id="database_agent",
                name="database_agent",
                display_name="Database Agent",
                version="1.3.0",
                description="Query and manage databases (SQLite, PostgreSQL, MySQL)",
                long_description="Connect to databases, run queries, visualize results, generate reports, and manage schemas. Supports SQLite, PostgreSQL, MySQL, and MongoDB.",
                author="DataOps",
                author_email="db@community.nexus",
                category=AgentCategory.DEVELOPMENT,
                tags=["database", "sql", "postgresql", "mysql", "mongodb"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["psycopg2", "mysql-connector-python", "pymongo"],
                file_size=78000,
                verification_status=VerificationStatus.PENDING,
                download_count=4567,
                install_count=2123,
                rating=4.1,
                rating_count=67,
                is_featured=False,
                is_official=False,
                capabilities=["query_db", "create_table", "export_data", "schema_info"],
                dependencies=[
                    MarketplaceDependency(name="terminal_agent", dep_type=DependencyType.OPTIONAL),
                ],
                permissions=["network_access", "filesystem_access"],
            ),
            MarketplaceAgent(
                id="home_automation_agent",
                name="home_automation_agent",
                display_name="Home Automation Agent",
                version="1.0.0",
                description="Control smart home devices through NEXUS",
                long_description="Integrate with Home Assistant, Philips Hue, smart plugs, thermostats, and cameras. Create automation routines and monitor device status.",
                author="SmartHome",
                author_email="home@community.nexus",
                category=AgentCategory.AUTOMATION,
                tags=["smart home", "home assistant", "iot", "automation", "hue"],
                license="MIT",
                min_nexus_version="1.0.0",
                python_dependencies=["requests"],
                file_size=52000,
                verification_status=VerificationStatus.UNVERIFIED,
                download_count=3456,
                install_count=1234,
                rating=4.0,
                rating_count=45,
                is_featured=False,
                is_official=False,
                capabilities=["control_lights", "set_thermostat", "camera_view", "automation_rules"],
                permissions=["network_access", "local_network"],
            ),
        ]

        for agent in agents:
            self._catalog[agent.name] = agent
            self.storage.save_agent(agent.to_dict())

    def get_agent(self, agent_id: str = None, agent_name: str = None) -> Optional[MarketplaceAgent]:
        """Get a single agent by ID or name."""
        if agent_name and agent_name in self._catalog:
            return self._catalog[agent_name]
        if agent_id:
            for agent in self._catalog.values():
                if agent.id == agent_id:
                    return agent
        data = self.storage.get_agent(agent_id=agent_id, agent_name=agent_name)
        if data:
            return MarketplaceAgent.from_dict(data)
        return None

    def browse(self, category: str = None, verified_only: bool = False,
               featured_only: bool = False, limit: int = 50, offset: int = 0) -> List[MarketplaceAgent]:
        """Browse the marketplace catalog with filters."""
        agents = self.storage.get_agents(
            category=category, verified_only=verified_only,
            featured_only=featured_only, limit=limit, offset=offset,
        )
        result = []
        for data in agents:
            agent = MarketplaceAgent.from_dict(data)
            result.append(agent)
            self._catalog[agent.name] = agent
        return result

    def search(self, query: str, limit: int = 50) -> List[MarketplaceAgent]:
        """Search the marketplace by name, description, or tags."""
        agents = self.storage.search_agents(query, limit=limit)
        result = []
        for data in agents:
            agent = MarketplaceAgent.from_dict(data)
            result.append(agent)
            self._catalog[agent.name] = agent
        return result

    def get_featured(self, limit: int = 10) -> List[MarketplaceAgent]:
        """Get featured agents."""
        return self.browse(featured_only=True, limit=limit)

    def get_categories(self) -> Dict[str, int]:
        """Get agent counts by category."""
        stats = self.storage.get_stats()
        return stats.get("categories", {})

    def get_stats(self) -> MarketplaceStats:
        """Get marketplace statistics."""
        stats_data = self.storage.get_stats()
        return MarketplaceStats(**stats_data)

    def increment_download(self, agent_name: str):
        """Increment download count for an agent."""
        agent = self._catalog.get(agent_name)
        if agent:
            agent.download_count += 1
            self.storage.update_agent_stats(agent.id, downloads=1)

    def increment_install(self, agent_name: str):
        """Increment install count for an agent."""
        agent = self._catalog.get(agent_name)
        if agent:
            agent.install_count += 1
            self.storage.update_agent_stats(agent.id, installs=1)

    def add_agent(self, agent: MarketplaceAgent):
        """Add a new agent to the marketplace."""
        self._catalog[agent.name] = agent
        self.storage.save_agent(agent.to_dict())
        self.logger.info(f"Added agent to marketplace: {agent.name} v{agent.version}")

    def get_all_agents(self) -> List[MarketplaceAgent]:
        """Get all agents in the catalog."""
        return list(self._catalog.values())
