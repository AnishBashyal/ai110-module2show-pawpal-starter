from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from itertools import combinations
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
    pet_name: str = ""  # set automatically by Pet.add_task
    due_date: date = field(default_factory=date.today)

    def edit(self, title: str, duration: int, priority: str) -> None:
        """Change the task's title, duration, and priority."""
        self.title = title
        self.duration = duration
        self.priority = priority

    def mark_complete(self):
        """Mark the task as done.

        Returns a new not-done copy due tomorrow (daily) or in 7 days (weekly).
        Returns None for "once" tasks, since they do not repeat.
        """
        self.completed = True
        # timedelta is a length of time, so date + timedelta gives a new date
        # and handles month/year changes for us (Jan 31 + 1 day = Feb 1).
        days = {"daily": 1, "weekly": 7}.get(self.frequency)
        if days is None:  # "once" tasks do not repeat
            return None
        return replace(self, completed=False, due_date=date.today() + timedelta(days=days))


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list and remember whose it is."""
        task.pet_name = self.name
        self.tasks.append(task)

    def complete_task(self, task: Task) -> None:
        """Mark a task done and, if it repeats, add the next copy to this pet's tasks."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)


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

    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> List[Task]:
        """Get tasks for one pet and/or by done status.

        pet_name: only this pet's tasks. completed: True for done, False for not done.
        Leaving either as None means don't filter on it. Returns a new list.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks


class Scheduler:
    def __init__(self, owner: Owner, start_time: str = "08:00"):
        """Set up a scheduler for an owner, with the time the day's plan starts."""
        self.owner = owner
        self.start_time = start_time

    def get_pending_tasks(self) -> List[Task]:
        """Tasks that are not done and due today or earlier, most important first."""
        today = date.today()
        pending = [
            t for t in self.owner.get_all_tasks()
            if not t.completed and t.due_date <= today  # skip future repeats
        ]
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

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by preferred time ("HH:MM"), earliest first, tasks with no time last.

        Returns a new list and does not change the one passed in.
        """
        # "HH:MM" with zero padding sorts correctly as plain text.
        # (t.time == "") is False for tasks with a time, True for blank ones,
        # and False sorts before True, so blank times go to the end.
        return sorted(tasks, key=lambda t: (t.time == "", t.time))

    def find_conflicts(self, tasks: List[Task]) -> List[str]:
        """Check every pair of timed tasks and warn about the ones that overlap.

        Tasks with no preferred time are ignored. Back-to-back tasks (one ends
        when the next starts) are not a conflict. Same pet or different pets both
        count. Returns a list of warning strings, empty if there are no conflicts.
        It never raises, so the program keeps running.
        """
        # only tasks with a preferred time have a fixed slot
        timed = [t for t in tasks if t.time]
        warnings = []
        for a, b in combinations(timed, 2):  # every pair once
            a_start = self._minutes(a.time)
            b_start = self._minutes(b.time)
            # two slots overlap if each one starts before the other ends
            if a_start < b_start + b.duration and b_start < a_start + a.duration:
                who = "same pet" if a.pet_name == b.pet_name else "different pets"
                warnings.append(
                    f"Warning: {a.title} ({a.pet_name}, {a.time}) overlaps "
                    f"{b.title} ({b.pet_name}, {b.time}) - {who}."
                )
        return warnings

    @staticmethod
    def _minutes(hhmm: str) -> int:
        """Turn "08:30" into minutes since midnight (510)."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

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
