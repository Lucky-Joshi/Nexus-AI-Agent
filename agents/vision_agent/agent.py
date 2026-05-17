"""
Vision Agent for NEXUS.
Provides visual understanding of the desktop environment through screenshots,
OCR, UI detection, window tracking, and screen analysis.
"""

import re
from typing import Any, Dict, List, Optional

from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config

from .models import ScreenRegion
from .services import (
    ScreenshotService, OCRService, UIDetector,
    WindowTracker, ScreenAnalyzer, NotificationMonitor,
)


class VisionAgent(BaseAgent):
    """
    Vision/Desktop agent for NEXUS.
    Thin orchestrator that delegates to specialized service classes.
    """

    def __init__(self):
        super().__init__("vision_agent", "Visual desktop understanding, OCR, and screen analysis")
        self.logger = Logger().get_logger("VisionAgent")
        self.config = Config()

        self._screenshot = ScreenshotService()
        self._ocr = OCRService()
        self._ui_detector = UIDetector()
        self._window_tracker = WindowTracker()
        self._analyzer = ScreenAnalyzer(
            screenshot_service=self._screenshot,
            ocr_service=self._ocr,
            window_tracker=self._window_tracker,
            ui_detector=self._ui_detector,
        )
        self._notifications = NotificationMonitor()

        self.logger.info("VisionAgent initialized")

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["screenshot", "screen capture", "capture screen", "take screenshot"]):
                return self._handle_screenshot(command)

            elif self._matches(cmd, ["ocr", "read text", "extract text", "text from screen"]):
                return self._handle_ocr(command)

            elif self._matches(cmd, ["find text", "search text", "look for text"]):
                return self._handle_find_text(command)

            elif self._matches(cmd, ["active window", "current window", "focused window", "what window"]):
                return self._handle_active_window()

            elif self._matches(cmd, ["list windows", "show windows", "all windows", "open windows"]):
                return self._handle_list_windows()

            elif self._matches(cmd, ["analyze screen", "screen analysis", "analyze desktop", "what's on screen", "what is on screen"]):
                return self._handle_analyze_screen()

            elif self._matches(cmd, ["screen size", "screen resolution", "display info", "monitor info"]):
                return self._handle_screen_info()

            elif self._matches(cmd, ["monitor windows", "track windows", "watch windows", "window history"]):
                return self._handle_window_history(command)

            elif self._matches(cmd, ["screen summary", "screen status", "desktop status"]):
                return self._handle_screen_summary()

            elif self._matches(cmd, ["vision", "status", "capabilities"]):
                return self._handle_vision_status()

            elif self._matches(cmd, ["screenshot history", "saved screenshots", "list screenshots"]):
                return self._handle_screenshot_history()

            elif self._matches(cmd, ["compare screens", "screen change", "what changed"]):
                return self._handle_compare_screens()

            elif self._matches(cmd, ["capture region", "screenshot region", "capture area"]):
                return self._handle_capture_region(command)

            else:
                return self._handle_screenshot(command)

        except Exception as e:
            self.logger.error(f"VisionAgent error: {e}")
            return {
                "success": False,
                "response": f"Vision error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "screenshot",
            "screenshot_region",
            "ocr_extract",
            "find_text_on_screen",
            "get_active_window",
            "list_windows",
            "analyze_screen",
            "screen_summary",
            "screen_info",
            "window_history",
            "screenshot_history",
            "compare_screens",
            "register_template",
            "find_template",
            "vision_status",
        ]

    def _handle_screenshot(self, command: str) -> Dict[str, Any]:
        monitor = self._extract_number(command, default=0)
        capture = self._screenshot.capture(monitor=monitor, save=True)

        if not capture:
            return {
                "success": False,
                "response": "Screenshot failed. Ensure 'mss' is installed: pip install mss",
            }

        size_info = f"{capture.width}x{capture.height}"
        path_info = f"Saved to: {capture.file_path}" if capture.file_path else ""
        return {
            "success": True,
            "response": f"Screenshot captured ({size_info})\n{path_info}",
            "data": capture.to_dict(),
        }

    def _handle_ocr(self, command: str) -> Dict[str, Any]:
        if not self._ocr.is_available():
            return {
                "success": False,
                "response": "OCR not available. Install easyocr: pip install easyocr",
            }

        capture = self._screenshot.capture(save=True)
        if not capture or not capture.file_path:
            return {"success": False, "response": "Screenshot failed"}

        results = self._ocr.extract_text(capture.file_path)

        if not results:
            return {
                "success": True,
                "response": "No text found on screen.",
                "data": [],
            }

        lines = [f"Found {len(results)} text regions on screen:\n"]
        for i, r in enumerate(results[:20], 1):
            lines.append(f"{i}. \"{r.text}\" (confidence: {r.confidence:.2f})")

        if len(results) > 20:
            lines.append(f"\n... and {len(results) - 20} more regions")

        full_text = " ".join(r.text for r in results)
        lines.append(f"\nFull text:\n{full_text[:1000]}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [r.to_dict() for r in results],
        }

    def _handle_find_text(self, command: str) -> Dict[str, Any]:
        search = self._extract_content(command, [
            "find text ", "search text ", "look for text ",
            "find text on screen for ", "search screen for ",
        ])

        if not search:
            return {"success": False, "response": "Please provide text to search for."}

        results = self._analyzer.find_text_on_screen(search)

        if not results:
            return {
                "success": True,
                "response": f"Text '{search}' not found on screen.",
                "data": [],
            }

        lines = [f"Found '{search}' in {len(results)} locations:\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. \"{r.text}\" at ({r.region.x}, {r.region.y}) confidence: {r.confidence:.2f}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [r.to_dict() for r in results],
        }

    def _handle_active_window(self) -> Dict[str, Any]:
        window = self._window_tracker.get_active_window()

        if not window:
            return {"success": True, "response": "No active window detected."}

        lines = [
            f"Active Window:",
            f"  Title: {window.title}",
            f"  Process: {window.process_name or 'Unknown'}",
            f"  Position: ({window.region.x}, {window.region.y})",
            f"  Size: {window.region.width}x{window.region.height}",
            f"  Minimized: {window.is_minimized}",
            f"  Visible: {window.is_visible}",
        ]

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": window.to_dict(),
        }

    def _handle_list_windows(self) -> Dict[str, Any]:
        windows = self._window_tracker.get_all_windows()

        if not windows:
            return {"success": True, "response": "No windows detected."}

        lines = [f"Open windows ({len(windows)}):\n"]
        for i, w in enumerate(windows[:15], 1):
            minimized = " (minimized)" if w.is_minimized else ""
            lines.append(f"{i}. {w.title}{minimized}")
            lines.append(f"   Size: {w.region.width}x{w.region.height}")

        if len(windows) > 15:
            lines.append(f"\n... and {len(windows) - 15} more")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [w.to_dict() for w in windows],
        }

    def _handle_analyze_screen(self) -> Dict[str, Any]:
        analysis = self._analyzer.analyze(save_screenshot=True)

        if not analysis:
            return {"success": False, "response": "Screen analysis failed."}

        lines = [f"Screen Analysis:\n"]

        if analysis.active_window:
            lines.append(f"Active: {analysis.active_window.title}")

        lines.append(f"Windows: {len(analysis.all_windows)} open")
        lines.append(f"Text regions: {len(analysis.ocr_results)}")

        if analysis.ocr_results:
            preview = " ".join(r.text for r in analysis.ocr_results[:5])
            lines.append(f"Text preview: {preview[:200]}")

        if analysis.description:
            lines.append(f"\nSummary: {analysis.description}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": analysis.to_dict(),
        }

    def _handle_screen_info(self) -> Dict[str, Any]:
        width, height = self._screenshot.get_screen_size()
        monitors = self._screenshot.get_monitor_count()

        lines = [
            f"Display Information:",
            f"  Primary: {width}x{height}",
            f"  Monitors: {monitors}",
        ]

        for i in range(monitors):
            w, h = self._screenshot.get_screen_size(i)
            lines.append(f"  Monitor {i}: {w}x{h}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": {"width": width, "height": height, "monitors": monitors},
        }

    def _handle_window_history(self, command: str) -> Dict[str, Any]:
        if self._matches(command, ["start", "begin", "enable", "on"]):
            self._window_tracker.start_monitoring()
            return {"success": True, "response": "Window monitoring started."}

        if self._matches(command, ["stop", "end", "disable", "off"]):
            self._window_tracker.stop_monitoring()
            return {"success": True, "response": "Window monitoring stopped."}

        limit = self._extract_number(command, default=10)
        history = self._window_tracker.get_history(limit)

        if not history:
            return {"success": True, "response": "No window history available."}

        lines = [f"Recent window activity ({len(history)} entries):\n"]
        for i, w in enumerate(history, 1):
            lines.append(f"{i}. [{w.timestamp[:19]}] {w.title}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": [w.to_dict() for w in history],
        }

    def _handle_screen_summary(self) -> Dict[str, Any]:
        summary = self._analyzer.get_screen_summary()

        lines = [
            f"Screen Summary:",
            f"  Active window: {summary['active_window']}",
            f"  Resolution: {summary['screen_size']}",
            f"  Monitors: {summary['monitor_count']}",
            f"  Open windows: {summary['open_windows']}",
            f"  OCR available: {summary['ocr_available']}",
        ]

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": summary,
        }

    def _handle_vision_status(self) -> Dict[str, Any]:
        lines = [
            "Vision Agent Status:",
            f"  Screenshot (mss): {'Available' if self._screenshot._mss else 'Not installed'}",
            f"  OCR (easyocr): {'Available' if self._ocr.is_available() else 'Not installed'}",
            f"  UI Detection (OpenCV): {'Available' if self._ui_detector._cv2_available else 'Not installed'}",
            f"  Window Tracking: {'Monitoring' if self._window_tracker.is_monitoring else 'Idle'}",
            f"  Notifications: {'Monitoring' if self._notifications.is_monitoring else 'Idle'}",
            f"  Screenshot history: {len(self._screenshot.get_screenshot_history(limit=1))} saved",
            f"  Analysis history: {len(self._analyzer.get_history())} analyses",
        ]

        return {
            "success": True,
            "response": "\n".join(lines),
        }

    def _handle_screenshot_history(self) -> Dict[str, Any]:
        history = self._screenshot.get_screenshot_history(limit=20)

        if not history:
            return {"success": True, "response": "No screenshots saved."}

        lines = [f"Saved screenshots ({len(history)}):\n"]
        for i, h in enumerate(history[:10], 1):
            size_kb = h["size"] / 1024
            lines.append(f"{i}. {h['filename']} ({size_kb:.1f}KB) - {h['modified'][:19]}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": history,
        }

    def _handle_compare_screens(self) -> Dict[str, Any]:
        comparison = self._analyzer.compare_screenshots()

        if not comparison:
            return {"success": True, "response": "Need at least 2 screen analyses to compare."}

        lines = ["Screen Comparison:\n"]

        if comparison["window_changed"]:
            lines.append("  Window changed!")

        if comparison["windows_opened"]:
            lines.append(f"  Opened: {', '.join(comparison['windows_opened'])}")
        if comparison["windows_closed"]:
            lines.append(f"  Closed: {', '.join(comparison['windows_closed'])}")
        if comparison["text_added"]:
            lines.append(f"  New text: {', '.join(comparison['text_added'][:5])}")
        if comparison["text_removed"]:
            lines.append(f"  Removed text: {', '.join(comparison['text_removed'][:5])}")

        if not any([comparison["window_changed"], comparison["windows_opened"],
                     comparison["windows_closed"], comparison["text_added"],
                     comparison["text_removed"]]):
            lines.append("  No significant changes detected.")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": comparison,
        }

    def _handle_capture_region(self, command: str) -> Dict[str, Any]:
        coords = self._extract_coords(command)
        if not coords or len(coords) < 4:
            return {"success": False, "response": "Please provide coordinates: x y width height"}

        x, y, w, h = coords
        capture = self._screenshot.capture_region(x, y, w, h, save=True)

        if not capture:
            return {"success": False, "response": "Region capture failed."}

        return {
            "success": True,
            "response": f"Captured region ({w}x{h}) at ({x}, {y})\nSaved: {capture.file_path}",
            "data": capture.to_dict(),
        }

    def capture_screenshot(self, monitor: int = 0) -> Optional[Dict[str, Any]]:
        """Programmatic API: capture screenshot."""
        cap = self._screenshot.capture(monitor=monitor, save=True)
        return cap.to_dict() if cap else None

    def extract_screen_text(self) -> List[Dict[str, Any]]:
        """Programmatic API: extract all text from screen."""
        cap = self._screenshot.capture(save=True)
        if not cap or not cap.file_path:
            return []
        results = self._ocr.extract_text(cap.file_path)
        return [r.to_dict() for r in results]

    def get_active_window_info(self) -> Optional[Dict[str, Any]]:
        """Programmatic API: get active window info."""
        window = self._window_tracker.get_active_window()
        return window.to_dict() if window else None

    def analyze_current_screen(self) -> Optional[Dict[str, Any]]:
        """Programmatic API: full screen analysis."""
        analysis = self._analyzer.analyze(save_screenshot=True)
        return analysis.to_dict() if analysis else None

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_content(command: str, prefixes: List[str]) -> str:
        cmd_lower = command.lower()
        for prefix in prefixes:
            if cmd_lower.startswith(prefix):
                return command[len(prefix):].strip()
        return ""

    @staticmethod
    def _extract_number(command: str, default: int = 0) -> int:
        match = re.search(r"\b(\d+)\b", command)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_coords(command: str) -> List[int]:
        numbers = re.findall(r"\b(\d+)\b", command)
        return [int(n) for n in numbers]
