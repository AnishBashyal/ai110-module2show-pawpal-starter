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

The scheduler looks at three things: the minutes the owner has today, the priority of each task (high, medium, low), and the preferred time of a task. It also skips tasks that are done or due in the future.

I decided that time available matters most, because it is a hard limit: if a task does not fit, it cannot happen. Priority comes next, since a vet visit or medicine should not be skipped for grooming. The preferred time is the weakest one. It only breaks ties between tasks with the same priority, and it is used for the conflict warnings. I did this because an owner can change a time easily, but cannot make the day longer.

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

I used Claude Code for most of the project. I used it to turn my UML into class stubs, to write the scheduling logic in small steps, to plan and write tests, and to connect the logic to the Streamlit app. It also helped me update the UML and the README at the end.

The features that helped me most:

- **Reading my files first.** It read the README and pawpal_system.py before it answered, so the suggestions fit my code and not a random example.
- **Running the code.** It ran the tests and main.py, so I saw real output and not a guess. This also caught a bad time like "8am" that crashed find_conflicts.
- **Test planning.** When I asked for edge cases (a pet with no tasks, two tasks at the same time), I got a list of things I did not think about.

The prompts that worked best were small and clear, like "list 3-5 core behaviors to verify" or "what edge cases should I test for sorting and recurring tasks?". Big vague prompts gave me more code than I could understand.

**b. Judgment and verification**

When I looked at how to simplify find_conflicts, the AI showed a shorter version that sorts the tasks and only checks the neighbors in one list comprehension. I did not use it. It was shorter, but I had to stop and think to understand it, and I found it can miss an overlap (a long task from 08:00 to 10:00 and a task at 09:00 with a short one in between). I kept the version that checks every pair with `itertools.combinations`. It is simple and always right, and an owner only has about 10 tasks a day.

I checked suggestions by running them. I ran pytest, and I wrote a test for the exact case that worried me before I trusted the code.

**c. Separate chat sessions**

I used a different chat for each phase (design, logic, testing, UI and docs). Each chat only had the files and the goal for that phase, so the answers stayed on topic and I did not get old ideas mixed in. It also made it easier to find things later, because I knew which chat had the testing decisions and which had the design. The tradeoff is that a new chat does not remember anything, so I had to give it the README and the code again.

**d. Being the lead architect**

The AI is fast and can write a lot of code, but it does not know what I want unless I decide it. I learned that my job is to choose the design (few classes, simple code), say what is in scope, and say no when a suggestion is too clever or too big. The AI gives options, and I pick one and check it. If I do not understand a piece of code, I should not keep it, even if it works. The project stayed simple because I kept making these decisions, and the tests told me if I was right.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 27 tests. They cover:

- **Sorting:** clock order, tasks with no time last, an empty list, and the original list not changed.
- **Recurring tasks:** daily goes to tomorrow, weekly to 7 days later, "once" does not repeat, and Jan 31 goes to Feb 1.
- **Conflicts:** same time, overlap, one task inside another, back-to-back (no warning), and bad times like "8am" (no crash).
- **Plan:** high priority first, a task that exactly fits, a big task skipped while a small one still fits, and a pet with no tasks or 0 minutes.
- **Filtering and explain:** by pet and by status, and the text says what was added or skipped.

These matter because the scheduler is the main point of the app. If sorting or the time limit is wrong, the owner gets a bad plan and does not know it.

**b. Confidence**

I am fairly confident, 4 out of 5. All 27 tests pass and they cover the normal cases and the edge cases I could think of. I did not give 5 because the tests do not check the Streamlit app, and the plan only warns about conflicts, it does not fix them.

If I had more time I would test:

- Two tasks with the same preferred time inside the plan itself.
- A task that is longer than the whole day, or goes past midnight.
- Two pets with the same name (filtering uses the name, so it would mix them up).
- The app buttons, like Done and the filters, in a real browser.

---

## 5. Reflection

**a. What went well**

I am most happy with how simple the design stayed. I have four small classes, and the smart parts (sorting, filtering, recurring, conflicts) are short methods that I can read and explain. I am also happy that the tests found a real problem, the bad time text crashing find_conflicts, and I fixed it.

**b. What you would improve**

I would make generate_plan use the preferred times, so it moves tasks to fix conflicts and not only warns about them. I would also save the pets and tasks to a file, because right now everything is lost when the page refreshes. And I would give each pet an id, so two pets with the same name do not get mixed up.

**c. Key takeaway**

AI can write code very fast, but I am the one who decides what the system should be. Keeping the design small, checking every suggestion with tests, and not keeping code I do not understand made the project better than just accepting everything.
