# Web Agent

> Web search, page scraping, text summarization, and multi-source research for the NEXUS platform.

## Purpose

The Web Agent provides intelligent web research capabilities within the NEXUS multi-agent platform. It performs web searches across engines, scrapes and extracts structured content from pages, summarizes text using both extractive and LLM-based methods, and conducts multi-source research with synthesized reports. Built as a thin orchestrator over four specialized service classes.

## Architecture

```
WebAgent (orchestrator)
├── SearchService       — Multi-engine web search (DuckDuckGo)
├── ScraperService      — Page scraping, structured data extraction
├── SummarizerService   — Extractive + LLM summarization, keyword extraction
└── ResearchService     — Multi-source research, comparison, report generation
```

### Command Routing

Natural-language commands are parsed and dispatched to the appropriate service:

```
"search for latest AI news"          → SearchService.search()
"summarize https://example.com"      → SummarizerService.summarize()
"scrape https://docs.python.org"     → ScraperService.scrape()
"research quantum computing"         → ResearchService.research()
"compare Python vs Rust vs Go"       → ResearchService.compare()
```

## Capabilities

| Category | Operations |
|---|---|
| **Web Search** | DuckDuckGo search with rate limiting, multi-engine support |
| **Page Scraping** | Full page content extraction, link/image extraction, structured data (headings, lists, tables) |
| **Summarization** | Extractive (TF-IDF scoring) and LLM-based summarization with configurable sentence count |
| **Research** | Multi-source research pipeline: search → scrape → summarize → synthesize report |
| **Comparison** | Research and compare multiple options on a topic |
| **Keyword Extraction** | Frequency-based keyword extraction from text or URLs |
| **Page Reading** | Structured page reading with headings, paragraphs, and metadata |

## Internal Structure

```
web_agent/
├── __init__.py      — Package exports
├── agent.py         — WebAgent class: command parsing, 8 handlers (318 lines)
├── services.py      — Four service classes (612 lines total):
│   ├── SearchService      — DuckDuckGo HTML search, rate limiter (20 rpm)
│   ├── ScraperService     — BeautifulSoup scraping, structured extraction
│   ├── SummarizerService  — Extractive + LLM summarization, stop words, scoring
│   └── ResearchService    — Multi-source pipeline, LLM report synthesis
└── utils.py         — URLParser, RateLimiter, clean_text, truncate, extract_keywords
```

### Key Design Patterns

- **Rate Limiting**: Built-in `RateLimiter` with configurable delay and requests-per-minute caps
- **Dual Summarization**: Falls back from LLM to extractive when LLM unavailable
- **URL Resolution**: Handles DuckDuckGo redirect URLs, relative URL normalization
- **Content Cleaning**: Strips scripts, styles, nav, footer, header, aside, iframe, noscript

## Usage Examples

### Natural Language Commands

```python
from agents.web_agent.agent import WebAgent

agent = WebAgent()

# Web search
agent.execute("search for Python 3.12 release notes")
agent.execute("find latest news about climate change")

# Summarization
agent.execute("summarize https://example.com/article")
agent.execute("summarize this: Long text to summarize...")

# Scraping
agent.execute("scrape https://docs.python.org/3/tutorial/")

# Research
agent.execute("research machine learning applications in healthcare")

# Comparison
agent.execute("compare React vs Vue vs Angular")

# Keywords
agent.execute("keywords from https://example.com")
agent.execute("extract keywords from this article text...")

# Page reading
agent.execute("read https://example.com/docs")
```

### Programmatic API

```python
# Direct service access
results = agent._search_service.search("quantum computing", num_results=10)
scraped = agent._scraper_service.scrape("https://example.com", extract_links=True)
summary = agent._summarizer_service.summarize(long_text, max_sentences=3)
research = agent._research_service.research("topic", max_sources=5)
comparison = agent._research_service.compare("frameworks", ["React", "Vue", "Angular"])
```

## Configuration

| Setting | Default | Description |
|---|---|---|
| `agents.web_agent.user_agent` | `NEXUS-WebAgent/1.0` | HTTP User-Agent header |
| `llm.use_in_agents` | `true` | Enable LLM-enhanced summarization and research |

### Dependencies

```
requests        — HTTP requests
beautifulsoup4  — HTML parsing
```

### Optional Dependencies

```
LLMProvider     — For LLM-based summarization and research synthesis
```

## Capabilities Reference

```
web_search, summarize_url, summarize_text, scrape_page, scrape_multiple,
research_topic, compare_options, extract_keywords, read_page,
extract_links, extract_structured_data
```
