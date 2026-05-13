import os
import pytest
from click.testing import CliRunner
from habit_tracker.cli import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = os.path.join(os.getcwd(), "test.db")
        os.environ["HABIT_TRACKER_DB_PATH"] = db_path
        yield runner
        os.environ.pop("HABIT_TRACKER_DB_PATH", None)


class TestInitDbCreateDeleteList:
    def test_init_db(self, runner):
        result = runner.invoke(cli, ["init-db"])
        assert result.exit_code == 0
        assert "initialized" in result.output.lower() or "created" in result.output.lower()

    def test_create_habit(self, runner):
        runner.invoke(cli, ["init-db"])
        result = runner.invoke(cli, ["create", "Drink Water", "--periodicity", "daily"])
        assert result.exit_code == 0
        assert "Drink Water" in result.output

    def test_list_habits(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["create", "Test Habit", "--periodicity", "daily"])
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Test Habit" in result.output

    def test_delete_habit(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["create", "ToDelete", "--periodicity", "daily"])
        result = runner.invoke(cli, ["delete", "ToDelete"])
        assert result.exit_code == 0
        result = runner.invoke(cli, ["list"])
        assert "ToDelete" not in result.output

    def test_list_with_periodicity_filter(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["create", "Daily1", "--periodicity", "daily"])
        runner.invoke(cli, ["create", "Weekly1", "--periodicity", "weekly"])
        result = runner.invoke(cli, ["list", "--periodicity", "daily"])
        assert "Daily1" in result.output
        assert "Weekly1" not in result.output


class TestComplete:
    def test_complete_habit(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["create", "Read", "--periodicity", "daily"])
        result = runner.invoke(cli, ["complete", "Read"])
        assert result.exit_code == 0
        assert "completed" in result.output.lower() or "Read" in result.output

    def test_complete_with_date(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["create", "Walk", "--periodicity", "daily"])
        result = runner.invoke(cli, ["complete", "Walk", "--date", "2026-01-15T09:00:00"])
        assert result.exit_code == 0

    def test_complete_nonexistent(self, runner):
        runner.invoke(cli, ["init-db"])
        result = runner.invoke(cli, ["complete", "Ghost"])
        assert result.exit_code != 0 or "not found" in result.output.lower()


class TestLoadFixtures:
    def test_load_fixtures_reset(self, runner):
        runner.invoke(cli, ["init-db"])
        result = runner.invoke(cli, ["load-fixtures", "--reset"])
        assert result.exit_code == 0
        result = runner.invoke(cli, ["list"])
        assert "Drink Water" in result.output
        assert "Weekly Review" in result.output

    def test_load_fixtures_twice(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["load-fixtures", "--reset"])
        result = runner.invoke(cli, ["load-fixtures"])
        assert result.exit_code == 0
        result = runner.invoke(cli, ["list"])
        assert "Drink Water" in result.output
        assert result.output.count("daily") + result.output.count("weekly") >= 5


class TestAnalytics:
    def test_analytics_all(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["load-fixtures", "--reset"])
        result = runner.invoke(cli, ["analytics", "all"])
        assert result.exit_code == 0
        assert "Drink Water" in result.output

    def test_analytics_periodicity(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["load-fixtures", "--reset"])
        result = runner.invoke(cli, ["analytics", "periodicity", "daily"])
        assert result.exit_code == 0
        assert "Drink Water" in result.output

    def test_analytics_longest_streak(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["load-fixtures", "--reset"])
        result = runner.invoke(cli, ["analytics", "longest-streak"])
        assert result.exit_code == 0

    def test_analytics_habit_streak(self, runner):
        runner.invoke(cli, ["init-db"])
        runner.invoke(cli, ["load-fixtures", "--reset"])
        result = runner.invoke(cli, ["analytics", "habit-streak", "Drink Water"])
        assert result.exit_code == 0
