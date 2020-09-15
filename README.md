![GitHub](https://img.shields.io/github/license/thiagojobson/uri-com-cuscuz)

# URI Online Judge... com cuscuz

Um feed de atividades dos alunos da UERN no URI Online Judge com Flask e web scraping.

## Instalação

É preciso ter qualquer versão do python igual ou superior ao 3.6.
Clone este repositório na sua máquina e crie um **ambiente virtual** para instalar o app localmente:

```bash
git clone https://github.com/thiagojobson/uri-com-cuscuz
cd uri-com-cuscuz

# Linux
python3.6 -m venv venv
# ou (caso tenha o virtualenv instalado)
virtualenv --python=/usr/bin/python3.6 venv

# Windows
py -m venv venv
```

Ative o ambiente virtual e instale o app e as dependências:

```bash
# Linux
source venv/bin/activate

# Windows
venv\Scripts\activate.bat

# Instalar o app e as dependências
python -m pip install --upgrade pip
pip install -e .
```

Para o app funcionar, é necessário definir algumas variáveis de ambiente 
(adicione as seguintes linhas a um arquivo com nome `.env`):

```
FLASK_APP=uricomcuscuz
FLASK_ENV=development
APP_SETTINGS=config.DevelopmentConfig
DATABASE_URL=sqlite:///db.sqlite3
UNIVERSITY=UERN
UNIVERSITY_TOTAL_PAGES=1
```

Em seguida rode os comando para criar o banco de dados, testar o app para ver se está tudo funcionando e 
atualizar o banco de dados com os dados do URI Online Judge:

```bash
# Criar as tabelas do banco
flask db upgrade

# Testes
pytest uricomcuscuz

# Atualizar o banco de dados
flask uri update

# Rodar o app
flask run
```

Depois de rodar o app, vá até a url `localhost:5000` no navegador para acessa-lo.

Por padrão, o crawler so irá indexar a primeira página da universiade (`?page=1`). Para definir o número de páginas
adicione `UNIVERSITY_TOTAL_PAGES=n` com `n` igual à paginação máxima ao arquivo `.env`.
