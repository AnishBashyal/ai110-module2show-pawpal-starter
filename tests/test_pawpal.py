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
