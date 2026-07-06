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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
=================
[07:00 AM] Rex - Morning walk (30 min, high priority)
[07:00 AM] Whiskers - Litter box cleaning (15 min, medium priority)
[07:30 AM] Rex - Feed breakfast (10 min, high priority)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
========================================================================== test session starts ===========================================================================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Jhostin\Documents\Codepath\AI 110\Week 4 Project\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 21 items                                                                                                                                                        

tests\test_pawpal.py .....................                                                                                                                          [100%]

=========================================================================== 21 passed in 0.05s ===========================================================================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority`, `Scheduler.sort_by_time` | Sorts by priority (high → low) for building the plan, or chronologically by `start_time` for display; unscheduled tasks sort last. |
| Filtering | `Owner.filter_tasks`, `Scheduler.assign_time_slots` | `filter_tasks` filters by pet name and/or completion status; `assign_time_slots` skips (rather than schedules) tasks once the owner's available minutes run out, marking them "Not enough time available today". |
| Conflict handling | `Scheduler.detect_conflicts` | Compares adjacent tasks (by start time) across pets and returns a warning string for each pair whose time windows overlap, without raising. |
| Recurring tasks | `Task.next_occurrence`, `Pet.complete_task` | Completing a "daily"/"weekly" task via `complete_task` marks it done and automatically creates+adds the next occurrence, with `due_date` advanced by a day or a week. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Add one or more pets under **Pets** by entering a name and species, then clicking **Add pet**.
2. Select a pet under **Tasks**, fill in the task title, category, duration, and priority, then click **Add task**. Repeat for as many tasks as you like; added tasks appear in a table below.
3. Click **Generate schedule** under **Build Schedule** to have the `Scheduler` sort the pet's tasks by priority, fit them into the owner's available time window, and order the result chronologically.
4. Review the schedule table (start time, duration, priority, and the reason each task was placed where it was), any conflict warnings, and any tasks that couldn't be scheduled due to insufficient time.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
