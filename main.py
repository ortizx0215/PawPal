"""Demo script: build an owner with pets and tasks, then print today's schedule."""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)

    mochi = Pet("Mochi", "dog", breed="Shiba Inu", age=3)
    luna = Pet("Luna", "cat", breed="Tabby", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Breakfast", time(7, 30), 10, Priority.HIGH, Frequency.DAILY))
    mochi.add_task(Task("Morning walk", time(8, 0), 30, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task("Medication", time(8, 45), 5, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task("Play session", time(17, 0), 20, Priority.MEDIUM))
    mochi.add_task(Task("Grooming", time(18, 30), 45, Priority.LOW, Frequency.WEEKLY))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    print(f"Today's Schedule - {date.today():%A, %B %d, %Y}")
    print("=" * 44)
    print(scheduler.explain())

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nWarnings:")
        for warning in conflicts:
            print(f"  {warning}")


if __name__ == "__main__":
    main()
