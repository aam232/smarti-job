from app.statuses import (
    APPOINTMENT_ALLOWED, APPOINTMENT_STATUSES, JOB_ALLOWED, ONBOARDING_ALLOWED, can_transition,
)


def test_onboarding_follows_the_allowed_moves():
    assert can_transition(ONBOARDING_ALLOWED, "New Enquiry", "In Progress")  # allowed
    assert not can_transition(ONBOARDING_ALLOWED, "New Enquiry", "Active")  # can't skip a step


def test_job_follows_the_allowed_moves():
    assert can_transition(JOB_ALLOWED, "Pending", "In Progress")  # allowed
    assert not can_transition(JOB_ALLOWED, "Pending", "Completed")  # can't skip a step


def test_completed_and_cancelled_appointments_are_final():
    for final_status in ["Completed", "Cancelled"]:
        for new_status in APPOINTMENT_STATUSES:
            assert not can_transition(APPOINTMENT_ALLOWED, final_status, new_status)
