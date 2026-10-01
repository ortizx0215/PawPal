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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
