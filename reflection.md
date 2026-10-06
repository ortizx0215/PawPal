# PawPal+ Project Reflection

## 1. System Design
 - Users should able to:
 - Add pets
 - See Feeding schedule
- Add or edit tasks
**a. Initial design**

in my UML design, I made 
Owner: for whoever is usin the app. They have their name and emails and lets them keep track of the pets. 
Pet: name of the pets, what type of pet, age., 
Task: general to do list i.e feeding or vet visits. Descriptions, Due dates, and way to mark the task as completed.
Walk: scheduled walk days and is more specific to the scheduled time and duration of the walk.


**b. Design changes**

- So we made 4 changes after reviewing the skeleton. Tasks are now able to records their pet by adding pet_name to task. 

Then we added a SchedultedTask class. The app needed to be able to show a timed daily plan so not planned tasks carry start_time and reason. Owner also got day_start so that the scheduler knows when the day begins

We moved Completion from Task to Schedule. this was because the completed flag on the task would never reset so if you were to mark daily walk completed then it would drop out of every future schedule. Putting it into schedule makes recurring tasks start fresh every day.

Lastly, Priority became an Enum. Priority used to free test so a typo such as "High" would sort wrong without any error. Priority enum would catch bad values right away and gives each level a number for sorting.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- Time: the owner's available_minutes is a hard limit. Generate_plan() adds task only while they still fit, and skips the rest with a reason. ("needs 45 min, only 35 min left")

Priority: tasks are chosen high -> med -> low so important care is picked first

Duration: when two tasks have the same priority, the shorter one goes first, which fits more tasks into the time.

Start time: it doesn't affect which tasksa re picked. It's used to order the final plan and to find overlapping tasks.

Due date and completion: only tasks due today that aren't already done are considered. Recurring tasks come back on their next due date.

- How did you decide which constraints mattered most?

Priority comes first because pet health matters the most. Missing medication or a meal can overly hurt the pet.

Time is the hard limit because te owner can't make more time. 

Duration is the tiebreaker. It fits more tasks in, but it never actually beats the prority. A long high-priority walk wins over two short low priority tasks.

Start time is for display and warnings, not selection. The owner already chose when tasks happen, so the scheduler respects those tiems instead of moving things arond.

We just left out Preferences.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler only warns about conflicts. It doesn't fix them. If two tasks overlap (like Mochi's morning walk at 8:00 and Luna's vet call at 8:10), `detect_conflicts()` prints a warning but both tasks stay in the plan, and both count against the owner's available minutes even though they can't be done at the same time. A smarter scheduler would move the lower-priority task to the next open slot.

I think this is reasonable because the owner knows things the app doesn't. Some "conflicts" aren't real problems, like brushing Mochi's teeth right before the walk, or feeding both pets at once. If the app moved tasks on its own, it could push something like medication to a bad time. Warning instead of auto-fixing keeps the owner in control, keeps the code simple, and the program never crashes over a conflict. It just reports it.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

Making the first Mermaid UML with the four ideas: owner, pet, tasks, schedules. I had a hard time trying to figure out HOW I wanted to do it so AI gave me a really good frame of how to structure it.

- What kinds of prompts or questions were most helpful?

The prompts that helped the most were the ones where I asked it to double check any changes as well as the ones where I had it make a change and ask WHY it decided to make that change. It really helped me understand the logic behind their decisions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

So while asking about the Mermaid UML, Claude had six ideas for it. I only approved 4 of the six. One of the fixes would have removed the owner's prefered walk time because I wasn't sure if I wanted to add that preference just yet and if it were to get added, it would have messed up with the workflow I had going on in my head.

- How did you evaluate or verify what the AI suggested?

Asking for the reasoning was the main check. For each fix, I looked at the problem it described and asked myself whether it would actualyl break something in my app. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

The behaviors I tested were Sorting, Recurring Tasks, Conflict Detection, Daily plan, and Basics & Filtering.

- Why were these tests important?

These tests were important because these tests target the edge cases, where scheduling bugs are hardest to notice by hand. The tests also use a fixed date instead of today's date so they give the same result whenever they run. 

**b. Confidence**

- How confident are you that your scheduler works correctly?

I'm pretty confident. Like a 3.5 - 4 out of 5. All 22 tests pass and they cover the core behaviors and the edge cases most liekly to break them, like back-to-back tasks, a task that exactly fills the time budget, and a task completed late. I also tried the full workflow in the Streamlit app and checked that the plan, warnings and next-day tasks came out as expected.

- What edge cases would you test next if you had more time?

I would try tasks that cross into midnight since conflicts are only checked within one day so a task from 11:30pm - 12:30 am isn't compared with a task at 12:15 AM the next day.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am satisfied with how recurring tasks work. My first ever design was to store completion as a flag that never reset, so a daily walk marked done would disappread from every future schedule. The final design treats each task as one occurence: completing it creates the next one, one day or one week later. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would link tasks directly to the pets instead of by name. Task stores pet_name as text, so renaming or remove a pet breaks the link. Storing a reference to the Pet object or a unique ID, would fix both of the known gaps.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Claude was most useful when I made it explain its reasoning behind its suggestions and deciding for myself. Asking for its opinions before changes let me accept only the fixes I agreed with

Questioning why completion shouldn't live in two places led to a better design than either of us started with.