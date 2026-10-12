# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule for Sam
========================================================
Time         Task              Pet       Priority
--------------------------------------------------------
08:00-08:10  Feeding           Mochi     high
08:10-08:40  Morning walk      Biscuit   high
08:40-08:45  Give medicine     Mochi     high
08:45-09:05  Play with toys    Mochi     medium
--------------------------------------------------------
Total: 65 of 90 min

Skipped (not enough time):
  - Grooming (40 min, low)

Why this plan:
Sam has 90 minutes today. Tasks are picked by priority (high first), then by time and length.
- 08:00: Feeding (10 min, high) was added.
- 08:10: Morning walk (30 min, high) was added.
- 08:40: Give medicine (5 min, high) was added.
- 08:45: Play with toys (20 min, medium) was added.
- Grooming (40 min, low) was skipped, not enough time left.
```

## 🧪 Testing PawPal+

Run the tests with:

```bash
python -m pytest
```

My 27 tests check the main things the scheduler must do:

- **Sorting:** tasks come out in clock order, tasks with no time go last, an empty list works, and the original list is not changed.
- **Recurring tasks:** a daily task makes a new one for tomorrow, a weekly one for 7 days later, and a "once" task makes nothing. I also test Jan 31 going to Feb 1, and that the new copy is a separate task.
- **Conflicts:** same time, overlapping, and one task inside another all give a warning. Back-to-back tasks, tasks with no time, and bad times like "8am" give no warning and no crash.
- **Plan:** high priority goes first, a task that exactly fits is added, a big task is skipped but a small one after it still fits, and a pet with no tasks or 0 minutes gives an empty plan.
- **Filtering and explain:** filter by pet and by done status, and the explanation says which tasks were added or skipped.

Test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/anishbashyal/Desktop/CodePath/ai110-module2show-pawpal-starter
collected 27 items

tests/test_pawpal.py ...........................                         [100%]

============================== 27 passed in 0.01s ==============================
```

**Confidence Level: ★★★★☆ (4 out of 5)**

All 27 tests pass, and they cover the happy paths and the edge cases I could think of. I am not giving 5 stars because the tests do not check the Streamlit UI, and the plan does not move tasks to fix conflicts, it only warns.

## 📐 Smarter Scheduling

| Feature            | Method(s)                                                | Notes                                                     |
| ------------------ | -------------------------------------------------------- | --------------------------------------------------------- |
| Sorting by time    | `Scheduler.sort_by_time()`                               | "HH:MM" text sorts in clock order, tasks with no time last |
| Filtering          | `Owner.filter_tasks()`                                   | by pet name and/or done status                            |
| Recurring tasks    | `Task.mark_complete()`, `Pet.complete_task()`            | daily = +1 day, weekly = +7 days, "once" does not repeat  |
| Conflict detection | `Scheduler.find_conflicts()`                             | warns about overlapping tasks, never crashes              |

**Sorting.** `Scheduler.sort_by_time(tasks)` uses `sorted()` with a lambda key: `(t.time == "", t.time)`. Zero-padded "HH:MM" strings already sort in clock order. The `t.time == ""` part pushes tasks with no time to the end. It returns a new list. The plan itself (`generate_plan`) is still ordered by priority first, using `get_pending_tasks()`.

**Filtering.** `Owner.filter_tasks(pet_name=None, completed=None)` keeps only the tasks that match. `None` means "don't filter on this", so you can filter by pet, by status, or both. This works because `Pet.add_task()` saves the pet's name on every task (`task.pet_name`).

**Recurring tasks.** Each task has a `frequency` ("once", "daily", "weekly") and a `due_date`. When you call `Pet.complete_task(task)`, it runs `Task.mark_complete()`, which marks the task done and returns a new copy. The copy's due date is today + 1 day (daily) or today + 7 days (weekly), worked out with `timedelta`. "once" tasks return nothing. `Scheduler.get_pending_tasks()` skips tasks due in the future, so tomorrow's copy does not show up in today's plan.

**Conflict detection.** `Scheduler.find_conflicts(tasks)` looks at every pair of tasks that have a preferred time. Two tasks overlap if each one starts before the other ends. Back-to-back tasks are fine. It returns a list of warning messages (empty if none), says whether the clash is the same pet or different pets, and never raises an error.

Tradeoff: conflicts are checked on the times the owner asked for. `generate_plan()` does not move tasks around to fix them. See `reflection.md` section 2b.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
