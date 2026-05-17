"""
Data models for NEXUS Vision Agent.
Defines structured types for screen captures, OCR results, UI elements, and analysis.
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ScreenRegion:
    """Defines a rectangular region on screen."""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        return self.width * self.height

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScreenRegion":
        return cls(**{k: v for k, v in data.items() if k in ("x", "y", "width", "height")})


@dataclass
class ScreenCapture:
    """Represents a screenshot with metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    monitor: int = 0
    width: int = 0
    height: int = 0
    file_path: Optional[str] = None
    image_data: Optional[bytes] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("image_data", None)
        return d


@dataclass
class OCRResult:
    """Result from OCR text extraction."""
    text: str = ""
    confidence: float = 0.0
    region: Optional[ScreenRegion] = None
    language: str = "en"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.region:
            d["region"] = self.region.to_dict()
        return d


@dataclass
class WindowInfo:
    """Information about a desktop window."""
    title: str = ""
    process_name: str = ""
    pid: int = 0
    region: Optional[ScreenRegion] = None
    is_active: bool = False
    is_visible: bool = True
    is_minimized: bool = False
    hwnd: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.region:
            d["region"] = self.region.to_dict()
        return d


@dataclass
class UIElement:
    """Detected UI element (button, icon, text field, etc.)."""
    element_type: str = ""
    text: str = ""
    region: Optional[ScreenRegion] = None
    confidence: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.region:
            d["region"] = self.region.to_dict()
        return d


@dataclass
class ScreenAnalysis:
    """Comprehensive analysis of the current screen state."""
    capture_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    active_window: Optional[WindowInfo] = None
    all_windows: List[WindowInfo] = field(default_factory=list)
    ocr_results: List[OCRResult] = field(default_factory=list)
    ui_elements: List[UIElement] = field(default_factory=list)
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    description: str = ""
    notifications: List[str] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Get all extracted text as a single string."""
        return " ".join(r.text for r in self.ocr_results if r.text)

    def get_text_near(self, x: int, y: int, radius: int = 50) -> List[OCRResult]:
        """Get OCR results near a specific point."""
        results = []
        for r in self.ocr_results:
            if r.region and r.region.contains(x, y):
                results.append(r)
            elif r.region:
                cx, cy = r.region.center
                if abs(cx - x) < radius and abs(cy - y) < radius:
                    results.append(r)
        return results

    def find_element_by_text(self, text: str) -> Optional[UIElement]:
        """Find a UI element containing specific text."""
        for elem in self.ui_elements:
            if text.lower() in elem.text.lower():
                return elem
        return None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["full_text"] = self.full_text
        return d
