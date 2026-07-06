"""Testing ground for verifying pawpal_system.py logic in the terminal."""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler


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

    dog.add_task(Task(title="Morning walk", category="exercise", duration_minutes=30, priority="high", start_time=time(7, 30)))
    dog.add_task(Task(title="Feed breakfast", category="feeding", duration_minutes=10, priority="high", start_time=time(8, 0)))
    cat.add_task(Task(title="Litter box cleaning", category="hygiene", duration_minutes=15, priority="medium", start_time=time(9, 0)))

    scheduler = Scheduler()
    all_scheduled = []
    for pet in owner.pets:
        all_scheduled.extend(scheduler.build_plan(owner, pet))

    all_scheduled.sort(key=lambda t: t.start_time or time.max)

    print("Today's Schedule")
    print("=================")
    for task in all_scheduled:
        pet_name = next(pet.name for pet in owner.pets if task in pet.tasks)
        start = task.start_time.strftime("%I:%M %p") if task.start_time else "Unscheduled"
        print(f"[{start}] {pet_name} - {task.title} ({task.duration_minutes} min, {task.priority} priority)")


if __name__ == "__main__":
    main()
