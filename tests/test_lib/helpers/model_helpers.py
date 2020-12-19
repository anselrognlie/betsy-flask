import datetime

from betsy.models.record import Record
from betsy.models.product import Product
from betsy.models.merchant import Merchant
from betsy.models.category import Category
from betsy.models.order import Order
from betsy.models.order_item import OrderItem
from betsy.models.order_status import OrderStatus
from betsy.models.review import Review

def make_category(session, uid):
    category = Category(
        name=f'category-{uid}'
    )

    session.add(category)
    session.commit()
    return category

def make_merchant(session, uid):
    merchant = Merchant(
        name=f'merchant-{uid}',
        email=f'email-{uid}@email.com',
        provider='sample',
        uid=str(uid)
    )

    session.add(merchant)
    session.commit()
    return merchant

def make_product_hash(uid):
    return dict(
        name=f'product-{uid}',
        description=f'description-{uid}',
        price=(int(uid) + 1) * 1000,
        photo_url=f'http://url.com/{uid}',
        stock=(int(uid) + 1) % 5,
        discontinued=False
    )

def make_product(session, uid, merchant=None):
    if merchant is None:
        merchant = make_merchant(session, uid)

    product = Product(
        **make_product_hash(uid),
        merchant=merchant
    )

    session.add(product)
    session.commit()
    return product

def make_review(session, uid, product=None):
    if product is None:
        product = make_product(session, uid)

    review = Review(
        rating=(int(uid) + 1) % 5,
        comment=f'comment: {(int(uid) + 1) % 5} stars',
        product=product
    )

    session.add(review)
    session.commit()
    return review

def make_order_hash(uid):
    return dict(
        email=f'email-{uid}@email.com',
        mailing_address=f'{uid} Main St, Anytown, USA 11111',
        cc_name=f'name on card {uid}',
        cc_number='1234 5678 9012 3456',
        cc_exp='01/2025',
        cc_cvv='123',
        cc_zipcode='11111'
    )

def make_checkout_kwargs(uid):
    return dict(
        **make_order_hash(uid),
        ordered_date=datetime.datetime(2020, 9, 1)
    )

def make_order_init_hash(uid):
    return dict(
        email=f'email-{uid}@email.com',
        mailing_address=f'{uid} Main St, Anytown, USA 11111',
        cc_name=f'name on card {uid}',
        cc_number='1234 5678 9012 3456',
        cc_exp='01/2025',
        cc_cvv='123',
        cc_zipcode='11111',
        ordered_date=datetime.datetime(2020, 9, 1),
        status=OrderStatus.PENDING.value
    )

def make_order(session, uid):
    order = Order(
        **make_order_init_hash(uid)
    )

    session.add(order)
    session.commit()
    return order

def add_order_product(session, order, product, quantity):
    item = OrderItem(
        order=order,
        product=product,
        quantity=quantity
    )

    if order.status in [OrderStatus.PAID.value, OrderStatus.COMPLETED.value]:
        item.purchase_price = product.price

    session.add(item)
    session.commit()
    return item

def add_product_category(session, product, category):
    product.categories.append(category)
    session.commit()

def make_revenue_summary(count, total):
    record = Record()
    record.count = count
    record.total = total

    return record

def make_order_with_status(session, uid):
    statuses = OrderStatus.all()
    order_hash = make_order_init_hash(uid)
    order_hash['status'] = statuses[int(uid) % len(statuses)]
    order = Order(**order_hash)

    session.add(order)
    session.commit()
    return order
