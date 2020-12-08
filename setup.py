'''
Basic task-list Ada assignment
'''

# import io

from setuptools import find_packages
from setuptools import setup

# with io.open("README.rst", "rt", encoding="utf8") as f:
#     readme = f.read()

setup(
    name="betsy",
    version="1.0.0",
    # url="http://flask.pocoo.org/docs/tutorial/",
    # license="BSD",
    # maintainer="Pallets team",
    # maintainer_email="contact@palletsprojects.com",
    description="bEtsy Ada assignment",
    # long_description=readme,
    long_description=__doc__,
    packages=find_packages(),
    # include_package_data=True,
    zip_safe=False,
    install_requires=["betsy", "sqlalchemy", "flask-sqlalchemy"],
    extras_require={"test": ["pytest", "coverage"]},
)
