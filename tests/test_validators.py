from wtforms import Form, StringField

from app.validators import uk_phone, uk_postcode


# Tiny forms with one field each, so the validators run the same way they do in the app.
class PostcodeForm(Form):
    postcode = StringField(validators=[uk_postcode])


class PhoneForm(Form):
    phone = StringField(validators=[uk_phone])


def test_valid_postcodes_are_accepted():
    for postcode in ["SW1A 1AA", "M1 1AE", "B15 2TT"]:
        form = PostcodeForm(data={"postcode": postcode})

        assert form.validate()


def test_postcode_is_tidied_to_capitals_with_one_space():
    form = PostcodeForm(data={"postcode": "ls6 2ab"})

    assert form.validate()
    assert form.postcode.data == "LS6 2AB"


def test_invalid_postcodes_are_rejected_with_a_message():
    for postcode in ["ABC 123", "12345", "SW1A"]:
        form = PostcodeForm(data={"postcode": postcode})

        assert not form.validate()
        assert "Enter a valid UK postcode" in form.postcode.errors[0]


def test_valid_phone_numbers_are_accepted():
    for phone in ["07700 900123", "+44 7700 900123"]:
        form = PhoneForm(data={"phone": phone})

        assert form.validate()


def test_invalid_phone_numbers_are_rejected_with_a_message():
    for phone in ["12345", "abc", "07700-900123"]:
        form = PhoneForm(data={"phone": phone})

        assert not form.validate()
        assert "Enter a valid UK phone number" in form.phone.errors[0]
