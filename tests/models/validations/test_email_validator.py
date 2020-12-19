import pytest

from betsy.errors.validation_error import ValidationError
from betsy.models.validations.email_validator import EmailValidator

class Fields: pass  # pylint: disable=multiple-statements

#pylint: disable=attribute-defined-outside-init
class TestValidation:
    def test_valid_no_trim(self):
        record = Fields()
        record.email = 'address@domain.com'
        validator = EmailValidator('email', trim=False)
        validator(record)

    def test_invalid_no_trim(self):
        record = Fields()
        record.email = 'invalid'
        validator = EmailValidator('email', trim=False)

        with pytest.raises(ValidationError):
            validator(record)

    def test_valid_with_trim(self):
        record = Fields()
        record.email = '   address@domain.com    '
        validator = EmailValidator('email')
        validator(record)

    def test_invalid_with_trim(self):
        record = Fields()
        record.email = '   invalid    '
        validator = EmailValidator('email')

        with pytest.raises(ValidationError):
            validator(record)

    def test_valid_with_allow_empty(self):
        record = Fields()
        record.email = ''
        validator = EmailValidator('email', allow_empty=True)
        validator(record)
