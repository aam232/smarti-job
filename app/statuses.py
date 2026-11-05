ROLES = ["Fitter", "Maintenance Engineer"]

ONBOARDING_STATUSES = ["New Enquiry", "In Progress", "Active", "Cancelled"]
JOB_STATUSES = ["Pending", "In Progress", "Completed", "Cancelled"]
APPOINTMENT_STATUSES = ["Scheduled", "Completed", "Cancelled"]

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
