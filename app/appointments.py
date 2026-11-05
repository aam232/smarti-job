from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .forms import (
    BLANK, AppointmentForm, AppointmentStatusForm, customer_choices, job_choices, staff_choices,
)
from .models import Appointment
from .statuses import (
    APPOINTMENT_ALLOWED, APPOINTMENT_STATUSES, CANCELLED, SCHEDULED, can_transition,
)

bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@bp.route("/")
def index():
    now = datetime.now()
    scheduled = db.select(Appointment).where(Appointment.status == SCHEDULED)

    # Scheduled but already over: nobody has marked them Completed or Cancelled yet.
    overdue = db.session.scalars(
        scheduled.where(Appointment.end_at < now).order_by(Appointment.start_at)
    ).all()
    upcoming = db.session.scalars(
        scheduled.where(Appointment.start_at >= now).order_by(Appointment.start_at)
    ).all()
    cancelled = db.session.scalars(
        db.select(Appointment)
        .where(Appointment.status == CANCELLED)
        .order_by(Appointment.start_at.desc())  # most recent first
    ).all()

    # Group the upcoming ones by day. The query is already in time order, so each
    # day's list stays in order too.
    days = {}
    for appointment in upcoming:
        days.setdefault(appointment.start_at.date(), []).append(appointment)

    # Every appointment with a form (overdue and upcoming) is Scheduled, so they all
    # get the same dropdown and one form object can be reused for every row.
    status_form = AppointmentStatusForm()
    allowed = APPOINTMENT_ALLOWED[SCHEDULED]
    status_form.status.choices = [(s, s) for s in APPOINTMENT_STATUSES if s in allowed]
    return render_template(
        "appointments/list.html",
        overdue=overdue, days=days, cancelled=cancelled, status_form=status_form,
    )


@bp.route("/new", methods=["GET", "POST"])
def new():
    # ?customer_id=3&job_id=5 pre-select those. On a POST the submitted values win.
    form = AppointmentForm(
        customer=request.args.get("customer_id", type=int),
        job=request.args.get("job_id", type=int),
    )
    form.customer.choices = customer_choices()
    form.staff.choices = [(BLANK, "Select a staff member")] + staff_choices()
    form.job.choices = job_choices()

    if form.validate_on_submit():
        appointment = Appointment(
            customer_id=form.customer.data,
            staff_id=form.staff.data,
            job_id=form.job.data or None,  # 0 means "No job", which is stored as NULL
            start_at=form.start_at(),
            end_at=form.end_at(),  # start + duration; the duration itself is not stored
        )  # status is not set here: the column default is "Scheduled"
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment booked.", "success")
        return redirect(url_for("appointments.index"))
    return render_template(
        "appointments/form.html", form=form, title="Book appointment",
        cancel_url=url_for("appointments.index"),
    )


@bp.route("/<int:appointment_id>/status", methods=["POST"])
def change_status(appointment_id):
    appointment = db.get_or_404(Appointment, appointment_id)
    form = AppointmentStatusForm()
    # The field only has to accept any real status. Whether the move is allowed
    # is decided by can_transition, not by what the dropdown showed.
    form.status.choices = [(s, s) for s in APPOINTMENT_STATUSES]

    if not form.validate_on_submit():
        flash("Invalid status change request.", "error")
    elif can_transition(APPOINTMENT_ALLOWED, appointment.status, form.status.data):
        appointment.status = form.status.data
        db.session.commit()
        flash(f"Appointment marked {appointment.status}.", "success")
    else:
        flash(
            f"Cannot change status from {appointment.status} to {form.status.data}.", "error",
        )
    return redirect(url_for("appointments.index"))
