from datetime import date, time, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


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


# --- Shared helpers --------------------------------------------------------

DAY = date(2026, 10, 6)  # fixed date so tests don't depend on when they run


def make_owner(*pet_names, minutes=120):
    owner = Owner("Jordan", available_minutes=minutes)
    for name in pet_names:
        owner.add_pet(Pet(name, "dog"))
    return owner


def add(owner, pet_name, desc, hh, mm, duration=15, **kwargs):
    task = Task(desc, time(hh, mm), duration_minutes=duration,
                due_date=kwargs.pop("due_date", DAY), **kwargs)
    owner.get_pet(pet_name).add_task(task)
    return task


# --- Sorting ---------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    owner = make_owner("Mochi")
    dinner = add(owner, "Mochi", "Dinner", 18, 0)
    breakfast = add(owner, "Mochi", "Breakfast", 7, 30)
    lunch = add(owner, "Mochi", "Lunch", 12, 0)
    tasks = owner.get_all_tasks()

    result = Scheduler.sort_by_time(tasks)

    assert result == [breakfast, lunch, dinner]
    assert tasks == [dinner, breakfast, lunch]  # input list left unchanged


def test_sort_by_time_uses_date_not_just_clock_time():
    owner = make_owner("Mochi")
    tomorrow_early = add(owner, "Mochi", "Walk", 7, 30,
                         due_date=DAY + timedelta(days=1))
    today_late = add(owner, "Mochi", "Dinner", 18, 30)

    result = Scheduler.sort_by_time([tomorrow_early, today_late])

    assert result == [today_late, tomorrow_early]


def test_sort_by_time_keeps_insertion_order_for_same_time():
    owner = make_owner("Mochi")
    first = add(owner, "Mochi", "Meds", 8, 0)
    second = add(owner, "Mochi", "Breakfast", 8, 0)

    assert Scheduler.sort_by_time([first, second]) == [first, second]


def test_sort_by_priority_breaks_ties_by_duration_then_time():
    owner = make_owner("Mochi")
    low = add(owner, "Mochi", "Brush", 6, 0, priority=Priority.LOW)
    high_long = add(owner, "Mochi", "Hike", 7, 0, duration=60,
                    priority=Priority.HIGH)
    high_short_late = add(owner, "Mochi", "Meds", 9, 0, duration=5,
                          priority=Priority.HIGH)
    high_short_early = add(owner, "Mochi", "Pill", 8, 0, duration=5,
                           priority=Priority.HIGH)

    result = Scheduler.sort_by_priority(owner.get_all_tasks())

    assert result == [high_short_early, high_short_late, high_long, low]


# --- Recurrence ------------------------------------------------------------

def test_completing_daily_task_creates_task_for_next_day():
    owner = make_owner("Mochi")
    walk = add(owner, "Mochi", "Walk", 8, 0, frequency=Frequency.DAILY)
    scheduler = Scheduler(owner)

    next_walk = scheduler.complete_task(walk, completed_on=DAY)

    assert walk.completed is True
    assert next_walk.due_date == DAY + timedelta(days=1)
    assert next_walk.time == walk.time
    assert scheduler.get_tasks_for_day(DAY) == []
    assert scheduler.get_tasks_for_day(DAY + timedelta(days=1)) == [next_walk]


def test_weekly_task_completed_early_keeps_original_schedule():
    owner = make_owner("Mochi")
    groom = add(owner, "Mochi", "Grooming", 18, 0, frequency=Frequency.WEEKLY)

    next_groom = groom.mark_complete(completed_on=DAY - timedelta(days=2))

    assert next_groom.due_date == DAY + timedelta(weeks=1)


# --- Conflict detection ----------------------------------------------------

def test_conflict_flagged_for_tasks_at_same_time():
    owner = make_owner("Mochi")
    add(owner, "Mochi", "Walk", 8, 0)
    add(owner, "Mochi", "Breakfast", 8, 0)

    warnings = Scheduler(owner).detect_conflicts(DAY)

    assert len(warnings) == 1
    assert "Mochi has two tasks at once" in warnings[0]


def test_conflict_between_different_pets_names_both():
    owner = make_owner("Mochi", "Luna")
    add(owner, "Mochi", "Walk", 8, 0, duration=30)
    add(owner, "Luna", "Feed", 8, 15, duration=30)

    warnings = Scheduler(owner).detect_conflicts(DAY)

    assert len(warnings) == 1
    assert "Mochi and Luna both need you" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    owner = make_owner("Mochi")
    add(owner, "Mochi", "Walk", 8, 0, duration=30)
    add(owner, "Mochi", "Breakfast", 8, 30)

    assert Scheduler(owner).detect_conflicts(DAY) == []


def test_long_task_conflicts_with_every_task_inside_it():
    owner = make_owner("Mochi")
    add(owner, "Mochi", "Hike", 8, 0, duration=120)
    add(owner, "Mochi", "Meds", 8, 30)
    add(owner, "Mochi", "Snack", 9, 0)

    assert len(Scheduler(owner).detect_conflicts(DAY)) == 2


def test_completed_and_other_day_tasks_ignored_for_conflicts():
    owner = make_owner("Mochi")
    add(owner, "Mochi", "Walk", 8, 0)
    add(owner, "Mochi", "Old walk", 8, 0, completed=True)
    add(owner, "Mochi", "Tomorrow walk", 8, 0, due_date=DAY + timedelta(days=1))

    assert Scheduler(owner).detect_conflicts(DAY) == []


# --- Planning --------------------------------------------------------------

def test_empty_owner_produces_empty_plan():
    scheduler = Scheduler(make_owner("Mochi"))

    assert scheduler.generate_plan(DAY) == []
    assert scheduler.detect_conflicts(DAY) == []
    assert scheduler.explain() == "No tasks scheduled."


def test_plan_keeps_task_that_exactly_fills_budget():
    owner = make_owner("Mochi", minutes=30)
    walk = add(owner, "Mochi", "Walk", 8, 0, duration=30)
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan(DAY) == [walk]
    assert scheduler.skipped == []


def test_plan_skips_task_that_does_not_fit_and_keeps_going():
    owner = make_owner("Mochi", minutes=60)
    hike = add(owner, "Mochi", "Hike", 9, 0, duration=50, priority=Priority.HIGH)
    bath = add(owner, "Mochi", "Bath", 7, 0, duration=20, priority=Priority.MEDIUM)
    brush = add(owner, "Mochi", "Brush", 6, 0, duration=10, priority=Priority.LOW)
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan(DAY)

    assert plan == [brush, hike]  # kept by priority, shown by time
    assert scheduler.total_minutes() == 60
    assert [t for t, _ in scheduler.skipped] == [bath]
    assert "needs 20 min, only 10 min left" in scheduler.skipped[0][1]


# --- Filtering -------------------------------------------------------------

def test_filter_combines_pet_and_status_case_insensitively():
    owner = make_owner("Mochi", "Luna")
    luna_open = add(owner, "Luna", "Feed", 8, 0)
    add(owner, "Luna", "Walk", 9, 0, completed=True)
    add(owner, "Mochi", "Feed", 8, 0)

    result = Scheduler(owner).filter_tasks(pet_name="luna", completed=False)

    assert result == [luna_open]
