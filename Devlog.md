# Development log — Smarti CRM & Job Management

A timestamped record of how the project was built: decisions, problems found, and how AI tools were used and checked. The README's section C summarises this log.

## Time summary

| Phase | When | Active time | Notes |
|---|---|---|---|
| Design (architecture + data model) | 5 Nov, 17:33–20:51 | ~1h 35m | Breaks 18:34–19:19 and 19:50–20:46. Decisions, assumptions and scope written down before any code |
| 1. Setup: models, seed, base template | 5 Nov, 20:51–21:24 | 33 min (budget 20) | Over budget: Python wasn't installed |
| 2. Customers + onboarding | 5 Nov, 21:24–21:45 | 21 min (budget 30) | |
| 3. Staff | 5 Nov, 21:45–21:57 | 12 min (budget 10) | |
| 4. Jobs + appointments | 5 Nov, 21:57–22:16 | ~19 min (budget 35) | Including the Appointments page rework |
| 5. Tests | 5 Nov, 22:16–22:26 | 10 min (budget 10) | 18 pytest tests |
| 6. Documentation | 7–8 Nov | ~30m | README drafted, then edited in my own words |
| **Total** | | **~3h 40m** | a little over the 3-hour guide. Build + tests: 1h 35m against a 2-hour budget |

## Log

### 5 November

**17:33–20:51 — Design** (breaks 18:34–19:19 and 19:50–20:46)
- Read the brief and marking scheme. Documentation (30%) and problem-solving and prioritisation (15%) carry heavy weight, and sophistication isn't marked, so I aimed for simple, explainable code with every decision written down.
- Stack: considered React with a Flask API, Next.js and Django. Chose Flask + Jinja + SQLAlchemy + SQLite: my main language, previous Flask experience, one app, easy to explain and change.
- Structure: one blueprint per feature plus an app factory, so tests can use an in-memory database.
- Data model: separate Job and Appointment tables. An appointment needs a customer, has an optional job, and has exactly one staff member. Job ↔ staff is many-to-many through `job_staff`. One Staff table with a `role` column.
- Revised my first schema draft:
  - added `customer_id` to Job
  - replaced `Job.staff_id` with the join table
  - dropped the Onboarding table in favour of a status column on Customer
  - removed staff address (GDPR data minimisation)
  - split addresses into line 1, line 2, city and postcode
  - stored appointment times as `start_at` and `end_at`
- Status lifecycles and transition maps for onboarding, jobs and appointments.
- Double-booking rule: strict overlap, same staff member, Scheduled appointments only.
- Forms with Flask-WTF (new to me). Database setup with `create_all` and a `flask seed` command.
- During design, Claude replaced my assumption that appointments happen at our office with "on site". I caught it and reverted it.
- Set a time budget of about two hours for the build and tests, and cut the scope to exactly what the brief asks. Cut: a separate onboarding page, search and filters, job editing, appointment rescheduling, and deletes. Staff editing was later put back in, because brief D says "maintain a basic list".

**20:51–20:59 — Block 1 generated with Claude Code, then reviewed before running**
- My prompt specified: requirements, `.gitignore`, the app factory, `statuses.py`, the models, `flask seed` and the base template.
- **Challenge:** the machine had no real Python, only the Microsoft Store placeholder.
- Kept the extra two-way relationships (`back_populates`).
- Accepted no database CHECK constraints; values are enforced in the app.
- **Found:** `can_transition` returns False for an unchanged status, which would break saving an edit form. Fixed by design: status changes only through a dedicated status form, and edit forms never include status.
- **Found:** the seed data called an appointment a "site survey", contradicting my office-appointment assumption. Renamed it to an office consultation.
- **Found:** a route defined inside `create_app()`. Moved it into its own `appointments` blueprint.
- **Found:** `requirements.txt` was unpinned. Pinned it with `pip freeze`.

**21:12–21:16 — Understanding the models**
- `models.py` holds the full schema, structure only. The data comes from `flask seed`.
- Onboarding is a column, not a table.
- The composite address is stored as separate columns, because relational tables can't nest columns. I considered SQLAlchemy `composite()` and didn't use it.

**21:16–21:24 — Python install; block 1 done**
- `python` and `py` weren't recognised. The VS Code Python extension isn't an interpreter. Installed Python 3.12 and restarted VS Code.
- Seed and run both worked, and every nav link loaded.

**21:28 — Reviewed `models.py`**
- It matched the design. Found:
  - SQLite doesn't enforce `String(n)` lengths, so I added matching `Length(max=n)` validators.
  - Default statuses were repeated as strings, so I moved them to constants.
  - SQLite doesn't enforce foreign keys by default. There's no delete feature, so this is a known limitation.

**21:24–21:45 — Block 2: customers + onboarding**
- Kept: the status POST accepts any real status and `can_transition` decides, so the server is the authority even if the dropdown is tampered with. Also kept: blank inputs stored as NULL, and `novalidate` so the server's messages show.
- Fixed: a KeyError for an unknown status.
- Manual tests (me): create; postcode validation, including `ls6 2ab` → `LS6 2AB`; phone, email and blank fields; status changes; edits; and a devtools tamper test. All passed.

**21:45–21:57 — Block 3: staff**
- Role dropdown defaulted to "Fitter", so I added a blank "Select a role" option and made it required.
- Job count changed to **open** jobs only.
- Accepted: one query per row (N+1, fine at this size), and duplicate error messages on long, invalid values.

**21:57 — Understood `find_clash`.** Same staff member, Scheduled only, strict overlap, `exclude_id`, and it returns the clashing appointment so the error message can name it. Known follow-ups: a race condition between two simultaneous bookings, and an index on `(staff_id, start_at)` as the data grows.

**21:57–22:16 — Block 4: jobs + appointments**
- Jobs with multi-select staff (at least one required) and status changes. Booking built from date, start time and duration into `start_at` and `end_at`. Past bookings blocked. The job must belong to the customer.
- `populate_obj` couldn't be used for jobs, because the form returns ids and the relationships need objects.
- **Found:** past appointments got stuck as Scheduled. Added an Overdue section.
- **Found:** the job dropdown listed finished jobs. Now open jobs only.
- **Found:** the "Book appointment" button appeared on closed jobs. Now hidden.
- **My change:** "Upcoming" became an **Appointments** page with Overdue, Upcoming and Cancelled sections. Cancelling is a status change, not a delete, so history is kept.
- **Found:** an in-progress appointment appeared in neither section, because Overdue used `end_at` and Upcoming used `start_at`. Both now use `end_at`.

**22:16–22:26 — Block 5: tests**
- 18 pytest tests covering scheduling, statuses, validators and routes, each with a fresh in-memory database.
- Claude Code checked the tests by deliberately breaking the app. That found that the back-to-back test only covered one side of the boundary, and the test was extended.

### 7–8 November — Documentation (~30m active)
- README drafted with Claude from my decisions and this log.
- Rewrote the technology and Staff-table reasons in my own words. Reorganised the technology table so each alternative has its own row with the reason I didn't choose it.
- Standardised the app name to **Smarti** (page titles, README, database file `instance/smarti.db`).
- Fixed the README's `SECRET_KEY` instruction to use PowerShell syntax.

## AI usage

| When | Tool | What it produced | How I verified it / what I changed |
|---|---|---|---|
| Design | Claude (chat) | Explained options and trade-offs; kept a decisions log | Made every decision myself; corrected it where it was wrong |
| Blocks 1–5 | Claude Code | Code written from my specifications | Read every file before running or committing; found and fixed the issues listed above; tested every feature by hand; ran pytest myself |
| Docs | Claude (chat) | README draft | Edited and rewrote the reasons in my own words |

## Known limitations

See README section C: the double-booking race condition, SQLite foreign keys and CHECK constraints, `novalidate`, the N+1 query on the staff list, duplicate error messages, tests sharing one database session, and the WTForms deprecation warning.