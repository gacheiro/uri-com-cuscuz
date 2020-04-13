def init_app(app):
    """Inicia e pluga as extensões ao app."""
    from .import db, cli, jinja
    for ext in (db, cli, jinja):
        ext.init_app(app)
