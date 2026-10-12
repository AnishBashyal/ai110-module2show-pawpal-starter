from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    title: str
    duration: int  # minutes
    priority: str  # "high", "medium", or "low"

    def edit(self, title: str, duration: int, priority: str) -> None:
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
    available_minutes: int
    preferences: str = ""
    pet: Optional[Pet] = None


class Scheduler:
    def __init__(self, owner: Owner, start_time: str = "08:00"):
        self.owner = owner
        self.start_time = start_time

    def generate_plan(self) -> dict:
        pass

    def explain_plan(self) -> str:
        pass
