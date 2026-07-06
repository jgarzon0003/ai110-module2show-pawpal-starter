"""Testing ground for verifying pawpal_system.py logic in the terminal."""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(title: str, tasks) -> None:
    print(title)
    print("=" * len(title))
    for task in tasks:
        start = task.start_time.strftime("%I:%M %p") if task.start_time else "Unscheduled"
        status = "done" if task.completed else "pending"
        print(f"[{start}] {task.title} ({task.duration_minutes} min, {task.priority} priority, {status})")
    print()


def main() -> None:
    owner = Owner(
        name="Jordan",
        available_start=time(7, 0),
        available_end=time(20, 0),
        max_minutes_per_day=180,
    )

    dog = Pet(name="Rex", species="Dog")
    cat = Pet(name="Whiskers", species="Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Tasks added out of order on purpose to prove sort_by_time works.
    feed = Task(title="Feed breakfast", category="feeding", duration_minutes=10, priority="high", frequency="daily", start_time=time(8, 0))
    walk = Task(title="Morning walk", category="exercise", duration_minutes=30, priority="high", frequency="once", start_time=time(7, 30))
    vet = Task(title="Vet checkup", category="health", duration_minutes=45, priority="medium", frequency="once", start_time=time(12, 0))
    dog.add_task(feed)
    dog.add_task(walk)
    dog.add_task(vet)

    litter = Task(title="Litter box cleaning", category="hygiene", duration_minutes=15, priority="medium", frequency="weekly", start_time=time(9, 0))
    # Same start_time as the litter box task, to trigger conflict detection below.
    grooming = Task(title="Grooming", category="hygiene", duration_minutes=20, priority="low", frequency="once", start_time=time(9, 0))
    cat.add_task(litter)
    cat.add_task(grooming)

    scheduler = Scheduler()

    # --- Sorting Logic ---
    all_tasks = owner.get_all_tasks()
    print_schedule("All tasks, sorted by time", scheduler.sort_by_time(all_tasks))

    # --- Filtering Logic ---
    print_schedule("Rex's tasks only", owner.filter_tasks(pet_name="Rex"))
    walk.mark_complete()
    print_schedule("Pending tasks only", owner.filter_tasks(completed=False))
    print_schedule("Completed tasks only", owner.filter_tasks(completed=True))

    # --- Recurring Tasks ---
    next_feed = dog.complete_task(feed)
    if next_feed:
        print(f"'{feed.title}' is daily -> next occurrence due {next_feed.due_date}\n")

    next_litter = cat.complete_task(litter)
    if next_litter:
        print(f"'{litter.title}' is weekly -> next occurrence due {next_litter.due_date}\n")

    # --- Conflict Detection ---
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())
    if conflicts:
        print("Scheduling Warnings")
        print("====================")
        for warning in conflicts:
            print(warning)
        print()
    else:
        print("No scheduling conflicts detected.\n")


if __name__ == "__main__":
    main()
