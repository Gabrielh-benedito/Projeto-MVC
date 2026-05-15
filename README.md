# Instalar as bibliotecas

``` bash
pip install -r requirements.txt
``` 

# Inicializar o alembic
``` bash
python -m alembic init migration
``` 

# Editar o arquivo alembic init - na linha 89:
sqlalchemy.url = 

# Gerar a migration

``` bash
python -m alembic revision --autogenerate -m "Criar tabela de usuarios"
``` 

# Aplicar a migration no banco 

``` bash
python -m alembic upgrade head
``` 

# Rodar o codigo
``` bash
python -m uvicorn app.main:app --reload
``` 




