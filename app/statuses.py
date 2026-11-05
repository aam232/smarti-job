ROLES = ["Fitter", "Maintenance Engineer"]

ONBOARDING_STATUSES = ["New Enquiry", "In Progress", "Active", "Cancelled"]
JOB_STATUSES = ["Pending", "In Progress", "Completed", "Cancelled"]
APPOINTMENT_STATUSES = ["Scheduled", "Completed", "Cancelled"]

# The first status in each list is the one new records start with.
DEFAULT_ONBOARDING_STATUS = ONBOARDING_STATUSES[0]
DEFAULT_JOB_STATUS = JOB_STATUSES[0]
DEFAULT_APPOINTMENT_STATUS = APPOINTMENT_STATUSES[0]

# Jobs in these statuses still have work to do (used for staff workload counts).
OPEN_JOB_STATUSES = ["Pending", "In Progress"]

# The appointment status that books up a staff member's diary and shows as upcoming.
SCHEDULED = "Scheduled"

# The appointment status that is final; these are only listed, read-only.
CANCELLED = "Cancelled"

# current status -> set of statuses it is allowed to move to
ONBOARDING_ALLOWED = {
    "New Enquiry": {"In Progress", "Cancelled"},
    "In Progress": {"Active", "Cancelled"},
    "Active": {"In Progress", "Cancelled"},
    "Cancelled": {"In Progress"},
}

JOB_ALLOWED = {
    "Pending": {"In Progress", "Cancelled"},
    "In Progress": {"Completed", "Cancelled"},
    "Completed": {"In Progress"},
    "Cancelled": {"Pending"},
}

APPOINTMENT_ALLOWED = {
    "Scheduled": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}


def can_transition(allowed_map, current, new):
    # Staying on the same status is not a transition, so it returns False.
    # Callers should check "new == current" themselves before calling this.
    return new in allowed_map.get(current, set())
