# Personality Agent

> Manages conversational style, emotional tone, persona profiles, and human-like interaction patterns for NEXUS.

## Purpose

The Personality Agent provides NEXUS with the ability to adapt its communication style to match user preferences, maintain consistent personas across sessions, simulate emotional responses, and transform raw AI outputs into personality-appropriate responses. It enables NEXUS to feel more natural, relatable, and contextually aware in its interactions.

## Architecture

```
personality_agent/
├── __init__.py
├── agent.py              # PersonalityAgent orchestrator
├── models.py             # PersonalityProfile, ToneType, Emotion, SessionContext
├── services.py           # PersonalityEngine, ToneManager, StyleAdapter, EmotionSimulator, ResponseTransformer
├── storage.py            # PersonalityStorage, PresetStorage
└── presets/              # Built-in personality preset definitions
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `PersonalityEngine` | Core engine managing active profile, applying presets, switching profiles, and persisting state |
| `ToneManager` | Detects user tone (formal, casual, hostile, friendly, etc.) and adapts response tone accordingly |
| `StyleAdapter` | Translates personality profiles into LLM system prompts and conversation style parameters |
| `EmotionSimulator` | Simulates emotional states (joy, concern, curiosity, etc.) with intensity decay over time |
| `ResponseTransformer` | Applies personality filters to raw responses, generating greetings, signoffs, and tone-adjusted text |
| `PersonalityStorage` | JSON-based persistence for custom profiles, session contexts, and event history |
| `PresetStorage` | Manages built-in and user-created personality presets |

### Data Flow

```
User Message
    │
    ▼
┌─────────────────┐     ┌───────────────┐
│ ToneManager     │────>│ EmotionSim.   │  Detect tone, update emotion
└─────────────────┘     └───────┬───────┘
                                │
    Raw LLM Response            │
    │                           ▼
    ▼                    ┌───────────────┐
┌─────────────────┐     │ ResponseTrans.│  Apply personality filters
│ StyleAdapter    │────>│               │
│ (system prompt) │     └───────┬───────┘
└─────────────────┘             │
                                ▼
                        Personality-Appropriate Response
```

## Capabilities

### Personality Presets

| Command | Description |
|---------|-------------|
| `set personality <preset>` | Switch to a built-in personality preset |
| `list personalities` | Show all available personality presets |
| `personality status` | Display current active personality |
| `reset personality` | Reset to default personality |

### Tone & Style Dimensions

| Command | Description |
|---------|-------------|
| `set tone <type>` | Set conversation tone (formal, casual, friendly, professional, etc.) |
| `set humor <0-100>` | Adjust humor level |
| `set formality <0-100>` | Adjust formality level |
| `set verbosity <0-100>` | Adjust response verbosity |
| `set empathy <0-100>` | Adjust empathy level |
| `set creativity <0-100>` | Adjust creativity level |
| `set confidence <0-100>` | Adjust confidence level |
| `set emoji <0-100>` | Adjust emoji usage |
| `set slang <0-100>` | Adjust slang tolerance |

### Profile Management

| Command | Description |
|---------|-------------|
| `create profile name: <name>` | Create a custom personality profile |
| `list profiles` | Show all saved profiles |
| `switch profile <id>` | Activate a saved profile |
| `delete profile <id>` | Remove a profile |

### Session & Emotion

| Command | Description |
|---------|-------------|
| `emotion status` | Show current simulated emotion |
| `session status` | Display session context and metrics |
| `personality stats` | Show usage statistics |
| `detect tone <text>` | Analyze tone of provided text |

### Programmatic API

```python
# Transform a response through personality filters
transformed = personality_agent.transform_response(
    response="Here is the answer.",
    session_id="abc123",
    user_message="Can you help me?",
)

# Generate a personality-appropriate greeting
greeting = personality_agent.generate_greeting(session_id="abc123")

# Get personality-encoded system prompt for LLM
prompt = personality_agent.get_system_prompt(session_id="abc123")

# Detect user tone from message
tone = personality_agent.detect_user_tone("This is really frustrating!")

# Adapt conversation style based on user history
personality_agent.adapt_session("abc123", ["help me", "thanks!", "great job"])
```

## Internal Structure

### PersonalityProfile Model

```python
@dataclass
class PersonalityProfile:
    id: str
    name: str
    description: str
    tone: ToneType                # formal, casual, friendly, professional, etc.
    humor_level: float            # 0.0 - 1.0
    formality_level: float        # 0.0 - 1.0
    verbosity: float              # 0.0 - 1.0
    empathy_level: float          # 0.0 - 1.0
    creativity: float             # 0.0 - 1.0
    confidence: float             # 0.0 - 1.0
    emoji_usage: float            # 0.0 - 1.0
    slang_tolerance: float        # 0.0 - 1.0
    greeting_style: str           # warm, formal, playful, etc.
    signoff_style: str            # helpful, professional, witty, etc.
```

### Tone Types

`formal`, `casual`, `friendly`, `professional`, `playful`, `serious`, `empathetic`, `analytical`

### Emotion Types

`neutral`, `joy`, `concern`, `curiosity`, `excitement`, `empathy`, `surprise`

## Usage Examples

### Switching Personality

```
> set personality mentor
Tone: friendly | Humor: 30% | Formality: 60%
Personality set to: mentor
```

### Adjusting Individual Traits

```
> set humor 75
Humor level set to: 75%

> be brief
Verbosity set to: 20%
```

### Creating a Custom Profile

```
> create profile name: TechBuddy
Created profile: TechBuddy (ID: a1b2c3d4)

> switch profile a1b2c3d4
Switched to profile: TechBuddy
```

### Tone Detection

```
> detect tone I'm really happy with the results!
Detected tone: friendly
Detected emotion: joy (intensity: 0.85)
```

## Configuration

```json
{
  "agents": {
    "personality_agent": {
      "enabled": true,
      "default_preset": "default",
      "auto_adapt_tone": true,
      "emotion_simulation": true,
      "max_profiles": 20
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `default_preset` | string | `"default"` | Initial personality preset on startup |
| `auto_adapt_tone` | bool | `true` | Automatically adapt tone based on user messages |
| `emotion_simulation` | bool | `true` | Enable emotional state simulation |
| `max_profiles` | int | `20` | Maximum number of custom profiles |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `core.llm_provider` | Local | LLM access for tone analysis and prompt generation |
