# Logica de autencação

# 1. hash e verificação de senhas com bcrypt

# 2. Geração de token JWT

# 3. Leitura a validação do token vindo do cookie

from datetime import datetime, timedelta, timezone
import token
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configurar o algoritmo do hash = bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funções de senha 

def hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)

def criar_token(dados: dict):

    payload = dados.copy()

    #Define quando o token expira
    expira = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expira})

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token


def decodificar_token(token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
#Função para usar nas rotas protegida
def get_usuario_logado(request: Request):
    
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado"
        )
    
    try:
        payload = decodificar_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token inválido"
            )
        return payload
    except JWTError:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado"
        )
    
def get_usuario_opcional(request: Request):
    try:
        return get_usuario_logado(request)
    except HTTPException:
        return None
    
#Dependencia que exige login e perfil de admin
def get_admin(request: Request):
    usuario = get_usuario_logado(request)
    if usuario.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    else:
        return usuario