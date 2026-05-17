"""
Analytics Agent Services
Core services for metrics collection, report generation, resource monitoring,
productivity tracking, and dashboard data aggregation.
"""

import time
import threading
import psutil
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta

from core.logger import Logger
from core.config import Config

from .models import (
    UsageRecord, AgentPerformance, ResourceSnapshot, ProductivitySession,
    AnalyticsReport, DashboardData, MetricType, TimeRange, ReportFormat,
)
from .storage import AnalyticsStorage


class MetricsCollector:
    """Collects and tracks usage metrics across all agents."""

    def __init__(self, storage: AnalyticsStorage):
        self.logger = Logger().get_logger("MetricsCollector")
        self._storage = storage
        self._performances: Dict[str, AgentPerformance] = {}
        self._current_session: Optional[ProductivitySession] = None
        self._session_lock = threading.Lock()
        self._start_session()

    def record_usage(self, agent_name: str, action: str, command: str,
                     success: bool, duration: float, session_id: str = "",
                     user_input_length: int = 0, output_length: int = 0):
        record = UsageRecord(
            agent_name=agent_name,
            action=action,
            command=command,
            success=success,
            duration=duration,
            session_id=session_id,
            user_input_length=user_input_length,
            output_length=output_length,
        )
        self._storage.save_usage_record(record.to_dict())
        self._update_performance(agent_name, duration, success)
        self._update_session(agent_name)

    def _update_performance(self, agent_name: str, duration: float, success: bool, error: str = ""):
        if agent_name not in self._performances:
            self._performances[agent_name] = AgentPerformance(agent_name=agent_name)

        perf = self._performances[agent_name]
        perf.update(duration, success, error)
        self._storage.save_agent_performance(perf.to_dict())

    def _start_session(self):
        self._current_session = ProductivitySession(
            start_time=datetime.now().isoformat(),
            session_type="general",
        )

    def _update_session(self, agent_name: str):
        with self._session_lock:
            if self._current_session:
                self._current_session.commands_executed += 1
                if agent_name not in self._current_session.agents_used:
                    self._current_session.agents_used.append(agent_name)

    def close_session(self):
        with self._session_lock:
            if self._current_session:
                self._current_session.close()
                self._storage.save_productivity_session(self._current_session.to_dict())
                self._start_session()

    def get_performance(self, agent_name: Optional[str] = None) -> List[AgentPerformance]:
        if agent_name and agent_name in self._performances:
            return [self._performances[agent_name]]
        stored = self._storage.get_agent_performance(agent_name)
        return [AgentPerformance.from_dict(d) for d in stored]

    def get_all_performances(self) -> Dict[str, AgentPerformance]:
        stored = self._storage.get_agent_performance()
        for d in stored:
            self._performances[d["agent_name"]] = AgentPerformance.from_dict(d)
        return self._performances

    def get_current_session(self) -> Optional[ProductivitySession]:
        return self._current_session

    def get_session_stats(self) -> Dict[str, Any]:
        if not self._current_session:
            return {}
        return {
            "commands_executed": self._current_session.commands_executed,
            "agents_used": self._current_session.agents_used,
            "duration_minutes": self._current_session.duration_minutes or 0.0,
            "start_time": self._current_session.start_time,
        }


class ReportGenerator:
    """Generates analytics reports with insights and recommendations."""

    def __init__(self, storage: AnalyticsStorage, collector: MetricsCollector):
        self.logger = Logger().get_logger("ReportGenerator")
        self._storage = storage
        self._collector = collector

    def generate_usage_report(self, time_range: TimeRange = TimeRange.DAY) -> AnalyticsReport:
        now = datetime.now()
        if time_range == TimeRange.HOUR:
            start = now - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            start = now - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            start = now - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(days=365)

        start_str = start.isoformat()
        end_str = now.isoformat()

        stats = self._storage.get_usage_stats(start_time=start_str, end_time=end_str)
        hourly = self._storage.get_hourly_distribution()
        daily = self._storage.get_daily_activity(days=30 if time_range != TimeRange.HOUR else 1)
        performances = self._collector.get_all_performances()

        top_agents = sorted(performances.values(), key=lambda p: p.total_calls, reverse=True)[:5]
        slowest_agents = sorted(performances.values(), key=lambda p: p.avg_duration, reverse=True)[:3]
        error_agents = sorted(performances.values(), key=lambda p: p.failed_calls, reverse=True)[:3]

        recommendations = self._generate_recommendations(stats, top_agents, slowest_agents, error_agents)

        summary_lines = [
            f"Usage Report ({time_range.value})",
            f"Total Commands: {stats['total_commands']}",
            f"Success Rate: {stats['success_rate']}%",
            f"Avg Response Time: {stats['avg_duration']:.3f}s",
            f"Agents Used: {len(performances)}",
        ]

        metrics = {
            "stats": stats,
            "hourly_distribution": hourly,
            "daily_activity": daily,
            "top_agents": [p.to_dict() for p in top_agents],
            "slowest_agents": [p.to_dict() for p in slowest_agents],
            "error_agents": [p.to_dict() for p in error_agents],
        }

        trends = {
            "peak_hours": sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3],
            "daily_trend": daily[-7:] if daily else [],
        }

        report = AnalyticsReport(
            report_type="usage",
            time_range=time_range.value,
            summary="\n".join(summary_lines),
            metrics=metrics,
            trends=trends,
            recommendations=recommendations,
        )

        self._storage.save_report(report.to_dict())
        return report

    def generate_performance_report(self) -> AnalyticsReport:
        performances = self._collector.get_all_performances()

        total_calls = sum(p.total_calls for p in performances.values())
        total_success = sum(p.successful_calls for p in performances.values())
        overall_rate = (total_success / max(total_calls, 1)) * 100

        avg_duration = sum(p.avg_duration for p in performances.values()) / max(len(performances), 1)

        summary_lines = [
            "Performance Report",
            f"Total Agent Calls: {total_calls}",
            f"Overall Success Rate: {overall_rate:.1f}%",
            f"Average Response Time: {avg_duration:.3f}s",
            f"Active Agents: {len(performances)}",
        ]

        metrics = {
            "total_calls": total_calls,
            "overall_success_rate": round(overall_rate, 2),
            "avg_response_time": round(avg_duration, 3),
            "agents": {name: perf.to_dict() for name, perf in performances.items()},
        }

        recommendations = []
        for name, perf in performances.items():
            if perf.success_rate < 80 and perf.total_calls > 5:
                recommendations.append(f"{name} has low success rate ({perf.success_rate:.1f}%) - investigate errors")
            if perf.avg_duration > 5.0 and perf.total_calls > 5:
                recommendations.append(f"{name} is slow ({perf.avg_duration:.2f}s avg) - consider optimization")

        report = AnalyticsReport(
            report_type="performance",
            time_range="all",
            summary="\n".join(summary_lines),
            metrics=metrics,
            recommendations=recommendations,
        )

        self._storage.save_report(report.to_dict())
        return report

    def generate_productivity_report(self) -> AnalyticsReport:
        sessions = self._storage.get_productivity_sessions(limit=50)

        total_sessions = len(sessions)
        total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
        total_commands = sum(s.get("commands_executed", 0) for s in sessions)
        total_workflows = sum(s.get("workflows_run", 0) for s in sessions)
        avg_focus = sum(s.get("focus_score", 0) for s in sessions) / max(total_sessions, 1)

        agent_usage: Dict[str, int] = {}
        for s in sessions:
            for agent in s.get("agents_used", []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        summary_lines = [
            "Productivity Report",
            f"Total Sessions: {total_sessions}",
            f"Total Time: {total_duration:.1f} minutes",
            f"Total Commands: {total_commands}",
            f"Workflows Run: {total_workflows}",
            f"Average Focus Score: {avg_focus:.1f}/10",
        ]

        metrics = {
            "total_sessions": total_sessions,
            "total_duration_minutes": round(total_duration, 1),
            "total_commands": total_commands,
            "total_workflows": total_workflows,
            "avg_focus_score": round(avg_focus, 1),
            "agent_usage": agent_usage,
            "recent_sessions": sessions[:10],
        }

        recommendations = []
        if total_sessions == 0:
            recommendations.append("No productivity sessions recorded yet. Start using NEXUS to begin tracking.")
        if avg_focus < 5:
            recommendations.append("Low focus score detected. Consider using Deep Work mode for better concentration.")
        if total_commands > 0 and total_duration > 0:
            cmd_per_min = total_commands / total_duration
            if cmd_per_min > 10:
                recommendations.append("High command rate - consider batching tasks with workflow chains.")

        report = AnalyticsReport(
            report_type="productivity",
            time_range="all",
            summary="\n".join(summary_lines),
            metrics=metrics,
            recommendations=recommendations,
        )

        self._storage.save_report(report.to_dict())
        return report

    @staticmethod
    def _generate_recommendations(stats: Dict, top_agents: list, slowest_agents: list, error_agents: list) -> List[str]:
        recs = []
        if stats.get("success_rate", 100) < 90:
            recs.append(f"Success rate is {stats['success_rate']}% - review failed commands for patterns.")
        if stats.get("avg_duration", 0) > 3.0:
            recs.append("Average response time is high - consider using async execution for long tasks.")
        if error_agents and error_agents[0].failed_calls > 3:
            recs.append(f"{error_agents[0].agent_name} has {error_agents[0].failed_calls} failures - check error logs.")
        if slowest_agents and slowest_agents[0].avg_duration > 5.0:
            recs.append(f"{slowest_agents[0].agent_name} averages {slowest_agents[0].avg_duration:.1f}s - may need optimization.")
        if not recs:
            recs.append("System is performing well. No immediate recommendations.")
        return recs


class ResourceMonitor:
    """Monitors system resources and captures snapshots."""

    def __init__(self, storage: AnalyticsStorage, interval: int = 60):
        self.logger = Logger().get_logger("ResourceMonitor")
        self._storage = storage
        self._interval = interval
        self._monitoring = False
        self._thread: Optional[threading.Thread] = None

    def start_monitoring(self, interval: Optional[int] = None):
        if self._monitoring:
            return {"success": False, "message": "Resource monitoring already active"}
        if interval:
            self._interval = interval
        self._monitoring = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        self.logger.info(f"Resource monitoring started (interval: {self._interval}s)")
        return {"success": True, "message": "Resource monitoring started"}

    def stop_monitoring(self):
        self._monitoring = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("Resource monitoring stopped")
        return {"success": True, "message": "Resource monitoring stopped"}

    def capture_snapshot(self) -> ResourceSnapshot:
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        processes = list(psutil.process_iter())
        net = psutil.net_connections(kind="inet")
        uptime = time.time() - psutil.boot_time()

        snapshot = ResourceSnapshot(
            cpu_percent=cpu,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            memory_total_gb=memory.total / (1024**3),
            disk_percent=disk.percent,
            disk_used_gb=disk.used / (1024**3),
            disk_total_gb=disk.total / (1024**3),
            process_count=len(processes),
            network_connections=len(net),
            uptime_seconds=uptime,
        )

        self._storage.save_resource_snapshot(snapshot.to_dict())
        return snapshot

    def get_latest_snapshot(self) -> Optional[ResourceSnapshot]:
        snapshots = self._storage.get_resource_snapshots(limit=1)
        if snapshots:
            return ResourceSnapshot.from_dict(snapshots[0])
        return None

    def get_resource_history(self, hours: int = 24) -> List[ResourceSnapshot]:
        start = (datetime.now() - timedelta(hours=hours)).isoformat()
        snapshots = self._storage.get_resource_snapshots(start_time=start, limit=1000)
        return [ResourceSnapshot.from_dict(s) for s in snapshots]

    def _monitor_loop(self):
        while self._monitoring:
            try:
                self.capture_snapshot()
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
            time.sleep(self._interval)


class ProductivityTracker:
    """Tracks user productivity sessions and generates insights."""

    def __init__(self, storage: AnalyticsStorage):
        self.logger = Logger().get_logger("ProductivityTracker")
        self._storage = storage
        self._active_sessions: Dict[str, ProductivitySession] = {}

    def start_session(self, session_type: str = "general") -> ProductivitySession:
        session = ProductivitySession(
            start_time=datetime.now().isoformat(),
            session_type=session_type,
        )
        self._active_sessions[session.id] = session
        self.logger.info(f"Productivity session started: {session.id} ({session_type})")
        return session

    def end_session(self, session_id: str) -> Optional[ProductivitySession]:
        if session_id in self._active_sessions:
            session = self._active_sessions.pop(session_id)
            session.close()
            self._storage.save_productivity_session(session.to_dict())
            self.logger.info(f"Productivity session ended: {session_id} ({session.duration_minutes:.1f}min)")
            return session
        return None

    def log_command(self, session_id: str, agent_name: str):
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            session.commands_executed += 1
            if agent_name not in session.agents_used:
                session.agents_used.append(agent_name)

    def log_workflow(self, session_id: str):
        if session_id in self._active_sessions:
            self._active_sessions[session_id].workflows_run += 1

    def log_interruption(self, session_id: str):
        if session_id in self._active_sessions:
            self._active_sessions[session_id].interruptions += 1

    def calculate_focus_score(self, session: ProductivitySession) -> float:
        if session.duration_minutes <= 0:
            return 0.0

        commands_per_min = session.commands_executed / session.duration_minutes
        interruption_penalty = session.interruptions * 0.5

        score = min(commands_per_min * 2, 8.0)
        score -= interruption_penalty
        if session.workflows_run > 0:
            score += min(session.workflows_run * 0.5, 2.0)

        return max(0.0, min(10.0, score))

    def get_session_history(self, limit: int = 20) -> List[ProductivitySession]:
        sessions = self._storage.get_productivity_sessions(limit=limit)
        return [ProductivitySession.from_dict(s) for s in sessions]

    def get_productivity_summary(self, days: int = 7) -> Dict[str, Any]:
        sessions = self._storage.get_productivity_sessions(limit=days * 5)

        total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
        total_commands = sum(s.get("commands_executed", 0) for s in sessions)
        total_workflows = sum(s.get("workflows_run", 0) for s in sessions)
        total_interruptions = sum(s.get("interruptions", 0) for s in sessions)
        avg_focus = sum(s.get("focus_score", 0) for s in sessions) / max(len(sessions), 1)

        return {
            "period_days": days,
            "total_sessions": len(sessions),
            "total_duration_minutes": round(total_duration, 1),
            "total_commands": total_commands,
            "total_workflows": total_workflows,
            "total_interruptions": total_interruptions,
            "avg_focus_score": round(avg_focus, 1),
            "commands_per_session": round(total_commands / max(len(sessions), 1), 1),
            "avg_session_duration": round(total_duration / max(len(sessions), 1), 1),
        }


class AnalyticsEngine:
    """Central engine coordinating all analytics services."""

    def __init__(self, storage: AnalyticsStorage):
        self.logger = Logger().get_logger("AnalyticsEngine")
        self._storage = storage
        self._collector = MetricsCollector(storage)
        self._reporter = ReportGenerator(storage, self._collector)
        self._resource_monitor = ResourceMonitor(storage)
        self._productivity = ProductivityTracker(storage)

    @property
    def collector(self) -> MetricsCollector:
        return self._collector

    @property
    def reporter(self) -> ReportGenerator:
        return self._reporter

    @property
    def resource_monitor(self) -> ResourceMonitor:
        return self._resource_monitor

    @property
    def productivity(self) -> ProductivityTracker:
        return self._productivity

    def track_command(self, agent_name: str, command: str, result: Dict[str, Any],
                      duration: float, session_id: str = ""):
        self._collector.record_usage(
            agent_name=agent_name,
            action="execute",
            command=command,
            success=result.get("success", False),
            duration=duration,
            session_id=session_id,
            user_input_length=len(command),
            output_length=len(result.get("response", "")),
        )

    def get_dashboard(self) -> DashboardData:
        data = self._storage.get_dashboard_data()
        return DashboardData(
            total_commands=data.get("total_commands", 0),
            total_agents_used=data.get("total_agents_used", 0),
            active_sessions=len(self._productivity._active_sessions),
            avg_response_time=data.get("avg_response_time", 0.0),
            success_rate=data.get("success_rate", 0.0),
            top_agents=data.get("top_agents", []),
            recent_activity=data.get("recent_activity", [])[:5],
            resource_usage=data.get("latest_resource", {}),
            productivity_score=self._calculate_productivity_score(),
        )

    def _calculate_productivity_score(self) -> float:
        summary = self._productivity.get_productivity_summary(days=7)
        if summary["total_sessions"] == 0:
            return 0.0

        score = 0.0
        if summary["total_duration_minutes"] > 60:
            score += 2.0
        if summary["total_commands"] > 20:
            score += 2.0
        if summary["total_workflows"] > 0:
            score += 2.0
        score += summary["avg_focus_score"] * 0.4
        score -= summary["total_interruptions"] * 0.3

        return max(0.0, min(10.0, score))

    def cleanup(self, days: int = 90):
        deleted = self._storage.cleanup_old_records(days)
        self.logger.info(f"Cleaned up {deleted} old analytics records")
        return deleted
