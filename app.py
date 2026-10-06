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
all_tasks = scheduler.sort_by_time(owner.get_all_tasks())
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {
            "time": f"{t.time:%H:%M}",
            "pet": t.pet_name,
            "task": t.description,
            "minutes": t.duration_minutes,
            "priority": t.priority.name.lower(),
            "repeats": t.frequency.value,
            "done": t.completed,
        }
        for t in all_tasks
    ])

    pending = [t for t in all_tasks if not t.completed]
    if pending:
        col1, col2 = st.columns([3, 1])
        with col1:
            to_complete = st.selectbox(
                "Mark a task complete",
                range(len(pending)),
                format_func=lambda i: (
                    f"{pending[i].due_date:%m/%d} {pending[i].time:%H:%M} "
                    f"{pending[i].pet_name} - {pending[i].description}"
                ),
            )
        with col2:
            st.write("")  # nudge the button down to line up with the dropdown
            if st.button("Complete"):
                done = pending[to_complete]
                next_task = scheduler.complete_task(done)
                if next_task:
                    st.session_state.flash = (
                        f"Done! Next '{done.description}' is due {next_task.due_date:%a %m/%d}."
                    )
                else:
                    st.session_state.flash = f"Done! '{done.description}' won't repeat."
                st.rerun()  # redraw the table so it shows the new status

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

st.divider()

st.subheader("Build Schedule")
st.caption("Plans today's tasks by priority within your available time.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if not plan and not scheduler.skipped:
        st.info("No tasks due today.")
    else:
        st.success(
            f"Planned {len(plan)} task(s): "
            f"{scheduler.total_minutes()} of {owner.available_minutes} minutes."
        )
        for warning in scheduler.detect_conflicts():
            st.warning(warning)
        st.code(scheduler.explain(), language="text")
