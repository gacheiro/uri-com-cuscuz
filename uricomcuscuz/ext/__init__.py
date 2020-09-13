def init_app(app):
    """Inicia e pluga as extensões ao app."""
    from .import db, uri
    for ext in (db, uri):
        ext.init_app(app)
