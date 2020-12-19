import pytest

from betsy.errors.validation_error import ValidationError
from betsy.models.validations.range_validator import RangeValidator

class Fields: pass  # pylint: disable=multiple-statements

#pylint: disable=attribute-defined-outside-init
class TestValidation:
    def test_valid(self):
        record = Fields()
        record.value = 3
        validator = RangeValidator('value', 1, 5)
        validator(record)

    def test_required_args(self):
        with pytest.raises(ValueError):
            RangeValidator('value')

    def test_invalid_below(self):
        record = Fields()
        record.value = 0
        validator = RangeValidator('value', 1, 5)

        with pytest.raises(ValidationError):
            validator(record)

    def test_invalid_above(self):
        record = Fields()
        record.value = 6
        validator = RangeValidator('value', 1, 5)

        with pytest.raises(ValidationError):
            validator(record)

    def test_valid_lower_bound(self):
        record = Fields()
        record.value = 1
        validator = RangeValidator('value', 1, 5)
        validator(record)

    def test_valid_upper_bound(self):
        record = Fields()
        record.value = 5
        validator = RangeValidator('value', 1, 5)
        validator(record)

    def test_invalid_none(self):
        record = Fields()
        record.value = None
        validator = RangeValidator('value', 1, 5)

        with pytest.raises(ValidationError):
            validator(record)

    def test_valid_no_upper(self):
        record = Fields()
        record.value = 3
        validator = RangeValidator('value', min_val=1)
        validator(record)

    def test_invalid_no_upper(self):
        record = Fields()
        record.value = 0
        validator = RangeValidator('value', min_val=1)

        with pytest.raises(ValidationError):
            validator(record)

    def test_valid_no_lower(self):
        record = Fields()
        record.value = 3
        validator = RangeValidator('value', max_val=5)
        validator(record)

    def test_invalid_no_lower(self):
        record = Fields()
        record.value = 7
        validator = RangeValidator('value', max_val=5)

        with pytest.raises(ValidationError):
            validator(record)
