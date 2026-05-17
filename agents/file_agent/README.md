# File Agent

> File operations, application management, system monitoring, and download organization for the NEXUS platform.

## Purpose

The File Agent is a comprehensive file system and system management orchestrator within the NEXUS multi-agent platform. It provides natural-language-driven control over file/folder operations, application launching, system monitoring, process management, and download folder organization. Designed as a thin orchestrator, it delegates domain-specific work to four specialized service classes.

## Architecture

```
FileAgent (orchestrator)
├── FileService        — File/folder CRUD, search, read, open
├── AppService         — Application launching, process management
├── SystemService      — CPU, RAM, disk, network, uptime monitoring
└── DownloadService    — Download folder organization and statistics
```

### Command Routing

The agent parses natural-language commands and routes them to the appropriate service handler using keyword matching:

```
"create file report.txt in Documents"  → FileService.create_file()
"open vscode"                          → AppService.open_app()
"system status"                        → SystemService.get_system_info()
"organize downloads"                   → DownloadService.organize()
```

## Capabilities

| Category | Operations |
|---|---|
| **File Operations** | Create, delete, rename, move, copy, read, list directory |
| **Folder Operations** | Create, open common folders (Desktop, Downloads, Documents, etc.) |
| **Search** | Recursive file/folder search with skip-list for noisy directories |
| **Application Management** | Launch 30+ known apps, URL opening, PATH resolution, URI schemes |
| **Process Management** | List running processes (sorted by memory), kill by PID or name |
| **System Monitoring** | CPU per-core usage, RAM/swap, disk partitions, network I/O, uptime |
| **Download Management** | Auto-organize by file type, folder statistics, cleanup by age |
| **Media/PDF** | Find and open PDFs or media files in specified folders |

## Internal Structure

```
file_agent/
├── __init__.py      — Package exports
├── agent.py         — FileAgent class: command parsing, routing, 22+ handlers
├── services.py      — Four service classes (888 lines total):
│   ├── FileService      — 15 file/folder methods
│   ├── AppService       — App map (35+ apps), 3-strategy resolution, process mgmt
│   ├── SystemService    — 5 system info methods with psutil
│   └── DownloadService  — 7-category organization, stats, cleanup
└── utils.py         — PathResolver, format_size, is_safe_path, extract_filename
```

### Key Design Patterns

- **Service-Oriented**: Agent is a thin router; all business logic lives in services
- **Path Resolution**: `PathResolver` searches across home, Downloads, Desktop, Documents, OneDrive, and CWD
- **Cross-Platform**: Detects Windows/macOS/Linux and adapts commands accordingly
- **Safety**: `is_safe_path()` prevents directory traversal attacks

## Usage Examples

### Natural Language Commands

```python
from agents.file_agent.agent import FileAgent

agent = FileAgent()

# File operations
agent.execute("create file notes.txt in C:\\Users\\lucky\\Documents")
agent.execute("delete old_report.pdf")
agent.execute("rename report.docx to final_report.docx")
agent.execute("move draft.txt to C:\\Users\\lucky\\Desktop")

# Application management
agent.execute("open vscode")
agent.execute("launch chrome")
agent.execute("open settings")

# System monitoring
agent.execute("system status")
agent.execute("cpu")
agent.execute("disk info")
agent.execute("network")

# Process management
agent.execute("show processes")
agent.execute("kill notepad")

# Download management
agent.execute("organize downloads")
agent.execute("download stats")
```

### Programmatic API

```python
# Direct service access
agent._file_service.create_file("data.csv", parent="D:\\work")
agent._app_service.get_running_processes(limit=10)
agent._system_service.get_system_info()
agent._download_service.organize()
```

## Configuration

Configuration is managed through the NEXUS `Config` system. Key settings:

| Setting | Default | Description |
|---|---|---|
| `agents.file_agent.workspace_path` | `~` | Default working directory |
| `llm.use_in_agents` | `true` | Enable LLM-enhanced features |

### Dependencies

```
psutil          — System monitoring and process management
```

### Optional Dependencies

None — all core features use standard library + psutil.

## Capabilities Reference

Full list returned by `get_capabilities()`:

```
open_application, open_file, open_folder, open_pdf, open_media,
create_file, create_folder, delete, rename, move, copy,
search_files, read_file, list_directory,
system_info, cpu_info, memory_info, disk_info, network_info,
processes, kill_process, organize_downloads, download_stats
```
