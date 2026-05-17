#!/usr/bin/env python3
"""
NEXUS - AI Operating Environment
Terminal-native AI operating companion.
"""

import sys
import os

# ── CRITICAL: Must happen before ANY other imports ──
# Suppress all warnings and redirect stderr during startup
import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Ensure UTF-8 encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    """Parse command-line arguments."""
    args = {
        "verbose": "--verbose" in sys.argv or "-v" in sys.argv,
        "debug": "--debug" in sys.argv or "-d" in sys.argv,
        "cli": "--cli" in sys.argv,
    }
    return args


def initialize_nexus(loader=None, phases=None):
    """Initialize the NEXUS AI ecosystem with cinematic tracking."""
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

    config = Config()
    logger = Logger()
    log = logger.get_logger("NEXUS")

    log.info("=" * 60)
    log.info("NEXUS AI System Starting")
    log.info(f"Version: {config.get('app.version', '2.0.0')}")
    log.info("=" * 60)

    if loader and phases:
        from terminal.loader import PhaseTracker

        # ── Phase 1: Core Systems ──
        with PhaseTracker(phases["core"], loader) as tracker:
            with tracker.step("Configuration"):
                pass
            with tracker.step("Logging System"):
                pass
            with tracker.step("Database Engine"):
                db = Database()
                log.info(f"Database initialized: {db.db_path}")

        # ── Phase 2: AI Systems ──
        with PhaseTracker(phases["ai"], loader) as tracker:
            with tracker.step("LLM Provider"):
                pass
            with tracker.step("Memory Systems"):
                pass
            with tracker.step("Knowledge Base"):
                pass

            manager = AIManager()
            log.info(f"AIManager initialized (session: {manager.session_id})")

        # ── Phase 3: Agent Systems ──
        agents_list = [
            ("File Agent", FileAgent()),
            ("Web Agent", WebAgent()),
            ("Coding Agent", CodingAgent()),
            ("Automation Agent", AutomationAgent()),
            ("Terminal Agent", TerminalAgent()),
            ("Vision Agent", VisionAgent()),
            ("Notification Agent", NotificationAgent()),
            ("Scheduler Agent", SchedulerAgent()),
            ("Knowledge Agent", KnowledgeAgent()),
            ("Personality Agent", PersonalityAgent()),
            ("Workflow Agent", WorkflowAgent()),
            ("Security Agent", SecurityAgent()),
            ("Plugin Agent", PluginAgent()),
            ("Workflow Chain Agent", WorkflowChainAgent()),
            ("Analytics Agent", AnalyticsAgent()),
            ("Context Awareness Agent", ContextAwarenessAgent()),
            ("Learning Agent", LearningAgent()),
            ("Communication Bus", CommunicationBusAgent()),
            ("Planner Agent", PlannerAgent()),
            ("Marketplace Agent", MarketplaceAgent()),
        ]

        with PhaseTracker(phases["agents"], loader) as tracker:
            for name, agent in agents_list:
                with tracker.step(name) as st:
                    if config.get(f"agents.{agent.name}.enabled", True):
                        manager.register_agent(agent)
                        log.info(f"Agent enabled: {agent.name}")
                    else:
                        st.skip("disabled")
                        log.info(f"Agent disabled: {agent.name}")

        # ── Phase 4: Services ──
        with PhaseTracker(phases["services"], loader) as tracker:
            with tracker.step("Event Bus"):
                pass
            with tracker.step("Task Executor"):
                pass
            with tracker.step("Security Layer"):
                pass

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

        # ── Phase 5: Finalization ──
        with PhaseTracker(phases["final"], loader) as tracker:
            with tracker.step("Health Checks"):
                pass
            with tracker.step("Agent Registration"):
                log.info(f"NEXUS initialized with {len(manager.agents)} agents")
            with tracker.step("System Ready"):
                pass

        return manager

    # ── Fallback: no loader (verbose/debug mode) ──
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


def run_terminal_mode(manager):
    """Run NEXUS in terminal-native mode using Textual."""
    try:
        from terminal.app import NEXUSTerminalApp
        app = NEXUSTerminalApp(manager)
        app.run()
    except ImportError:
        print("Textual not found. Install with: pip install textual")
        run_simple_cli(manager)


def run_simple_cli(manager):
    """Fallback simple CLI mode."""
    print("\n" + "=" * 60)
    print("  NEXUS AI - Terminal Operating Environment")
    print("  Type 'help' for commands, 'exit' to quit")
    print("=" * 60 + "\n")

    while manager.is_running:
        try:
            command = input("nexus> ").strip()

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


def main():
    """Main entry point."""
    args = parse_args()

    if args["debug"]:
        log_mode = "debug"
    elif args["verbose"]:
        log_mode = "verbose"
    else:
        log_mode = "normal"

    from core.logger import Logger
    logger = Logger()
    logger.set_mode(log_mode)

    if args["cli"]:
        manager = initialize_nexus()
        run_simple_cli(manager)
        return

    if log_mode == "normal":
        from rich.console import Console
        from terminal.loader import CinematicLoader, create_default_phases

        console = Console()
        loader = CinematicLoader(console=console)
        phases = create_default_phases(loader)

        manager = loader.run(
            init_fn=lambda: initialize_nexus(loader=loader, phases=phases)
        )
    else:
        manager = initialize_nexus()

    run_terminal_mode(manager)


if __name__ == "__main__":
    main()
