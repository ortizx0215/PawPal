from datetime import time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your pet care planning assistant. Tell it how much time you
have today, add your pets and their care tasks, and it builds a daily plan that
puts the most important tasks first.
"""
)

with st.expander("How it works", expanded=False):
    st.markdown(
        """
1. **Set your time.** Enter how many minutes you have for pet care today.
2. **Add your pets.** Each pet keeps its own list of tasks.
3. **Schedule tasks.** Give each task a time, duration, priority, and how often it repeats.
4. **Generate your schedule.** PawPal+ keeps the highest-priority tasks that fit your
   time, orders them by time of day, warns you about overlapping tasks, and explains
   anything it had to skip.
"""
    )

st.divider()

# Keep one Owner alive across reruns; create it only on the first run.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Time available today (minutes)",
            min_value=0, max_value=1440, value=owner.available_minutes,
        )
    )

st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Enter a pet name.")
    elif owner.get_pet(pet_name) is not None:
        st.warning(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(pet_name.strip(), species))
        st.success(f"Added {pet_name}.")

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.subheader("Schedule a Task")
if not owner.pets:
    st.caption("Add a pet first.")
else:
    task_pet = st.selectbox("For pet", [p.name for p in owner.pets])
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task", value="Morning walk")
        task_time = st.time_input("Time", value=time(8, 0))
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        owner.get_pet(task_pet).add_task(
            Task(
                task_title,
                task_time,
                int(duration),
                Priority[priority.upper()],
                Frequency(frequency),
            )
        )
        st.success(f"Added '{task_title}' for {task_pet}.")

scheduler = Scheduler(owner)

PRIORITY_LABELS = {
    Priority.HIGH: "🔴 High",
    Priority.MEDIUM: "🟡 Medium",
    Priority.LOW: "🟢 Low",
}


def task_rows(tasks: list[Task], conflicted: set[int] = frozenset()) -> list[dict]:
    """Turn tasks into display rows; `conflicted` holds id()s of overlapping tasks."""
    rows = []
    for t in tasks:
        if t.completed:
            status = "✅ Done"
        elif id(t) in conflicted:
            status = "⚠️ Overlaps"
        else:
            status = "⏳ To do"
        rows.append({
            "Date": f"{t.due_date:%a %m/%d}",
            "Time": f"{t.time:%H:%M}–{t.end():%H:%M}",
            "Pet": t.pet_name,
            "Task": t.description,
            "Minutes": t.duration_minutes,
            "Priority": PRIORITY_LABELS[t.priority],
            "Repeats": t.frequency.value.title(),
            "Status": status,
        })
    return rows


def conflict_message(a: Task, b: Task) -> str:
    """Explain an overlap in plain words and suggest which task to move."""
    if a.pet_name == b.pet_name:
        headline = f"{a.pet_name} has two tasks at once"
    else:
        headline = f"{a.pet_name} and {b.pet_name} both need you at the same time"
    # Suggest moving the less important task; on a tie, move the later one.
    move, keep = (a, b) if a.priority.value < b.priority.value else (b, a)
    return (
        f"**{headline}.** {a.pet_name}'s *{a.description}* "
        f"({a.time:%H:%M}–{a.end():%H:%M}) overlaps {b.pet_name}'s "
        f"*{b.description}* ({b.time:%H:%M}–{b.end():%H:%M}).  \n"
        f"💡 Try moving *{move.description}* to {keep.end():%H:%M} or later."
    )


conflicts = scheduler.find_conflicts()
conflicted_ids = {id(t) for pair in conflicts for t in pair}

st.subheader("Tasks")
all_tasks = owner.get_all_tasks()
if not all_tasks:
    st.info("No tasks yet. Add one above.")
else:
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.radio("Show", ["All", "To do", "Done"], horizontal=True)

    shown = scheduler.sort_by_time(
        scheduler.filter_tasks(
            pet_name=None if pet_filter == "All pets" else pet_filter,
            completed={"All": None, "To do": False, "Done": True}[status_filter],
        )
    )
    if shown:
        st.dataframe(task_rows(shown, conflicted_ids), hide_index=True, width="stretch")
    else:
        st.info("No tasks match these filters.")
    st.caption(f"Showing {len(shown)} of {len(all_tasks)} tasks, sorted by date and time.")

    # Flag overlaps right where tasks are entered, so they can be fixed immediately.
    for a, b in conflicts:
        st.warning(conflict_message(a, b), icon="⚠️")

    pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if pending:
        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            to_complete = st.selectbox(
                "Mark a task complete",
                range(len(pending)),
                format_func=lambda i: (
                    f"{pending[i].due_date:%a %m/%d} {pending[i].time:%H:%M} · "
                    f"{pending[i].pet_name} · {pending[i].description}"
                ),
            )
        with col2:
            if st.button("Complete", width="stretch"):
                done = pending[to_complete]
                next_task = scheduler.complete_task(done)
                if next_task:
                    st.session_state.flash = (
                        f"Nice work! '{done.description}' is done. "
                        f"Next one is due {next_task.due_date:%a %m/%d}."
                    )
                else:
                    st.session_state.flash = f"Nice work! '{done.description}' is done."
                st.rerun()  # redraw the table so it shows the new status

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"), icon="✅")

st.divider()

st.subheader("Today's Schedule")
st.caption("Keeps your highest-priority tasks that fit your available time, in time order.")

if st.button("Generate schedule", type="primary"):
    st.session_state.show_plan = True

# Rebuilt on every rerun so the plan stays current as tasks change.
if st.session_state.get("show_plan"):
    plan = scheduler.generate_plan()
    if not plan and not scheduler.skipped:
        st.info("No tasks due today. Enjoy the free time!")
    else:
        used = scheduler.total_minutes()
        col1, col2, col3 = st.columns(3)
        col1.metric("Tasks planned", len(plan))
        col2.metric("Time used", f"{used} / {owner.available_minutes} min")
        col3.metric("Skipped", len(scheduler.skipped))
        if owner.available_minutes:
            st.progress(min(used / owner.available_minutes, 1.0))

        if conflicts:
            st.warning(
                f"{len(conflicts)} overlap(s) in today's plan, marked ⚠️ below. "
                "See the suggestions under **Tasks** to fix them.",
                icon="⚠️",
            )
        else:
            st.success("No time conflicts. Your day fits together.", icon="✅")

        if plan:
            st.dataframe(task_rows(plan, conflicted_ids), hide_index=True, width="stretch")

        for task, reason in scheduler.skipped:
            st.info(
                f"Skipped **{task.description}** for {task.pet_name} "
                f"({PRIORITY_LABELS[task.priority]} priority): {reason}.",
                icon="⏭️",
            )

        with st.expander("Why this plan?"):
            st.code(scheduler.explain(), language="text")
