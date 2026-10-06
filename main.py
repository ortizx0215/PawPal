"""Demo script: build an owner with pets and tasks, then print today's schedule."""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a heading followed by one line per task."""
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (none)")
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(
            f"  {t.due_date:%m/%d} {t.time:%H:%M}  {t.pet_name:<6} {t.description:<14} "
            f"{t.duration_minutes:>3} min  [{t.priority.name.lower()}] ({status})"
        )


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)

    mochi = Pet("Mochi", "dog", breed="Shiba Inu", age=3)
    luna = Pet("Luna", "cat", breed="Tabby", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of time order on purpose, so sorting has something to fix.
    mochi.add_task(Task("Grooming", time(18, 30), 45, Priority.LOW, Frequency.WEEKLY))
    luna.add_task(Task("Play session", time(17, 0), 20, Priority.MEDIUM))
    mochi.add_task(Task("Morning walk", time(8, 0), 30, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task("Medication", time(8, 45), 5, Priority.HIGH, Frequency.DAILY))
    mochi.add_task(Task("Breakfast", time(7, 30), 10, Priority.HIGH, Frequency.DAILY))

    # Deliberate clashes, so conflict detection has something to report.
    mochi.add_task(Task("Brush teeth", time(8, 0), 5, Priority.MEDIUM))  # same pet, same time
    luna.add_task(Task("Litter box", time(17, 0), 10, Priority.MEDIUM))  # same pet, same time
    luna.add_task(Task("Vet call", time(8, 10), 15, Priority.HIGH))  # different pet, overlaps walk

    scheduler = Scheduler(owner)

    # Mark one task done so the status filter has something to separate.
    breakfast = next(t for t in mochi.tasks if t.description == "Breakfast")
    scheduler.complete_task(breakfast)

    print_tasks("All tasks (as added)", owner.get_all_tasks())
    print_tasks("All tasks (sorted by time)", scheduler.sort_by_time(owner.get_all_tasks()))
    print_tasks("Mochi's tasks", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi")))
    print_tasks("Completed tasks", scheduler.filter_tasks(completed=True))
    print_tasks(
        "Luna's tasks still to do",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna", completed=False)),
    )

    scheduler.generate_plan()
    title = f"Today's Schedule - {date.today():%A, %B %d, %Y}"
    print(f"\n{title}")
    print("=" * len(title))
    print(scheduler.explain())

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nWarnings:")
        for warning in conflicts:
            print(f"  {warning}")


if __name__ == "__main__":
    main()
