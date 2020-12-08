from datetime import datetime

from betsy.helpers.format_helper import *  # pylint: disable=unused-wildcard-import, wildcard-import

def test_display_empty_price():
    price = None
    result = price_display(price)
    assert result is None

def test_display_price():
    price = 1000
    result = price_display(price)
    assert result == '$10.00'

def test_display_empty_cc_num():
    cc_num = None
    result = cc_display(cc_num)
    assert result is None

def test_display_cc_num():
    cc_num = '1000200030004000'
    result = cc_display(cc_num)
    assert result == '**** **** **** 4000'

def test_display_empty_date():
    date = None
    result = date_display(date)
    assert result is None

def test_display_date():
    date = datetime(2000, 2, 1)
    result = date_display(date)
    assert result == '2000-02-01'
