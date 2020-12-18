import flask

from betsy.views.helper.error_helper import flash_errors
from betsy.errors.validation_error import ValidationError

from ..test_lib.mocks.simple_mocker import SimpleMocker
from ..test_lib.mocks.mock_attributes import MockAttributes

class MockFlash():
    def __init__(self):
        self.flashes = []

    def flash(self, message, category='missing'):
        self.flashes.append(dict(message=message, category=category))

def test_error_setting():
    mock = MockAttributes()
    mock_flash = MockFlash()

    mock.register(flask, 'flash', mock_flash.flash)

    errors = []
    errors.append(ValidationError(None, 'field', 'message'))
    errors.append(ValidationError(None, None, 'message'))

    with SimpleMocker([mock]):
        flash_errors(errors)

    assert len(mock_flash.flashes) == 2
    assert mock_flash.flashes[0]['message'] == 'field message'
    assert mock_flash.flashes[1]['message'] == 'message'
