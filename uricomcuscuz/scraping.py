import asyncio
import datetime
from itertools import chain
from collections import namedtuple

import aiohttp
from bs4 import BeautifulSoup


BASE_URL = 'https://www.urionlinejudge.com.br'
UERN = BASE_URL + '/judge/pt/users/university/uern'


# user solution fields
_fields = [
    'user_name', 
    'user_id', 
    'user_url',
    'problem_id',
    'problem_name',
    'problem_url',
    'ranking',
    'submission_id',
    'language',
    'exec_time',
    'date',
]

UserSolution = namedtuple('UserSolution', _fields)


def profile_url(id):
    return f'{BASE_URL}/judge/pt/profile/{id}'


def profile_url_sorted(id):
    return f'{profile_url(id)}?sort=Ranks.created&direction=desc'


def problem_url(id):
    return f'{BASE_URL}/judge/pt/problems/view/{id}'


def uern_pages(pages):
    for index in range(1, pages + 1):
        yield UERN + f'?page={index}'


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()
        
        
def parse_users(soup):
    '''Gera tuplas (id, nome) dos usuários na página da universidade.'''
            
    if soup.tbody is None:
        return

    # os dados do usuário ficam entre tags <tr>
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
    '''Gera as soluções encontradas na página do perfil do usuário.'''
        
    if soup.tbody is None:
        return

    # os dados das soluções ficam entre tags <tr>
    for tr in soup.tbody.find_all('tr'):
        
        lines = tr.get_text().split('\n')
        
        # esse 'if l' no final remove as strings vazias '' que ficam
        sol = tuple(l.strip() for l in lines if l)
       
        if len(sol) == 7:
            yield sol


def parse_date(date, format='%d/%m/%y %H:%M:%S'):
    return datetime.datetime.strptime(date, format)
    

async def fetch_users(session, page):
    '''Retorna os usuários na página da universidade.'''
    
    html = await fetch(session, page)
    soup = BeautifulSoup(html, 'html.parser')
    return parse_users(soup)


# TODO: o uri retorna as datas com 3h a frente do horário local
#       talvez fazer alguma transformação com o campo date
async def fetch_latest_solutions(session, id):
    '''Retorna até 30 soluções mais recentes do usuário.'''
    
    profile_url = profile_url_sorted(id)
    html = await fetch(session, profile_url)
    soup = BeautifulSoup(html, 'html.parser')
    return parse_solutions(soup)


# TODO: pages should be str not int
async def fetch_all(pages):

    async with aiohttp.ClientSession() as session:

        users_by_page = await asyncio.gather(
            *(fetch_users(session, p) for p in uern_pages(pages))
        )
        
        all_users = list(chain.from_iterable(users_by_page))

        solutions = await asyncio.gather(
            *(fetch_latest_solutions(session, id) for id, name in all_users)
        )

        return all_users, solutions
        

def create_user_solutions(users, solutions):

    for (user_id, user_name), user_sols in zip(users, solutions):

        for sol in user_sols:
            # unpack solution
            (problem_id, 
            problem_name, 
            ranking, 
            submission_id,
            language, 
            exec_time, 
            date) = sol

            yield UserSolution(
                user_name, 
                int(user_id),
                profile_url_sorted(user_id),
                int(problem_id),
                problem_name,
                problem_url(problem_id),
                int(ranking[:-1]),  # remove o º do final
                int(submission_id),
                language,
                float(exec_time),
                parse_date(date)
            )


async def latest_solutions(pages, max=100):
    users, solutions = await fetch_all(pages)
    users_solutions = create_user_solutions(users, solutions)

    # ordena pela data  
    sorted_user_solutions = sorted(
        users_solutions, 
        key=lambda u: u.date, 
        reverse=True
    )  

    return sorted_user_solutions[:max]
