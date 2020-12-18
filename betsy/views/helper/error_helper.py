import flask

def flash_errors(errors):
    for error in errors:
        field = error.field
        if field:
            flask.flash(f'{error.field} {error.message}', 'error')
        else:
            flask.flash(f'{error.message}', 'error')
