# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Today's Schedule - Tuesday, October 06, 2026
============================================
Plan for Jordan (85/90 min):
  08:00  Morning walk for Mochi (30 min) [high]
  08:00  Brush teeth for Mochi (5 min) [medium]
  08:10  Vet call for Luna (15 min) [high]
  08:45  Medication for Luna (5 min) [high]
  17:00  Litter box for Luna (10 min) [medium]
  17:00  Play session for Luna (20 min) [medium]
Skipped:
  Grooming for Mochi [low] - needs 45 min, only 5 min left

Warnings:
  Conflict (Mochi has two tasks at once): 'Morning walk' (08:00-08:30) overlaps 'Brush teeth' (08:00-08:05)
  Conflict (Mochi and Luna both need you): 'Morning walk' (08:00-08:30) overlaps 'Vet call' (08:10-08:25)
  Conflict (Luna has two tasks at once): 'Play session' (17:00-17:20) overlaps 'Litter box' (17:00-17:10)
```


## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. Run `python main.py` to see each feature in the terminal.

| Feature | Method(s) | What it does |
|---------|-----------|--------------|
| Sorting by time | `Scheduler.sort_by_time()` | Orders tasks by date and start time |
| Sorting by priority | `Scheduler.sort_by_priority()` | High → medium → low; ties go to the shorter task, then the earlier one |
| Filtering | `Scheduler.filter_tasks()`, `filter_by_pet()`, `filter_by_status()` | Shows tasks for one pet, by completion status, or both |
| Daily plan | `Scheduler.generate_plan()`, `explain()` | Keeps the most important tasks that fit the owner's time and explains what was skipped |
| Conflict detection | `Scheduler.detect_conflicts()`, `Task.overlaps()` | Warns when tasks start together or overlap, for the same pet or different pets |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.complete_task()`, `Frequency.interval()` | Completing a daily or weekly task creates its next occurrence |

### Sorting
`sort_by_time()` uses `sorted()` with a lambda key, `key=lambda t: t.start()`. `start()` combines the task's date and time, so tomorrow's 07:30 sorts after today's 18:30. `sort_by_priority()` sorts on the tuple `(-priority, duration, start)`. Python compares tuples left to right, so priority decides first and the other fields only break ties.

### Filtering
`filter_tasks(pet_name=None, completed=None)` combines filters. Any filter left as `None` is ignored, so `filter_tasks(pet_name="Luna", completed=False)` returns Luna's unfinished tasks. Pet names match regardless of capitalization. `filter_by_pet()` and `filter_by_status()` are shortcuts that call it.

### Conflict detection
`detect_conflicts()` sorts today's tasks by start time and checks each pair for a shared start time or an overlapping time window. It is lightweight: it returns a list of warning messages and never raises an error, so the app keeps running and the plan is still usable. Each warning says whether one pet has two tasks at once or two pets need the owner at the same time. Because the list is sorted, it stops checking a task once later tasks start after it ends.

### Recurring tasks
Each task has a `Frequency` (`ONCE`, `DAILY` or `WEEKLY`). When `complete_task()` marks a repeating task done, `mark_complete()` creates a copy due one day or one week later and adds it to the same pet. The next date counts from whichever is later, the due date or the day it was completed, so a task finished late doesn't come back already overdue. Completing the same task twice doesn't create a duplicate.

### Tradeoffs
- **Conflicts are warned about, not fixed.** Both overlapping tasks stay in the plan. The owner decides which conflicts matter.
- **Greedy planning.** The highest-priority tasks are kept first, even if a different mix would use more of the available time.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
