from datetime import datetime

import pytest

from app import create_app, db
from app.models import Appointment, Customer, Staff


@pytest.fixture
def app():
    """A new app with its own empty in-memory database for every test."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,  # the tests post forms directly, without a CSRF token
    })
    with app.app_context():  # db.session only works inside an app context
        db.create_all()
        yield app  # the test runs here, still inside the app context


@pytest.fixture
def client(app):
    """A fake browser for making requests like client.get("/customers/")."""
    return app.test_client()


@pytest.fixture
def customer(app):  # asking for `app` first makes sure the database exists
    customer = Customer(
        first_name="Jane", last_name="Doe", phone_number="07700 900123",
        address_line1="1 High Street", city="Leeds", postcode="LS1 1AA",
    )  # onboarding_status is left out, so it gets the default "New Enquiry"
    db.session.add(customer)
    db.session.commit()
    return customer


@pytest.fixture
def staff_member(app):
    staff_member = Staff(
        first_name="Sam", last_name="Smith", phone_number="07700 900456", role="Fitter",
    )
    db.session.add(staff_member)
    db.session.commit()
    return staff_member


@pytest.fixture
def appointment(customer, staff_member):
    """A Scheduled appointment, 10:00-11:00 on 1 January 2030 (far in the future)."""
    appointment = Appointment(
        customer_id=customer.id, staff_id=staff_member.id,
        start_at=datetime(2030, 1, 1, 10, 0), end_at=datetime(2030, 1, 1, 11, 0),
    )  # status is left out, so it gets the default "Scheduled"
    db.session.add(appointment)
    db.session.commit()
    return appointment
