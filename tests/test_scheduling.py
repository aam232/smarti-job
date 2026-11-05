from datetime import datetime

from app import db
from app.models import Staff
from app.scheduling import find_clash

# The `appointment` fixture is booked 10:00-11:00 on 1 January 2030.


def test_overlapping_time_clashes(appointment):
    clash = find_clash(
        appointment.staff_id, datetime(2030, 1, 1, 10, 30), datetime(2030, 1, 1, 11, 30)
    )

    assert clash == appointment


def test_back_to_back_does_not_clash(appointment):
    # One starting at 11:00, exactly when the existing one ends...
    after = find_clash(
        appointment.staff_id, datetime(2030, 1, 1, 11, 0), datetime(2030, 1, 1, 12, 0)
    )
    # ...and one ending at 10:00, exactly when the existing one starts.
    before = find_clash(
        appointment.staff_id, datetime(2030, 1, 1, 9, 0), datetime(2030, 1, 1, 10, 0)
    )

    assert after is None
    assert before is None


def test_same_time_with_different_staff_does_not_clash(appointment):
    other_staff = Staff(
        first_name="Alex", last_name="Jones", phone_number="07700 900789", role="Fitter",
    )
    db.session.add(other_staff)
    db.session.commit()

    clash = find_clash(other_staff.id, datetime(2030, 1, 1, 10, 0), datetime(2030, 1, 1, 11, 0))

    assert clash is None


def test_cancelled_appointment_does_not_block_the_slot(appointment):
    appointment.status = "Cancelled"
    db.session.commit()

    clash = find_clash(
        appointment.staff_id, datetime(2030, 1, 1, 10, 0), datetime(2030, 1, 1, 11, 0)
    )

    assert clash is None


def test_exclude_id_stops_an_appointment_clashing_with_itself(appointment):
    clash = find_clash(
        appointment.staff_id, datetime(2030, 1, 1, 10, 0), datetime(2030, 1, 1, 11, 0),
        exclude_id=appointment.id,
    )

    assert clash is None
