import os
import asyncio
import datetime
from itertools import chain

import aiohttp
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://www.urionlinejudge.com.br'
UNIVERSITY_URL = BASE_URL + f"/judge/pt/users/university/{os.environ['UNIVERSITY']}"
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
    for index in range(1, total_pages + 1):
        yield UNIVERSITY_URL + f'?page={index}'


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


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


async def fetch_users(session, page):
    """Retorna os usuários na página da universidade."""
    print(f'get {page}')
    html = await fetch(session, page)
    soup = BeautifulSoup(html, 'html.parser')
    return parse_users(soup)


# TODO: o uri retorna as datas com 3h a frente do horário local
#       talvez fazer alguma transformação com o campo date
async def fetch_latest_solutions(session, id):
    """Retorna até 30 soluções mais recentes do usuário."""
    html = await fetch(session, profile_url(id))
    soup = BeautifulSoup(html, 'html.parser')
    return parse_solutions(soup)


async def fetch_all(total_pages):
    async with aiohttp.ClientSession(headers=HEADERS) as session:

        # Pega todos os estudantes que estão na universidade
        users_by_page = await asyncio.gather(
            *(fetch_users(session, p) for p in university_pages(total_pages))
        )
        all_users = list(chain.from_iterable(users_by_page))

        # Pega as últimas soluções de cada estudante
        solutions = await asyncio.gather(
            *(fetch_latest_solutions(session, id) for id, name in all_users)
        )

        return all_users, solutions
