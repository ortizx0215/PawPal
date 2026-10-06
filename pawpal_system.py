"""PawPal+ core system: owners, pets, care tasks, and the scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from enum import Enum


class Priority(Enum):
    """How important a task is. Higher value = kept first when time is short."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a task repeats."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"

    def interval(self) -> timedelta | None:
        """Return the gap until the next occurrence, or None if it doesn't repeat."""
        return {
            Frequency.DAILY: timedelta(days=1),
            Frequency.WEEKLY: timedelta(weeks=1),
        }.get(self)


@dataclass
class Task:
    """One occurrence of a pet care activity (walk, feeding, meds, etc.)."""

    description: str
    time: time
    duration_minutes: int = 15
    priority: Priority = Priority.MEDIUM
    frequency: Frequency = Frequency.ONCE
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task()

    def start(self) -> datetime:
        """Return the full date and time this task begins."""
        return datetime.combine(self.due_date, self.time)

    def end(self) -> datetime:
        """Return the full date and time this task finishes."""
        return self.start() + timedelta(minutes=self.duration_minutes)

    def is_due_on(self, day: date) -> bool:
        """Return True if this task is scheduled for the given day."""
        return self.due_date == day

    def overlaps(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another's."""
        return self.start() < other.end() and other.start() < self.end()

    def mark_complete(self, completed_on: date | None = None) -> "Task | None":
        """Mark this occurrence done. Return the next occurrence if it repeats.

        The next occurrence is a copy of this task moved forward by the
        frequency's interval (1 day or 1 week). The interval counts from
        whichever is later, the due date or the day it was completed, so a
        task finished late doesn't create a next occurrence that is already
        overdue. Completing an already-completed task returns None, so it
        can't create duplicates. One-time tasks also return None.
        """
        if self.completed:
            return None  # already done; don't spawn a duplicate next occurrence
        self.completed = True
        step = self.frequency.interval()
        if step is None:
            return None
        # Count from today if the task was overdue, so the next one isn't already past.
        base = max(self.due_date, completed_on or date.today())
        return replace(self, due_date=base + step, completed=False)


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> bool:
        """Remove a task. Return True if it was found and removed."""
        if task in self.tasks:
            self.tasks.remove(task)
            return True
        return False

    def get_tasks(self, include_completed: bool = True) -> list[Task]:
        """Return this pet's tasks, optionally hiding completed ones."""
        if include_completed:
            return list(self.tasks)
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """A pet owner, their pets, and their daily time budget."""

    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Return True if one was removed."""
        pet = self.get_pet(pet_name)
        if pet is None:
            return False
        self.pets.remove(pet)
        return True

    def get_pet(self, pet_name: str) -> Pet | None:
        """Look up a pet by name (case-insensitive)."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner with an empty plan."""
        self.owner = owner
        self.plan: list[Task] = []
        self.skipped: list[tuple[Task, str]] = []

    # --- Retrieval ---------------------------------------------------------

    def get_tasks_for_day(self, day: date | None = None) -> list[Task]:
        """Return incomplete tasks due on the given day (default: today)."""
        day = day or date.today()
        return [
            t for t in self.owner.get_all_tasks()
            if t.is_due_on(day) and not t.completed
        ]

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Return tasks matching every filter given; a filter left as None is ignored.

        Filters combine with AND: filter_tasks(pet_name="Luna", completed=False)
        returns Luna's unfinished tasks. Pet names match case-insensitively.
        """
        return [
            t for t in self.owner.get_all_tasks()
            if (pet_name is None or t.pet_name.lower() == pet_name.lower())
            and (completed is None or t.completed == completed)
        ]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to one pet."""
        return self.filter_tasks(pet_name=pet_name)

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return all tasks that are (or aren't) completed."""
        return self.filter_tasks(completed=completed)

    # --- Organization ------------------------------------------------------

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by start date and time.

        Uses Task.start() (date + time) as the sort key rather than the time
        alone, so tomorrow's 07:30 task sorts after today's 18:30 task.
        Returns a new list and leaves the input unchanged.
        """
        return sorted(tasks, key=lambda t: t.start())

    @staticmethod
    def sort_by_priority(tasks: list[Task]) -> list[Task]:
        """Return tasks ordered high priority first; ties go to shorter, then earlier.

        The key is a tuple (-priority, duration, start). Python compares tuples
        left to right, so priority decides first, and the later fields only
        break ties. Priority is negated so higher values sort first.
        """
        return sorted(
            tasks,
            key=lambda t: (-t.priority.value, t.duration_minutes, t.start()),
        )

    def detect_conflicts(self, day: date | None = None) -> list[str]:
        """Return a warning for each pair of tasks that start together or overlap.

        Lightweight by design: conflicts are reported as messages, never raised,
        so the caller can show them and still use the plan.
        """
        tasks = self.sort_by_time(self.get_tasks_for_day(day))
        warnings = []
        for i, a in enumerate(tasks):
            for b in tasks[i + 1:]:
                if b.start() > a.start() and b.start() >= a.end():
                    break  # sorted by start, so nothing later can overlap a
                if a.pet_name == b.pet_name:
                    who = f"{a.pet_name} has two tasks at once"
                else:
                    who = f"{a.pet_name} and {b.pet_name} both need you"
                warnings.append(
                    f"Conflict ({who}): '{a.description}' "
                    f"({a.time:%H:%M}-{a.end():%H:%M}) overlaps "
                    f"'{b.description}' ({b.time:%H:%M}-{b.end():%H:%M})"
                )
        return warnings

    # --- Planning ----------------------------------------------------------

    def generate_plan(self, day: date | None = None) -> list[Task]:
        """Keep the highest-priority tasks that fit the time budget, ordered by time.

        Greedy strategy: walk through today's incomplete tasks in priority
        order and keep each one that still fits in the owner's remaining
        minutes. Tasks that don't fit go to self.skipped with a reason. The
        kept tasks are then re-sorted by start time for display.
        """
        self.plan, self.skipped = [], []
        minutes_left = self.owner.available_minutes

        for task in self.sort_by_priority(self.get_tasks_for_day(day)):
            if task.duration_minutes <= minutes_left:
                self.plan.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append(
                    (task, f"needs {task.duration_minutes} min, "
                           f"only {minutes_left} min left")
                )

        self.plan = self.sort_by_time(self.plan)
        return self.plan

    def total_minutes(self) -> int:
        """Return the total duration of the current plan."""
        return sum(t.duration_minutes for t in self.plan)

    def complete_task(self, task: Task, completed_on: date | None = None) -> Task | None:
        """Mark a task done and, if it repeats, add the next occurrence to its pet.

        Returns the new occurrence, or None if the task doesn't repeat.
        """
        next_task = task.mark_complete(completed_on)
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    def explain(self) -> str:
        """Describe the current plan and why any tasks were skipped."""
        if not self.plan and not self.skipped:
            return "No tasks scheduled."
        lines = [
            f"Plan for {self.owner.name} "
            f"({self.total_minutes()}/{self.owner.available_minutes} min):"
        ]
        for t in self.plan:
            lines.append(
                f"  {t.time:%H:%M}  {t.description} for {t.pet_name} "
                f"({t.duration_minutes} min) [{t.priority.name.lower()}]"
            )
        if self.skipped:
            lines.append("Skipped:")
            for t, reason in self.skipped:
                lines.append(
                    f"  {t.description} for {t.pet_name} "
                    f"[{t.priority.name.lower()}] - {reason}"
                )
        return "\n".join(lines)
