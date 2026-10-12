import os
import sys

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_task_count():
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, "high"))

    assert len(pet.tasks) == 1


def test_sort_by_time_orders_earliest_first_and_blank_last():
    owner = Owner(name="Sam", available_minutes=90)
    tasks = [
        Task("Grooming", 40, "low", time="17:00"),
        Task("Play", 20, "medium"),
        Task("Feeding", 10, "high", time="07:30"),
        Task("Medicine", 5, "high", time="12:00"),
    ]

    result = Scheduler(owner).sort_by_time(tasks)

    assert [t.title for t in result] == ["Feeding", "Medicine", "Grooming", "Play"]


def test_filter_tasks_by_pet_and_status():
    owner = Owner(name="Sam", available_minutes=90)
    biscuit = Pet(name="Biscuit", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    walk = Task("Walk", 30, "high")
    biscuit.add_task(walk)
    mochi.add_task(Task("Feeding", 10, "high"))
    walk.mark_complete()

    assert [t.title for t in owner.filter_tasks(pet_name="Mochi")] == ["Feeding"]
    assert [t.title for t in owner.filter_tasks(completed=True)] == ["Walk"]
    assert owner.filter_tasks(pet_name="Mochi", completed=True) == []
    assert len(owner.filter_tasks()) == 2


def test_completing_daily_task_creates_next_day_task():
    pet = Pet(name="Mochi", species="cat")
    feeding = Task("Feeding", 10, "high", frequency="daily")
    pet.add_task(feeding)

    pet.complete_task(feeding)

    assert feeding.completed is True
    assert len(pet.tasks) == 2
    new_task = pet.tasks[1]
    assert new_task.completed is False
    assert new_task.due_date == date.today() + timedelta(days=1)
    assert new_task.pet_name == "Mochi"


def test_completing_weekly_task_is_due_in_seven_days():
    pet = Pet(name="Biscuit", species="dog")
    bath = Task("Bath", 30, "low", frequency="weekly")
    pet.add_task(bath)

    pet.complete_task(bath)

    assert pet.tasks[1].due_date == date.today() + timedelta(days=7)


def test_completing_once_task_does_not_repeat():
    pet = Pet(name="Biscuit", species="dog")
    vet = Task("Vet visit", 60, "high", frequency="once")
    pet.add_task(vet)

    pet.complete_task(vet)

    assert len(pet.tasks) == 1


def test_future_task_is_not_in_pending_tasks():
    owner = Owner(name="Sam", available_minutes=90)
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)
    feeding = Task("Feeding", 10, "high")
    pet.add_task(feeding)
    pet.complete_task(feeding)  # makes tomorrow's copy

    assert Scheduler(owner).get_pending_tasks() == []


def _conflict_setup():
    owner = Owner(name="Sam", available_minutes=90)
    biscuit = Pet(name="Biscuit", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    return owner, biscuit, mochi


def test_same_pet_same_time_is_a_conflict():
    owner, biscuit, _ = _conflict_setup()
    biscuit.add_task(Task("Walk", 30, "high", time="08:00"))
    biscuit.add_task(Task("Bath", 20, "low", time="08:00"))

    warnings = Scheduler(owner).find_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "same pet" in warnings[0]


def test_different_pets_overlapping_is_a_conflict():
    owner, biscuit, mochi = _conflict_setup()
    biscuit.add_task(Task("Walk", 30, "high", time="08:00"))
    mochi.add_task(Task("Feeding", 10, "high", time="08:20"))

    warnings = Scheduler(owner).find_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_back_to_back_and_untimed_tasks_do_not_conflict():
    owner, biscuit, mochi = _conflict_setup()
    biscuit.add_task(Task("Walk", 30, "high", time="08:00"))   # ends 08:30
    mochi.add_task(Task("Feeding", 10, "high", time="08:30"))  # starts 08:30
    mochi.add_task(Task("Play", 20, "low"))                    # no time

    assert Scheduler(owner).find_conflicts(owner.get_all_tasks()) == []


# ---------- extra edge-case tests ----------

import pawpal_system


def test_sort_by_time_empty_list_and_original_unchanged():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=90))
    assert scheduler.sort_by_time([]) == []

    tasks = [Task("B", 10, "low", time="12:00"), Task("A", 10, "low", time="07:00")]
    scheduler.sort_by_time(tasks)

    assert [t.title for t in tasks] == ["B", "A"]  # the list we passed in is not changed


def test_sort_by_time_same_time_keeps_original_order():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=90))
    tasks = [Task("First", 10, "low", time="08:00"), Task("Second", 10, "low", time="08:00")]

    result = scheduler.sort_by_time(tasks)

    assert [t.title for t in result] == ["First", "Second"]


def test_daily_task_on_last_day_of_month_rolls_to_next_month(monkeypatch):
    class FakeDate(date):
        @classmethod
        def today(cls):
            return date(2026, 1, 31)

    monkeypatch.setattr(pawpal_system, "date", FakeDate)
    task = Task("Feeding", 10, "high", frequency="daily")

    new_task = task.mark_complete()

    assert new_task.due_date == date(2026, 2, 1)


def test_new_recurring_copy_is_a_separate_task():
    task = Task("Feeding", 10, "high", frequency="daily")

    new_task = task.mark_complete()
    new_task.edit("Dinner", 20, "low")

    assert task.title == "Feeding"
    assert task.completed is True


def test_conflicts_empty_and_single_task_return_nothing():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=90))

    assert scheduler.find_conflicts([]) == []
    assert scheduler.find_conflicts([Task("Walk", 30, "high", time="08:00")]) == []


def test_task_inside_another_task_is_a_conflict():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=90))
    long_task = Task("Grooming", 60, "low", time="09:00")
    short_task = Task("Medicine", 10, "high", time="09:15")

    assert len(scheduler.find_conflicts([long_task, short_task])) == 1


def test_three_overlapping_tasks_give_three_warnings():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=90))
    tasks = [Task(n, 30, "high", time="08:00") for n in ("A", "B", "C")]

    assert len(scheduler.find_conflicts(tasks)) == 3  # A-B, A-C, B-C


def test_pet_with_no_tasks_gives_empty_plan():
    owner = Owner(name="Sam", available_minutes=90)
    owner.add_pet(Pet(name="Mochi", species="cat"))

    plan = Scheduler(owner).generate_plan()

    assert plan["scheduled"] == []
    assert plan["skipped"] == []
    assert plan["minutes_used"] == 0


def test_zero_available_minutes_skips_everything():
    owner = Owner(name="Sam", available_minutes=0)
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)
    pet.add_task(Task("Feeding", 10, "high"))

    plan = Scheduler(owner).generate_plan()

    assert plan["scheduled"] == []
    assert len(plan["skipped"]) == 1


def test_task_that_exactly_fits_is_scheduled():
    owner = Owner(name="Sam", available_minutes=30)
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high"))

    plan = Scheduler(owner).generate_plan()

    assert len(plan["scheduled"]) == 1
    assert plan["minutes_used"] == 30


def test_plan_is_priority_first_and_chains_start_times():
    owner = Owner(name="Sam", available_minutes=90)
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task("Short low", 5, "low"))
    pet.add_task(Task("Long high", 30, "high"))

    plan = Scheduler(owner, start_time="08:00").generate_plan()

    assert [(s, t.title) for s, t in plan["scheduled"]] == [
        ("08:00", "Long high"),
        ("08:30", "Short low"),
    ]


def test_big_task_is_skipped_but_later_small_task_still_fits():
    owner = Owner(name="Sam", available_minutes=20)
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task("Big", 60, "high"))
    pet.add_task(Task("Small", 10, "low"))

    plan = Scheduler(owner).generate_plan()

    assert [t.title for _, t in plan["scheduled"]] == ["Small"]
    assert [t.title for t in plan["skipped"]] == ["Big"]


def test_completed_tasks_are_left_out_of_the_plan():
    owner = Owner(name="Sam", available_minutes=90)
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    walk = Task("Walk", 30, "high", frequency="once")
    pet.add_task(walk)
    pet.complete_task(walk)

    assert Scheduler(owner).generate_plan()["scheduled"] == []


def test_filter_unknown_pet_and_owner_with_no_pets():
    owner = Owner(name="Sam", available_minutes=90)
    assert owner.filter_tasks() == []

    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)
    pet.add_task(Task("Feeding", 10, "high"))

    assert owner.filter_tasks(pet_name="Rex") == []


def test_explain_plan_mentions_added_and_skipped_tasks():
    owner = Owner(name="Sam", available_minutes=10)
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)
    pet.add_task(Task("Feeding", 10, "high"))
    pet.add_task(Task("Grooming", 40, "low"))
    scheduler = Scheduler(owner)

    text = scheduler.explain_plan(scheduler.generate_plan())

    assert "Feeding" in text and "was added" in text
    assert "Grooming" in text and "was skipped" in text


def test_bad_time_text_is_ignored_and_does_not_crash():
    scheduler = Scheduler(Owner(name="Sam", available_minutes=90))
    tasks = [
        Task("Walk", 30, "high", time="8am"),
        Task("Feeding", 10, "high", time="25:99"),
        Task("Bath", 20, "low", time="08:00"),
    ]

    assert scheduler.find_conflicts(tasks) == []
