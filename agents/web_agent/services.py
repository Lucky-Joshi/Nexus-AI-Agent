"""
Service classes for the Web Agent.
Each service handles a specific domain: search, scraping, summarization, research.
"""

import re
import time
import requests
from typing import Any, Dict, List, Optional
from urllib.parse import quote
from bs4 import BeautifulSoup
from core.logger import Logger
from core.config import Config
from .utils import URLParser, RateLimiter, clean_text, truncate, extract_keywords


class SearchService:
    """Handles web search operations across multiple engines."""

    def __init__(self, user_agent: str = "NEXUS-WebAgent/1.0", timeout: int = 15):
        self.logger = Logger().get_logger("SearchService")
        self.timeout = timeout
        self.rate_limiter = RateLimiter(min_delay=1.0, max_requests_per_minute=20)

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def search(self, query: str, engine: str = "duckduckgo", num_results: int = 10) -> List[Dict[str, str]]:
        """Search the web using specified engine."""
        engines = {
            "duckduckgo": self._search_duckduckgo,
            "ddg": self._search_duckduckgo,
        }

        search_fn = engines.get(engine.lower(), self._search_duckduckgo)

        try:
            self.rate_limiter.wait()
            results = search_fn(query)
            return results[:num_results]
        except Exception as e:
            self.logger.error(f"Search failed ({engine}): {e}")
            return []

    def _search_duckduckgo(self, query: str) -> List[Dict[str, str]]:
        """Search using DuckDuckGo HTML interface."""
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"

        response = self._session.get(url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result"):
            title_elem = result.select_one(".result__a")
            snippet_elem = result.select_one(".result__snippet")

            if title_elem and snippet_elem:
                title = title_elem.get_text(strip=True)
                raw_url = title_elem.get("href", "")
                snippet = snippet_elem.get_text(strip=True)

                final_url = self._resolve_ddg_url(raw_url)

                results.append({
                    "title": title,
                    "url": final_url,
                    "snippet": snippet,
                    "source": "duckduckgo",
                })

        self.logger.info(f"DuckDuckGo search returned {len(results)} results for '{query}'")
        return results

    def _resolve_ddg_url(self, raw_url: str) -> str:
        """Resolve DuckDuckGo redirect URL to actual URL."""
        if not raw_url.startswith("//duckduckgo.com"):
            return raw_url

        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(raw_url)
            params = urllib.parse.parse_qs(parsed.query)
            if "uddg" in params:
                return params["uddg"][0]
        except Exception:
            pass

        return raw_url

    def search_multiple(self, query: str, engines: list = None) -> Dict[str, List[Dict]]:
        """Search across multiple engines and combine results."""
        if engines is None:
            engines = ["duckduckgo"]

        all_results = {}
        for engine in engines:
            results = self.search(query, engine=engine)
            all_results[engine] = results

        return all_results


class ScraperService:
    """Handles web page scraping and content extraction."""

    def __init__(self, user_agent: str = "NEXUS-WebAgent/1.0", timeout: int = 15):
        self.logger = Logger().get_logger("ScraperService")
        self.timeout = timeout
        self.rate_limiter = RateLimiter(min_delay=1.5, max_requests_per_minute=15)

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def scrape(self, url: str, extract_links: bool = True, extract_images: bool = False) -> Dict[str, Any]:
        """Scrape a web page and extract structured content."""
        url = URLParser.normalize(url)

        try:
            self.rate_limiter.wait()
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            content = self._extract_text(soup)
            title = self._extract_title(soup)
            meta = self._extract_meta(soup)

            result = {
                "url": url,
                "title": title,
                "content": content,
                "content_length": len(content),
                "meta": meta,
                "status_code": response.status_code,
            }

            if extract_links:
                result["links"] = self._extract_links(soup, url)

            if extract_images:
                result["images"] = self._extract_images(soup, url)

            self.logger.info(f"Scraped {url} ({len(content)} chars)")
            return result

        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout scraping {url}")
            return {"url": url, "error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            return {"url": url, "error": str(e)}
        except Exception as e:
            self.logger.error(f"Scraping error for {url}: {e}")
            return {"url": url, "error": str(e)}

    def scrape_multiple(self, urls: list, delay: float = 2.0) -> List[Dict[str, Any]]:
        """Scrape multiple pages with delay between requests."""
        results = []
        for url in urls:
            result = self.scrape(url)
            results.append(result)
            time.sleep(delay)
        return results

    def extract_structured_data(self, url: str) -> Dict[str, Any]:
        """Extract structured data from a page (headings, lists, tables)."""
        url = URLParser.normalize(url)

        try:
            self.rate_limiter.wait()
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            return {
                "url": url,
                "title": self._extract_title(soup),
                "headings": self._extract_headings(soup),
                "paragraphs": self._extract_paragraphs(soup),
                "lists": self._extract_lists(soup),
                "tables": self._extract_tables(soup),
            }
        except Exception as e:
            self.logger.error(f"Structured extraction failed for {url}: {e}")
            return {"url": url, "error": str(e)}

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML."""
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        text = clean_text(text)
        return text

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return ""

    def _extract_meta(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags."""
        meta = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                meta[name] = content
        return meta

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from a page."""
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("http://", "https://")):
                links.append({
                    "url": href,
                    "text": a.get_text(strip=True)[:100],
                })
            elif href.startswith("/"):
                from urllib.parse import urljoin
                links.append({
                    "url": urljoin(base_url, href),
                    "text": a.get_text(strip=True)[:100],
                })
        return links[:50]

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract image URLs from a page."""
        images = []
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if not src.startswith(("http://", "https://")):
                from urllib.parse import urljoin
                src = urljoin(base_url, src)
            images.append(src)
        return images[:20]

    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract headings by level."""
        headings = {}
        for level in range(1, 7):
            tags = soup.find_all(f"h{level}")
            if tags:
                headings[f"h{level}"] = [t.get_text(strip=True) for t in tags]
        return headings

    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract all paragraphs."""
        return [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

    def _extract_lists(self, soup: BeautifulSoup) -> List[List[str]]:
        """Extract all lists."""
        lists = []
        for ul in soup.find_all(["ul", "ol"]):
            items = [li.get_text(strip=True) for li in ul.find_all("li") if li.get_text(strip=True)]
            if items:
                lists.append(items)
        return lists

    def _extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extract all tables as nested lists."""
        tables = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)
        return tables


class SummarizerService:
    """Handles text summarization using extractive methods and optional LLM."""

    def __init__(self, max_sentences: int = 5, min_sentence_length: int = 20, use_llm: bool = False):
        self.logger = Logger().get_logger("SummarizerService")
        self.max_sentences = max_sentences
        self.min_sentence_length = min_sentence_length
        self._stop_words = self._load_stop_words()
        self._use_llm = use_llm
        if self._use_llm:
            try:
                from core.llm_provider import LLMProvider
                self._llm = LLMProvider()
            except Exception as e:
                self.logger.warning(f"LLM not available for summarization: {e}")
                self._use_llm = False
                self._llm = None

    def summarize(self, text: str, max_sentences: int = None) -> str:
        """Generate a summary of text. Uses LLM if available, otherwise extractive."""
        max_s = max_sentences or self.max_sentences

        if self._use_llm and self._llm and self._llm.is_available():
            return self._summarize_llm(text, max_s)

        return self._summarize_extractive(text, max_s)

    def _summarize_llm(self, text: str, max_sentences: int) -> str:
        truncated = text[:4000]
        prompt = f"Summarize the following text in {max_sentences} concise sentences:\n\n{truncated}"
        try:
            return self._llm.generate(prompt, system_prompt="You are a concise summarization expert.")
        except Exception as e:
            self.logger.warning(f"LLM summarization failed, falling back to extractive: {e}")
            return self._summarize_extractive(text, max_sentences)

    def _summarize_extractive(self, text: str, max_sentences: int) -> str:
        """Generate an extractive summary of text."""
        sentences = self._split_sentences(text)
        if not sentences:
            return "No meaningful content found."

        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        word_freq = self._compute_word_frequencies(text)
        if not word_freq:
            return " ".join(sentences[:max_sentences])

        sentence_scores = self._score_sentences(sentences, word_freq)
        top_indices = self._get_top_sentences(sentence_scores, max_sentences)

        summary = " ".join(sentences[i] for i in sorted(top_indices))
        return summary

    def summarize_urls(self, urls: list, max_sentences: int = None, scraper: ScraperService = None) -> List[Dict[str, Any]]:
        """Scrape and summarize multiple URLs."""
        if scraper is None:
            scraper = ScraperService()

        summaries = []
        for url in urls:
            result = scraper.scrape(url)
            if "error" not in result:
                summary = self.summarize(result["content"], max_sentences)
                summaries.append({
                    "url": url,
                    "title": result.get("title", ""),
                    "summary": summary,
                })
            else:
                summaries.append({
                    "url": url,
                    "error": result["error"],
                })

        return summaries

    def get_key_points(self, text: str, max_points: int = 5) -> list:
        """Extract key points from text."""
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        word_freq = self._compute_word_frequencies(text)
        if not word_freq:
            return sentences[:max_points]

        sentence_scores = self._score_sentences(sentences, word_freq)
        top_indices = self._get_top_sentences(sentence_scores, max_points)

        return [sentences[i] for i in sorted(top_indices)]

    def get_keywords(self, text: str, max_keywords: int = 15) -> list:
        """Extract top keywords from text."""
        return extract_keywords(text, max_keywords)

    def _load_stop_words(self) -> set:
        """Load common English stop words."""
        return {
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

    def _split_sentences(self, text: str) -> list:
        """Split text into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if len(s.strip()) >= self.min_sentence_length]

    def _compute_word_frequencies(self, text: str) -> dict:
        """Compute normalized word frequencies."""
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        freq = {}

        for word in words:
            if word not in self._stop_words:
                freq[word] = freq.get(word, 0) + 1

        if not freq:
            return {}

        max_freq = max(freq.values())
        for word in freq:
            freq[word] /= max_freq

        return freq

    def _score_sentences(self, sentences: list, word_freq: dict) -> dict:
        """Score sentences based on word frequencies."""
        scores = {}
        for i, sentence in enumerate(sentences):
            words = re.findall(r"\b[a-z]{3,}\b", sentence.lower())
            if not words:
                scores[i] = 0
                continue

            score = sum(word_freq.get(w, 0) for w in words)
            scores[i] = score / len(words)

            position_bonus = 1.0
            if i == 0:
                position_bonus = 1.5
            elif i < 3:
                position_bonus = 1.2

            scores[i] *= position_bonus

        return scores

    def _get_top_sentences(self, scores: dict, n: int) -> list:
        """Get indices of top N scored sentences."""
        sorted_indices = sorted(scores, key=scores.get, reverse=True)
        return sorted_indices[:n]


class ResearchService:
    """Handles multi-page research operations with optional LLM synthesis."""

    def __init__(self, search_service: SearchService = None, scraper_service: ScraperService = None, summarizer: SummarizerService = None, use_llm: bool = False):
        self.logger = Logger().get_logger("ResearchService")
        self.search = search_service or SearchService()
        self.scraper = scraper_service or ScraperService()
        self.summarizer = summarizer or SummarizerService(use_llm=use_llm)
        self._use_llm = use_llm
        if self._use_llm:
            try:
                from core.llm_provider import LLMProvider
                self._llm = LLMProvider()
            except Exception as e:
                self.logger.warning(f"LLM not available for research: {e}")
                self._use_llm = False
                self._llm = None

    def research(self, topic: str, max_sources: int = 5, max_summary_sentences: int = 3) -> Dict[str, Any]:
        """
        Conduct research on a topic:
        1. Search for relevant pages
        2. Scrape top results
        3. Summarize each page
        4. Combine into comprehensive report
        """
        self.logger.info(f"Researching topic: {topic}")

        search_results = self.search.search(topic, num_results=max_sources)
        if not search_results:
            return {
                "topic": topic,
                "success": False,
                "response": f"No search results found for: {topic}",
            }

        sources = []
        for result in search_results:
            scraped = self.scraper.scrape(result["url"])
            if "error" not in scraped:
                summary = self.summarizer.summarize(scraped["content"], max_summary_sentences)
                sources.append({
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                    "summary": summary,
                })

        if not sources:
            return {
                "topic": topic,
                "success": False,
                "response": f"Could not access any sources for: {topic}",
            }

        combined_summary = self._generate_report(topic, sources)

        return {
            "topic": topic,
            "success": True,
            "sources": sources,
            "response": combined_summary,
            "source_count": len(sources),
        }

    def compare(self, topic: str, options: list, max_sources_per_option: int = 3) -> Dict[str, Any]:
        """Research and compare multiple options on a topic."""
        results = {}
        for option in options:
            query = f"{topic} {option}"
            research = self.research(query, max_sources=max_sources_per_option)
            results[option] = research

        return {
            "topic": topic,
            "options": results,
        }

    def timeline(self, topic: str, max_sources: int = 5) -> Dict[str, Any]:
        """Research a topic and organize findings chronologically."""
        research = self.research(topic, max_sources=max_sources)

        if not research.get("success"):
            return research

        dates = []
        for source in research.get("sources", []):
            dates.append({
                "source": source["title"],
                "url": source["url"],
                "summary": source["summary"],
            })

        return {
            "topic": topic,
            "timeline": dates,
            "response": f"Research timeline for '{topic}':\n\n" + "\n".join(
                f"- {d['source']}: {d['summary']}" for d in dates
            ),
        }

    def _generate_report(self, topic: str, sources: list) -> str:
        """Generate a combined research report from multiple sources."""
        if self._use_llm and self._llm and self._llm.is_available():
            return self._generate_report_llm(topic, sources)

        lines = [f"Research Report: {topic}\n"]
        lines.append(f"Sources analyzed: {len(sources)}\n")

        for i, source in enumerate(sources, 1):
            lines.append(f"Source {i}: {source['title']}")
            lines.append(f"URL: {source['url']}")
            lines.append(f"Summary: {source['summary']}")
            lines.append("")

        if len(sources) > 1:
            lines.append("Key Findings:")
            all_summaries = " ".join(s["summary"] for s in sources)
            key_points = self.summarizer.get_key_points(all_summaries, max_points=5)
            for point in key_points:
                lines.append(f"  - {point}")

        return "\n".join(lines)

    def _generate_report_llm(self, topic: str, sources: list) -> str:
        """Generate an LLM-synthesized research report."""
        source_text = "\n\n".join(
            f"Source: {s['title']}\nURL: {s['url']}\nSummary: {s['summary']}"
            for s in sources
        )
        prompt = (
            f"Write a comprehensive research report on '{topic}' based on these sources:\n\n{source_text}\n\n"
            "Include key findings, compare perspectives, and provide a conclusion. "
            "Keep it concise but thorough."
        )
        try:
            return self._llm.generate(
                prompt,
                system_prompt="You are an expert research analyst. Synthesize multiple sources into a clear report."
            )
        except Exception as e:
            self.logger.warning(f"LLM report generation failed, falling back: {e}")
            return self._generate_report_fallback(topic, sources)

    def _generate_report_fallback(self, topic: str, sources: list) -> str:
        lines = [f"Research Report: {topic} (LLM fallback)\n"]
        lines.append(f"Sources analyzed: {len(sources)}\n")
        for i, source in enumerate(sources, 1):
            lines.append(f"Source {i}: {source['title']}")
            lines.append(f"URL: {source['url']}")
            lines.append(f"Summary: {source['summary']}")
            lines.append("")
        return "\n".join(lines)
