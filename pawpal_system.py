"""PawPal+ core system: owners, pets, care tasks, and daily schedules."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, grooming, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds"
    preferred_time: str | None = None  # e.g. "morning", "08:00"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def priority_score(self) -> int:
        """Convert the priority label into a number for sorting."""
        pass

    def fits_in(self, minutes_left: int) -> bool:
        """Return True if this task fits in the remaining time."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Return True if one was removed."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        pass


@dataclass
class Owner:
    """A pet owner, their pets, and their daily time constraints."""

    name: str
    available_minutes: int = 60
    preferred_walk_time: str | None = None
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Return True if one was removed."""
        pass

    def get_pet(self, pet_name: str) -> Pet | None:
        """Look up a pet by name."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks across all of this owner's pets."""
        pass


class Schedule:
    """A daily care plan built from an owner's pets and time budget."""

    def __init__(self, owner: Owner, day: date | None = None) -> None:
        self.owner = owner
        self.day = day or date.today()
        self.planned_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def generate(self) -> None:
        """Choose and order tasks by priority within the owner's available time."""
        pass

    def total_minutes(self) -> int:
        """Return the total duration of all planned tasks."""
        pass

    def explain(self) -> str:
        """Describe why each task was planned or skipped."""
        pass
