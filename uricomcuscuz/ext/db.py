from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand


db = SQLAlchemy()
migrate = Migrate()


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db, directory=app.config['MIGRATIONS_DIR'])
