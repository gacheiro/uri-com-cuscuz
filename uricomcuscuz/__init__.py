import os
from flask import (Flask, Blueprint, render_template,
                   request, current_app)

from uricomcuscuz.models import User, Submission, Problem

bp = Blueprint('app', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = Submission.query.order_by(Submission.date.desc())
    pagination = query.paginate(page,
                                current_app.config['SUBS_PER_PAGE'],
                                error_out=False)
    return render_template('index.html', pagination=pagination)


@bp.route('/users/<id>')
def users(id):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(id)
    query = Submission.query.filter_by(user_id=id) \
            .order_by(Submission.date.desc())
    pagination = query.paginate(page,
                                current_app.config['SUBS_PER_PAGE'],
                                error_out=False)
    return render_template('user.html',
                           user=user,
                           pagination=pagination)


@bp.route('/problems/<id>')
def problems(id):
    page = request.args.get('page', 1, type=int)
    problem = Problem.query.get_or_404(id)
    query = Submission.query.filter_by(problem_id=id) \
            .order_by(Submission.date.desc())
    pagination = query.paginate(page,
                                current_app.config['SUBS_PER_PAGE'],
                                error_out=False)
    return render_template('problem.html',
                           problem=problem,
                           pagination=pagination)


def create_app(**config):
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    # Configura as extensões do app: db, cli, filtros de template
    # customizados, etc
    from uricomcuscuz.ext import init_app
    init_app(app)
    # Adiciona as rotas do app
    app.register_blueprint(bp)
    return app
