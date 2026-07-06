"""PawPal+ logic layer.

Class skeletons mirroring diagrams/uml_draft.mmd. Keep this file in sync
with the UML as the design evolves.
"""

from dataclasses import dataclass, field
from datetime import time
from typing import List, Optional


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    start_time: Optional[time] = None
    reason: Optional[str] = None

    def mark_scheduled(self, start_time: time, reason: str) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_start: time
    available_end: time
    max_minutes_per_day: int

    def get_available_minutes(self) -> int:
        pass


class Scheduler:
    def build_plan(self, owner: Owner, pet: Pet) -> List[Task]:
        pass

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        pass

    def assign_time_slots(self, owner: Owner, tasks: List[Task]) -> List[Task]:
        pass
