import pytest

from betsy.errors.validation_error import ValidationError
from betsy.models.category import Category
from betsy.models.validations.unique_validator import UniqueValidator

from ...test_lib.helpers.model_helpers import (
    make_category
)

class TestValidation:
    @pytest.fixture(autouse=True)
    def before(self, app, session):
        # pylint: disable=attribute-defined-outside-init
        self.app = app
        self.session = session

    def test_no_conflict_valid_no_trim(self):
        with self.app.app_context():
            category = Category(name='name')
            validator = UniqueValidator('name', trim=False)
            validator(category)

    def test_no_conflict_valid_with_trim(self):
        with self.app.app_context():
            category = Category(name='  name  ')
            validator = UniqueValidator('name')
            validator(category)

    def test_self_conflict_valid_no_trim(self):
        with self.app.app_context():
            category = make_category(self.session, 0)
            validator = UniqueValidator('name', trim=False)
            validator(category)

    def test_self_conflict_valid_with_trim(self):
        with self.app.app_context():
            category = make_category(self.session, 0)
            validator = UniqueValidator('name')
            validator(category)

    def test_conflict_valid_no_trim(self):
        with self.app.app_context():
            original = make_category(self.session, 0)
            category = Category(name=original.name)
            validator = UniqueValidator('name', trim=False)

            with pytest.raises(ValidationError):
                validator(category)

    def test_conflict_valid_with_trim(self):
        with self.app.app_context():
            original = make_category(self.session, 0)
            category = Category(name=f'  {original.name}  ')
            validator = UniqueValidator('name')

            with pytest.raises(ValidationError):
                validator(category)
