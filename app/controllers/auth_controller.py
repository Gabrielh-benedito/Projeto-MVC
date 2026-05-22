#Rotas de autenticação

from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.usuarios import Usuario
from app.auth import hash_senha, verificar_senha, criar_token

# APIRouter agrupas as rotas dentro desse modulo com prefixo /auth
router = APIRouter(prefix="/auth", tags=["Autenticação"])

templates = Jinja2Templates(directory="app/templates")

#TELA DE CADASTRO
@router.get("/cadastro")
def tela_cadastro(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/cadastro.html",
        {"request": request}
    )

@router.get("/login")
def tela_login(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {"request": request}
    )


# ROTA PARA CRIAR O USUÁRIO
@router.post("/cadastro")
def fazer_cadastro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verificar se o email esta cadastrado
    usuario_existente = db.query(Usuario).filter_by(email=email).first()

    # Mensagem de erro se o email já estiver cadastrado
    if usuario_existente:
        return templates.TemplateResponse(
            request,
            "auth/cadastro.html",
            {"request": request, "erro": "Email já cadastrado"}
        )
    
    # Criar usuario - criar objeeto
    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_senha(senha)
    )
    db.add(novo_usuario)
    db.commit()

    return RedirectResponse(url="/auth/login?cadastro=ok", status_code=302)   
#Rota para fazer login
@router.post("/login") 
def fazer_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Buscar o usuário pelo email no db
    usuario = db.query(Usuario).filter_by(email=email).first()
    
    # 2. Verificar a senha com bcrypt
    senha_correta = (
        usuario is not None and verificar_senha(senha, usuario.senha_hash)
    )
    if not senha_correta:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {   "request": request,
                "erro": "Email ou senha incorretos"
            }
        )
    #Verificar se o usuário esta ativo
    if not usuario.ativo:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {   "request": request,
                "erro": "Usuário inativo, contate o administrador"
            }
        )
   

    # 3. Gera o token JWT
    token_data = {
        "sub": usuario.email,
        "nome": usuario.nome,
        "role": usuario.role,
        "id": usuario.id
    }

    token = criar_token(token_data)


    # 4. Salvar o token em um cookie e redirecionar para página home
    response = RedirectResponse(url="/", status_code=302)

    # Definir o cookie com o token JWT
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True, # Impede acesso via JavaScript
        max_age=3600, # Expira em  1 dia
        samesite="lax" # Proteção contra CSRF
    )

    return response

#Rota de sair
@router.get("/logout")
def sair(response: RedirectResponse):
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response