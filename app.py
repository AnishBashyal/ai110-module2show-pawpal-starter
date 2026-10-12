from datetime import datetime

import streamlit as st

from pawpal_system import PRIORITY_ICON, Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit reruns this file on every click, so keep the Owner in session_state.
# Only create it the first time, after that reuse the one already in the "vault".
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner = st.session_state.owner
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input("Minutes available today", min_value=1, max_value=1440, value=owner.available_minutes)
)

st.subheader("Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # the UI hands the form data to Owner.add_pet, which stores the new Pet
    owner.add_pet(Pet(name=pet_name, species=species))

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.subheader("Tasks")
if owner.pets:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_pet = st.selectbox("For pet", [p.name for p in owner.pets])
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    col1, col2, col3 = st.columns(3)
    with col1:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col2:
        task_time = st.text_input("Preferred time (HH:MM, optional)", value="")
    with col3:
        frequency = st.selectbox("Repeats", ["daily", "weekly", "once"])

    if st.button("Add task"):
        time_ok = True
        if task_time:
            try:
                datetime.strptime(task_time, "%H:%M")
            except ValueError:
                time_ok = False
        if time_ok:
            pet = next(p for p in owner.pets if p.name == task_pet)
            pet.add_task(
                Task(title=task_title, duration=int(duration), priority=priority,
                     time=task_time, frequency=frequency)
            )
        else:
            st.error(f'"{task_time}" is not a time. Use 24-hour HH:MM, like 08:30.')
else:
    st.caption("Add a pet first, then you can add tasks for it.")

if owner.get_all_tasks():
    scheduler = Scheduler(owner)

    # filters use Owner.filter_tasks
    col1, col2 = st.columns(2)
    with col1:
        pet_choice = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_choice = st.selectbox("Show status", ["All", "Not done", "Done"])
    shown = owner.filter_tasks(
        pet_name=None if pet_choice == "All pets" else pet_choice,
        completed={"All": None, "Not done": False, "Done": True}[status_choice],
    )

    # sorting uses Scheduler.sort_by_time
    st.write("Current tasks (sorted by preferred time):")
    if shown:
        st.table(
            [
                {
                    "Time": t.time or "any time",
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Minutes": t.duration,
                    "Priority": f"{PRIORITY_ICON[t.priority]} {t.priority}",
                    "Repeats": t.frequency,
                    "Due": t.due_date.isoformat(),
                    "Done": "✅" if t.completed else "⬜",
                }
                for t in scheduler.sort_by_time(shown)
            ]
        )
    else:
        st.info("No tasks match this filter.")

    # conflict warnings use Scheduler.find_conflicts, only on tasks still to do
    todo = owner.filter_tasks(completed=False)
    conflicts = scheduler.find_conflicts(todo)
    if conflicts:
        st.warning(f"{len(conflicts)} time conflict(s) found. You cannot be in two places at once!")
        for message in conflicts:
            st.warning(message.replace("Warning: ", ""))
        st.caption("Tip: change the preferred time of one task, then add it again. Back-to-back is fine.")
    elif any(t.time for t in todo):
        st.success("No time conflicts between your timed tasks.")

    st.write("Mark a task as done:")
    for i, t in enumerate(todo):
        if st.button(f"Done: {t.title} ({t.pet_name})", key=f"done_{i}_{id(t)}"):
            pet = next(p for p in owner.pets if p.name == t.pet_name)
            pet.complete_task(t)  # repeating tasks get a new copy for later
            st.rerun()
else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    if plan["scheduled"]:
        st.success(f"Planned {plan['minutes_used']} of {owner.available_minutes} minutes.")
        st.table(
            [
                {"Start": start, "Task": t.title, "Pet": t.pet_name, "Minutes": t.duration, "Priority": f"{PRIORITY_ICON[t.priority]} {t.priority}"}
                for start, t in plan["scheduled"]
            ]
        )
    else:
        st.warning("Nothing to schedule. Add some tasks first.")

    if plan["skipped"]:
        st.write("Skipped (not enough time):")
        st.table([{"Task": t.title, "Minutes": t.duration, "Priority": f"{PRIORITY_ICON[t.priority]} {t.priority}"} for t in plan["skipped"]])

    st.markdown("**Why this plan:**")
    st.text(scheduler.explain_plan(plan))
