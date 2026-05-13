"""Domain model for the Habit Tracker application.

Defines the Habit class and periodicity constants.
"""

from datetime import datetime

DAILY = "daily"
WEEKLY = "weekly"
VALID_PERIODICITIES = {DAILY, WEEKLY}


class Habit:
    """Represents a habit that must be completed daily or weekly.

    Attributes:
        id: Database row ID (None if not persisted).
        name: Human-readable habit name.
        description: Optional longer description.
        periodicity: Either 'daily' or 'weekly'.
        created_at: ISO timestamp of creation.
    """

    def __init__(self, name, description="", periodicity=DAILY, created_at=None, habit_id=None):
        """Initialize a Habit.

        Args:
            name: Non-empty habit name.
            description: Optional description text.
            periodicity: 'daily' or 'weekly'.
            created_at: ISO timestamp string, or None for auto-generation.
            habit_id: Database row ID, or None.

        Raises:
            ValueError: If name is empty or periodicity is invalid.
        """
        if not name or not name.strip():
            raise ValueError("Habit name must not be empty.")
        if periodicity not in VALID_PERIODICITIES:
            raise ValueError(f"Invalid periodicity '{periodicity}'. Must be one of {VALID_PERIODICITIES}.")
        self.id = habit_id
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")
