""""URI com cuscuz."""

from setuptools import setup

requires = [
    'aiohttp>=3.5.4',
    'beautifulsoup4>=4.7.1',
    'coverage>=5.3',
    'Flask>=1.0.3',
    'Flask-SQLAlchemy>=2.4.0',
    'Flask-Migrate>=2.5.2',
    'gunicorn>=19.9.0',
    'psycopg2-binary>=2.8.5',
    'pytest>=5.3.0',
    'python-dotenv>=0.12.0',
]


setup(
    name='Uri com cuscuz',
    version='0.3',
    long_description=__doc__,
    packages=['uricomcuscuz'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
