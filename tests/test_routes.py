from datetime import datetime, timedelta

from app import db
from app.models import Appointment, Customer

VALID_CUSTOMER = {
    "first_name": "Jane", "last_name": "Doe", "phone_number": "07700 900123", "email": "",
    "address_line1": "1 High Street", "address_line2": "", "city": "Leeds",
    "postcode": "LS1 1AA",
}


def test_creating_a_customer_saves_it_and_redirects(client):
    response = client.post("/customers/new", data=VALID_CUSTOMER)

    customer = db.session.scalars(db.select(Customer)).one()  # exactly one customer saved
    assert customer.first_name == "Jane"
    assert customer.onboarding_status == "New Enquiry"
    assert response.status_code == 302
    assert response.headers["Location"] == f"/customers/{customer.id}"


def test_invalid_postcode_shows_an_error_and_saves_nothing(client):
    bad_data = dict(VALID_CUSTOMER, postcode="not a postcode")

    response = client.post("/customers/new", data=bad_data)

    assert response.status_code == 200  # the form is shown again, not a redirect
    assert "Enter a valid UK postcode" in response.get_data(as_text=True)
    assert db.session.scalars(db.select(Customer)).all() == []


def test_disallowed_status_change_is_rejected_and_status_is_unchanged(client, customer):
    # "New Enquiry" cannot go straight to "Active".
    response = client.post(
        f"/customers/{customer.id}/status", data={"status": "Active"}, follow_redirects=True
    )

    assert "Cannot change status from New Enquiry to Active." in response.get_data(as_text=True)
    assert customer.onboarding_status == "New Enquiry"


def test_booking_a_clashing_appointment_is_rejected(client, customer, staff_member, appointment):
    # Same staff member, 10:30-11:30, but the fixture appointment is 10:00-11:00.
    clashing_booking = {
        "customer": customer.id, "staff": staff_member.id, "job": 0,
        "date": "2030-01-01", "start_time": "10:30", "duration": 60,
    }

    response = client.post("/appointments/new", data=clashing_booking)

    assert response.status_code == 200
    assert "Sam Smith is already booked" in response.get_data(as_text=True)
    assert len(db.session.scalars(db.select(Appointment)).all()) == 1  # only the fixture one


def test_in_progress_appointment_is_upcoming_not_overdue(client, customer, staff_member):
    now = datetime.now()
    in_progress = Appointment(
        customer_id=customer.id, staff_id=staff_member.id,
        start_at=now - timedelta(minutes=30), end_at=now + timedelta(minutes=30),
    )
    db.session.add(in_progress)
    db.session.commit()

    page = client.get("/appointments/").get_data(as_text=True)

    assert "Overdue" not in page  # that section only appears when something is overdue
    assert "Jane Doe" in page.split("<h2>Upcoming</h2>")[1]  # the text after the Upcoming heading
