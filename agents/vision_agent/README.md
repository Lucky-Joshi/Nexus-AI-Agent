# Vision Agent

> Visual desktop understanding, OCR, UI detection, window tracking, and screen analysis for the NEXUS platform.

## Purpose

The Vision Agent provides comprehensive visual perception of the desktop environment within the NEXUS multi-agent platform. It captures screenshots, extracts text via OCR, detects UI elements, tracks window activity, analyzes screen content, and monitors for changes between screen states. Built as a thin orchestrator over six specialized service classes with graceful degradation when optional dependencies are unavailable.

## Architecture

```
VisionAgent (orchestrator)
├── ScreenshotService     — Fast multi-monitor screenshot capture (mss)
├── OCRService            — Text extraction (EasyOCR primary, Tesseract fallback)
├── UIDetector            — UI element detection via OpenCV template/color matching
├── WindowTracker         — Active window tracking via ctypes/pygetwindow
├── ScreenAnalyzer        — Comprehensive analysis combining all services
└── NotificationMonitor   — Windows notification monitoring (stub)
```

### Command Routing

```
"screenshot"                         → ScreenshotService.capture()
"ocr" / "read text"                  → OCRService.extract_text()
"find text 'Save'"                   → ScreenAnalyzer.find_text_on_screen()
"active window"                      → WindowTracker.get_active_window()
"analyze screen"                     → ScreenAnalyzer.analyze()
"screen resolution"                  → ScreenshotService.get_screen_size()
"compare screens"                    → ScreenAnalyzer.compare_screenshots()
"capture region 100 200 300 400"     → ScreenshotService.capture_region()
```

## Capabilities

| Category | Operations |
|---|---|
| **Screenshot Capture** | Full-screen, region-specific, multi-monitor, auto-save with history |
| **OCR** | Text extraction with confidence scores, text search on screen, EasyOCR + Tesseract fallback |
| **Window Tracking** | Active window detection (ctypes), list all windows, background monitoring with callbacks |
| **UI Detection** | Template matching (OpenCV), color-based button detection, text region detection |
| **Screen Analysis** | Combined analysis: active window + all windows + OCR + description generation |
| **Screen Comparison** | Diff between consecutive analyses: window changes, text added/removed |
| **Display Info** | Screen resolution, monitor count, per-monitor dimensions |
| **Notification Monitoring** | Windows notification monitoring via WinRT APIs |

## Internal Structure

```
vision_agent/
├── __init__.py      — Package exports
├── agent.py         — VisionAgent class: command parsing, 14 handlers (462 lines)
├── models.py        — Data models (146 lines):
│   ├── ScreenRegion     — Rectangular region with center, area, contains()
│   ├── ScreenCapture    — Screenshot with metadata, dimensions, file path
│   ├── OCRResult        — Extracted text with confidence and region
│   ├── WindowInfo       — Window title, process, position, state
│   ├── UIElement        — Detected element with type, text, region
│   └── ScreenAnalysis   — Full analysis combining all data sources
└── services.py      — Six service classes (758 lines):
    ├── ScreenshotService    — mss-based capture, multi-monitor, history, cleanup
    ├── OCRService           — EasyOCR + pytesseract fallback, text finding
    ├── UIDetector           — OpenCV template matching, color detection, edge-based text regions
    ├── WindowTracker        — ctypes primary, pygetwindow fallback, background monitoring
    ├── ScreenAnalyzer       — Orchestrates all services, comparison, summaries
    └── NotificationMonitor  — WinRT notification monitoring
```

### Key Design Patterns

- **Graceful Degradation**: Each service checks for dependency availability and provides fallbacks or informative messages
- **Multi-Monitor Support**: Screenshot capture works across multiple monitors with per-monitor indexing
- **Background Monitoring**: WindowTracker runs in a daemon thread with configurable polling interval and callback registration
- **Analysis History**: ScreenAnalyzer maintains a rolling history of 20 analyses for comparison
- **Region-Based Operations**: All screen coordinates use `ScreenRegion` dataclass with geometric helpers

## Usage Examples

### Natural Language Commands

```python
from agents.vision_agent.agent import VisionAgent

agent = VisionAgent()

# Screenshots
agent.execute("screenshot")
agent.execute("screenshot monitor 1")
agent.execute("capture region 100 200 400 300")

# OCR
agent.execute("ocr")
agent.execute("read text from screen")
agent.execute("find text 'Save Button'")

# Window management
agent.execute("active window")
agent.execute("list windows")
agent.execute("monitor windows start")
agent.execute("window history")
agent.execute("monitor windows stop")

# Screen analysis
agent.execute("analyze screen")
agent.execute("screen summary")
agent.execute("screen resolution")
agent.execute("compare screens")

# Vision status
agent.execute("vision status")
agent.execute("saved screenshots")
```

### Programmatic API

```python
# Direct method calls
capture = agent.capture_screenshot(monitor=0)
text_results = agent.extract_screen_text()
window = agent.get_active_window_info()
analysis = agent.analyze_current_screen()

# Service-level access
captures = agent._screenshot.capture_all_monitors()
ocr_results = agent._ocr.extract_text("screenshot.png")
windows = agent._window_tracker.get_all_windows()
recent_apps = agent._window_tracker.get_recent_apps(limit=5)
comparison = agent._analyzer.compare_screenshots()
summary = agent._analyzer.get_screen_summary()

# UI detection
agent._ui_detector.register_template("save_button", "templates/save_btn.png")
element = agent._ui_detector.find_template("screenshot.png", "save_button")
```

## Configuration

| Setting | Default | Description |
|---|---|---|
| `agents.vision_agent.screenshots_dir` | `data/screenshots` | Directory for saved screenshots |
| `agents.vision_agent.ocr_languages` | `["en"]` | OCR language codes |
| `agents.vision_agent.ocr_use_gpu` | `false` | Enable GPU acceleration for OCR |

### Dependencies

```
mss             — Fast cross-platform screenshot capture
```

### Optional Dependencies

```
easyocr         — Primary OCR engine (recommended)
pytesseract     — Fallback OCR engine
opencv-python   — UI element detection (template matching, color analysis)
pygetwindow     — Enhanced window tracking (ctypes fallback available)
Pillow          — Image processing (OCR dependency)
numpy           — Image array operations
winrt           — Windows notification monitoring
```

## Capabilities Reference

```
screenshot, screenshot_region, ocr_extract, find_text_on_screen,
get_active_window, list_windows, analyze_screen, screen_summary,
screen_info, window_history, screenshot_history, compare_screens,
register_template, find_template, vision_status
```
