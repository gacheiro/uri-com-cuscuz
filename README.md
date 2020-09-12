![GitHub](https://img.shields.io/github/license/thiagojobson/uri-com-cuscuz)

# URI Online Judge... com cuscuz

Um feed de atividades dos alunos da UERN no URI Online Judge com Flask e web scraping.

## Instalação


Clone o repositório e crie um `virtualenv`:

```
git clone https://github.com/thiagojobson/uri-com-cuscuz
cd uri-com-cuscuz
python3 -m venv venv
```

Ative o `virtualenv` e instale as dependências:

```

# Linux
source venv/bin/activate

# Windows
venv\Scripts\activate.bat

# Instalar o pacote e as dependências
python -m pip install --upgrade pip
pip install -e .
```

Para o app funcionar, é necessário definir algumas variáveis de ambiente (em um arquivo `.env`):

```
FLASK_APP=uricomcuscuz
FLASK_ENV=development
APP_SETTINGS=config.DevelopmentConfig
DATABASE_URL=sqlite:///db.sqlite3
UNIVERSITY=UERN
UNIVERSITY_TOTAL_PAGES=1
```

Rodar testes, atualizar o banco de dados e rodar o app:

```
# Criar as tabelas do banco
flask db upgrade

# Testes
pytest uricomcuscuz

# Atualizar o banco de dados
flask fetch-subs

# Rodar o app
flask run
```

Por padrão, o crawler so irá indexar a primeira página da universiade (`?page=1`). Para definir o número de páginas
adicione `UNIVERSITY_TOTAL_PAGES=n` com `n` igual à paginação máxima ao arquivo `.env`.
