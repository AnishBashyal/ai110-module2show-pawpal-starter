# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

- Enter owner and pet info, including how much time the owner has available each day.
- Add and edit care tasks (walks, feeding, meds, grooming), each with a duration and priority.
- Generate and view today's plan, with an explanation of why tasks were chosen and ordered that way.

**a. Initial design**

Main objects I think the system needs:

- **Owner**
  - Attributes: name, time available per day, preferences, pet
  - Methods: none for now, it just holds the info
- **Pet**
  - Attributes: name, species, list of tasks
  - Methods: add a task
- **Task**
  - Attributes: title, duration, priority
  - Methods: edit the task
- **Scheduler**
  - Attributes: the owner (and through the owner, the pet and tasks), start time of the day
  - Methods: make the daily plan (returns the scheduled tasks with times, the skipped tasks, and the reasoning), explain why it chose them

My UML has four classes. I tried to keep it simple and only add what the README needs.

- **Owner** keeps the basic info about the person: name, how many minutes they have each day, and their preferences. It also holds the pet. It does not do any work, it is just the place where the owner info lives.
- **Pet** keeps the pet's name and species, and the list of tasks for that pet. Its job is to hold the tasks and let us add a new one.
- **Task** is one care activity, like a walk or feeding. It has a title, a duration, and a priority. Its job is to store that info and let the user edit it later.
- **Scheduler** is the one that does the thinking. It takes the owner (and gets the pet and tasks from there) and makes the daily plan using the time available and the priorities. It also explains why it chose those tasks, and which ones it skipped.

I put the logic only in Scheduler so the other classes stay simple and easy to understand.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed a little after I looked at it again. I made two small changes:

- **explain_plan() now takes the plan.** At first it took nothing, but then it would not know which plan to explain. Now I pass the plan from generate_plan() into it, so it does not need to remember anything.
- **I added a priority order.** Priority is a word like "high" or "low", and if I sort the words normally "high" comes before "low" but "medium" would be in the wrong place. So I added a small map (high = 1, medium = 2, low = 3) that the Scheduler can use to sort tasks correctly.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My conflict check (find_conflicts) only looks at the times the owner asked for, and it only warns. It does not move anything. generate_plan still stacks the tasks one after another from the start time, so the warnings are about what the owner typed in, not about the final plan.

I also check every pair of tasks instead of sorting first and only checking neighbors. The sorted way is faster, but I found it can miss a case: a long task from 08:00 to 10:00 can overlap a task at 09:00 even when a short task at 08:30 sits between them. Checking every pair is slower on paper, but a pet owner has maybe 10 tasks a day, so it does not matter.

When I looked at how to simplify it, I thought about two versions. The first one uses `itertools.combinations` instead of the nested loop with `timed[i + 1:]`. I kept that one, because it reads like plain English ("every pair") and it removed the slicing. The second one sorts the tasks and does the whole check in one list comprehension. I did not use that one. It is shorter, but I had to stop and think to see what it does, and it is the same version that could miss overlaps.

This is reasonable here because a warning is enough for the owner to fix the times, and a simple check that is always right is better than a clever one that is sometimes wrong.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
