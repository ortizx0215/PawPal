from datetime import date, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", time(8, 0))
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", time(7, 30)))

    assert len(pet.tasks) == 1


# --- Recurring tasks -------------------------------------------------------

def make_scheduler_with(task):
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(task)
    return Scheduler(owner), pet


def test_daily_task_next_occurrence_is_tomorrow():
    today = date.today()
    walk = Task("Walk", time(8, 0), frequency=Frequency.DAILY, due_date=today)
    scheduler, pet = make_scheduler_with(walk)

    next_walk = scheduler.complete_task(walk)

    assert walk.completed is True
    assert next_walk.due_date == today + timedelta(days=1)
    assert next_walk.completed is False
    assert next_walk.pet_name == "Mochi"
    assert next_walk in pet.tasks
    assert len(pet.tasks) == 2


def test_weekly_task_next_occurrence_is_one_week_later():
    today = date.today()
    groom = Task("Grooming", time(18, 0), frequency=Frequency.WEEKLY, due_date=today)
    scheduler, _ = make_scheduler_with(groom)

    next_groom = scheduler.complete_task(groom)

    assert next_groom.due_date == today + timedelta(weeks=1)


def test_one_time_task_does_not_repeat():
    vet = Task("Vet visit", time(10, 0))  # Frequency.ONCE by default
    scheduler, pet = make_scheduler_with(vet)

    assert scheduler.complete_task(vet) is None
    assert len(pet.tasks) == 1


def test_overdue_daily_task_repeats_from_completion_day():
    today = date(2026, 10, 6)
    overdue = Task("Walk", time(8, 0), frequency=Frequency.DAILY,
                   due_date=today - timedelta(days=3))

    next_walk = overdue.mark_complete(completed_on=today)

    assert next_walk.due_date == today + timedelta(days=1)


def test_completing_twice_does_not_duplicate():
    walk = Task("Walk", time(8, 0), frequency=Frequency.DAILY)
    scheduler, pet = make_scheduler_with(walk)

    scheduler.complete_task(walk)
    scheduler.complete_task(walk)

    assert len(pet.tasks) == 2
