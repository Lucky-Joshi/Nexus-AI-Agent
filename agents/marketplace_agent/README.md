# Marketplace Agent

> Community agent discovery, installation, verification, dependency resolution, and review management for the NEXUS ecosystem.

## Purpose

The Marketplace Agent enables users to browse, search, install, update, and manage community-built agents for NEXUS. It provides a complete package management experience: catalog browsing with categories and filters, security verification with checksum and sandbox testing, automatic dependency resolution, user reviews and ratings, and update management. This transforms NEXUS from a fixed system into an extensible platform that grows with its community.

## Architecture

```
marketplace_agent/
├── __init__.py
├── agent.py              # MarketplaceAgent orchestrator
├── models.py             # MarketplaceAgent, InstallRecord, AgentReview, VerificationReport, MarketplaceDependency
├── marketplace_api.py    # MarketplaceAPI - catalog browsing, search, featured agents, stats
├── agent_installer.py    # AgentInstaller - installation, uninstallation, updates
├── verification.py       # AgentVerifier - security scanning, checksum validation, sandbox testing
├── dependency_resolver.py# DependencyResolver - dependency tree resolution, conflict detection
├── storage.py            # MarketplaceStorage - installed agents, reviews, verification reports
└── installed_agents/     # Directory for installed marketplace agents
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `MarketplaceAPI` | Interfaces with the marketplace catalog: browse by category, search, get featured agents, retrieve agent details, track downloads |
| `AgentInstaller` | Handles the complete installation lifecycle: download, verify, resolve dependencies, install, enable/disable, update, uninstall |
| `AgentVerifier` | Security verification pipeline: checksum validation, signature verification, static security scan, dependency check, compatibility check, sandbox testing |
| `DependencyResolver` | Resolves agent dependencies (required and optional), detects circular dependencies, builds dependency trees, checks for conflicts |
| `MarketplaceStorage` | Persistent storage for installed agent records, user reviews, and verification reports |

### Installation Pipeline

```
Browse/Search ──> Select Agent ──> Verify Security ──> Resolve Dependencies
                      │                    │                      │
                      ▼                    ▼                      ▼
                 Agent details        Checksum, signature    Required agents
                 Capabilities         Security scan          Optional agents
                 Reviews              Sandbox test           Version compatibility
                      │                    │                      │
                      └────────────────────┴──────────────────────┘
                                           │
                                           ▼
                                    Install Agent
                                           │
                                           ▼
                                    Enable & Register
```

### Verification Pipeline

```
Agent Source Code
    │
    ▼
┌──────────────────────┐
│ Checksum Validation  │  Verify file integrity
└────────┬─────────────┘
         │
┌────────┴─────────────┐
│ Signature Verify     │  Verify publisher signature
└────────┬─────────────┘
         │
┌────────┴─────────────┐
│ Security Scan        │  Static analysis for risky patterns
└────────┬─────────────┘
         │
┌────────┴─────────────┐
│ Dependency Check     │  Verify all dependencies available
└────────┬─────────────┘
         │
┌────────┴─────────────┐
│ Compatibility Check  │  NEXUS version, OS, Python version
└────────┬─────────────┘
         │
┌────────┴─────────────┐
│ Sandbox Test         │  Execute in isolation, monitor behavior
└────────┬─────────────┘
         │
         ▼
   Verification Report (PASS/FAIL/WARN)
```

## Capabilities

### Browse & Search

| Command | Description |
|---------|-------------|
| `browse [category]` | Browse the marketplace catalog |
| `search <query>` | Search for agents by name or description |
| `featured` | Show featured agents |
| `categories` | List agent categories |
| `agent info <name>` | Get detailed agent information |

### Install & Manage

| Command | Description |
|---------|-------------|
| `install <name>` | Install an agent from the marketplace |
| `uninstall <name>` | Remove an installed agent |
| `update <name>` | Update an installed agent |
| `check updates` | Check for available updates |
| `installed` | List all installed agents |
| `enable <name>` | Enable an installed agent |
| `disable <name>` | Disable an installed agent |

### Reviews & Verification

| Command | Description |
|---------|-------------|
| `review <name> <rating>` | Submit a review (1-5 stars) |
| `reviews <name>` | Read reviews for an agent |
| `verify <name>` | Run security verification on an agent |

### Dependencies

| Command | Description |
|---------|-------------|
| `dependency tree <name>` | Show full dependency tree |

### Statistics

| Command | Description |
|---------|-------------|
| `stats` | Get marketplace statistics |

### Programmatic API

```python
# Browse agents
agents = marketplace_agent.browse_agents(category="data", limit=20)

# Install an agent programmatically
record = marketplace_agent.install_agent_programmatic(
    agent_name="data_processor",
    source_code=custom_source,  # optional
)

# Get installed agents
installed = marketplace_agent.get_installed_agents()
```

## Internal Structure

### Marketplace Agent Model

```python
@dataclass
class MarketplaceAgent:
    id: str
    name: str
    display_name: str
    version: str
    description: str
    author: str
    category: AgentCategory           # data, automation, security, productivity, etc.
    license: str
    verification_status: VerificationStatus  # unverified, pending, verified, flagged
    is_official: bool
    is_featured: bool
    rating: float                     # 1.0 - 5.0
    rating_count: int
    install_count: int
    download_count: int
    file_size: int                    # bytes
    capabilities: list[str]
    permissions: list[str]
    dependencies: list[MarketplaceDependency]
    python_dependencies: list[str]
    created_at: str
    updated_at: str
```

### Install Record Model

```python
@dataclass
class InstallRecord:
    agent_name: str
    version: str
    status: InstallStatus             # installed, failed, disabled, updating
    install_path: str
    installed_at: str
    enabled: bool
    available_update: str             # None or newer version
    error_message: str
    install_log: list[str]
```

### Verification Report Model

```python
@dataclass
class VerificationReport:
    agent_name: str
    version: str
    status: VerificationStatus        # passed, failed, warnings
    checksum_valid: bool
    signature_valid: bool
    security_scan_passed: bool
    dependency_check_passed: bool
    compatibility_check_passed: bool
    sandbox_test_passed: bool
    issues: list[str]
    warnings: list[str]
    verified_at: str
```

### Agent Categories

`data`, `automation`, `security`, `productivity`, `communication`, `development`, `monitoring`, `integration`, `utility`, `ai`

### Dependency Types

| Type | Behavior |
|------|----------|
| `required` | Must be installed for agent to function |
| `optional` | Enhances functionality but not required |
| `conflict` | Cannot be installed alongside this agent |

## Usage Examples

### Browsing the Marketplace

```
> browse
Marketplace Agents (15):

  [V] [FEATURED] Data Processor v2.1.0
      Process and transform data from multiple sources
      Category: data | Rating: 4.8/5 (124) | Installs: 2,847
      Author: data-team | License: MIT

  [V] Slack Notifier v1.3.2
      Send NEXUS notifications to Slack channels
      Category: communication | Rating: 4.5/5 (89) | Installs: 1,523
      Author: community | License: Apache-2.0

  [ ] [INSTALLED] Weather Widget v0.9.1
      Display weather forecasts in NEXUS UI
      Category: utility | Rating: 4.2/5 (45) | Installs: 678
      Author: weather-dev | License: MIT
```

### Searching

```
> search data processing
Search results for 'data processing' (3):

  Data Processor v2.1.0 - Process and transform data from multiple sources
      Rating: 4.8/5 | Installs: 2,847 | Category: data

  CSV Analyzer v1.0.0 - Analyze CSV files and generate insights
      Rating: 4.3/5 | Installs: 412 | Category: data

  JSON Formatter v0.5.2 - Format and validate JSON data
      Rating: 4.1/5 | Installs: 289 | Category: data
```

### Installing an Agent

```
> install data_processor
Installed: Data Processor v2.1.0
Path: agents/marketplace_agent/installed_agents/data_processor
```

### Checking for Updates

```
> check updates
Available updates:

  weather_widget: 0.9.1 -> 1.0.0
  slack_notifier: 1.3.2 -> 1.4.0
```

### Viewing Dependency Tree

```
> dependency tree data_processor
Dependency tree for Data Processor:

data_processor v2.1.0 [installed]
  +-- csv_parser v1.2.0 [installed] (required)
  +-- json_handler v0.8.0 [installed] (required)
  +-- chart_generator v1.0.0 (optional)
        +-- matplotlib v3.7.0 (required)
```

### Security Verification

```
> verify data_processor
Verification Report: Data Processor v2.1.0
  Status: passed
  Checksum: Valid
  Signature: Valid
  Security Scan: Passed
  Dependencies: Passed
  Compatibility: Passed
  Sandbox Test: Passed
```

### Submitting a Review

```
> review data_processor 5
Review submitted for data_processor: 5/5 stars
```

### Marketplace Statistics

```
> stats
Marketplace Statistics:
  Total agents: 47
  Installed: 12
  Featured: 5
  Official: 8
  Verified: 34
  Total downloads: 15,847
  Total reviews: 892
  Average rating: 4.4/5
  Updates available: 3

  By category:
    data: 12
    automation: 8
    security: 7
    communication: 6
    utility: 5
    development: 4
    productivity: 3
    ai: 2
```

## Configuration

```json
{
  "agents": {
    "marketplace_agent": {
      "enabled": true,
      "marketplace_url": "https://marketplace.nexus-ai.dev/api/v1",
      "install_dir": "agents/marketplace_agent/installed_agents",
      "auto_check_updates": true,
      "update_check_interval_hours": 24,
      "verify_before_install": true,
      "require_verified_for_official": true,
      "max_download_retries": 3
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `marketplace_url` | string | API URL | Base URL for marketplace API |
| `install_dir` | string | `installed_agents/` | Directory for installed marketplace agents |
| `auto_check_updates` | bool | `true` | Automatically check for updates on startup |
| `update_check_interval_hours` | int | `24` | How often to check for updates |
| `verify_before_install` | bool | `true` | Run security verification before installation |
| `require_verified_for_official` | bool | `true` | Only install verified agents as official |
| `max_download_retries` | int | `3` | Maximum download retry attempts |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `requests` | external | HTTP client for marketplace API |
| `hashlib` | stdlib | Checksum validation |
