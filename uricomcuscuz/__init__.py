import os

from flask import Flask, render_template, request, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

# Configura as extensões do app: cli e filtros de template
# customizados
import uricomcuscuz.ext.cli as cli
import uricomcuscuz.ext.template_filters as filters

cli.init_app(app)
filters.init_app(app)

from uricomcuscuz.models import User, Submission, Problem


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = Submission.query.order_by(Submission.date.desc())
    pagination = query.paginate(page, app.config['SUBS_PER_PAGE'], 
                                error_out=False)
    return render_template('index.html', pagination=pagination)


@app.route('/users/<id>')
def users(id):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(id)
    query = Submission.query.filter_by(user_id=id) \
            .order_by(Submission.date.desc())
    pagination = query.paginate(page, app.config['SUBS_PER_PAGE'],
                                error_out=False)
    return render_template('user.html',
                           user=user,
                           pagination=pagination)


@app.route('/problems/<id>')
def problems(id):
    page = request.args.get('page', 1, type=int)
    problem = Problem.query.get_or_404(id)
    query = Submission.query.filter_by(problem_id=id) \
            .order_by(Submission.date.desc())
    pagination = query.paginate(page, app.config['SUBS_PER_PAGE'],
                                error_out=False)
    return render_template('problem.html',
                           problem=problem,
                           pagination=pagination)
