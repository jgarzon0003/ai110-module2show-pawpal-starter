from datetime import date, time

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


def test_scheduler_sort_by_time_returns_chronological_order():
    scheduler = Scheduler()
    afternoon = Task(title="Afternoon", category="misc", duration_minutes=10, priority="low")
    afternoon.mark_scheduled(time(14, 0), "manual")
    morning = Task(title="Morning", category="misc", duration_minutes=10, priority="low")
    morning.mark_scheduled(time(7, 0), "manual")
    midday = Task(title="Midday", category="misc", duration_minutes=10, priority="low")
    midday.mark_scheduled(time(12, 0), "manual")

    ordered = scheduler.sort_by_time([afternoon, morning, midday])

    assert [task.title for task in ordered] == ["Morning", "Midday", "Afternoon"]


def test_scheduler_sort_by_time_puts_unscheduled_tasks_last():
    scheduler = Scheduler()
    unscheduled = Task(title="Unscheduled", category="misc", duration_minutes=10, priority="low")
    scheduled = Task(title="Scheduled", category="misc", duration_minutes=10, priority="low")
    scheduled.mark_scheduled(time(9, 0), "manual")

    ordered = scheduler.sort_by_time([unscheduled, scheduled])

    assert [task.title for task in ordered] == ["Scheduled", "Unscheduled"]


def test_task_next_occurrence_daily_advances_one_day():
    task = Task(
        title="Feed",
        category="feeding",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        due_date=date(2026, 7, 6),
    )

    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.title == "Feed"
    assert next_task.due_date == date(2026, 7, 7)
    assert next_task.completed is False


def test_task_next_occurrence_weekly_advances_one_week():
    task = Task(
        title="Groom",
        category="hygiene",
        duration_minutes=20,
        priority="medium",
        frequency="weekly",
        due_date=date(2026, 7, 6),
    )

    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 13)


def test_task_next_occurrence_once_returns_none():
    task = Task(
        title="One-time vet visit",
        category="health",
        duration_minutes=30,
        priority="high",
        frequency="once",
        due_date=date(2026, 7, 6),
    )

    assert task.next_occurrence() is None


def test_pet_complete_task_creates_next_occurrence_for_daily_task():
    pet = Pet(name="Rex", species="Dog")
    task = Task(
        title="Feed",
        category="feeding",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        due_date=date(2026, 7, 6),
    )
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 7)
    assert next_task.completed is False
    assert pet.tasks == [task, next_task]


def test_pet_complete_task_once_task_does_not_add_new_task():
    pet = Pet(name="Rex", species="Dog")
    task = Task(title="One-time vet visit", category="health", duration_minutes=30, priority="high")
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert next_task is None
    assert pet.tasks == [task]


def test_scheduler_detect_conflicts_flags_overlapping_times():
    scheduler = Scheduler()
    first = Task(title="Walk", category="exercise", duration_minutes=30, priority="high")
    first.mark_scheduled(time(8, 0), "manual")
    second = Task(title="Feed", category="feeding", duration_minutes=10, priority="high")
    second.mark_scheduled(time(8, 15), "manual")

    warnings = scheduler.detect_conflicts([first, second])

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feed" in warnings[0]


def test_scheduler_detect_conflicts_flags_duplicate_start_times():
    scheduler = Scheduler()
    first = Task(title="Walk", category="exercise", duration_minutes=30, priority="high")
    first.mark_scheduled(time(8, 0), "manual")
    second = Task(title="Feed", category="feeding", duration_minutes=10, priority="high")
    second.mark_scheduled(time(8, 0), "manual")

    warnings = scheduler.detect_conflicts([first, second])

    assert len(warnings) == 1


def test_scheduler_detect_conflicts_no_overlap_returns_empty():
    scheduler = Scheduler()
    first = Task(title="Walk", category="exercise", duration_minutes=30, priority="high")
    first.mark_scheduled(time(8, 0), "manual")
    second = Task(title="Feed", category="feeding", duration_minutes=10, priority="high")
    second.mark_scheduled(time(8, 30), "manual")

    assert scheduler.detect_conflicts([first, second]) == []


def test_scheduler_detect_conflicts_ignores_unscheduled_tasks():
    scheduler = Scheduler()
    unscheduled = Task(title="Unscheduled", category="misc", duration_minutes=10, priority="low")

    assert scheduler.detect_conflicts([unscheduled]) == []
