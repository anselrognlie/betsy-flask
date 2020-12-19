import pytest

from betsy.errors.validation_error import ValidationError
from betsy.models.validations.required_if_validator import RequiredIfValidator

class Fields: pass  # pylint: disable=multiple-statements

#pylint: disable=attribute-defined-outside-init
class TestValidation:
    def test_check_required_valid(self):
        record = Fields()
        record.name = 'name'
        record.dependency = 'set'
        validator = RequiredIfValidator('name', check=lambda inst:inst.dependency == 'set')
        validator(record)

    def test_check_required_invalid(self):
        record = Fields()
        record.dependency = 'set'
        validator = RequiredIfValidator('name', check=lambda inst:inst.dependency == 'set')

        with pytest.raises(ValidationError):
            validator(record)

    def test_check_not_required_valid(self):
        record = Fields()
        record.name = 'name'
        record.dependency = 'notset'
        validator = RequiredIfValidator('name', check=lambda inst:inst.dependency == 'set')
        validator(record)

    def test_check_not_required_invalid(self):
        record = Fields()
        record.dependency = 'notset'
        validator = RequiredIfValidator('name', check=lambda inst:inst.dependency == 'set')
        validator(record)
