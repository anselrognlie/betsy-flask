from flask import flash

def flash_errors(errors):
    for error in errors:
        field = error.field
        if field:
            flash(f'{error.field} {error.message}', 'error')
        else:
            flash(f'{error.message}', 'error')
