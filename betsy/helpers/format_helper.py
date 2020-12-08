def price_display(price, default=None):
    return f'${price / 100:.2f}' if price is not None else default

def cc_display(cc_num, default=None):
    return f'**** **** **** {cc_num.strip()[-4:]}' if cc_num is not None else default

def date_display(date, default=None):
    return f'{date:%Y-%m-%d}' if date else default

def register_format_helpers(app):
    def format_helpers():
        return dict(
            price_display=price_display,
            date_display=date_display,
            cc_display=cc_display
            )

    app.context_processor(format_helpers)
