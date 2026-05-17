"""
Analytics Agent
Tracks system usage, workflows, agent performance, and productivity metrics.
Provides real-time tracking, dashboard APIs, and historical activity logs.
"""

import time
from typing import Dict, Any, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import TimeRange, ReportFormat
from .storage import AnalyticsStorage
from .services import AnalyticsEngine


class AnalyticsAgent(BaseAgent):
    """Analytics and metrics tracking agent for NEXUS."""

    def __init__(self):
        super().__init__("analytics_agent", "System usage analytics, performance tracking, and productivity metrics")

        self.logger = Logger().get_logger("AnalyticsAgent")
        self.config = Config()

        self._storage = AnalyticsStorage()
        self._engine = AnalyticsEngine(self._storage)

        self._ai_manager = None
        self.logger.info("AnalyticsAgent initialized")

    def set_ai_manager(self, manager):
        self._ai_manager = manager

    def track_execution(self, agent_name: str, command: str, result: Dict[str, Any], duration: float, session_id: str = ""):
        self._engine.track_command(agent_name, command, result, duration, session_id)

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["dashboard", "analytics dashboard", "system dashboard", "overview"]):
                return self._handle_dashboard(command)
            elif self._matches(cmd, ["usage stats", "usage statistics", "command stats", "activity stats"]):
                return self._handle_usage_stats(command)
            elif self._matches(cmd, ["agent performance", "agent stats", "agent metrics", "performance report"]):
                return self._handle_agent_performance(command)
            elif self._matches(cmd, ["usage report", "activity report", "command report"]):
                return self._handle_usage_report(command)
            elif self._matches(cmd, ["productivity report", "productivity stats", "productivity metrics"]):
                return self._handle_productivity_report(command)
            elif self._matches(cmd, ["resource monitor", "resource stats", "resource history", "system resources"]):
                return self._handle_resource_monitor(command)
            elif self._matches(cmd, ["start monitoring", "start resource monitoring", "enable monitoring"]):
                return self._handle_start_monitoring(command)
            elif self._matches(cmd, ["stop monitoring", "stop resource monitoring", "disable monitoring"]):
                return self._handle_stop_monitoring(command)
            elif self._matches(cmd, ["resource snapshot", "capture resources", "current resources"]):
                return self._handle_resource_snapshot(command)
            elif self._matches(cmd, ["session start", "start session", "new session", "begin session"]):
                return self._handle_start_session(command)
            elif self._matches(cmd, ["session end", "end session", "close session", "stop session"]):
                return self._handle_end_session(command)
            elif self._matches(cmd, ["session history", "session log", "past sessions"]):
                return self._handle_session_history(command)
            elif self._matches(cmd, ["productivity summary", "weekly productivity", "monthly productivity"]):
                return self._handle_productivity_summary(command)
            elif self._matches(cmd, ["top agents", "most used agents", "agent ranking"]):
                return self._handle_top_agents(command)
            elif self._matches(cmd, ["hourly activity", "hourly usage", "usage by hour"]):
                return self._handle_hourly_activity(command)
            elif self._matches(cmd, ["daily activity", "daily usage", "usage by day"]):
                return self._handle_daily_activity(command)
            elif self._matches(cmd, ["recent activity", "recent commands", "recent usage"]):
                return self._handle_recent_activity(command)
            elif self._matches(cmd, ["reports", "list reports", "show reports", "saved reports"]):
                return self._handle_list_reports(command)
            elif self._matches(cmd, ["cleanup", "clean data", "purge old data"]):
                return self._handle_cleanup(command)
            elif self._matches(cmd, ["analytics", "analytics agent", "analytics help"]):
                return self._handle_help(command)
            else:
                return self._handle_dashboard(command)
        except Exception as e:
            return {"success": False, "response": f"Error: {e}", "error": str(e)}
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "dashboard",
            "usage_stats",
            "agent_performance",
            "usage_report",
            "productivity_report",
            "resource_monitor",
            "resource_snapshot",
            "start_session",
            "end_session",
            "session_history",
            "productivity_summary",
            "top_agents",
            "hourly_activity",
            "daily_activity",
            "recent_activity",
            "list_reports",
            "cleanup",
        ]

    def _handle_dashboard(self, command: str) -> Dict[str, Any]:
        dashboard = self._engine.get_dashboard()

        lines = [
            "NEXUS Analytics Dashboard",
            "=" * 40,
            f"Total Commands: {dashboard.total_commands}",
            f"Agents Used: {dashboard.total_agents_used}",
            f"Active Sessions: {dashboard.active_sessions}",
            f"Avg Response Time: {dashboard.avg_response_time:.3f}s",
            f"Success Rate: {dashboard.success_rate}%",
            f"Productivity Score: {dashboard.productivity_score:.1f}/10",
        ]

        if dashboard.top_agents:
            lines.append("\nTop Agents:")
            for agent in dashboard.top_agents[:5]:
                name = agent.get("agent_name", "unknown")
                count = agent.get("count", 0)
                rate = agent.get("rate", 0)
                lines.append(f"  {name}: {count} calls ({rate:.0f}% success)")

        if dashboard.recent_activity:
            lines.append("\nRecent Activity:")
            for activity in dashboard.recent_activity[:5]:
                ts = activity.get("timestamp", "")[:19]
                agent = activity.get("agent_name", "?")
                action = activity.get("action", "?")
                status = "OK" if activity.get("success") else "FAIL"
                lines.append(f"  [{ts}] [{status}] {agent}: {action}")

        if dashboard.resource_usage:
            res = dashboard.resource_usage
            lines.append("\nSystem Resources:")
            lines.append(f"  CPU: {res.get('cpu_percent', 0):.1f}%")
            lines.append(f"  Memory: {res.get('memory_percent', 0):.1f}%")
            lines.append(f"  Disk: {res.get('disk_percent', 0):.1f}%")

        return {"success": True, "response": "\n".join(lines), "data": dashboard.to_dict()}

    def _handle_usage_stats(self, command: str) -> Dict[str, Any]:
        agent_name = self._extract_agent_name(command)
        stats = self._storage.get_usage_stats(agent_name=agent_name)

        lines = [
            f"Usage Statistics{' for ' + agent_name if agent_name else ''}",
            "=" * 40,
            f"Total Commands: {stats['total_commands']}",
            f"Success Rate: {stats['success_rate']}%",
            f"Avg Duration: {stats['avg_duration']:.3f}s",
            f"Max Duration: {stats['max_duration']:.3f}s",
            f"Min Duration: {stats['min_duration']:.3f}s",
            f"Successful: {stats['success_count']}",
        ]

        return {"success": True, "response": "\n".join(lines), "data": stats}

    def _handle_agent_performance(self, command: str) -> Dict[str, Any]:
        agent_name = self._extract_agent_name(command)
        performances = self._engine.collector.get_performance(agent_name)

        if not performances:
            return {"success": True, "response": "No performance data available."}

        lines = ["Agent Performance:\n"]
        for perf in performances:
            lines.append(f"  {perf.agent_name}")
            lines.append(f"    Calls: {perf.total_calls} (Success: {perf.successful_calls}, Failed: {perf.failed_calls})")
            lines.append(f"    Success Rate: {perf.success_rate:.1f}%")
            lines.append(f"    Avg Duration: {perf.avg_duration:.3f}s (Min: {perf.min_duration:.3f}s, Max: {perf.max_duration:.3f}s)")
            if perf.error_counts:
                top_errors = sorted(perf.error_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                lines.append(f"    Top Errors: {', '.join(f'{e}({c})' for e, c in top_errors)}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [p.to_dict() for p in performances]}

    def _handle_usage_report(self, command: str) -> Dict[str, Any]:
        time_range = TimeRange.DAY
        if "week" in command.lower():
            time_range = TimeRange.WEEK
        elif "month" in command.lower():
            time_range = TimeRange.MONTH
        elif "hour" in command.lower():
            time_range = TimeRange.HOUR

        report = self._engine.reporter.generate_usage_report(time_range)
        lines = [report.summary]

        if report.recommendations:
            lines.append("\nRecommendations:")
            for rec in report.recommendations:
                lines.append(f"  - {rec}")

        return {"success": True, "response": "\n".join(lines), "data": report.to_dict()}

    def _handle_productivity_report(self, command: str) -> Dict[str, Any]:
        report = self._engine.reporter.generate_productivity_report()
        lines = [report.summary]

        if report.recommendations:
            lines.append("\nRecommendations:")
            for rec in report.recommendations:
                lines.append(f"  - {rec}")

        return {"success": True, "response": "\n".join(lines), "data": report.to_dict()}

    def _handle_resource_monitor(self, command: str) -> Dict[str, Any]:
        hours = self._extract_number(command, default=24)
        snapshots = self._engine.resource_monitor.get_resource_history(hours=hours)

        if not snapshots:
            return {"success": True, "response": "No resource history available. Start monitoring to collect data."}

        avg_cpu = sum(s.cpu_percent for s in snapshots) / len(snapshots)
        avg_mem = sum(s.memory_percent for s in snapshots) / len(snapshots)
        avg_disk = sum(s.disk_percent for s in snapshots) / len(snapshots)
        max_cpu = max(s.cpu_percent for s in snapshots)
        max_mem = max(s.memory_percent for s in snapshots)

        lines = [
            f"Resource History (Last {hours}h, {len(snapshots)} snapshots)",
            "=" * 40,
            f"CPU: Avg {avg_cpu:.1f}%, Max {max_cpu:.1f}%",
            f"Memory: Avg {avg_mem:.1f}%, Max {max_mem:.1f}%",
            f"Disk: Avg {avg_disk:.1f}%",
        ]

        if snapshots:
            latest = snapshots[0]
            lines.append(f"\nLatest ({latest.timestamp[:19]}):")
            lines.append(f"  CPU: {latest.cpu_percent:.1f}%")
            lines.append(f"  Memory: {latest.memory_percent:.1f}% ({latest.memory_used_gb:.1f}GB / {latest.memory_total_gb:.1f}GB)")
            lines.append(f"  Disk: {latest.disk_percent:.1f}% ({latest.disk_used_gb:.1f}GB / {latest.disk_total_gb:.1f}GB)")
            lines.append(f"  Processes: {latest.process_count}")
            lines.append(f"  Network Connections: {latest.network_connections}")
            lines.append(f"  Uptime: {latest.uptime_seconds / 3600:.1f}h")

        return {"success": True, "response": "\n".join(lines), "data": [s.to_dict() for s in snapshots[:20]]}

    def _handle_start_monitoring(self, command: str) -> Dict[str, Any]:
        interval = self._extract_number(command, default=60)
        result = self._engine.resource_monitor.start_monitoring(interval)
        return {"success": result["success"], "response": result["message"]}

    def _handle_stop_monitoring(self, command: str) -> Dict[str, Any]:
        result = self._engine.resource_monitor.stop_monitoring()
        return {"success": result["success"], "response": result["message"]}

    def _handle_resource_snapshot(self, command: str) -> Dict[str, Any]:
        snapshot = self._engine.resource_monitor.capture_snapshot()
        lines = [
            "Resource Snapshot:",
            f"CPU: {snapshot.cpu_percent:.1f}%",
            f"Memory: {snapshot.memory_percent:.1f}% ({snapshot.memory_used_gb:.1f}GB / {snapshot.memory_total_gb:.1f}GB)",
            f"Disk: {snapshot.disk_percent:.1f}% ({snapshot.disk_used_gb:.1f}GB / {snapshot.disk_total_gb:.1f}GB)",
            f"Processes: {snapshot.process_count}",
            f"Network Connections: {snapshot.network_connections}",
            f"Uptime: {snapshot.uptime_seconds / 3600:.1f}h",
        ]
        return {"success": True, "response": "\n".join(lines), "data": snapshot.to_dict()}

    def _handle_start_session(self, command: str) -> Dict[str, Any]:
        session_type = self._extract_content(command, ["session start", "start session", "new session", "begin session"])
        if not session_type or session_type.lower() in ("session", "start", "new", "begin"):
            session_type = "general"

        session = self._engine.productivity.start_session(session_type)
        return {
            "success": True,
            "response": f"Productivity session started (ID: {session.id}, Type: {session_type})",
            "data": {"session_id": session.id},
        }

    def _handle_end_session(self, command: str) -> Dict[str, Any]:
        session_id = self._extract_id(command)
        if not session_id:
            active = self._engine.productivity._active_sessions
            if active:
                session_id = list(active.keys())[0]
            else:
                return {"success": False, "response": "No active sessions to end."}

        session = self._engine.productivity.end_session(session_id)
        if session:
            focus = self._engine.productivity.calculate_focus_score(session)
            return {
                "success": True,
                "response": f"Session ended: {session.duration_minutes:.1f} minutes, {session.commands_executed} commands, Focus Score: {focus:.1f}/10",
                "data": session.to_dict(),
            }
        return {"success": False, "response": f"Session {session_id} not found."}

    def _handle_session_history(self, command: str) -> Dict[str, Any]:
        sessions = self._engine.productivity.get_session_history(limit=10)

        if not sessions:
            return {"success": True, "response": "No session history available."}

        lines = [f"Session History ({len(sessions)}):\n"]
        for s in sessions:
            lines.append(f"  [{s.start_time[:19]}] {s.session_type} - {s.duration_minutes:.1f}min")
            lines.append(f"    Commands: {s.commands_executed}, Agents: {', '.join(s.agents_used[:3])}")
            lines.append(f"    Workflows: {s.workflows_run}, Focus: {s.focus_score:.1f}/10")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": [s.to_dict() for s in sessions]}

    def _handle_productivity_summary(self, command: str) -> Dict[str, Any]:
        days = 7
        if "month" in command.lower():
            days = 30
        elif "week" in command.lower():
            days = 7

        summary = self._engine.productivity.get_productivity_summary(days=days)

        lines = [
            f"Productivity Summary (Last {days} days)",
            "=" * 40,
            f"Sessions: {summary['total_sessions']}",
            f"Total Time: {summary['total_duration_minutes']:.1f} minutes",
            f"Commands Executed: {summary['total_commands']}",
            f"Workflows Run: {summary['total_workflows']}",
            f"Interruptions: {summary['total_interruptions']}",
            f"Avg Focus Score: {summary['avg_focus_score']:.1f}/10",
            f"Commands/Session: {summary['commands_per_session']:.1f}",
            f"Avg Session: {summary['avg_session_duration']:.1f} minutes",
        ]

        return {"success": True, "response": "\n".join(lines), "data": summary}

    def _handle_top_agents(self, command: str) -> Dict[str, Any]:
        performances = self._engine.collector.get_all_performances()
        sorted_agents = sorted(performances.values(), key=lambda p: p.total_calls, reverse=True)

        if not sorted_agents:
            return {"success": True, "response": "No agent usage data available."}

        lines = ["Top Agents by Usage:\n"]
        for i, perf in enumerate(sorted_agents[:10], 1):
            lines.append(f"  {i}. {perf.agent_name}")
            lines.append(f"     Calls: {perf.total_calls}, Success: {perf.success_rate:.1f}%, Avg: {perf.avg_duration:.3f}s")

        return {"success": True, "response": "\n".join(lines), "data": [p.to_dict() for p in sorted_agents[:10]]}

    def _handle_hourly_activity(self, command: str) -> Dict[str, Any]:
        agent_name = self._extract_agent_name(command)
        hourly = self._storage.get_hourly_distribution(agent_name)

        if not hourly:
            return {"success": True, "response": "No hourly activity data available."}

        lines = ["Hourly Activity Distribution:\n"]
        max_count = max(hourly.values()) if hourly else 1
        for hour in sorted(hourly.keys()):
            count = hourly[hour]
            bar = "#" * int(count / max(max_count, 1) * 30)
            lines.append(f"  {hour}:00  {count:4d}  {bar}")

        return {"success": True, "response": "\n".join(lines), "data": hourly}

    def _handle_daily_activity(self, command: str) -> Dict[str, Any]:
        days = self._extract_number(command, default=30)
        daily = self._storage.get_daily_activity(days=days)

        if not daily:
            return {"success": True, "response": "No daily activity data available."}

        lines = [f"Daily Activity (Last {days} days):\n"]
        for day in daily:
            lines.append(f"  {day['day']}: {day['commands']} commands, Avg {day.get('avg_dur', 0):.3f}s, {day.get('successes', 0)} successful")

        return {"success": True, "response": "\n".join(lines), "data": daily}

    def _handle_recent_activity(self, command: str) -> Dict[str, Any]:
        limit = self._extract_number(command, default=20)
        records = self._storage.get_usage_records(limit=limit)

        if not records:
            return {"success": True, "response": "No recent activity."}

        lines = [f"Recent Activity ({len(records)}):\n"]
        for r in records[:15]:
            status = "OK" if r.get("success") else "FAIL"
            lines.append(f"  [{r['timestamp'][:19]}] [{status}] {r['agent_name']}: {r['action']} ({r['duration']:.3f}s)")

        return {"success": True, "response": "\n".join(lines), "data": records}

    def _handle_list_reports(self, command: str) -> Dict[str, Any]:
        reports = self._storage.get_reports(limit=10)

        if not reports:
            return {"success": True, "response": "No saved reports. Generate a report first."}

        lines = [f"Saved Reports ({len(reports)}):\n"]
        for r in reports:
            lines.append(f"  [{r['generated_at'][:19]}] {r['report_type']} ({r['time_range']})")
            lines.append(f"    {r['summary'][:100]}")
            lines.append("")

        return {"success": True, "response": "\n".join(lines), "data": reports}

    def _handle_cleanup(self, command: str) -> Dict[str, Any]:
        days = self._extract_number(command, default=90)
        deleted = self._engine.cleanup(days)
        return {"success": True, "response": f"Cleaned up {deleted} records older than {days} days."}

    def _handle_help(self, command: str) -> Dict[str, Any]:
        lines = [
            "Analytics Agent Commands:",
            "",
            "Dashboard & Overview:",
            "  dashboard               - Show analytics dashboard",
            "  usage stats [agent]     - Show usage statistics",
            "  top agents              - Show most used agents",
            "",
            "Reports:",
            "  usage report [day/week/month] - Generate usage report",
            "  productivity report     - Generate productivity report",
            "  agent performance       - Show agent performance metrics",
            "  reports                 - List saved reports",
            "",
            "Resources:",
            "  resource monitor        - Show resource history",
            "  resource snapshot       - Capture current resources",
            "  start monitoring [sec]  - Start resource monitoring",
            "  stop monitoring         - Stop resource monitoring",
            "",
            "Productivity:",
            "  start session [type]    - Start productivity session",
            "  end session [id]        - End productivity session",
            "  session history         - Show session history",
            "  productivity summary    - Show productivity summary",
            "",
            "Activity:",
            "  hourly activity         - Show hourly usage distribution",
            "  daily activity [days]   - Show daily activity",
            "  recent activity [count] - Show recent commands",
            "",
            "Maintenance:",
            "  cleanup [days]          - Clean up old records",
        ]

        return {"success": True, "response": "\n".join(lines)}

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: list) -> str:
        lower = command.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                return command[len(prefix):].strip()
            idx = lower.find(prefix)
            if idx >= 0:
                return command[idx + len(prefix):].strip()
        return command.strip()

    @staticmethod
    def _extract_id(command: str) -> str:
        import re
        match = re.search(r'\b([a-f0-9]{8})\b', command)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        import re
        match = re.search(r'\b(\d+)\b', command)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_agent_name(command: str) -> Optional[str]:
        agent_names = [
            "file_agent", "web_agent", "automation_agent", "coding_agent",
            "memory_agent", "vision_agent", "notification_agent", "scheduler_agent",
            "knowledge_agent", "terminal_agent", "personality_agent", "workflow_agent",
            "plugin_agent", "security_agent", "workflow_chain_agent",
        ]
        lower = command.lower()
        for name in agent_names:
            if name in lower:
                return name
        return None
