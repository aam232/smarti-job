import re

from wtforms.validators import ValidationError

# Outward code (e.g. SW1A, M1, EC1A) then inward code (digit + 2 letters),
# matched with the space removed.
POSTCODE_PATTERN = re.compile(r"[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][A-Z]{2}")

# Optional leading +, then 10-13 digits (spaces are removed before matching).
PHONE_PATTERN = re.compile(r"\+?[0-9]{10,13}")


# A WTForms validator is any function that takes (form, field) and raises
# ValidationError if the value is bad.
def uk_postcode(form, field):
    """Check a UK postcode and rewrite it as 'OUTWARD INWARD', e.g. 'sw1a1aa' -> 'SW1A 1AA'."""
    compact = re.sub(r"\s", "", field.data or "").upper()
    if not POSTCODE_PATTERN.fullmatch(compact):
        raise ValidationError("Enter a valid UK postcode, for example SW1A 1AA.")
    # The inward code is always the last 3 characters
    field.data = f"{compact[:-3]} {compact[-3:]}"


def uk_phone(form, field):
    """Check a phone number is digits and spaces with an optional leading +, 10-13 digits."""
    compact = (field.data or "").replace(" ", "")
    if not PHONE_PATTERN.fullmatch(compact):
        raise ValidationError(
            "Enter a valid UK phone number, for example 07700 900123 or +44 7700 900123."
        )
