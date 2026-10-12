from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

# lower number = more important, so we can sort tasks with it
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}


@dataclass
class Task:
    title: str
    duration: int  # minutes
    priority: str  # "high", "medium", or "low"
    time: str = ""  # preferred time like "08:00", empty means no preference
    frequency: str = "daily"  # "once", "daily", or "weekly"
    completed: bool = False

    def edit(self, title: str, duration: int, priority: str) -> None:
        """Change the task's title, duration, and priority."""
        self.title = title
        self.duration = duration
        self.priority = priority

    def mark_complete(self) -> None:
        """Mark the task as done."""
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
    available_minutes: int
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Collect the tasks from every pet."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    def __init__(self, owner: Owner, start_time: str = "08:00"):
        """Set up a scheduler for an owner, with the time the day's plan starts."""
        self.owner = owner
        self.start_time = start_time

    def get_pending_tasks(self) -> List[Task]:
        """All tasks that are not done yet, most important first."""
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        # same priority: tasks with a preferred time first, then shorter ones
        return sorted(
            pending,
            key=lambda t: (
                PRIORITY_ORDER.get(t.priority, len(PRIORITY_ORDER) + 1),
                t.time == "",
                t.time,
                t.duration,
            ),
        )

    def generate_plan(self) -> dict:
        """Fit tasks into the owner's available minutes, in priority order."""
        current = datetime.strptime(self.start_time, "%H:%M")
        minutes_left = self.owner.available_minutes
        scheduled = []
        skipped = []

        for task in self.get_pending_tasks():
            if task.duration <= minutes_left:
                scheduled.append((current.strftime("%H:%M"), task))
                current += timedelta(minutes=task.duration)
                minutes_left -= task.duration
            else:
                skipped.append(task)

        return {
            "scheduled": scheduled,
            "skipped": skipped,
            "minutes_used": self.owner.available_minutes - minutes_left,
        }

    def explain_plan(self, plan: dict) -> str:
        """Return plain text saying which tasks were added or skipped, and why."""
        lines = [
            f"{self.owner.name} has {self.owner.available_minutes} minutes today. "
            "Tasks are picked by priority (high first), then by time and length."
        ]
        for start, task in plan["scheduled"]:
            lines.append(
                f"- {start}: {task.title} ({task.duration} min, {task.priority}) was added."
            )
        for task in plan["skipped"]:
            lines.append(
                f"- {task.title} ({task.duration} min, {task.priority}) was skipped, not enough time left."
            )
        return "\n".join(lines)
