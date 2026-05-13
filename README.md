# Habit Tracker CLI

A command-line habit tracking application built with Python, SQLite, and Click. Create, complete, and analyze daily and weekly habits with persistent storage.

## Features

- Create daily or weekly habits
- Complete habits with optional date override
- List all habits or filter by periodicity
- Load 5 predefined habits with 4 weeks of sample data
- Analytics: longest streaks, filtering, habit summaries
- Persistent SQLite storage between sessions

## Requirements

- Python 3.8+
- Click
- pytest (for testing)

## Installation

```bash
git clone <repository-url>
cd habit-trcl
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

## Database Setup

```bash
python -m habit_tracker.cli init-db
```

## Loading Sample Data

```bash
python -m habit_tracker.cli load-fixtures --reset
```

This loads 5 predefined habits with 4 weeks of completion data:

| Habit | Periodicity |
|---|---|
| Drink Water | daily |
| Read 10 Pages | daily |
| Morning Walk | daily |
| Weekly Review | weekly |
| Clean Workspace | weekly |

## CLI Usage

### Create a habit

```bash
python -m habit_tracker.cli create "Meditate" --periodicity daily --description "sleep for 10 minutes"
```

### Delete a habit

```bash
python -m habit_tracker.cli delete "Meditate"
```

### Complete a habit

```bash
python -m habit_tracker.cli complete "Drink Water"
python -m habit_tracker.cli complete "Drink Water" --date "2026-01-15T09:00:00"
```

### List habits

```bash
python -m habit_tracker.cli list
python -m habit_tracker.cli list --periodicity daily
```

## Analytics Commands

```bash
python -m habit_tracker.cli analytics all
python -m habit_tracker.cli analytics periodicity daily
python -m habit_tracker.cli analytics longest-streak
python -m habit_tracker.cli analytics habit-streak "Drink Water"
```

## Running Tests

```bash
pytest
```

## Project Structure

```text
habit_tracker/
  __init__.py
  analytics.py     # Pure functional analytics (streaks, filtering)
  cli.py           # Click CLI commands
  database.py      # SQLite connection and schema
  fixtures.py      # Predefined habits and sample data
  models.py        # Habit class and periodicity constants
  repository.py    # Data access layer
tests/
  test_analytics.py
  test_cli.py
  test_models.py
  test_repository.py
data/
  .gitkeep         # Database files are generated at runtime
requirements.txt
README.md
```
