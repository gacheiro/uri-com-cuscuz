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
