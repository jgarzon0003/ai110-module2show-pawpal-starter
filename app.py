import streamlit as st

from datetime import date, time as dtime

from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit reruns this whole script on every interaction, so plain variables
# reset each time. st.session_state is the "vault" that survives reruns —
# check for a key before creating the object, otherwise you'll wipe it out.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_start=dtime(7, 0),
        available_end=dtime(21, 0),
        max_minutes_per_day=120,
    )
owner = st.session_state.owner

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
owner_name = st.text_input("Owner name", value=owner.name)
owner.name = owner_name

st.markdown("### Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if any(pet.name == pet_name for pet in owner.pets):
        st.warning(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species))

if owner.pets:
    st.write("Current pets:", ", ".join(pet.name for pet in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if owner.pets:
    pet_names = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Pet for this task", pet_names)
    selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.text_input("Category", value="exercise")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        due = st.date_input("Due date", value=date.today())

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                title=task_title,
                category=category,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
                due_date=due,
            )
        )

    show_completed = st.checkbox("Show completed tasks", value=True)
    visible_tasks = owner.filter_tasks(
        pet_name=selected_pet.name, completed=None if show_completed else False
    )

    if visible_tasks:
        st.write(f"Current tasks for {selected_pet.name}:")
        for task in visible_tasks:
            row = st.columns([3, 2, 2, 2, 2, 2])
            row[0].write(task.title)
            row[1].write(task.category)
            row[2].write(f"{task.duration_minutes} min")
            row[3].write(task.priority)
            row[4].write("Done" if task.completed else task.frequency)
            if not task.completed:
                if row[5].button("Mark complete", key=f"complete-{id(task)}"):
                    next_task = selected_pet.complete_task(task)
                    if next_task is not None:
                        st.success(f"Completed! Next occurrence due {next_task.due_date}.")
                    st.rerun()
            else:
                row[5].write("✅")
    else:
        st.info(f"No tasks yet for {selected_pet.name}. Add one above.")
else:
    st.info("Add a pet first before creating tasks.")

if owner.pets:
    with st.expander("All tasks across pets"):
        all_tasks = owner.get_all_tasks()
        if all_tasks:
            st.table(
                [
                    {
                        "pet": pet.name,
                        "title": task.title,
                        "priority": task.priority,
                        "frequency": task.frequency,
                        "completed": task.completed,
                    }
                    for pet in owner.pets
                    for task in pet.tasks
                ]
            )
        else:
            st.info("No tasks yet for any pet.")

st.divider()

st.subheader("Build Schedule")

if owner.pets:
    st.caption(f"Owner: {owner.name} | Pet: {selected_pet.name} ({selected_pet.species})")

    if st.button("Generate schedule"):
        scheduler = Scheduler()

        # Each due_date gets its own day's worth of the owner's availability,
        # so tasks due on different days don't compete for the same time window.
        tasks_by_date = {}
        for task in selected_pet.tasks:
            tasks_by_date.setdefault(task.due_date or date.today(), []).append(task)

        any_scheduled = False
        for task_date in sorted(tasks_by_date):
            ordered = scheduler.sort_by_priority(tasks_by_date[task_date])
            plan = scheduler.assign_time_slots(owner, ordered)
            plan = scheduler.sort_by_time(plan)

            st.markdown(f"**{task_date.strftime('%A, %B %d, %Y')}**")

            if plan:
                any_scheduled = True
                st.success(f"Scheduled {len(plan)} task(s) for {selected_pet.name}.")
                st.table(
                    [
                        {
                            "start_time": task.start_time.strftime("%H:%M") if task.start_time else "-",
                            "title": task.title,
                            "duration_minutes": task.duration_minutes,
                            "priority": task.priority,
                            "reason": task.reason,
                        }
                        for task in plan
                    ]
                )

                conflicts = scheduler.detect_conflicts(plan)
                if conflicts:
                    for warning in conflicts:
                        st.warning(warning)
                else:
                    st.success("No scheduling conflicts detected.")
            else:
                st.warning(f"No tasks could be scheduled for {selected_pet.name} on this day.")

            skipped = [task for task in tasks_by_date[task_date] if task.start_time is None]
            if skipped:
                st.caption("Skipped tasks:")
                for task in skipped:
                    st.error(f"{task.title}: {task.reason}")

        if not any_scheduled and not tasks_by_date:
            st.warning("No tasks could be scheduled for this pet.")
else:
    st.info("Add a pet and at least one task before generating a schedule.")
