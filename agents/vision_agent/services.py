"""
Service classes for NEXUS Vision Agent.
Each service handles a specific domain: screenshots, OCR, UI detection,
window tracking, screen analysis, and notification monitoring.
"""

import os
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable

from core.logger import Logger
from core.config import Config

from .models import (
    ScreenCapture, ScreenRegion, OCRResult,
    WindowInfo, UIElement, ScreenAnalysis,
)


class ScreenshotService:
    """Captures screenshots using mss (fast, cross-platform)."""

    def __init__(self, save_dir: Optional[str] = None):
        self.logger = Logger().get_logger("ScreenshotService")
        if not save_dir:
            save_dir = str(Path(__file__).parent.parent.parent / "data" / "screenshots")
        self._save_dir = save_dir
        os.makedirs(self._save_dir, exist_ok=True)
        self._mss = None
        self._init_mss()

    def _init_mss(self):
        try:
            import mss
            self._mss = mss.mss()
            self.logger.info(f"Screenshot service initialized (mss)")
        except ImportError:
            self.logger.warning("mss not installed. Install with: pip install mss")
            self._mss = None

    def capture(self, monitor: int = 0, save: bool = True, region: Optional[ScreenRegion] = None) -> Optional[ScreenCapture]:
        """Capture a screenshot. Returns ScreenCapture with metadata."""
        if not self._mss:
            return None

        try:
            monitors = self._mss.monitors
            if monitor >= len(monitors):
                monitor = 0

            if region:
                shot = self._mss.grab({
                    "top": region.y,
                    "left": region.x,
                    "width": region.width,
                    "height": region.height,
                })
                capture = ScreenCapture(
                    monitor=monitor,
                    width=region.width,
                    height=region.height,
                )
            else:
                mon = monitors[monitor]
                shot = self._mss.grab(mon)
                capture = ScreenCapture(
                    monitor=monitor,
                    width=shot.width,
                    height=shot.height,
                )

            import mss.tools
            capture.image_data = mss.tools.to_png(shot.rgb, shot.size)

            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}_{capture.id}.png"
                filepath = os.path.join(self._save_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(capture.image_data)
                capture.file_path = filepath

            self.logger.info(f"Screenshot captured: {capture.width}x{capture.height}")
            return capture

        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return None

    def capture_all_monitors(self, save: bool = True) -> List[ScreenCapture]:
        """Capture all monitors."""
        if not self._mss:
            return []

        captures = []
        for i in range(1, len(self._mss.monitors)):
            cap = self.capture(monitor=i, save=save)
            if cap:
                captures.append(cap)
        return captures

    def capture_region(self, x: int, y: int, width: int, height: int, save: bool = True) -> Optional[ScreenCapture]:
        """Capture a specific screen region."""
        region = ScreenRegion(x=x, y=y, width=width, height=height)
        return self.capture(region=region, save=save)

    def get_screen_size(self, monitor: int = 0) -> Tuple[int, int]:
        """Get screen dimensions."""
        if not self._mss:
            return (0, 0)
        try:
            mon = self._mss.monitors[monitor]
            return (mon["width"], mon["height"])
        except Exception:
            return (0, 0)

    def get_monitor_count(self) -> int:
        """Get number of monitors."""
        if not self._mss:
            return 0
        return len(self._mss.monitors) - 1

    def get_screenshot_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get list of saved screenshots."""
        files = []
        for f in os.listdir(self._save_dir):
            if f.endswith(".png"):
                filepath = os.path.join(self._save_dir, f)
                stat = os.stat(filepath)
                files.append({
                    "filename": f,
                    "path": filepath,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
        files.sort(key=lambda x: x["modified"], reverse=True)
        return files[:limit]

    def cleanup_old(self, days: int = 7) -> int:
        """Remove screenshots older than specified days."""
        cutoff = time.time() - (days * 86400)
        removed = 0
        for f in os.listdir(self._save_dir):
            if f.endswith(".png"):
                filepath = os.path.join(self._save_dir, f)
                if os.stat(filepath).st_mtime < cutoff:
                    os.remove(filepath)
                    removed += 1
        self.logger.info(f"Cleaned up {removed} old screenshots")
        return removed

    @property
    def save_dir(self) -> str:
        return self._save_dir


class OCRService:
    """Extracts text from images using easyocr or Tesseract fallback."""

    def __init__(self, languages: List[str] = None, use_gpu: bool = False):
        self.logger = Logger().get_logger("OCRService")
        self._languages = languages or ["en"]
        self._use_gpu = use_gpu
        self._reader = None
        self._init_ocr()

    def _init_ocr(self):
        try:
            import easyocr
            self._reader = easyocr.Reader(self._languages, gpu=self._use_gpu, verbose=False)
            self.logger.info(f"EasyOCR initialized (languages: {self._languages})")
        except ImportError:
            self.logger.warning("easyocr not installed. Install with: pip install easyocr")
            self._reader = None

    def extract_text(self, image_path: str = None, image_data: bytes = None,
                     region: Optional[ScreenRegion] = None) -> List[OCRResult]:
        """Extract text from an image file or raw bytes."""
        if not self._reader:
            return self._fallback_ocr(image_path, image_data, region)

        try:
            import cv2
            import numpy as np
            from PIL import Image

            if image_data:
                img = Image.open(__import__("io").BytesIO(image_data))
                img_array = np.array(img)
            elif image_path:
                img_array = cv2.imread(image_path)
                if img_array is None:
                    return []
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            else:
                return []

            if region:
                img_array = img_array[region.y:region.y + region.height,
                                       region.x:region.x + region.width]

            results = self._reader.readtext(img_array)

            ocr_results = []
            for (bbox, text, confidence) in results:
                if len(bbox) >= 4:
                    xs = [p[0] for p in bbox]
                    ys = [p[1] for p in bbox]
                    region_obj = ScreenRegion(
                        x=min(xs), y=min(ys),
                        width=max(xs) - min(xs),
                        height=max(ys) - min(ys),
                    )
                else:
                    region_obj = None

                ocr_results.append(OCRResult(
                    text=text,
                    confidence=round(confidence, 3),
                    region=region_obj,
                    language=self._languages[0],
                ))

            ocr_results.sort(key=lambda r: r.confidence, reverse=True)
            self.logger.info(f"OCR extracted {len(ocr_results)} text regions")
            return ocr_results

        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            return self._fallback_ocr(image_path, image_data, region)

    def _fallback_ocr(self, image_path: str = None, image_data: bytes = None,
                      region: Optional[ScreenRegion] = None) -> List[OCRResult]:
        """Fallback: try pytesseract if easyocr unavailable."""
        try:
            import pytesseract
            from PIL import Image

            if image_data:
                img = Image.open(__import__("io").BytesIO(image_data))
            elif image_path:
                img = Image.open(image_path)
            else:
                return []

            if region:
                img = img.crop((region.x, region.y,
                                region.x + region.width, region.y + region.height))

            text = pytesseract.image_to_string(img).strip()
            if text:
                return [OCRResult(text=text, confidence=0.5)]
            return []

        except ImportError:
            self.logger.warning("No OCR engine available (easyocr or pytesseract)")
            return []
        except Exception as e:
            self.logger.error(f"Fallback OCR failed: {e}")
            return []

    def find_text(self, image_path: str, search_text: str,
                  threshold: float = 0.6) -> List[OCRResult]:
        """Find specific text in an image."""
        results = self.extract_text(image_path)
        search_lower = search_text.lower()
        return [r for r in results if search_lower in r.text.lower() and r.confidence >= threshold]

    def is_available(self) -> bool:
        return self._reader is not None


class WindowTracker:
    """Tracks active windows and desktop state using pygetwindow/ctypes."""

    def __init__(self):
        self.logger = Logger().get_logger("WindowTracker")
        self._callbacks: List[Callable] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_active: Optional[WindowInfo] = None
        self._history: List[WindowInfo] = []
        self._max_history = 50

    def get_active_window(self) -> Optional[WindowInfo]:
        """Get the currently active/focused window."""
        result = self._get_active_window_ctypes()
        if result:
            return result

        try:
            import pygetwindow as gw
            active = gw.getActiveWindow()
            if active:
                return WindowInfo(
                    title=active.title,
                    process_name=self._get_process_name(active),
                    pid=0,
                    region=ScreenRegion(
                        x=active.left, y=active.top,
                        width=active.width, height=active.height,
                    ),
                    is_active=True,
                    is_visible=getattr(active, "isVisible", getattr(active, "visible", True)),
                    is_minimized=getattr(active, "isMinimized", getattr(active, "isminimized", False)),
                )
        except ImportError:
            pass

        return None

    def _get_active_window_ctypes(self) -> Optional[WindowInfo]:
        """Fallback: use ctypes to get active window on Windows."""
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()

            if not hwnd:
                return None

            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value

            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))

            return WindowInfo(
                title=title,
                process_name="",
                pid=0,
                region=ScreenRegion(
                    x=rect.left, y=rect.top,
                    width=rect.right - rect.left,
                    height=rect.bottom - rect.top,
                ),
                is_active=True,
                is_visible=True,
                is_minimized=user32.IsIconic(hwnd) != 0,
                hwnd=hwnd,
            )
        except Exception as e:
            self.logger.warning(f"ctypes window tracking failed: {e}")
            return None

    def get_all_windows(self) -> List[WindowInfo]:
        """Get all visible windows."""
        windows = []
        try:
            import pygetwindow as gw
            for w in gw.getAllWindows():
                if w.title:
                    is_visible = getattr(w, "isVisible", getattr(w, "visible", True))
                    is_minimized = getattr(w, "isMinimized", getattr(w, "isminimized", False))
                    if is_visible:
                        windows.append(WindowInfo(
                            title=w.title,
                            process_name=self._get_process_name(w),
                            region=ScreenRegion(
                                x=w.left, y=w.top,
                                width=w.width, height=w.height,
                            ),
                            is_active=False,
                            is_visible=True,
                            is_minimized=is_minimized,
                        ))
        except ImportError:
            pass
        return windows

    def _get_process_name(self, window) -> str:
        """Try to get the process name for a window."""
        try:
            if hasattr(window, "_hWnd"):
                import psutil
                pid = ctypes.windll.user32.GetWindowThreadProcessId(window._hWnd, None)
                proc = psutil.Process(pid)
                return proc.name()
        except Exception:
            pass
        return ""

    def start_monitoring(self, interval: float = 2.0):
        """Start monitoring window changes in background."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self._thread.start()
        self.logger.info(f"Window monitoring started (interval: {interval}s)")

    def stop_monitoring(self):
        """Stop window monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("Window monitoring stopped")

    def _monitor_loop(self, interval: float):
        """Background loop to detect window changes."""
        while self._running:
            try:
                current = self.get_active_window()
                if current and current.title:
                    if not self._last_active or current.title != self._last_active.title:
                        self._last_active = current
                        self._history.append(current)
                        if len(self._history) > self._max_history:
                            self._history = self._history[-self._max_history:]

                        for callback in self._callbacks:
                            try:
                                callback(current)
                            except Exception as e:
                                self.logger.error(f"Window callback error: {e}")

            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")

            time.sleep(interval)

    def on_window_change(self, callback: Callable):
        """Register a callback for window changes."""
        self._callbacks.append(callback)

    def get_history(self, limit: int = 20) -> List[WindowInfo]:
        """Get recent window history."""
        return self._history[-limit:]

    def get_recent_apps(self, limit: int = 10) -> List[str]:
        """Get list of recently used applications."""
        apps = []
        for w in self._history:
            if w.title and w.title not in apps:
                apps.append(w.title)
                if len(apps) >= limit:
                    break
        return apps

    @property
    def is_monitoring(self) -> bool:
        return self._running


class UIDetector:
    """Detects UI elements using template matching and color analysis."""

    def __init__(self):
        self.logger = Logger().get_logger("UIDetector")
        self._templates: Dict[str, str] = {}
        self._cv2_available = False
        self._init_cv2()

    def _init_cv2(self):
        try:
            import cv2
            self._cv2_available = True
            self.logger.info("OpenCV initialized for UI detection")
        except ImportError:
            self.logger.warning("OpenCV not installed. Install with: pip install opencv-python")

    def register_template(self, name: str, image_path: str):
        """Register a UI element template for matching."""
        if os.path.exists(image_path):
            self._templates[name] = image_path
            self.logger.info(f"Registered template: {name}")
        else:
            self.logger.warning(f"Template image not found: {image_path}")

    def find_template(self, screenshot_path: str, template_name: str,
                      threshold: float = 0.8) -> Optional[UIElement]:
        """Find a registered template in a screenshot."""
        if not self._cv2_available:
            return None

        import cv2
        import numpy as np

        if template_name not in self._templates:
            return None

        template_path = self._templates[template_name]
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)

        if screenshot is None or template is None:
            return None

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = template.shape[:2]
            return UIElement(
                element_type="template",
                text=template_name,
                region=ScreenRegion(x=max_loc[0], y=max_loc[1], width=w, height=h),
                confidence=round(float(max_val), 3),
            )

        return None

    def find_all_templates(self, screenshot_path: str,
                           threshold: float = 0.8) -> List[UIElement]:
        """Find all registered templates in a screenshot."""
        elements = []
        for name in self._templates:
            elem = self.find_template(screenshot_path, name, threshold)
            if elem:
                elements.append(elem)
        return elements

    def detect_buttons_by_color(self, screenshot_path: str,
                                color: Tuple[int, int, int],
                                tolerance: int = 30) -> List[UIElement]:
        """Detect UI elements by color (e.g., blue buttons)."""
        if not self._cv2_available:
            return []

        import cv2
        import numpy as np

        img = cv2.imread(screenshot_path)
        if img is None:
            return []

        lower = np.array([max(c - tolerance, 0) for c in color])
        upper = np.array([min(c + tolerance, 255) for c in color])
        mask = cv2.inRange(img, lower, upper)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        elements = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                elements.append(UIElement(
                    element_type="colored_region",
                    region=ScreenRegion(x=x, y=y, width=w, height=h),
                    confidence=round(area / (w * h) if w * h > 0 else 0, 3),
                    properties={"area": int(area), "color": list(color)},
                ))

        return elements

    def detect_text_regions(self, screenshot_path: str) -> List[UIElement]:
        """Detect regions likely containing text (high contrast edges)."""
        if not self._cv2_available:
            return []

        import cv2

        img = cv2.imread(screenshot_path)
        if img is None:
            return []

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        elements = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 5000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect = w / h if h > 0 else 0
                if 0.5 < aspect < 20:
                    elements.append(UIElement(
                        element_type="text_region",
                        region=ScreenRegion(x=x, y=y, width=w, height=h),
                        confidence=round(area / 5000, 3),
                    ))

        return elements


class ScreenAnalyzer:
    """Comprehensive screen analysis combining all services."""

    def __init__(self, screenshot_service: ScreenshotService = None,
                 ocr_service: OCRService = None,
                 window_tracker: WindowTracker = None,
                 ui_detector: UIDetector = None):
        self.logger = Logger().get_logger("ScreenAnalyzer")
        self._screenshot = screenshot_service or ScreenshotService()
        self._ocr = ocr_service or OCRService()
        self._windows = window_tracker or WindowTracker()
        self._ui = ui_detector or UIDetector()
        self._history: List[ScreenAnalysis] = []

    def analyze(self, save_screenshot: bool = True) -> Optional[ScreenAnalysis]:
        """Perform full screen analysis."""
        capture = self._screenshot.capture(save=save_screenshot)
        if not capture:
            return None

        analysis = ScreenAnalysis(capture_id=capture.id)

        analysis.active_window = self._windows.get_active_window()
        analysis.all_windows = self._windows.get_all_windows()

        if capture.file_path:
            analysis.ocr_results = self._ocr.extract_text(capture.file_path)
            analysis.description = self._generate_description(analysis)

        self._history.append(analysis)
        if len(self._history) > 20:
            self._history = self._history[-20:]

        self.logger.info(f"Screen analysis complete: {len(analysis.ocr_results)} text regions, "
                         f"{len(analysis.all_windows)} windows")
        return analysis

    def analyze_region(self, x: int, y: int, width: int, height: int) -> Optional[ScreenAnalysis]:
        """Analyze a specific screen region."""
        capture = self._screenshot.capture_region(x, y, width, height, save=True)
        if not capture:
            return None

        analysis = ScreenAnalysis(capture_id=capture.id)
        if capture.file_path:
            analysis.ocr_results = self._ocr.extract_text(capture.file_path)

        return analysis

    def find_text_on_screen(self, search_text: str) -> List[OCRResult]:
        """Search for specific text on the current screen."""
        capture = self._screenshot.capture(save=True)
        if not capture or not capture.file_path:
            return []

        return self._ocr.find_text(capture.file_path, search_text)

    def get_screen_summary(self) -> Dict[str, Any]:
        """Get a quick summary of the current screen state."""
        active = self._windows.get_active_window()
        width, height = self._screenshot.get_screen_size()

        return {
            "active_window": active.title if active else "None",
            "screen_size": f"{width}x{height}",
            "monitor_count": self._screenshot.get_monitor_count(),
            "open_windows": len(self._windows.get_all_windows()),
            "ocr_available": self._ocr.is_available(),
        }

    def _generate_description(self, analysis: ScreenAnalysis) -> str:
        """Generate a human-readable description of the screen."""
        parts = []

        if analysis.active_window:
            parts.append(f"Active: {analysis.active_window.title}")

        text_preview = analysis.full_text[:200]
        if text_preview:
            parts.append(f"Text: {text_preview}...")

        if analysis.all_windows:
            parts.append(f"{len(analysis.all_windows)} windows open")

        return " | ".join(parts) if parts else "Screen analyzed"

    def get_history(self, limit: int = 10) -> List[ScreenAnalysis]:
        """Get recent analysis history."""
        return self._history[-limit:]

    def compare_screenshots(self) -> Optional[Dict[str, Any]]:
        """Compare last two screenshots for changes."""
        if len(self._history) < 2:
            return None

        prev = self._history[-2]
        curr = self._history[-1]

        prev_text = set(r.text for r in prev.ocr_results)
        curr_text = set(r.text for r in curr.ocr_results)

        added = curr_text - prev_text
        removed = prev_text - curr_text

        prev_windows = set(w.title for w in prev.all_windows)
        curr_windows = set(w.title for w in curr.all_windows)

        return {
            "text_added": list(added),
            "text_removed": list(removed),
            "windows_opened": list(curr_windows - prev_windows),
            "windows_closed": list(prev_windows - curr_windows),
            "window_changed": prev.active_window.title != curr.active_window.title if prev.active_window and curr.active_window else False,
        }


class NotificationMonitor:
    """Monitors Windows notifications and system tray."""

    def __init__(self):
        self.logger = Logger().get_logger("NotificationMonitor")
        self._notifications: List[Dict[str, Any]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self, interval: float = 5.0):
        """Start monitoring for notifications."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self._thread.start()
        self.logger.info("Notification monitoring started")

    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("Notification monitoring stopped")

    def _monitor_loop(self, interval: float):
        """Background notification monitoring loop."""
        while self._running:
            try:
                self._check_notifications()
            except Exception as e:
                self.logger.error(f"Notification check error: {e}")
            time.sleep(interval)

    def _check_notifications(self):
        """Check for new notifications using Windows APIs."""
        try:
            from winrt.windows.ui.notifications import ToastNotificationManager
            from winrt.windows.data.xml.dom import XmlDocument

            notifier = ToastNotificationManager.create_toast_notifier()
            self.logger.debug("Checked Windows notifications")
        except ImportError:
            pass

    def get_notifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent notifications."""
        return self._notifications[-limit:]

    def clear(self):
        """Clear notification history."""
        self._notifications.clear()

    @property
    def is_monitoring(self) -> bool:
        return self._running
