from . import db
from .models import Appointment
from .statuses import SCHEDULED


def find_clash(staff_id, start_at, end_at, exclude_id=None):
    """Return the first Scheduled appointment that overlaps this time for this staff member, or None."""
    query = db.select(Appointment).where(
        Appointment.staff_id == staff_id,
        Appointment.status == SCHEDULED,  # cancelled and completed ones don't block the diary
        Appointment.start_at < end_at,    # it starts before the new one ends...
        Appointment.end_at > start_at,    # ...and ends after the new one starts
    )
    if exclude_id is not None:
        query = query.where(Appointment.id != exclude_id)  # so an appointment can't clash with itself
    return db.session.scalars(query.order_by(Appointment.start_at)).first()
