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
pip install -r requirements.txt

# Windows
venv\Scripts\activate.bat
pip install -r requirements.txt
```

Para o app funcionar, é necessário definir algumas variáveis de ambiente (em um arquivo `.env`):

```
FLASK_APP=uricomcuscuz
FLASK_ENV=development
APP_SETTINGS=config.DevelopmentConfig
DATABASE_URL=sqlite:///db.sqlite3
```

Rodar testes, atualizar o banco de dados e rodar o app:

```
# Testes
pytest uricomcuscuz

# Atualizar o banco de dados
flask fetch-subs

# Rodar o app
flask run
```
