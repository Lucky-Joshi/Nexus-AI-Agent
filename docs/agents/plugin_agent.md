# Plugin Agent

> Dynamic plugin lifecycle management, sandboxed execution, security scanning, and hot-reload capabilities for NEXUS.

## Purpose

The Plugin Agent enables NEXUS to be extended through third-party plugins without modifying core code. It handles the complete plugin lifecycle -- discovery, installation, loading, enabling/disabling, hot-reloading, security analysis, sandboxed execution, and uninstallation. Plugins can contribute new commands, hook into system events, and interact with other agents through a well-defined API.

## Architecture

```
plugin_agent/
├── __init__.py
├── agent.py              # PluginAgent orchestrator
├── models.py             # PluginInfo, PluginStatus, PluginType, SecurityLevel, PluginMetadata
├── loader.py             # PluginLoader - discovery and dynamic module loading
├── registry.py           # PluginRegistry - command indexing, capability tracking
├── services.py           # PluginLifecycleManager - install, enable, disable, reload
├── sandbox.py            # PluginSandbox, CodeAnalyzer - security isolation
├── plugin_api.py         # Plugin API interface for plugin developers
├── plugins/              # Plugin directory (auto-discovered)
└── examples/             # Example plugin templates
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `PluginLoader` | Discovers plugins in the plugins directory, dynamically loads Python modules, extracts metadata |
| `PluginRegistry` | Maintains plugin inventory, indexes commands and hooks, resolves command-to-plugin mappings |
| `PluginLifecycleManager` | Orchestrates install, enable, disable, reload, and uninstall operations |
| `PluginSandbox` | Isolates plugin execution with restricted permissions and resource limits |
| `CodeAnalyzer` | Static analysis of plugin source code for security vulnerabilities and risky patterns |
| `PluginAPI` | Defines the interface plugins use to interact with NEXUS (commands, hooks, events) |

### Plugin Lifecycle

```
Discovery ──> Loading ──> Validation ──> Registration ──> Enabled
    │              │            │              │              │
    ▼              ▼            ▼              ▼              ▼
  File scan    Import module  Security scan  Index commands  Execute
               Extract meta   Code analyze   Register hooks  Run commands
```

### Plugin Types

| Type | Description | Execution Model |
|------|-------------|-----------------|
| `command` | Adds new command prefixes to NEXUS | Direct invocation |
| `hook` | Listens for system events and reacts | Event-driven callback |
| `middleware` | Intercepts and modifies agent communication | Request/response pipeline |
| `service` | Provides background services or APIs | Long-running process |

## Capabilities

### Plugin Management

| Command | Description |
|---------|-------------|
| `install plugin <path>` | Install a plugin from a file path |
| `uninstall plugin <name>` | Remove an installed plugin |
| `enable plugin <name>` | Activate a plugin |
| `disable plugin <name>` | Deactivate a plugin |
| `reload plugin <name>` | Hot-reload a plugin without restart |
| `list plugins` | Show all installed plugins with status |
| `plugin info <name>` | Show detailed plugin information |
| `plugin commands <name>` | Show commands provided by a plugin |

### Discovery & Security

| Command | Description |
|---------|-------------|
| `discover plugins` | Scan plugins directory for new plugins |
| `plugin security <name>` | Run security analysis on a plugin |
| `plugin events <name>` | Show plugin event log |
| `plugin stats` | Show plugin system diagnostics |

### Execution

| Command | Description |
|---------|-------------|
| `run plugin <name> <command>` | Execute a plugin command |
| `plugin help` | Show all available plugin commands |

### Programmatic API

```python
# Execute a command through a specific plugin
result = plugin_agent.execute_plugin_command(
    plugin_name="weather_plugin",
    command="get_forecast",
    params={"location": "Tokyo", "days": 5},
)

# Trigger a hook event
plugin_agent.trigger_hook("user.login", {"user_id": "123"})

# Get all enabled plugins
plugins = plugin_agent.get_enabled_plugins()

# Find which plugin handles a command
plugin_name = plugin_agent.resolve_plugin_for_command("weather forecast")
```

## Internal Structure

### Plugin Metadata

```python
@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    security_level: SecurityLevel
    capabilities: list[PluginCapability]
    dependencies: list[PluginDependency]
    hooks: list[str]
    command_prefixes: list[str]
    tags: list[str]
```

### Plugin Status States

`loaded` -> `initialized` -> `enabled` -> `disabled` -> `error`

### Security Levels

| Level | Description | Sandbox |
|-------|-------------|---------|
| `trusted` | Verified official plugin | Disabled |
| `verified` | Community-verified plugin | Enabled |
| `unverified` | New or unknown plugin | Strict |
| `blocked` | Failed security check | N/A |

### Plugin API Interface

Plugins implement a standard interface:

```python
class NEXUSPlugin:
    def initialize(self, api: PluginAPI) -> None: ...
    def execute(self, command: str, params: dict) -> dict: ...
    def on_hook(self, hook_name: str, data: dict) -> None: ...
    def shutdown(self) -> None: ...
```

## Usage Examples

### Installing a Plugin

```
> install plugin C:\plugins\weather_plugin
Plugin installed: weather_plugin v1.2.0
  Type: command
  Security: verified
  Load time: 45.2ms
  Capabilities: get_weather, forecast, alerts
```

### Managing Plugins

```
> list plugins
Installed plugins (3):

  [ON] weather_plugin v1.2.0
      Type: command | Security: verified
      Provides weather data and forecasts

  [OFF] slack_notifier v0.9.1
      Type: hook | Security: unverified
      Sends notifications to Slack channels

  [ERR] legacy_tool v0.1.0
      Type: service | Security: unverified
      Error: Import failed - missing dependency
```

### Security Analysis

```
> plugin security weather_plugin
Security analysis for weather_plugin:
  Security level: verified
  Sandbox: Enabled
  No security warnings detected.
```

### Running a Plugin Command

```
> run plugin weather_plugin get_forecast Tokyo
{"success": true, "response": "Tokyo: Sunny, 22C, 5-day forecast available"}
```

## Configuration

```json
{
  "agents": {
    "plugin_agent": {
      "enabled": true,
      "plugins_dir": "agents/plugin_agent/plugins",
      "auto_load": true,
      "sandbox_enabled": true,
      "max_execution_time": 30,
      "security_scan_on_load": true,
      "allowed_permissions": ["network", "file_read"],
      "blocked_modules": ["os", "subprocess", "ctypes"]
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `plugins_dir` | string | `"plugins/"` | Directory to scan for plugins |
| `auto_load` | bool | `true` | Auto-load previously enabled plugins on startup |
| `sandbox_enabled` | bool | `true` | Enable sandboxed execution for untrusted plugins |
| `max_execution_time` | int | `30` | Maximum plugin execution time in seconds |
| `security_scan_on_load` | bool | `true` | Run security analysis when loading plugins |
| `allowed_permissions` | list | `["network", "file_read"]` | Permissions granted to sandboxed plugins |
| `blocked_modules` | list | `["os", "subprocess", "ctypes"]` | Python modules blocked in sandbox |

## Creating a Plugin

### Minimal Plugin Structure

```
my_plugin/
├── __init__.py
├── plugin.py           # Main plugin class
└── manifest.json       # Plugin metadata
```

### manifest.json

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "A sample NEXUS plugin",
  "author": "developer",
  "type": "command",
  "security_level": "unverified",
  "capabilities": [
    {
      "name": "my_command",
      "description": "Does something useful",
      "command_prefix": "my command"
    }
  ],
  "hooks": ["task.completed", "session.started"]
}
```

### plugin.py

```python
from plugin_agent.plugin_api import NEXUSPlugin, PluginAPI

class MyPlugin(NEXUSPlugin):
    def initialize(self, api: PluginAPI):
        self.api = api

    def execute(self, command: str, params: dict) -> dict:
        if "my command" in command:
            return {
                "success": True,
                "response": "Plugin executed successfully!",
                "data": {"result": "value"},
            }
        return {"success": False, "response": f"Unknown command: {command}"}

    def on_hook(self, hook_name: str, data: dict):
        if hook_name == "task.completed":
            self.api.log(f"Task completed: {data.get('task_id')}")

    def shutdown(self):
        pass
```

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `importlib` | stdlib | Dynamic module loading |
| `ast` | stdlib | Code analysis for security scanning |
