"""PawPal+ logic layer.

Class skeletons mirroring diagrams/uml_draft.mmd. Keep this file in sync
with the UML as the design evolves.
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import List, Optional

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

    def mark_scheduled(self, start_time: Optional[time], reason: str) -> None:
        """Record the assigned start time and reasoning for this task."""
        self.start_time = start_time
        self.reason = reason

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)


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
