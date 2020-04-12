from datetime import datetime

def same_day(datea, dateb):
    return datea.date() == dateb.date()


def month_name(month):
    return {
        1: 'Jan',
        2: 'Fev',
        3: 'Mar',
        4: 'Abr',
        5: 'Mai',
        6: 'Jun',
        7: 'Jul',
        8: 'Ago',
        9: 'Set',
        10: 'Out',
        11: 'Nov',
        12: 'Dez',
    }[month]


def init_app(app):
    """Adiciona os filtros de templates ao app."""

    @app.template_filter('format_date')
    def format_date(date, now=None):
        if now is None:
            now = datetime.now()
        if same_day(date, now):
            return f'{date.hour}:{date.minute:02d}'
        return f'{date.day} {month_name(date.month)}'
