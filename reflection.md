# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial design uses four classes:

- **Owner** — stores the owner's name and scheduling constraints (available time window and total minutes per day). Represents the limits the plan has to respect.
- **Pet** — stores the pet's name/species and holds the list of `Task`s that apply to it, linking care tasks to a specific animal.
- **Task** — represents one pet-care item (walk, feeding, meds, enrichment, grooming): title, category, `duration_minutes`, and `priority`. Once scheduled, it also carries its assigned `start_time` and a short reason string explaining why it was placed (or skipped).
- **Scheduler** — the only class with real logic. Takes an `Owner`'s constraints and a `Pet`'s tasks, sorts/filters by priority and available time, assigns time slots, and returns an ordered daily plan with reasoning attached to each task.

`Owner` and `Pet` describe the people/animals, `Task` describes the work, and `Scheduler` is the decision-maker that turns tasks + constraints into a plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

No since I was using AI directly and telling on how I wanted. For now it looks good. Thus, I made no change.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
Time and priority.

- How did you decide which constraints mattered most?
Priority matters most because this is a pet care app. Missing a high-priority task like medication is a real-world problem; missing grooming is just a minor delay. Time is the hard constraint—you can only schedule the minutes you actually have—so it acts as the cutoff. Priority simply decides which tasks survive that cutoff.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used it mainly to brainstorm and refactor code.

- What kinds of prompts or questions were most helpful?
Two shot prompt and making it question possible edge cases were helpful.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When trying to add unneccesary code.

- How did you evaluate or verify what the AI suggested?
It had a long chat. Also the app was not running properly.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - Add task
    - Add pet 
    - Add date
- Why were these tests important?
These are important since owners want to planify a task for their pets on some dates.


**b. Confidence**

- How confident are you that your scheduler works correctly? From a 1-5, I would say a 4.

- What edge cases would you test next if you had more time?
Multiple owners with same name dog trying a similar task. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The testing

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
Play around with more test cases.


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
UML helps to give structure on how the code connects and how it should work.
