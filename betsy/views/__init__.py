# pylint: disable=missing-module-docstring
from betsy.views import (
    merchant, product, page, auth, category, product_category, review, order, order_item
)

def register_blueprints(app):
    # apply the blueprints to the app
    app.register_blueprint(page.bp)
    app.register_blueprint(merchant.bp)
    app.register_blueprint(product.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(category.bp)
    app.register_blueprint(product_category.bp)
    app.register_blueprint(review.bp)
    app.register_blueprint(order.bp)
    app.register_blueprint(order_item.bp)
