import pytest
from wtforms.validators import ValidationError

from betsy.forms.validators.not_empty_string import NotEmptyString

class Field: pass

def test_rejects_empty_string():
    validator = NotEmptyString()
    field = Field()
    field.data = ''  # pylint: disable=attribute-defined-outside-init

    with pytest.raises(ValidationError) as exc:
        validator(None, field)

    assert str(exc.value) == 'field must not be empty'

def test_validates_not_empty_string():
    validator = NotEmptyString()
    field = Field()
    field.data = 'data'  # pylint: disable=attribute-defined-outside-init

    validator(None, field)
