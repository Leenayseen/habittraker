import os
import click

from habit_tracker.database import DEFAULT_DB_PATH, initialize_database
from habit_tracker.repository import (
    create_habit,
    delete_habit,
    get_all_habits,
    get_habit_by_name,
    add_completion,
    get_completions_grouped_by_habit,
)
from habit_tracker.analytics import (
    get_all_habits as analytics_get_all,
    get_habits_by_periodicity,
    get_longest_streak_for_habit,
    get_longest_streak_all,
)
from habit_tracker.fixtures import load_fixtures


def get_db_path():
    """Return the database path from the environment or the default."""
    return os.environ.get("HABIT_TRACKER_DB_PATH", DEFAULT_DB_PATH)


@click.group()
def cli():
    """Habit Tracker CLI - manage and analyze your daily and weekly habits."""
    pass


@cli.command("init-db")
def init_db():
    """Initialize the SQLite database and create tables."""
    db_path = get_db_path()
    initialize_database(db_path)
    click.echo(f"Database initialized at {db_path}")


@cli.command("create")
@click.argument("name")
@click.option("--periodicity", default="daily", type=click.Choice(["daily", "weekly"]))
@click.option("--description", default="")
def create(name, periodicity, description):
    """Create a new habit."""
    db_path = get_db_path()
    habit = create_habit(name, description, periodicity, db_path)
    click.echo(f"Created habit: {habit.name} ({habit.periodicity})")


@cli.command("delete")
@click.argument("name_or_id")
def delete(name_or_id):
    """Delete a habit by name or ID."""
    db_path = get_db_path()
    if delete_habit(name_or_id, db_path):
        click.echo(f"Deleted habit: {name_or_id}")
    else:
        click.echo(f"Habit not found: {name_or_id}")


@cli.command("list")
@click.option("--periodicity", default=None, type=click.Choice(["daily", "weekly"]))
def list_habits(periodicity):
    """List all habits, optionally filtered by periodicity."""
    db_path = get_db_path()
    habits = get_all_habits(db_path)
    if periodicity:
        habits = get_habits_by_periodicity(habits, periodicity)
    if not habits:
        click.echo("No habits found.")
        return
    click.echo(f"{'ID':<5} {'Name':<20} {'Periodicity':<12} {'Created At'}")
    click.echo("-" * 65)
    for h in habits:
        click.echo(f"{h.id:<5} {h.name:<20} {h.periodicity:<12} {h.created_at}")


@cli.command("complete")
@click.argument("name")
@click.option("--date", default=None, help="ISO date string, e.g. 2026-01-15T09:00:00")
def complete(name, date):
    """Complete a habit by name, optionally with a specific date."""
    db_path = get_db_path()
    habit = get_habit_by_name(name, db_path)
    if habit is None:
        click.echo(f"Habit not found: {name}")
        return
    add_completion(habit.id, date, db_path)
    click.echo(f"Completed: {name}")


@cli.command("load-fixtures")
@click.option("--reset", is_flag=True, help="Clear all data before loading fixtures")
def load_fixtures_cmd(reset):
    """Load predefined habits with four weeks of sample data."""
    db_path = get_db_path()
    count = load_fixtures(reset=reset, db_path=db_path)
    if count > 0:
        click.echo(f"Loaded {count} predefined habits with sample data.")
    else:
        click.echo("All predefined habits already exist. No new data loaded.")


@cli.group("analytics")
def analytics():
    """Analyze tracked habits."""
    pass


@analytics.command("all")
def analytics_all():
    """List all tracked habits."""
    db_path = get_db_path()
    habits = get_all_habits(db_path)
    result = analytics_get_all(habits)
    if not result:
        click.echo("No habits found.")
        return
    for h in result:
        click.echo(f"- {h.name} ({h.periodicity})")


@analytics.command("periodicity")
@click.argument("period", type=click.Choice(["daily", "weekly"]))
def analytics_periodicity(period):
    """List habits filtered by periodicity."""
    db_path = get_db_path()
    habits = get_all_habits(db_path)
    filtered = get_habits_by_periodicity(habits, period)
    if not filtered:
        click.echo(f"No {period} habits found.")
        return
    for h in filtered:
        click.echo(f"- {h.name}")


@analytics.command("longest-streak")
def analytics_longest_streak():
    """Show the longest streak across all habits."""
    db_path = get_db_path()
    habits = get_all_habits(db_path)
    grouped = get_completions_grouped_by_habit(db_path)
    completions_by_name = {}
    for h in habits:
        completions_by_name[h.name] = grouped.get(h.id, [])
    streak = get_longest_streak_all(habits, completions_by_name)
    click.echo(f"Longest streak across all habits: {streak}")


@analytics.command("habit-streak")
@click.argument("name")
def analytics_habit_streak(name):
    """Show the longest streak for a specific habit."""
    db_path = get_db_path()
    habit = get_habit_by_name(name, db_path)
    if habit is None:
        click.echo(f"Habit not found: {name}")
        return
    from habit_tracker.repository import get_completions_for_habit
    completions = get_completions_for_habit(habit.id, db_path)
    streak = get_longest_streak_for_habit(habit, completions)
    click.echo(f"Longest streak for '{name}': {streak}")


if __name__ == "__main__":
    cli()
