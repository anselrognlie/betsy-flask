from betsy.models.order_item import OrderItem
from betsy.storage.db import db
from sqlalchemy.exc import InvalidRequestError

def bad_create():
    try:
        item = OrderItem()
        db.session.add(item)
        db.session.commit()
    except InvalidRequestError as ex:
        print(type(ex).__name__)
        # pass

# bad_create()
