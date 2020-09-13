"""Módulo de integração com o URI Online Judge.
   Utiliza o BeautifulSoup para parsear as páginas HTML do URI e extrair
   as informações.

   Exporta o comando `flask uri update` para atualizar o banco de dados com
   novas submissões dos estudantes.

   Uso:
        flask uri update
"""
import os
import asyncio
import datetime

import aiohttp
from bs4 import BeautifulSoup
import click
from dotenv import load_dotenv
from flask import current_app
from flask.cli import with_appcontext

load_dotenv()

BASE_URL = 'https://www.urionlinejudge.com.br'
UNIVERSITY = os.environ['UNIVERSITY']
UNIVERSITY_URL = f'{BASE_URL}/judge/pt/users/university/{UNIVERSITY}'
HEADERS = {
    'accept': 'text/html',
    'accept-language': 'pt-BR, pt',
    'user-agent': 'UricomCuscuz/1',
}


def profile_url(id):
    """Retorna uma url para o perfil do usuário."""
    return f'{BASE_URL}/judge/pt/profile/{id}?sort=Ranks.created&direction=desc'


def problem_url(id):
    """Retorna uma url para a página do problema."""
    return f'{BASE_URL}/judge/pt/problems/view/{id}'


def university_pages(total_pages):
    """Gera urls para as páginas da universidade (?page=1, ?page=2, ...)."""
    for index in range(1, total_pages + 1):
        yield UNIVERSITY_URL + f'?page={index}'


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetch_all(urls):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        return await asyncio.gather(
            *(fetch(session, url) for url in urls)
        )


def fetch_students(total_pages):
    """Retorna uma lista de tuplas (id, name) de estudantes na universidade."""
    loop = asyncio.get_event_loop()
    urls = university_pages(total_pages)
    pages = loop.run_until_complete(fetch_all(urls))
    for page in pages:
        soup = BeautifulSoup(page, 'html.parser')
        for user in _parse_student(soup):
            yield user


# TODO: o uri retorna as datas com 3h a frente do horário local
#       talvez fazer alguma transformação com o campo date
def fetch_submissions(user_ids):
    """Retorna [até] as 30 soluções mais recentes de cada estudante."""
    loop = asyncio.get_event_loop()
    urls = (profile_url(id) for id in user_ids)
    pages = loop.run_until_complete(fetch_all(urls))
    for page in pages:
        soup = BeautifulSoup(page, 'html.parser')
        yield _parse_submissions(soup)


def fetch_categories(problem_ids):
    """O nome e id do problema já são obtidos em `fetch_submissions`. Aqui
       obtemos somente a categoria do problema.
    """
    loop = asyncio.get_event_loop()
    urls = (problem_url(id) for id in problem_ids)
    pages = loop.run_until_complete(fetch_all(urls))
    for page in pages:
        soup = BeautifulSoup(page, 'html.parser')
        yield _parse_category(soup)


def _parse_student(soup):
    """Gera tuplas (id, nome) dos estudantes da universidade."""
    if soup.tbody is None:
        return
    for user in soup.tbody.find_all('tr'):
        # <a href="/judge/pt/profile/[id]"> Nome do Estudante </a>
        atag = user.find('a')
        try:
            # pega só o id no final  href="/judge/pt/profile/[id]"
            id = atag.get('href').split('/')[-1]
            name = atag.get_text()
            yield (id, name)
        except AttributeError:
            # lista de usuários acabou
            return


def _parse_submissions(soup):
    """Gera as submissões encontradas na página do perfil do usuário."""
    if soup.tbody is None:
        return
    for tr in soup.tbody.find_all('tr'):
        lines = tr.get_text().split('\n')
        # esse 'if l' no final remove as strings vazias '' que ficam
        sol = tuple(l.strip() for l in lines if l)
        if len(sol) == 7:
            yield sol


def parse_date(date, format='%d/%m/%Y %H:%M:%S'):
    return datetime.datetime.strptime(date, format)


def _parse_category(soup):
    """Retorna a categoria do problema retirado do HTML. Por exemplo:

       <div id="page-name-c" class="pn-c-1 tour-step-problem-menu">
         <h1>URI 1001</h1>
         <ul>
           <li>Iniciante</li>
           ...
         </ul>
    """
    div = soup.find(id='page-name-c')
    if div is not None:
        return str(div.ul.li.get_text()).lower()


@click.group()
def uri():
    """Integração com o Uri Online Judge."""
    pass


@uri.command()
@with_appcontext
def update():
    """Faz a raspagem de dados no site do URI e atualiza o bd."""
    from uricomcuscuz.models import db, User, Problem, Submission

    current_app.logger.info('updating database with latest data...')
    total_pages = int(current_app.config['UNIVERSITY_TOTAL_PAGES'])
    ###
    # https://github.com/aio-libs/aiohttp/issues/4324
    # https://github.com/Azure/azure-sdk-for-python/issues/9060
    loop = asyncio.get_event_loop()
    current_app.logger.info('updating users...')
    users = list(fetch_students(total_pages))
    for (id, name) in users:
        user = User(id=id, name=name)
        db.session.merge(user)

    current_app.logger.info('updating solutions...')
    user_ids = (id for id, name in users)
    submissions = fetch_submissions(user_ids)
    for (user_id, _), submissions in zip(users, submissions):
        for submission in submissions:
            (problem_id, problem_name,
             ranking, submission_id,
             language, exec_time, date) = submission
            problem = Problem(id=problem_id,
                              name=problem_name)
            submission = Submission(id=submission_id,
                                    user_id=user_id,
                                    problem_id=problem_id,
                                    language=language,
                                    ranking=ranking[:-1], # remove o º do final
                                    exec_time=exec_time,
                                    date=parse_date(date))
            db.session.merge(problem)
            db.session.merge(submission)
    db.session.commit()

    # Atualiza as categorias dos problemas
    current_app.logger.info('updating problem categories...')
    problems = Problem.query.filter_by(category=None).all()
    problem_ids = (p.id for p in problems)
    categories = fetch_categories(problem_ids)
    for problem, category in zip(problems, categories):
        problem.category = category
    db.session.add_all(problems)
    db.session.commit()
    current_app.logger.info('done.')


def init_app(app):
    """Registra o comando no flask cli."""
    app.cli.add_command(uri)
