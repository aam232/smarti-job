from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired, Email, Optional

from .validators import uk_phone, uk_postcode


def clean(value):
    """Filter: trim spaces, and turn blank into None so optional columns store NULL, not ''."""
    if value is None:
        return None
    return value.strip() or None


class CustomerForm(FlaskForm):
    # onboarding_status is deliberately not here: it only changes via OnboardingStatusForm.
    first_name = StringField("First name", filters=[clean], validators=[DataRequired()])
    last_name = StringField("Last name", filters=[clean], validators=[DataRequired()])
    phone_number = StringField("Phone number", filters=[clean], validators=[DataRequired(), uk_phone])
    email = StringField(
        "Email (optional)", filters=[clean],
        validators=[Optional(), Email(message="Enter a valid email address.")],
    )
    address_line1 = StringField("Address line 1", filters=[clean], validators=[DataRequired()])
    address_line2 = StringField("Address line 2 (optional)", filters=[clean])
    city = StringField("City", filters=[clean], validators=[DataRequired()])
    postcode = StringField("Postcode", filters=[clean], validators=[DataRequired(), uk_postcode])


class OnboardingStatusForm(FlaskForm):
    # The choices depend on the customer's current status, so each route sets them.
    status = SelectField("Change status to")
