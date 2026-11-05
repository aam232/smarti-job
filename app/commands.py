from datetime import datetime, timedelta

import click
from flask.cli import with_appcontext

from . import db
from .models import Appointment, Customer, Job, Staff


@click.command("seed")
@with_appcontext  # gives us an app context so db works outside a web request
def seed():
    """Reset the database and fill it with demo data."""
    db.drop_all()
    db.create_all()

    # Fake data: 07700 900xxx numbers and example.com emails are reserved for examples.
    customers = [
        Customer(
            first_name="Priya", last_name="Sharma", phone_number="07700 900123",
            email="priya.sharma@example.com",
            address_line1="14 Maple Road", city="Leeds", postcode="LS6 2AB",
            onboarding_status="Active",
        ),
        Customer(
            first_name="Tom", last_name="Henderson", phone_number="07700 900456",
            address_line1="22 Harbour Street", address_line2="Flat 3",
            city="Bristol", postcode="BS1 4QA",
            onboarding_status="In Progress",
        ),
        Customer(
            first_name="Aisha", last_name="Khan", phone_number="07700 900789",
            email="aisha.khan@example.com",
            address_line1="5 Orchard Close", city="Manchester", postcode="M20 3JN",
            onboarding_status="New Enquiry",
        ),
        Customer(
            first_name="Graham", last_name="Wilson", phone_number="07700 900321",
            address_line1="41 Station Lane", city="Birmingham", postcode="B15 2TT",
            onboarding_status="Cancelled",
        ),
    ]
    priya, tom, aisha, _ = customers  # the 4th (cancelled) customer has no jobs yet

    staff = [
        Staff(first_name="Daniel", last_name="Cooper", phone_number="07700 900111",
              email="daniel.cooper@example.com", role="Fitter"),
        Staff(first_name="Sarah", last_name="Patel", phone_number="07700 900222",
              email="sarah.patel@example.com", role="Fitter"),
        Staff(first_name="Mark", last_name="Evans", phone_number="07700 900333",
              email="mark.evans@example.com", role="Maintenance Engineer"),
    ]
    daniel, sarah, mark = staff

    # Assigning a list to job.staff creates the rows in the job_staff table for us.
    jobs = [
        Job(
            customer=priya, title="Install water-saving taps",
            description="Replace the kitchen and bathroom taps with low-flow aerated taps.",
            location_line1="14 Maple Road", location_city="Leeds", location_postcode="LS6 2AB",
            status="In Progress", staff=[daniel, sarah],
        ),
        Job(
            customer=tom, title="Inspect AMR meter",
            description="Check the automatic meter reading unit is transmitting and log the reading.",
            location_line1="22 Harbour Street", location_line2="Flat 3",
            location_city="Bristol", location_postcode="BS1 4QA",
            status="Pending", staff=[mark],
        ),
    ]
    tap_job, meter_job = jobs

    # Times are relative to now so the demo always has a past and upcoming appointments.
    nine_today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    past_start = nine_today - timedelta(days=2)
    soon_start = nine_today + timedelta(days=1)
    later_start = nine_today + timedelta(days=3, hours=4)  # 13:00

    appointments = [
        Appointment(
            customer=priya, staff=daniel, job=tap_job,
            start_at=past_start, end_at=past_start + timedelta(hours=2),
            status="Completed",
        ),
        Appointment(
            customer=tom, staff=mark, job=meter_job,
            start_at=soon_start, end_at=soon_start + timedelta(hours=1),
            status="Scheduled",
        ),
        # No job yet: a site survey for a new enquiry.
        Appointment(
            customer=aisha, staff=sarah, job=None,
            start_at=later_start, end_at=later_start + timedelta(hours=1),
            status="Scheduled",
        ),
    ]

    db.session.add_all(customers + staff + jobs + appointments)
    db.session.commit()

    click.echo(
        f"Seeded {len(customers)} customers, {len(staff)} staff, "
        f"{len(jobs)} jobs and {len(appointments)} appointments."
    )
