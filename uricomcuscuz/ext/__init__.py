def init_app(app):
    """Inicia e pluga as extensões ao app."""
    from .import db, cli
    for ext in (db, cli):
        ext.init_app(app)
