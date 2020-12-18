import pytest

from betsy.errors.validation_error import ValidationError
from betsy.models.validations.required_validator import RequiredValidator

class Fields: pass  # pylint: disable=multiple-statements

#pylint: disable=attribute-defined-outside-init
class TestValidation:
    def test_valid_no_trim(self):
        record = Fields()
        record.name = 'name'
        validator = RequiredValidator('name', trim=False)
        validator(record)

    def test_invalid_no_trim(self):
        record = Fields()
        record.name = ''
        validator = RequiredValidator('name', trim=False)

        with pytest.raises(ValidationError):
            validator(record)

    def test_invalid_with_trim(self):
        record = Fields()
        record.name = '       '
        validator = RequiredValidator('name')

        with pytest.raises(ValidationError):
            validator(record)

    def test_none_as_invalid(self):
        record = Fields()
        record.name = None
        validator = RequiredValidator('name')

        with pytest.raises(ValidationError):
            validator(record)
