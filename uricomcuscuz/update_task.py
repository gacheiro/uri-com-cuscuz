"""This task is called by the Heroku scheduler add-on"""

import os
import asyncio

from .uricomcuscuz import User, Problem, Submission, db
from .scraping import fetch_all, parse_date


def update_latest_solutions():
    '''Faz a raspagem de dados no site do URI e atualiza o bd.'''

    print('Updating solutions...')
    total_pages = int(os.environ['TOTAL_PAGES'])
    users, user_submissions = asyncio.run(fetch_all(total_pages))

    for (user_id, user_name), submissions in zip(users, user_submissions):
        user = User(id=user_id, name=user_name)
        db.session.merge(user)

        for sub in submissions:
            (problem_id, 
            problem_name, 
            ranking, 
            submission_id,
            language, 
            exec_time, 
            date) = sub

            problem = Problem(id=problem_id, name=problem_name)
            submission = Submission(
                id=submission_id,
                user_id=user_id,
                problem_id=problem_id,
                language=language,
                ranking=ranking[:-1], # remove o º do final
                exec_time=exec_time,
                date=parse_date(date)
            )
            db.session.merge(problem)
            db.session.merge(submission)
            
    db.session.commit()
    print('done.')


if __name__ == '__main__':
    update_latest_solutions()
