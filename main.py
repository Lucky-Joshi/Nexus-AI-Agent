#!/usr/bin/env python3
"""
NEXUS - AI Desktop Operating Companion
Main entry point for the application.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import Config
from core.logger import Logger
from core.database import Database
from core.base_agent import AgentStatus
from manager.manager import AIManager
from agents.file_agent import FileAgent
from agents.web_agent import WebAgent
from agents.automation_agent import AutomationAgent
from agents.coding_agent import CodingAgent
from agents.memory_agent import MemoryAgent
from agents.vision_agent import VisionAgent
from agents.notification_agent import NotificationAgent
from agents.scheduler_agent import SchedulerAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.terminal_agent import TerminalAgent
from agents.personality_agent import PersonalityAgent
from agents.workflow_agent import WorkflowAgent
from agents.security_agent import SecurityAgent
from agents.plugin_agent import PluginAgent
from agents.workflow_chain_agent import WorkflowChainAgent
from agents.analytics_agent import AnalyticsAgent
from agents.context_awareness_agent import ContextAwarenessAgent
from agents.learning_agent import LearningAgent
from agents.communication_bus_agent import CommunicationBusAgent
from agents.planner_agent import PlannerAgent
from agents.marketplace_agent import MarketplaceAgent


def initialize_nexus() -> AIManager:
    """Initialize the NEXUS AI ecosystem."""
    config = Config()
    logger = Logger()
    log = logger.get_logger("NEXUS")

    log.info("=" * 60)
    log.info("NEXUS AI System Starting")
    log.info(f"Version: {config.get('app.version', '1.0.0')}")
    log.info("=" * 60)

    db = Database()
    log.info(f"Database initialized: {db.db_path}")

    manager = AIManager()

    agents = [
        FileAgent(),
        WebAgent(),
        AutomationAgent(),
        CodingAgent(),
        MemoryAgent(),
        VisionAgent(),
        NotificationAgent(),
        SchedulerAgent(),
        KnowledgeAgent(),
        TerminalAgent(),
        PersonalityAgent(),
        WorkflowAgent(),
        PluginAgent(),
        SecurityAgent(),
        WorkflowChainAgent(),
        AnalyticsAgent(),
        ContextAwarenessAgent(),
        LearningAgent(),
        CommunicationBusAgent(),
        PlannerAgent(),
        MarketplaceAgent(),
    ]

    for agent in agents:
        if config.get(f"agents.{agent.name}.enabled", True):
            manager.register_agent(agent)
            log.info(f"Agent enabled: {agent.name}")
        else:
            log.info(f"Agent disabled: {agent.name}")

    chain_agent = manager.agents.get("workflow_chain_agent")
    if chain_agent:
        chain_agent.set_ai_manager(manager)
        log.info("WorkflowChainAgent connected to AIManager")

    context_agent = manager.agents.get("context_awareness_agent")
    if context_agent:
        context_agent.set_ai_manager(manager)
        log.info("ContextAwarenessAgent connected to AIManager")

    bus_agent = manager.agents.get("communication_bus_agent")
    if bus_agent:
        bus_agent.set_ai_manager(manager)
        log.info("CommunicationBusAgent connected to AIManager")

    planner_agent = manager.agents.get("planner_agent")
    if planner_agent:
        planner_agent.set_ai_manager(manager)
        log.info("PlannerAgent connected to AIManager")

    marketplace_agent = manager.agents.get("marketplace_agent")
    if marketplace_agent:
        marketplace_agent.set_ai_manager(manager)
        log.info("MarketplaceAgent connected to AIManager")

    log.info(f"NEXUS initialized with {len(manager.agents)} agents")
    return manager


def run_cli_mode(manager: AIManager):
    """Run NEXUS in CLI mode for testing."""
    print("\n" + "=" * 60)
    print("  NEXUS AI - Desktop Operating Companion")
    print("  Type 'help' for commands, 'exit' to quit")
    print("=" * 60 + "\n")

    while manager.is_running:
        try:
            command = input("NEXUS> ").strip()

            if not command:
                continue

            if command.lower() in ("exit", "quit", "q"):
                print("\nShutting down NEXUS...")
                break

            result = manager.process_command(command)

            print(f"\n[{result.get('agent', 'NEXUS').upper()}] {result.get('response', 'No response')}\n")

        except KeyboardInterrupt:
            print("\n\nShutting down NEXUS...")
            break
        except EOFError:
            break

    manager.shutdown()
    print("NEXUS shutdown complete.")


def run_gui_mode(manager: AIManager):
    """Run NEXUS with PyQt6 GUI."""
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        window = MainWindow(manager)
        window.show()

        sys.exit(app.exec())

    except ImportError:
        print("PyQt6 not found. Running in CLI mode.")
        print("Install with: pip install PyQt6")
        run_cli_mode(manager)


def main():
    """Main entry point."""
    manager = initialize_nexus()

    if "--cli" in sys.argv:
        run_cli_mode(manager)
    elif "--gui" in sys.argv:
        run_gui_mode(manager)
    else:
        try:
            from PyQt6.QtWidgets import QApplication
            run_gui_mode(manager)
        except ImportError:
            run_cli_mode(manager)


if __name__ == "__main__":
    main()
