from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import (
    DateField, SelectField, SelectMultipleField, StringField, TextAreaField, TimeField,
)
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError

from . import db
from .models import Customer, Job, Staff
from .scheduling import find_clash
from .statuses import ROLES
from .validators import uk_phone, uk_postcode

# Every Length(max=...) below matches the String(...) size of the same column in
# models.py, because SQLite does not enforce column lengths itself.

# Value of the first "Select a ..." / "No job" option in dropdowns that use coerce=int.
# 0 is never a real id, and DataRequired treats 0 as "nothing chosen".
BLANK = 0

DURATIONS = [30, 60, 90, 120]  # minutes


def clean(value):
    """Filter: trim spaces, and turn blank into None so optional columns store NULL, not ''."""
    if value is None:
        return None
    return value.strip() or None


def customer_choices():
    """Dropdown choices: a blank option, then every customer by name."""
    query = db.select(Customer).order_by(Customer.last_name, Customer.first_name)
    customers = db.session.scalars(query).all()
    return [(BLANK, "Select a customer")] + [(c.id, c.full_name) for c in customers]


def staff_choices():
    """Dropdown choices for every staff member, labelled 'Name (Role)'. No blank option."""
    query = db.select(Staff).order_by(Staff.last_name, Staff.first_name)
    return [(s.id, f"{s.full_name} ({s.role})") for s in db.session.scalars(query)]


def job_choices():
    """Dropdown choices: 'No job', then every job labelled 'Title - Customer'."""
    jobs = db.session.scalars(db.select(Job).order_by(Job.title)).all()
    return [(BLANK, "No job")] + [(j.id, f"{j.title} - {j.customer.full_name}") for j in jobs]


class CustomerForm(FlaskForm):
    # onboarding_status is deliberately not here: it only changes via OnboardingStatusForm.
    first_name = StringField(
        "First name", filters=[clean], validators=[DataRequired(), Length(max=50)]
    )
    last_name = StringField(
        "Last name", filters=[clean], validators=[DataRequired(), Length(max=50)]
    )
    phone_number = StringField(
        "Phone number", filters=[clean],
        validators=[DataRequired(), Length(max=20), uk_phone],
    )
    email = StringField(
        "Email (optional)", filters=[clean],
        validators=[Optional(), Email(message="Enter a valid email address."), Length(max=120)],
    )
    address_line1 = StringField(
        "Address line 1", filters=[clean], validators=[DataRequired(), Length(max=100)]
    )
    address_line2 = StringField(
        "Address line 2 (optional)", filters=[clean], validators=[Length(max=100)]
    )
    city = StringField("City", filters=[clean], validators=[DataRequired(), Length(max=50)])
    postcode = StringField(
        "Postcode", filters=[clean],
        validators=[DataRequired(), Length(max=10), uk_postcode],
    )


class OnboardingStatusForm(FlaskForm):
    # The choices depend on the customer's current status, so each route sets them.
    status = SelectField("Change status to")


class StaffForm(FlaskForm):
    first_name = StringField(
        "First name", filters=[clean], validators=[DataRequired(), Length(max=50)]
    )
    last_name = StringField(
        "Last name", filters=[clean], validators=[DataRequired(), Length(max=50)]
    )
    phone_number = StringField(
        "Phone number", filters=[clean],
        validators=[DataRequired(), Length(max=20), uk_phone],
    )
    email = StringField(
        "Email (optional)", filters=[clean],
        validators=[Optional(), Email(message="Enter a valid email address."), Length(max=120)],
    )
    # The blank first option has the value "", which DataRequired rejects, so the
    # role has to be chosen on purpose. SelectField also rejects any value that is
    # not one of the choices, even if someone edits the HTML.
    role = SelectField(
        "Role",
        choices=[("", "Select a role")] + [(role, role) for role in ROLES],
        validators=[DataRequired(message="Select a role."), Length(max=30)],
    )


class JobForm(FlaskForm):
    # The customer and staff choices are set in the route (they come from the database).
    customer = SelectField(
        "Customer", coerce=int, validators=[DataRequired(message="Select a customer.")]
    )
    title = StringField("Title", filters=[clean], validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description (optional)", filters=[clean])
    location_line1 = StringField(
        "Location address line 1", filters=[clean], validators=[DataRequired(), Length(max=100)]
    )
    location_line2 = StringField(
        "Location address line 2 (optional)", filters=[clean], validators=[Length(max=100)]
    )
    location_city = StringField(
        "Location city", filters=[clean], validators=[DataRequired(), Length(max=50)]
    )
    location_postcode = StringField(
        "Location postcode", filters=[clean],
        validators=[DataRequired(), Length(max=10), uk_postcode],
    )
    staff = SelectMultipleField("Assigned staff (hold Ctrl to pick several)", coerce=int)

    # WTForms runs any method called validate_<fieldname> as an extra check for that field.
    # With nothing ticked the browser sends no value at all, so we test the list directly.
    def validate_staff(self, field):
        if not field.data:
            raise ValidationError("Select at least one staff member.")


class JobStatusForm(FlaskForm):
    # Choices are set in the route, as for OnboardingStatusForm.
    status = SelectField("Change status to")


class AppointmentForm(FlaskForm):
    # The customer, staff and job choices are set in the route.
    customer = SelectField(
        "Customer", coerce=int, validators=[DataRequired(message="Select a customer.")]
    )
    staff = SelectField(
        "Staff member", coerce=int, validators=[DataRequired(message="Select a staff member.")]
    )
    job = SelectField("Job (optional)", coerce=int)
    date = DateField("Date", validators=[DataRequired(message="Enter a date.")])
    start_time = TimeField("Start time", validators=[DataRequired(message="Enter a start time.")])
    duration = SelectField(
        "Duration", coerce=int, default=60,
        choices=[(minutes, f"{minutes} minutes") for minutes in DURATIONS],
    )

    def start_at(self):
        return datetime.combine(self.date.data, self.start_time.data)

    def end_at(self):
        return self.start_at() + timedelta(minutes=self.duration.data)

    def validate(self, extra_validators=None):
        # First the normal per-field checks. The checks below need several fields
        # at once, so they only make sense once those pass.
        if not super().validate(extra_validators):
            return False

        if self.start_at() < datetime.now():
            self.start_time.errors.append("The start time is in the past.")

        job = db.session.get(Job, self.job.data) if self.job.data != BLANK else None
        if job is not None and job.customer_id != self.customer.data:
            self.job.errors.append("That job belongs to a different customer.")

        clash = find_clash(self.staff.data, self.start_at(), self.end_at())
        if clash:
            self.staff.errors.append(
                f"{clash.staff.full_name} is already booked "
                f"{clash.start_at.strftime('%H:%M')}–{clash.end_at.strftime('%H:%M')} "
                f"with {clash.customer.full_name}."
            )

        return not any(field.errors for field in (self.start_time, self.job, self.staff))


class AppointmentStatusForm(FlaskForm):
    # Choices are set in the route, as for OnboardingStatusForm.
    status = SelectField("Change status to")
