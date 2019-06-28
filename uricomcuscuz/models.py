from .uricomcuscuz import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    submissions = db.relationship('Submission', 
        backref=db.back_ref('user'), lazy=True)

    
class Submission(db.Model):

    id = id.Column(db.Integer, primary_key=True)
    user_id = id.Column(db.Integer, db.ForeignKey('user.id'), 
        nullable=False)
    problem_id = id.Column(db.Integer, db.ForeignKey('problem.id'), 
        nullable=False)
    language = db.Column(db.String(), nullable=False)
    ranking = id.Column(db.Integer, nullable=False)
    exec_time = id.Column(db.Float, nullable=False)
    date = id.Column(db.DateTime, nullable=False)


class Problem(db):

    id = id.Column(db.Integer, primary_key=True)
    name = id.Column(db.String(), nullable=False)
    submissions = db.relationship('Submission', 
        backref=db.back_ref('problem'), lazy=True)
