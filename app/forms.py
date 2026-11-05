from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional

from .statuses import ROLES
from .validators import uk_phone, uk_postcode

# Every Length(max=...) below matches the String(...) size of the same column in
# models.py, because SQLite does not enforce column lengths itself.


def clean(value):
    """Filter: trim spaces, and turn blank into None so optional columns store NULL, not ''."""
    if value is None:
        return None
    return value.strip() or None


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
    # SelectField checks the submitted value is one of the choices, so a role
    # that is not in ROLES is rejected even if someone edits the HTML.
    role = SelectField("Role", choices=ROLES, validators=[Length(max=30)])
