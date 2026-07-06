"""PawPal+ logic layer.

Class skeletons mirroring diagrams/uml_draft.mmd. Keep this file in sync
with the UML as the design evolves.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional

_RECURRING_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str = "once"
    completed: bool = False
    start_time: Optional[time] = None
    reason: Optional[str] = None
    due_date: Optional[date] = None

    def mark_scheduled(self, start_time: Optional[time], reason: str) -> None:
        """Record the assigned start time and reasoning for this task."""
        self.start_time = start_time
        self.reason = reason

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh instance for the next due date if this task recurs, else None.

        Returns:
            A new, incomplete Task with the same attributes and its due_date advanced
            by one day ("daily") or one week ("weekly"), or None if frequency is "once"
            or unrecognized.
        """
        interval = _RECURRING_INTERVALS.get(self.frequency.lower())
        if interval is None:
            return None

        base_date = self.due_date or date.today()
        return Task(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=base_date + interval,
        )


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add its next occurrence to this pet.

        Args:
            task: The Task to complete. Must belong to this pet's task list.

        Returns:
            The newly created next-occurrence Task if the completed task recurs
            ("daily"/"weekly"), otherwise None.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Owner:
    name: str
    available_start: time
    available_end: time
    max_minutes_per_day: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Return tasks optionally filtered by owning pet's name and/or completion status.

        Args:
            pet_name: If given, only include tasks belonging to the pet with this name.
            completed: If given, only include tasks whose completed flag matches this value.

        Returns:
            Tasks across this owner's pets matching all provided filters (unfiltered
            arguments are ignored).
        """
        results: List[Task] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def get_available_minutes(self) -> int:
        """Compute the owner's available minutes, capped by their daily max."""
        window_start = datetime.combine(datetime.min, self.available_start)
        window_end = datetime.combine(datetime.min, self.available_end)
        window_minutes = int((window_end - window_start).total_seconds() // 60)
        return min(window_minutes, self.max_minutes_per_day)


class Scheduler:
    def build_plan(self, owner: Owner, pet: Pet) -> List[Task]:
        """Build a scheduled task plan for a pet, ordered by priority and fit to the owner's availability."""
        ordered_tasks = self.sort_by_priority(pet.tasks)
        return self.assign_time_slots(owner, ordered_tasks)

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted from highest to lowest priority."""
        return sorted(tasks, key=lambda task: _PRIORITY_ORDER.get(task.priority.lower(), len(_PRIORITY_ORDER)))

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted chronologically by start_time; unscheduled tasks sort last.

        Args:
            tasks: Tasks to sort. Tasks with start_time=None are treated as occurring
                at the end of the day.

        Returns:
            A new list of the same tasks in chronological order.
        """
        return sorted(tasks, key=lambda task: task.start_time or time.max)

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Check scheduled tasks for overlapping time windows and return warning messages.

        Lightweight check: only compares tasks that already have a start_time, so it
        never raises even if some tasks are unscheduled.

        Args:
            tasks: Tasks to check, from any mix of pets. Tasks with start_time=None
                are ignored.

        Returns:
            A human-readable warning string for each pair of adjacent (by start_time)
            tasks whose duration overlaps the next task's start_time. Empty if no
            conflicts are found.
        """
        warnings: List[str] = []
        timed_tasks = self.sort_by_time([task for task in tasks if task.start_time is not None])

        for current_task, next_task in zip(timed_tasks, timed_tasks[1:]):
            current_end = datetime.combine(datetime.min, current_task.start_time) + timedelta(
                minutes=current_task.duration_minutes
            )
            next_start = datetime.combine(datetime.min, next_task.start_time)

            if current_end > next_start:
                warnings.append(
                    f"Conflict: '{current_task.title}' ({current_task.start_time.strftime('%H:%M')}) "
                    f"overlaps with '{next_task.title}' ({next_task.start_time.strftime('%H:%M')})"
                )

        return warnings

    def assign_time_slots(self, owner: Owner, tasks: List[Task]) -> List[Task]:
        """Assign start times to tasks that fit within the owner's available minutes."""
        available_minutes = owner.get_available_minutes()
        current_time = datetime.combine(datetime.min, owner.available_start)
        minutes_used = 0
        scheduled: List[Task] = []

        for task in tasks:
            if minutes_used + task.duration_minutes > available_minutes:
                task.mark_scheduled(None, "Not enough time available today")
                continue

            task.mark_scheduled(current_time.time(), "Scheduled based on priority and availability")
            scheduled.append(task)
            minutes_used += task.duration_minutes
            current_time += timedelta(minutes=task.duration_minutes)

        return scheduled
