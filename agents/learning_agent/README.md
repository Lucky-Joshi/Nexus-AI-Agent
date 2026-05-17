# Learning Agent

> Behavior pattern detection, habit analysis, action prediction, personalized recommendations, and adaptive workflow generation for NEXUS.

## Purpose

The Learning Agent observes user interactions with NEXUS over time to identify patterns, detect habits, predict likely next actions, and generate personalized recommendations. It transforms raw usage data into actionable insights -- suggesting automations for repetitive tasks, generating workflows from discovered patterns, and building a daily routine based on observed behavior. The more NEXUS is used, the smarter and more helpful the Learning Agent becomes.

## Architecture

```
learning_agent/
├── __init__.py
├── agent.py              # LearningAgent orchestrator
├── models.py             # BehaviorPattern, Habit, Recommendation, Prediction, RecommendationType
├── services.py           # LearningEngine (BehaviorTracker, PatternAnalyzer, Recommender, WorkflowGenerator)
├── storage.py            # LearningStorage - persistence for behaviors, patterns, habits, recommendations
```

### Component Breakdown

| Component | Responsibility |
|-----------|---------------|
| `LearningEngine` | Central coordinator managing the learning lifecycle and delegating to sub-engines |
| `BehaviorTracker` | Records user actions with context, timestamps, preceding actions, and outcomes |
| `PatternAnalyzer` | Analyzes behavior data to detect frequency patterns, sequences, time-based patterns, and contextual patterns |
| `Recommender` | Generates personalized recommendations for workflows, automations, habits, and app usage |
| `WorkflowGenerator` | Creates workflow definitions from detected patterns and generates daily routines |
| `LearningStorage` | Persistent storage for all learning data with pattern matching and statistical queries |

### Learning Pipeline

```
User Actions
    │
    ▼
┌──────────────────┐
│ BehaviorTracker  │  Record: action, agent, context, duration, success
└────────┬─────────┘
         │
         ▼ (periodic analysis)
┌──────────────────┐
│ PatternAnalyzer  │  Detect: frequency, sequence, time, context patterns
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌──────────────┐
│ Habit │ │ Recommender  │
│ Det.  │ │              │
└───┬───┘ └──────┬───────┘
    │            │
    ▼            ▼
┌──────────────────────────┐
│   WorkflowGenerator      │  Create workflows, predict actions, generate routines
└──────────┬───────────────┘
           │
           ▼
    Recommendations & Predictions
```

## Capabilities

### Learning Control

| Command | Description |
|---------|-------------|
| `learn` / `start learning` | Start automatic learning engine |
| `stop learning` | Stop the learning engine |
| `analyze` | Run pattern analysis immediately |

### Patterns & Habits

| Command | Description |
|---------|-------------|
| `patterns [type]` | Show learned patterns (frequency, sequence, time, context) |
| `habits` | Show detected habits with consistency metrics |
| `most common` | Show most frequent actions |
| `hourly pattern` | Show activity distribution by hour |
| `daily pattern` | Show activity distribution by day of week |

### Recommendations

| Command | Description |
|---------|-------------|
| `recommendations [type]` | Show recommendations (workflow, automation, habit, app) |
| `accept recommendation <id>` | Accept and apply a recommendation |
| `dismiss recommendation <id>` | Dismiss a recommendation |

### Predictions

| Command | Description |
|---------|-------------|
| `predict` / `what next` | Predict the next likely action |
| `prediction accuracy` | Show prediction accuracy statistics |

### Workflows

| Command | Description |
|---------|-------------|
| `generate workflow [id]` | Generate a workflow from a detected pattern |
| `daily routine` | Generate a daily routine from morning patterns |

### History & Stats

| Command | Description |
|---------|-------------|
| `behavior history` | Show recorded behavior history |
| `learning stats` | Show comprehensive learning statistics |

### Maintenance

| Command | Description |
|---------|-------------|
| `cleanup [days]` | Clean up old behavior records |

### Programmatic API

```python
# Track a user action
learning_agent.track_action(
    action="open vscode",
    agent="file_agent",
    context="morning_routine",
    duration=2.5,
    success=True,
)
```

## Internal Structure

### Behavior Pattern Model

```python
@dataclass
class BehaviorPattern:
    id: str
    name: str
    pattern_type: PatternType        # frequency, sequence, time_based, contextual
    status: PatternStatus            # observing, learning, confirmed, active
    confidence: PatternConfidence    # low, medium, high, very_high
    frequency: int
    typical_time: str                # e.g., "09:00", "morning"
    typical_day: str                 # e.g., "Monday", "weekday"
    actions: list[str]               # Action sequence
    context: str
    automation_suggestion: str
```

### Habit Model

```python
@dataclass
class Habit:
    id: str
    name: str
    frequency_per_week: float
    consistency: float               # 0.0 - 1.0
    typical_time: str
    typical_days: list[str]
    automation_potential: float      # 0.0 - 1.0
    related_actions: list[str]
```

### Recommendation Model

```python
@dataclass
class Recommendation:
    id: str
    title: str
    description: str
    rec_type: RecommendationType     # workflow, automation, habit, app_suggestion
    confidence: float                # 0.0 - 1.0
    reason: str
    pattern_id: str                  # Source pattern
    status: RecommendationStatus     # active, accepted, dismissed
```

### Prediction Model

```python
@dataclass
class Prediction:
    predicted_action: str
    predicted_agent: str
    confidence: float
    reason: str
    time_relevance: float
    context_relevance: float
```

### Recommendation Types

| Type | Description | Example |
|------|-------------|---------|
| `workflow` | Suggest creating a workflow from patterns | "Create a morning setup workflow" |
| `automation` | Suggest automating repetitive actions | "Automate daily project opening" |
| `habit` | Suggest building or modifying habits | "You consistently code at 9am" |
| `app_suggestion` | Suggest app usage optimization | "You use Chrome for docs, try a reader" |

## Usage Examples

### Starting Learning

```
> learn
Learning engine started (interval: 300s). NEXUS will now learn from your behavior.
```

### Analyzing Patterns

```
> analyze
Analysis Complete:
========================================
New patterns detected: 3
Habits identified: 2
Recommendations generated: 4

New Patterns:
  - morning_coding_routine (confidence: high)
  - post_lunch_research (confidence: medium)
  - end_of_day_cleanup (confidence: high)

Top Recommendations:
  - Create morning coding workflow
  - Automate project loading at 9am
  - Schedule end-of-day cleanup
```

### Viewing Habits

```
> habits
Detected Habits (2):

  morning_coding_routine
    Frequency: 5.2 times/week
    Consistency: 87%
    Typical time: 09:00
    Typical days: Monday, Tuesday, Wednesday, Thursday, Friday
    Automation potential: 92%

  afternoon_research
    Frequency: 3.1 times/week
    Consistency: 65%
    Typical time: 14:00
    Typical days: Monday, Wednesday, Friday
    Automation potential: 71%
```

### Predicting Next Action

```
> predict
Predicted Next Actions (based on: open vscode, git status, npm install):

  run tests (78% confidence)
    Agent: terminal_agent
    Reason: Matches morning_coding_routine pattern
    Time relevance: 85%, Context relevance: 92%

  open documentation (45% confidence)
    Agent: web_agent
    Reason: Common after npm install in this context
    Time relevance: 60%, Context relevance: 55%
```

### Generating a Workflow

```
> generate workflow a1b2c3d4
Generated Workflow: Morning Coding Routine
Description: Automated morning setup based on observed patterns
Confidence: 0.87

Steps:
  step_1: Open VS Code -> file_agent
  step_2: Open Terminal -> terminal_agent (after step_1)
  step_3: Run Git Status -> terminal_agent (after step_2)
  step_4: Load Recent Project -> file_agent (after step_3)
```

### Activity Patterns

```
> hourly pattern
Hourly Activity Pattern (Last 14 days):
  08:00     5  #####
  09:00    42  ######################################
  10:00    38  ##################################
  11:00    25  ######################
  12:00     8  #######
  13:00    15  #############
  14:00    35  ###############################
  15:00    28  #########################
  16:00    20  ##################
  17:00    12  ###########
```

### Learning Statistics

```
> learning stats
Learning Statistics
========================================
Learning Days: 14
Behaviors Recorded: 847
Patterns Learned: 12
Confirmed Patterns: 5
Habits Detected: 2
Recommendations Made: 8
Recommendations Accepted: 3
Predictions Made: 24
Predictions Correct: 18
Most Common Action: open vscode
Most Active Hour: 09:00
Most Active Day: Tuesday

Top Patterns:
  morning_coding_routine (freq: 26, conf: 0.87)
  post_lunch_research (freq: 15, conf: 0.65)
  end_of_day_cleanup (freq: 12, conf: 0.78)
```

## Configuration

```json
{
  "agents": {
    "learning_agent": {
      "enabled": true,
      "auto_learn": true,
      "analysis_interval": 300,
      "min_pattern_confidence": 0.3,
      "min_habit_consistency": 0.6,
      "max_recommendations": 10,
      "retention_days": 90,
      "prediction_window_hours": 2
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable the agent |
| `auto_learn` | bool | `true` | Automatically start learning on startup |
| `analysis_interval` | int | `300` | Pattern analysis interval in seconds |
| `min_pattern_confidence` | float | `0.3` | Minimum confidence to report a pattern |
| `min_habit_consistency` | float | `0.6` | Minimum consistency to classify as a habit |
| `max_recommendations` | int | `10` | Maximum active recommendations at once |
| `retention_days` | int | `90` | How long to retain behavior data |
| `prediction_window_hours` | int | `2` | Time window for action predictions |

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `core.base_agent` | Local | BaseAgent, AgentStatus |
| `core.config` | Local | Configuration access |
| `core.logger` | Local | Structured logging |
| `collections.Counter` | stdlib | Action frequency analysis |
| `datetime` | stdlib | Time-based pattern analysis |
