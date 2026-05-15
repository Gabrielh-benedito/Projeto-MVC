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