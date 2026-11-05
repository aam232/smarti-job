from . import db
from .statuses import DEFAULT_APPOINTMENT_STATUS, DEFAULT_JOB_STATUS, DEFAULT_ONBOARDING_STATUS

# Association table for the many-to-many link between jobs and staff.
# The composite primary key (job_id + staff_id) stops the same person
# being added to the same job twice.
job_staff = db.Table(
    "job_staff",
    db.Column("job_id", db.Integer, db.ForeignKey("job.id"), primary_key=True),
    db.Column("staff_id", db.Integer, db.ForeignKey("staff.id"), primary_key=True),
)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)
    onboarding_status = db.Column(
        db.String(20), nullable=False, default=DEFAULT_ONBOARDING_STATUS
    )

    jobs = db.relationship("Job", back_populates="customer")
    appointments = db.relationship("Appointment", back_populates="customer")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Staff(db.Model):
    # Deliberately no address: we only store what we need (GDPR data minimisation).
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(30), nullable=False)  # one of statuses.ROLES, checked in the form

    jobs = db.relationship("Job", secondary=job_staff, back_populates="staff")
    appointments = db.relationship("Appointment", back_populates="staff")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # The job location can differ from the customer's own address.
    location_line1 = db.Column(db.String(100), nullable=False)
    location_line2 = db.Column(db.String(100), nullable=True)
    location_city = db.Column(db.String(50), nullable=False)
    location_postcode = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=DEFAULT_JOB_STATUS)

    customer = db.relationship("Customer", back_populates="jobs")
    staff = db.relationship("Staff", secondary=job_staff, back_populates="jobs")
    appointments = db.relationship("Appointment", back_populates="job")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    # Exactly one staff member per appointment.
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    # Nullable: an appointment (e.g. an office consultation) can happen before any job exists.
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=True)
    # Naive UK local time. No duration column: the form will compute end_at.
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=DEFAULT_APPOINTMENT_STATUS)

    customer = db.relationship("Customer", back_populates="appointments")
    staff = db.relationship("Staff", back_populates="appointments")
    job = db.relationship("Job", back_populates="appointments")
