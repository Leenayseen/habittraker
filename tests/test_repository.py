import pytest
from datetime import datetime
from habit_tracker.models import Habit, DAILY, WEEKLY
from habit_tracker.database import initialize_database
from habit_tracker.repository import (
    create_habit,
    get_all_habits,
    get_habit_by_name,
    delete_habit,
    add_completion,
    get_completions_for_habit,
    get_completions_grouped_by_habit,
)


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    initialize_database(db_path)
    return db_path


class TestCreateAndFetchHabit:
    def test_create_habit_returns_habit(self, db):
        habit = create_habit("Drink water", "Drink 2L", DAILY, db)
        assert isinstance(habit, Habit)
        assert habit.name == "Drink water"
        assert habit.periodicity == DAILY
        assert habit.id is not None

    def test_fetch_habit_by_name(self, db):
        create_habit("Read", "Read 10 pages", DAILY, db)
        habit = get_habit_by_name("Read", db)
        assert habit is not None
        assert habit.name == "Read"

    def test_fetch_nonexistent_returns_none(self, db):
        habit = get_habit_by_name("Ghost", db)
        assert habit is None


class TestListAllHabits:
    def test_list_empty(self, db):
        habits = get_all_habits(db)
        assert habits == []

    def test_list_multiple(self, db):
        create_habit("A", "desc a", DAILY, db)
        create_habit("B", "desc b", WEEKLY, db)
        habits = get_all_habits(db)
        assert len(habits) == 2
        names = [h.name for h in habits]
        assert "A" in names
        assert "B" in names


class TestDeleteHabit:
    def test_delete_by_name(self, db):
        create_habit("ToDelete", "desc", DAILY, db)
        result = delete_habit("ToDelete", db)
        assert result is True
        assert get_habit_by_name("ToDelete", db) is None

    def test_delete_by_id(self, db):
        habit = create_habit("ByID", "desc", DAILY, db)
        result = delete_habit(str(habit.id), db)
        assert result is True
        assert get_habit_by_name("ByID", db) is None

    def test_delete_nonexistent(self, db):
        result = delete_habit("Ghost", db)
        assert result is False


class TestAddAndFetchCompletion:
    def test_add_completion(self, db):
        habit = create_habit("Test", "", DAILY, db)
        ts = "2026-01-15T09:00:00"
        add_completion(habit.id, ts, db)
        completions = get_completions_for_habit(habit.id, db)
        assert len(completions) == 1
        assert completions[0] == ts

    def test_completions_default_timestamp(self, db):
        habit = create_habit("Test2", "", DAILY, db)
        add_completion(habit.id, db_path=db)
        completions = get_completions_for_habit(habit.id, db)
        assert len(completions) == 1

    def test_completions_empty_for_unknown(self, db):
        completions = get_completions_for_habit(9999, db)
        assert completions == []


class TestGroupedCompletions:
    def test_grouped_completions(self, db):
        h1 = create_habit("H1", "", DAILY, db)
        h2 = create_habit("H2", "", WEEKLY, db)
        add_completion(h1.id, "2026-01-15T09:00:00", db)
        add_completion(h1.id, "2026-01-16T09:00:00", db)
        add_completion(h2.id, "2026-01-15T10:00:00", db)
        grouped = get_completions_grouped_by_habit(db)
        assert len(grouped[h1.id]) == 2
        assert len(grouped[h2.id]) == 1

    def test_grouped_empty_db(self, db):
        grouped = get_completions_grouped_by_habit(db)
        assert grouped == {}


class TestDuplicateCompletions:
    def test_duplicate_same_period_stored(self, db):
        habit = create_habit("Dup", "", DAILY, db)
        ts = "2026-01-15T09:00:00"
        add_completion(habit.id, ts, db)
        add_completion(habit.id, ts, db)
        completions = get_completions_for_habit(habit.id, db)
        assert len(completions) == 2


class TestFixtureLoading:
    def test_load_fixtures_five_habits(self, db):
        from habit_tracker.fixtures import load_fixtures
        count = load_fixtures(reset=True, db_path=db)
        assert count == 5
        habits = get_all_habits(db)
        assert len(habits) == 5

    def test_load_fixtures_daily_and_weekly(self, db):
        from habit_tracker.fixtures import load_fixtures
        load_fixtures(reset=True, db_path=db)
        habits = get_all_habits(db)
        daily = [h for h in habits if h.periodicity == DAILY]
        weekly = [h for h in habits if h.periodicity == WEEKLY]
        assert len(daily) >= 1
        assert len(weekly) >= 1

    def test_load_fixtures_four_weeks_data(self, db):
        from habit_tracker.fixtures import load_fixtures
        load_fixtures(reset=True, db_path=db)
        habits = get_all_habits(db)
        for h in habits:
            completions = get_completions_for_habit(h.id, db)
            assert len(completions) > 0

    def test_load_fixtures_idempotent_no_reset(self, db):
        from habit_tracker.fixtures import load_fixtures
        load_fixtures(reset=True, db_path=db)
        habits_before = get_all_habits(db)
        count = load_fixtures(reset=False, db_path=db)
        assert count == 0
        habits_after = get_all_habits(db)
        assert len(habits_before) == len(habits_after)
