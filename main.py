from datetime import date, datetime, timedelta

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

    print(f"Today's Schedule for {owner.name}")
    print("=" * 56)
    print(f"{'Time':<13}{'Task':<18}{'Pet':<10}{'Priority':<8}")
    print("-" * 56)
    for start, task in plan["scheduled"]:
        end = (datetime.strptime(start, "%H:%M") + timedelta(minutes=task.duration)).strftime("%H:%M")
        print(f"{start}-{end}  {task.title:<18}{task.pet_name:<10}{task.priority:<8}")
    print("-" * 56)
    print(f"Total: {plan['minutes_used']} of {owner.available_minutes} min")

    if plan["skipped"]:
        print("\nSkipped (not enough time):")
        for task in plan["skipped"]:
            print(f"  - {task.title} ({task.duration} min, {task.priority})")

    print("\nWhy this plan:")
    print(scheduler.explain_plan(plan))

    show_sorting_and_filtering(owner, scheduler)
    show_conflicts(owner, scheduler)


def show_tasks(label, tasks):
    print(f"\n{label}")
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(f"  {t.time or '--:--'}  {t.title:<16}{t.pet_name:<9}{status}")
    if not tasks:
        print("  (none)")


def show_sorting_and_filtering(owner, scheduler):
    """Demo: add tasks out of order, then sort and filter them."""
    print("\n" + "=" * 56)
    print("Sorting and filtering demo")

    owner.pets[0].add_task(Task("Evening walk", 25, "medium", time="19:00"))
    owner.pets[1].add_task(Task("Brush fur", 10, "low"))
    owner.pets[1].add_task(Task("Breakfast", 10, "high", time="06:45"))
    owner.pets[0].complete_task(owner.pets[0].tasks[0])  # Morning walk is done

    show_tasks("All tasks, in the order they were added:", owner.get_all_tasks())
    show_tasks("Sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))
    show_tasks("Only Mochi's tasks:", owner.filter_tasks(pet_name="Mochi"))
    show_tasks("Only completed tasks:", owner.filter_tasks(completed=True))
    show_tasks(
        "Biscuit's tasks that are not done, sorted by time:",
        scheduler.sort_by_time(owner.filter_tasks(pet_name="Biscuit", completed=False)),
    )


def show_conflicts(owner, scheduler):
    """Demo: add tasks at the same time and print the warnings."""
    print("\n" + "=" * 56)
    print("Conflict detection demo")

    # same pet, same time
    owner.pets[1].add_task(Task("Nail trim", 15, "low", time="12:00"))
    # different pets, overlapping time (Mochi's Feeding is 07:30-07:40)
    owner.pets[0].add_task(Task("Vet call", 20, "medium", time="07:35"))

    warnings = scheduler.find_conflicts(scheduler.get_pending_tasks())
    if warnings:
        for w in warnings:
            print(w)
    else:
        print("No conflicts found.")


if __name__ == "__main__":
    main()
