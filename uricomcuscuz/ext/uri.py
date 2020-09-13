"""Módulo de integração com o URI Online Judge.
   Utiliza o BeautifulSoup para parsear as páginas HTML do URI e extrair
   as informações.

   Exporta o comando `fetch-subs` para atualizar o banco de dados com novas
   soluções dos estudantes.

   Uso:
        flask uri update
"""
import os
import asyncio
import datetime
from itertools import chain

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


@click.group()
def uri():
    """Integração com o Uri Online Judge."""
    pass


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


async def _fetch_students(session, page):
    """Retorna os estudantes na página da universidade."""
    current_app.logger.info(f'get {page}')
    html = await fetch(session, page)
    soup = BeautifulSoup(html, 'html.parser')
    return parse_users(soup)


# TODO: o uri retorna as datas com 3h a frente do horário local
#       talvez fazer alguma transformação com o campo date
async def _fetch_latest_solutions(session, user_id):
    """Retorna [até] as 30 soluções mais recentes do estudante."""
    html = await fetch(session, profile_url(user_id))
    soup = BeautifulSoup(html, 'html.parser')
    return parse_solutions(soup)


def parse_users(soup):
    """Gera tuplas (id, nome) dos usuários na página da universidade."""
    if soup.tbody is None:
        return
    for user in soup.tbody.find_all('tr'):
        # <a href="/judge/pt/profile/[id]"> Nome do Estudante </a>
        atag = user.find('a')
        try:
            # pega só o id no final  href="/judge/pt/profile/[id]"
            id = atag.get('href').split('/')[-1]
            name = atag.get_text()
            yield id, name
        except AttributeError:
            # lista de usuários acabou
            return


def parse_solutions(soup):
    """Gera as soluções encontradas na página do perfil do usuário."""
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


def parse_category(soup):
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


async def _fetch_all(total_pages):
    """Retorna dados dos estudantes na universidade e as suas últimas soluções.
       O tipo de retorno é uma tupla (estudantes, solucoes).
    """
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # Pega todos os estudantes que estão na universidade
        # students_by_page é uma lista de lista de estudantes
        students_by_page = await asyncio.gather(
            *(_fetch_students(session, p) for p in university_pages(total_pages))
        )
        # Combina todos os estudantes em uma única lista (flat map)
        students = list(chain.from_iterable(students_by_page))
        # Pega as últimas soluções de cada estudante
        solutions = await asyncio.gather(
            *(_fetch_latest_solutions(session, id) for id, name in students)
        )
        return students, solutions


@uri.command()
@with_appcontext
def update():
    """Faz a raspagem de dados no site do URI e atualiza o bd."""
    from uricomcuscuz.models import db, User, Problem, Submission

    current_app.logger.info('updating solutions...')
    total_pages = int(current_app.config['UNIVERSITY_TOTAL_PAGES'])
    ###
    # https://github.com/aio-libs/aiohttp/issues/4324
    # https://github.com/Azure/azure-sdk-for-python/issues/9060
    loop = asyncio.get_event_loop()
    users, user_submissions = loop.run_until_complete(_fetch_all(total_pages))
    ###
    for (user_id, user_name), submissions in zip(users, user_submissions):
        user = User(id=user_id, name=user_name)
        db.session.merge(user)
        for submission in submissions:
            (problem_id, problem_name,
             ranking, submission_id,
             language, exec_time, date) = submission
            problem = Problem(id=problem_id, name=problem_name)
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
    current_app.logger.info('done.')
    # Atualiza as categorias dos problemas
    # TODO: os dois comandos precisam ser refeitos em um só?
    update_categories()


def update_categories():
    """Atualiza a categoria dos problemas."""
    from uricomcuscuz.models import db, Problem

    async def _update():
        """Retorna as páginas dos problemas."""
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            return await asyncio.gather(
                *(fetch(session, p.link) for p in problems)
            )

    current_app.logger.info('updating problems categories...')
    problems = Problem.query.filter_by(category=None).all()
    loop = asyncio.get_event_loop()
    pages = loop.run_until_complete(_update())
    for problem, page in zip(problems, pages):
        problem.category = \
            parse_category(BeautifulSoup(page, 'html.parser'))
    db.session.add_all(problems)
    db.session.commit()
    current_app.logger.info('done.')


def init_app(app):
    """Registra o comando no flask cli."""
    app.cli.add_command(uri)
