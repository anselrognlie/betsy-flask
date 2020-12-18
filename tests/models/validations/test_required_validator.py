import pytest

from betsy.errors.validation_error import ValidationError
from betsy.models.category import Category
from betsy.models.validations.required_validator import RequiredValidator

class TestValidation:
    def test_valid_no_trim(self):
        category = Category(name='name')
        validator = RequiredValidator('name', trim=False)
        validator(category)

    def test_invalid_no_trim(self):
        category = Category(name='')
        validator = RequiredValidator('name', trim=False)

        with pytest.raises(ValidationError):
            validator(category)

    def test_invalid_with_trim(self):
        category = Category(name='       ')
        validator = RequiredValidator('name')

        with pytest.raises(ValidationError):
            validator(category)
