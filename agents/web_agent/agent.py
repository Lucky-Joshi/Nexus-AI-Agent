"""
Web Research Agent for NEXUS.
Orchestrates SearchService, ScraperService, SummarizerService, and ResearchService.
Handles command parsing and delegates to the appropriate service.
"""

from typing import Any, Dict, Optional
from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config
from .services import SearchService, ScraperService, SummarizerService, ResearchService
from .utils import URLParser, extract_query, truncate


class WebAgent(BaseAgent):
    """
    Web research agent for NEXUS.
    Thin orchestrator that delegates to specialized service classes.
    """

    def __init__(self):
        super().__init__("web_agent", "Web search, scraping, summarization, and research")
        self.logger = Logger().get_logger("WebAgent")

        config = Config()
        user_agent = config.get("agents.web_agent.user_agent", "NEXUS-WebAgent/1.0")
        use_llm = config.get("llm.use_in_agents", True)

        self._search_service = SearchService(user_agent=user_agent)
        self._scraper_service = ScraperService(user_agent=user_agent)
        self._summarizer_service = SummarizerService(use_llm=use_llm)
        self._research_service = ResearchService(
            search_service=self._search_service,
            scraper_service=self._scraper_service,
            summarizer=self._summarizer_service,
            use_llm=use_llm,
        )

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route command to the appropriate service handler."""
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if self._matches(cmd, ["search", "find", "look up", "google"]):
                return self._handle_search(command)

            elif self._matches(cmd, ["summarize", "summary"]) or URLParser.is_url(command):
                return self._handle_summarize(command)

            elif self._matches(cmd, ["scrape", "extract", "fetch"]):
                return self._handle_scrape(command)

            elif self._matches(cmd, ["research", "investigate"]):
                return self._handle_research(command)

            elif self._matches(cmd, ["compare"]):
                return self._handle_compare(command)

            elif self._matches(cmd, ["keywords", "key words"]):
                return self._handle_keywords(command)

            elif self._matches(cmd, ["read", "get content", "page content"]):
                return self._handle_read_page(command)

            else:
                return self._handle_search(command)

        except Exception as e:
            self.logger.error(f"WebAgent error: {e}")
            return {
                "success": False,
                "response": f"Web operation error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "web_search",
            "summarize_url",
            "summarize_text",
            "scrape_page",
            "scrape_multiple",
            "research_topic",
            "compare_options",
            "extract_keywords",
            "read_page",
            "extract_links",
            "extract_structured_data",
        ]

    def _handle_search(self, command: str) -> Dict[str, Any]:
        query = extract_query(
            command,
            prefixes=[
                "search web for ", "search internet for ", "search for ",
                "search the web for ", "search the internet for ",
                "look up ", "google ", "search ", "find ",
            ],
        )

        if not query:
            return {"success": False, "response": "Please provide a search query."}

        results = self._search_service.search(query, num_results=8)

        if not results:
            return {
                "success": True,
                "response": f"No results found for: {query}",
                "data": [],
            }

        lines = [f"Search results for '{query}':\n"]
        for i, r in enumerate(results[:5], 1):
            lines.append(f"{i}. {r['title']}")
            lines.append(f"   {truncate(r['snippet'], 150)}")
            lines.append(f"   {r['url']}\n")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": results[:5],
        }

    def _handle_summarize(self, command: str) -> Dict[str, Any]:
        url = URLParser.extract(command)

        if url:
            return self._summarize_url(url)

        text = extract_query(
            command,
            prefixes=["summarize ", "summary of ", "summarize this: ", "summarize text: "],
        )

        if text:
            summary = self._summarizer_service.summarize(text)
            return {
                "success": True,
                "response": f"Summary:\n\n{summary}",
                "data": {"type": "text", "summary": summary},
            }

        return {
            "success": False,
            "response": "Please provide a URL or text to summarize.",
        }

    def _summarize_url(self, url: str) -> Dict[str, Any]:
        """Summarize a specific URL."""
        scraped = self._scraper_service.scrape(url)

        if "error" in scraped:
            return {"success": False, "response": f"Could not fetch {url}: {scraped['error']}"}

        summary = self._summarizer_service.summarize(scraped["content"])

        return {
            "success": True,
            "response": f"Summary of {scraped.get('title', url)}:\n\n{summary}",
            "data": {
                "url": url,
                "title": scraped.get("title", ""),
                "summary": summary,
                "content_length": scraped.get("content_length", 0),
            },
        }

    def _handle_scrape(self, command: str) -> Dict[str, Any]:
        url = URLParser.extract(command)

        if not url:
            return {"success": False, "response": "Please provide a URL to scrape."}

        result = self._scraper_service.scrape(url, extract_links=True)

        if "error" in result:
            return {"success": False, "response": f"Could not scrape {url}: {result['error']}"}

        links_count = len(result.get("links", []))
        content_preview = truncate(result.get("content", ""), 500)

        lines = [
            f"Scraped: {result.get('title', url)}",
            f"URL: {url}",
            f"Content length: {result.get('content_length', 0)} characters",
            f"Links found: {links_count}",
            f"\nContent preview:\n{content_preview}",
        ]

        if links_count > 0:
            lines.append(f"\nTop links:")
            for link in result["links"][:5]:
                lines.append(f"  - {link['text'][:60]}: {link['url']}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": result,
        }

    def _handle_research(self, command: str) -> Dict[str, Any]:
        topic = extract_query(
            command,
            prefixes=["research ", "investigate ", "research topic: ", "research on "],
        )

        if not topic:
            return {"success": False, "response": "Please provide a research topic."}

        result = self._research_service.research(topic, max_sources=5, max_summary_sentences=3)

        return {
            "success": result.get("success", False),
            "response": result.get("response", "Research completed."),
            "data": result,
        }

    def _handle_compare(self, command: str) -> Dict[str, Any]:
        """Compare multiple options on a topic. Usage: compare X vs Y vs Z"""
        text = extract_query(
            command,
            prefixes=["compare ", "compare options: "],
        )

        if " vs " in text.lower():
            parts = [p.strip() for p in text.split(" vs ")]
            topic = parts[0]
            options = parts
        elif "," in text:
            parts = [p.strip() for p in text.split(",")]
            topic = parts[0]
            options = parts
        else:
            return {"success": False, "response": "Usage: compare X vs Y vs Z"}

        result = self._research_service.compare(topic, options, max_sources_per_option=2)

        lines = [f"Comparison: {topic}\n"]
        for option, data in result.get("options", {}).items():
            lines.append(f"## {option}")
            if data.get("success"):
                lines.append(f"  {data.get('response', 'No data')[:300]}")
            else:
                lines.append(f"  Could not research {option}")
            lines.append("")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": result,
        }

    def _handle_keywords(self, command: str) -> Dict[str, Any]:
        """Extract keywords from a URL or text."""
        url = URLParser.extract(command)

        if url:
            scraped = self._scraper_service.scrape(url)
            if "error" in scraped:
                return {"success": False, "response": f"Could not fetch {url}: {scraped['error']}"}
            keywords = self._summarizer_service.get_keywords(scraped["content"])
        else:
            text = extract_query(
                command,
                prefixes=["keywords ", "key words ", "extract keywords ", "keywords from "],
            )
            if not text:
                return {"success": False, "response": "Please provide text or a URL to extract keywords from."}
            keywords = self._summarizer_service.get_keywords(text)

        return {
            "success": True,
            "response": f"Keywords: {', '.join(keywords)}",
            "data": {"keywords": keywords},
        }

    def _handle_read_page(self, command: str) -> Dict[str, Any]:
        """Read and extract structured data from a page."""
        url = URLParser.extract(command)

        if not url:
            return {"success": False, "response": "Please provide a URL to read."}

        structured = self._scraper_service.extract_structured_data(url)

        if "error" in structured:
            return {"success": False, "response": f"Could not read {url}: {structured['error']}"}

        lines = [f"Page: {structured.get('title', url)}\n"]

        headings = structured.get("headings", {})
        if headings:
            lines.append("Headings:")
            for level, texts in headings.items():
                for t in texts[:5]:
                    lines.append(f"  {level}: {t}")
            lines.append("")

        paragraphs = structured.get("paragraphs", [])
        if paragraphs:
            lines.append(f"Paragraphs ({len(paragraphs)}):")
            for p in paragraphs[:3]:
                lines.append(f"  {truncate(p, 200)}")

        return {
            "success": True,
            "response": "\n".join(lines),
            "data": structured,
        }

    @staticmethod
    def _matches(text: str, keywords: list) -> bool:
        """Check if any keyword exists in text."""
        return any(kw in text for kw in keywords)
