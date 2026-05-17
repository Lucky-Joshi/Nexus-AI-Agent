"""
NEXUS - Cinematic Terminal Loader
Polished startup experience with animated spinners, grouped phases,
progress indicators, and clean status summaries.
"""

import sys
import os
import time
import warnings
import contextlib
import io
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.rule import Rule


class LogLevel(Enum):
    NORMAL = "normal"
    VERBOSE = "verbose"
    DEBUG = "debug"


class PhaseStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class PhaseStep:
    """A single initialization step within a phase."""
    name: str
    status: PhaseStatus = PhaseStatus.PENDING
    message: str = ""
    duration: float = 0.0
    _start_time: float = 0.0


@dataclass
class StartupPhase:
    """A group of initialization steps."""
    name: str
    steps: List[PhaseStep] = field(default_factory=list)
    status: PhaseStatus = PhaseStatus.PENDING

    def add_step(self, name: str) -> PhaseStep:
        step = PhaseStep(name=name)
        self.steps.append(step)
        return step

    @property
    def is_complete(self) -> bool:
        return all(
            s.status in (PhaseStatus.SUCCESS, PhaseStatus.SKIPPED, PhaseStatus.WARNING)
            for s in self.steps
        ) if self.steps else True

    @property
    def has_failures(self) -> bool:
        return any(s.status == PhaseStatus.FAILED for s in self.steps)

    @property
    def progress(self) -> float:
        if not self.steps:
            return 1.0
        done = sum(
            1 for s in self.steps
            if s.status in (PhaseStatus.SUCCESS, PhaseStatus.SKIPPED, PhaseStatus.WARNING)
        )
        return done / len(self.steps)


@contextlib.contextmanager
def suppress_output():
    """Suppress stdout and stderr completely."""
    devnull = open(os.devnull, "w", encoding="utf-8", errors="replace")
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = devnull
        sys.stderr = devnull
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        devnull.close()


class CinematicLoader:
    """
    Manages the cinematic startup experience for NEXUS.
    Displays animated phases, spinners, and a clean summary dashboard.
    """

    SPINNER_CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    BANNER_LINES = [
        "███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗",
        "████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝",
        "██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗",
        "██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║",
        "██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║",
        "╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝",
    ]

    def __init__(self, console: Optional[Console] = None, log_level: LogLevel = LogLevel.NORMAL):
        if console is None:
            console = Console(
                force_terminal=True,
                width=90,
                legacy_windows=False,
                color_system="truecolor",
            )
        self.console = console
        self.log_level = log_level
        self.phases: List[StartupPhase] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self._live: Optional[Live] = None
        self._spinner_idx = 0
        self._refresh_fn: Optional[Callable] = None
        self._warnings_caught: List[str] = []

    def add_phase(self, name: str) -> StartupPhase:
        phase = StartupPhase(name=name)
        self.phases.append(phase)
        return phase

    def get_phase(self, name: str) -> StartupPhase:
        for p in self.phases:
            if p.name == name:
                return p
        return self.add_phase(name)

    def _next_spinner(self) -> str:
        ch = self.SPINNER_CHARS[self._spinner_idx % len(self.SPINNER_CHARS)]
        self._spinner_idx += 1
        return ch

    def _render_banner(self) -> RenderableType:
        lines: list = []
        for line in self.BANNER_LINES:
            lines.append(Align.center(Text(line, style="bold #00D4FF")))
        lines.append(Align.center(Text("AI Operating Environment  •  Terminal-Native", style="dim #7B61FF")))
        lines.append(Align.center(Text("v2.0.0", style="dim #555555")))
        lines.append("")
        return Group(*lines)

    def _render_progress(self, pct: float) -> RenderableType:
        filled = int(pct * 30)
        bar = "#" * filled + "-" * (30 - filled)
        return Text(f"  [{bar}] {int(pct * 100)}%", style="#00D4FF")

    def _render_phase_line(self, phase: StartupPhase) -> RenderableType:
        if phase.status == PhaseStatus.RUNNING:
            icon = Text(f" {self._next_spinner()} ", style="#FFB800")
        elif phase.status == PhaseStatus.SUCCESS:
            icon = Text(" ✓ ", style="#00E676")
        elif phase.status == PhaseStatus.FAILED:
            icon = Text(" ✗ ", style="#FF4757")
        else:
            icon = Text(" · ", style="#555555")
        name = Text(phase.name, style="bold #E8E8E8")
        return Group(icon, name)

    def _render_step_line(self, step: PhaseStep) -> RenderableType:
        indent = "    "
        if step.status == PhaseStatus.RUNNING:
            icon = Text(f"{self._next_spinner()} ", style="#FFB800")
        elif step.status == PhaseStatus.SUCCESS:
            icon = Text("✓ ", style="#00E676")
        elif step.status == PhaseStatus.FAILED:
            icon = Text("✗ ", style="#FF4757")
        elif step.status == PhaseStatus.WARNING:
            icon = Text("! ", style="#FFB800")
        elif step.status == PhaseStatus.SKIPPED:
            icon = Text("- ", style="#555555")
        else:
            icon = Text("· ", style="#555555")

        name = Text(step.name, style="#C8C8C8")
        parts: list = [Text(indent), icon, name]

        if step.message:
            parts.append(Text(f"  {step.message}", style="dim #888888"))
        if step.duration > 0.01 and step.status in (PhaseStatus.SUCCESS, PhaseStatus.FAILED):
            parts.append(Text(f" ({step.duration:.1f}s)", style="dim #555555"))

        return Group(*parts)

    def _render_view(self) -> RenderableType:
        elements: list = [self._render_banner()]

        total = sum(len(p.steps) for p in self.phases)
        done = sum(
            1 for p in self.phases for s in p.steps
            if s.status in (PhaseStatus.SUCCESS, PhaseStatus.SKIPPED, PhaseStatus.WARNING)
        )
        pct = done / total if total > 0 else 0

        elements.append(self._render_progress(pct))
        elements.append("")

        for phase in self.phases:
            elements.append(self._render_phase_line(phase))
            if phase.status == PhaseStatus.RUNNING or phase.is_complete:
                for step in phase.steps:
                    elements.append(self._render_step_line(step))
            elements.append("")

        if self.start_time:
            elapsed = time.time() - self.start_time
            elements.append(Text(f"  elapsed {elapsed:.1f}s", style="dim #555555"))

        return Group(*elements)

    def _render_dashboard(self) -> RenderableType:
        total_time = (self.end_time or time.time()) - (self.start_time or time.time())
        success = sum(1 for p in self.phases for s in p.steps if s.status == PhaseStatus.SUCCESS)
        warns = sum(1 for p in self.phases for s in p.steps if s.status == PhaseStatus.WARNING)
        fails = sum(1 for p in self.phases for s in p.steps if s.status == PhaseStatus.FAILED)

        table = Table.grid(padding=(0, 2))
        table.add_column(style="#00D4FF", justify="right")
        table.add_column(style="#E8E8E8")

        table.add_row("startup", f"{total_time:.1f}s")
        table.add_row("phases", f"{len(self.phases)} / {len(self.phases)}")
        table.add_row("steps", f"{success} ok, {warns} warn, {fails} fail")
        table.add_row("", "")

        for phase in self.phases:
            ok = not phase.has_failures
            table.add_row(
                Text("  ✓" if ok else "  ✗", style="#00E676" if ok else "#FF4757"),
                Text(phase.name, style="#E8E8E8"),
            )

        return Group(
            Rule(style="#00D4FF"),
            Align.center(Text("NEXUS ONLINE", style="bold #00E676")),
            "",
            table,
            "",
            Align.center(Text("type /help to begin", style="dim #7B61FF")),
            Rule(style="#00D4FF"),
        )

    def run(self, init_fn: Callable[[], Any]) -> Any:
        """Run the cinematic loader with the given initialization function."""
        self.start_time = time.time()
        self._spinner_idx = 0

        if self.log_level == LogLevel.NORMAL:
            warnings.filterwarnings("ignore")

        result = None

        if self.log_level in (LogLevel.VERBOSE, LogLevel.DEBUG):
            result = init_fn()
            self.end_time = time.time()
            return result

        def refresh():
            self._live.update(self._render_view())

        self._refresh_fn = refresh

        with Live(
            self._render_view(),
            console=self.console,
            refresh_per_second=8,
            transient=False,
            vertical_overflow="visible",
        ) as live:
            self._live = live
            try:
                with suppress_output():
                    result = init_fn()
            finally:
                self.end_time = time.time()
                refresh()

        self.console.print()
        self.console.print(self._render_dashboard())
        self.console.print()

        return result

    def step_start(self, step: PhaseStep):
        step.status = PhaseStatus.RUNNING
        step._start_time = time.time()
        if self._refresh_fn:
            self._refresh_fn()

    def step_complete(self, step: PhaseStep, message: str = ""):
        step.status = PhaseStatus.SUCCESS
        step.message = message
        step.duration = time.time() - step._start_time
        if self._refresh_fn:
            self._refresh_fn()

    def step_fail(self, step: PhaseStep, message: str = ""):
        step.status = PhaseStatus.FAILED
        step.message = message
        step.duration = time.time() - step._start_time
        if self._refresh_fn:
            self._refresh_fn()

    def step_warn(self, step: PhaseStep, message: str = ""):
        step.status = PhaseStatus.WARNING
        step.message = message
        step.duration = time.time() - step._start_time
        if self._refresh_fn:
            self._refresh_fn()

    def step_skip(self, step: PhaseStep, message: str = ""):
        step.status = PhaseStatus.SKIPPED
        step.message = message
        if self._refresh_fn:
            self._refresh_fn()

    def phase_start(self, phase: StartupPhase):
        phase.status = PhaseStatus.RUNNING
        if self._refresh_fn:
            self._refresh_fn()

    def phase_complete(self, phase: StartupPhase):
        phase.status = PhaseStatus.FAILED if phase.has_failures else PhaseStatus.SUCCESS
        if self._refresh_fn:
            self._refresh_fn()


class PhaseTracker:
    """Context manager for tracking a phase and its steps."""

    def __init__(self, phase: StartupPhase, loader: CinematicLoader):
        self.phase = phase
        self.loader = loader

    def __enter__(self):
        self.loader.phase_start(self.phase)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loader.phase_complete(self.phase)
        return False

    def step(self, name: str) -> "StepTracker":
        step = self.phase.add_step(name)
        return StepTracker(step, self.loader)


class StepTracker:
    """Context manager for tracking an individual step."""

    def __init__(self, step: PhaseStep, loader: CinematicLoader):
        self.step = step
        self.loader = loader

    def __enter__(self):
        self.loader.step_start(self.step)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.loader.step_fail(self.step, message=str(exc_val))
        else:
            self.loader.step_complete(self.step)
        return exc_type is None

    def warn(self, message: str = ""):
        self.loader.step_warn(self.step, message=message)

    def skip(self, message: str = ""):
        self.loader.step_skip(self.step, message=message)


def create_default_phases(loader: CinematicLoader) -> Dict[str, StartupPhase]:
    """Create the default startup phases for NEXUS."""
    return {
        "core": loader.add_phase("Core Systems"),
        "ai": loader.add_phase("AI Systems"),
        "agents": loader.add_phase("Agent Systems"),
        "services": loader.add_phase("Services"),
        "final": loader.add_phase("Finalization"),
    }
