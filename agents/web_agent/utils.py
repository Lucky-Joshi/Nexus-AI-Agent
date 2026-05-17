"""
Utility functions for the Web Agent.
URL parsing, rate limiting, query extraction, and text processing.
"""

import re
import time
from typing import Optional
from urllib.parse import urlparse, quote, urljoin


class URLParser:
    """Validates, normalizes, and extracts components from URLs."""

    @staticmethod
    def is_valid(url: str) -> bool:
        """Check if a string is a valid URL."""
        pattern = r"^(https?://)?([\w-]+\.)+[\w-]+(/[\w-./?%&=]*)?$"
        return bool(re.match(pattern, url))

    @staticmethod
    def is_url(text: str) -> bool:
        """Check if text contains a URL."""
        return bool(re.search(r"https?://|www\.", text))

    @staticmethod
    def normalize(url: str) -> str:
        """Normalize a URL string."""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    @staticmethod
    def extract(text: str) -> Optional[str]:
        """Extract the first URL found in text."""
        pattern = r"https?://[^\s<>\"']+"
        match = re.search(pattern, text)
        if match:
            return match.group(0)

        pattern = r"www\.[^\s<>\"']+"
        match = re.search(pattern, text)
        if match:
            return "https://" + match.group(0)

        return None

    @staticmethod
    def get_domain(url: str) -> str:
        """Extract domain from a URL."""
        parsed = urlparse(url)
        return parsed.netloc

    @staticmethod
    def get_path(url: str) -> str:
        """Extract path from a URL."""
        parsed = urlparse(url)
        return parsed.path

    @staticmethod
    def resolve_relative(base_url: str, relative_url: str) -> str:
        """Resolve a relative URL against a base URL."""
        return urljoin(base_url, relative_url)


class RateLimiter:
    """Controls request frequency to avoid being blocked."""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 5.0, max_requests_per_minute: int = 30):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_rpm = max_requests_per_minute
        self._request_times: list = []

    def wait(self):
        """Wait appropriate delay before next request."""
        now = time.time()

        minute_ago = now - 60
        self._request_times = [t for t in self._request_times if t > minute_ago]

        if len(self._request_times) >= self.max_rpm:
            wait_time = 60 - (now - self._request_times[0])
            if wait_time > 0:
                time.sleep(wait_time)

        if self._request_times:
            elapsed = now - self._request_times[-1]
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)

        self._request_times.append(time.time())

    def reset(self):
        """Reset rate limiter state."""
        self._request_times.clear()


def extract_query(command: str, prefixes: list, suffixes: list = None) -> str:
    """Extract a search query from a command string."""
    text = command.strip()

    sorted_prefixes = sorted(prefixes, key=len, reverse=True)
    for prefix in sorted_prefixes:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):]
            break

    if suffixes:
        sorted_suffixes = sorted(suffixes, key=len, reverse=True)
        for suffix in sorted_suffixes:
            if text.lower().endswith(suffix.lower()):
                text = text[: -len(suffix)]

    return text.strip()


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def truncate(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 20) -> list:
    """Extract top keywords from text by frequency."""
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "must", "of", "in",
        "to", "for", "with", "on", "at", "from", "by", "about", "as", "into",
        "through", "during", "before", "after", "above", "below", "between",
        "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
        "neither", "each", "every", "all", "any", "few", "more", "most",
        "other", "some", "such", "no", "only", "own", "same", "than", "too",
        "very", "just", "because", "if", "when", "where", "which", "while",
        "who", "whom", "what", "how", "this", "that", "these", "those", "it",
        "its", "i", "me", "my", "myself", "we", "our", "ours", "you", "your",
        "he", "him", "his", "she", "her", "they", "them", "their", "there",
    }

    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    freq = {}
    for word in words:
        if word not in stop_words:
            freq[word] = freq.get(word, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]
