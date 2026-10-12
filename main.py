from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(name="Sam", available_minutes=90)

    biscuit = Pet(name="Biscuit", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", 30, "high", time="08:00"))
    biscuit.add_task(Task("Grooming", 40, "low", time="17:00"))
    mochi.add_task(Task("Feeding", 10, "high", time="07:30"))
    mochi.add_task(Task("Give medicine", 5, "high", time="12:00"))
    mochi.add_task(Task("Play with toys", 20, "medium", time="18:00"))

    scheduler = Scheduler(owner, start_time="08:00")
    plan = scheduler.generate_plan()

    # tasks don't know their pet, so build a lookup for printing
    pet_of = {id(t): p.name for p in owner.pets for t in p.tasks}

    print(f"Today's Schedule for {owner.name}")
    print("=" * 56)
    print(f"{'Time':<13}{'Task':<18}{'Pet':<10}{'Priority':<8}")
    print("-" * 56)
    for start, task in plan["scheduled"]:
        end = (datetime.strptime(start, "%H:%M") + timedelta(minutes=task.duration)).strftime("%H:%M")
        print(f"{start}-{end}  {task.title:<18}{pet_of[id(task)]:<10}{task.priority:<8}")
    print("-" * 56)
    print(f"Total: {plan['minutes_used']} of {owner.available_minutes} min")

    if plan["skipped"]:
        print("\nSkipped (not enough time):")
        for task in plan["skipped"]:
            print(f"  - {task.title} ({task.duration} min, {task.priority})")

    print("\nWhy this plan:")
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
