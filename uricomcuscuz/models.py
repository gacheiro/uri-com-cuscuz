from uricomcuscuz.ext.db import db
from uricomcuscuz.ext.uri import profile_url, problem_url


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    submissions = db.relationship('Submission',
                                  backref=db.backref('user'),
                                  order_by='Submission.date.desc()',
                                  lazy=True)

    @property
    def link(self):
        return profile_url(self.id)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'),
                           nullable=False)
    language = db.Column(db.String(), nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    exec_time = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def query_by(category=''):
        """Retorna uma query com as submissões filtradas pela categoria.
           Se a categoria não for especificada, retorna todos as submissões.

           A query retornada é ordernada pela data de forma descendente.
        """
        if category:
            query = (db.session.query(Submission)
                     .join(Problem)
                     .filter(Problem.category.ilike('%' + category + '%')))
        else:
            query = Submission.query
        query = query.order_by(Submission.date.desc())
        return query


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    submissions = db.relationship('Submission',
                                  backref=db.backref('problem'),
                                  order_by='Submission.date.desc()',
                                  lazy=True)

    @property
    def link(self):
        return problem_url(self.id)
