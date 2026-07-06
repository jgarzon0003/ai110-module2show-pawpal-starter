from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def make_owner(available_start=time(7, 0), available_end=time(20, 0), max_minutes_per_day=180):
    return Owner(
        name="Jordan",
        available_start=available_start,
        available_end=available_end,
        max_minutes_per_day=max_minutes_per_day,
    )


def test_task_mark_complete():
    task = Task(title="Feed", category="feeding", duration_minutes=10, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_mark_scheduled():
    task = Task(title="Walk", category="exercise", duration_minutes=30, priority="high")
    task.mark_scheduled(time(7, 30), "Scheduled based on priority and availability")
    assert task.start_time == time(7, 30)
    assert task.reason == "Scheduled based on priority and availability"


def test_pet_add_task():
    pet = Pet(name="Rex", species="Dog")
    task = Task(title="Walk", category="exercise", duration_minutes=30, priority="high")
    pet.add_task(task)
    assert pet.tasks == [task]


def test_owner_add_pet_and_get_all_tasks():
    owner = make_owner()
    dog = Pet(name="Rex", species="Dog")
    cat = Pet(name="Whiskers", species="Cat")
    dog.add_task(Task(title="Walk", category="exercise", duration_minutes=30, priority="high"))
    cat.add_task(Task(title="Litter box", category="hygiene", duration_minutes=15, priority="medium"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 2
    assert all_tasks[0].title == "Walk"
    assert all_tasks[1].title == "Litter box"


def test_owner_get_available_minutes_capped_by_window():
    owner = make_owner(available_start=time(7, 0), available_end=time(8, 0), max_minutes_per_day=180)
    assert owner.get_available_minutes() == 60


def test_owner_get_available_minutes_capped_by_max_minutes():
    owner = make_owner(available_start=time(7, 0), available_end=time(20, 0), max_minutes_per_day=90)
    assert owner.get_available_minutes() == 90


def test_scheduler_sort_by_priority():
    scheduler = Scheduler()
    low = Task(title="Low", category="misc", duration_minutes=10, priority="low")
    high = Task(title="High", category="misc", duration_minutes=10, priority="high")
    medium = Task(title="Medium", category="misc", duration_minutes=10, priority="medium")

    ordered = scheduler.sort_by_priority([low, high, medium])
    assert [task.title for task in ordered] == ["High", "Medium", "Low"]


def test_scheduler_assign_time_slots_within_availability():
    owner = make_owner(available_start=time(7, 0), available_end=time(20, 0), max_minutes_per_day=180)
    scheduler = Scheduler()
    task = Task(title="Walk", category="exercise", duration_minutes=30, priority="high")

    scheduled = scheduler.assign_time_slots(owner, [task])

    assert scheduled == [task]
    assert task.start_time == time(7, 0)
    assert task.reason == "Scheduled based on priority and availability"


def test_scheduler_assign_time_slots_not_enough_time():
    owner = make_owner(available_start=time(7, 0), available_end=time(7, 30), max_minutes_per_day=180)
    scheduler = Scheduler()
    task = Task(title="Long walk", category="exercise", duration_minutes=60, priority="high")

    scheduled = scheduler.assign_time_slots(owner, [task])

    assert scheduled == []
    assert task.start_time is None
    assert task.reason == "Not enough time available today"


def test_scheduler_build_plan_orders_and_schedules():
    owner = make_owner(available_start=time(7, 0), available_end=time(8, 0), max_minutes_per_day=180)
    pet = Pet(name="Rex", species="Dog")
    pet.add_task(Task(title="Nail trim", category="hygiene", duration_minutes=15, priority="low"))
    pet.add_task(Task(title="Feed", category="feeding", duration_minutes=10, priority="high"))

    scheduler = Scheduler()
    plan = scheduler.build_plan(owner, pet)

    assert [task.title for task in plan] == ["Feed", "Nail trim"]
    assert plan[0].start_time == time(7, 0)
    assert plan[1].start_time == time(7, 10)
