from .uricomcuscuz import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    submissions = db.relationship('Submission', 
        backref=db.backref('user'), lazy=True)

    
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
    submissions = db.relationship('Submission', 
        backref=db.backref('problem'), lazy=True)
