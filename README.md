# apiCondominioPy

API simples para gerenciar usuários, condomínios e vínculos de síndico.

## Descrição
Projeto em FastAPI com SQLAlchemy (SQLite) para gerenciar usuários (sindicose/moradores), autenticação JWT e cadastro de condomínios.

## Requisitos
- Python 3.10+ (verifique seu ambiente)
- Dependências listadas no seu ambiente virtual (venv)

## Instalação (local)
1. Crie e ative um virtualenv (escolha conforme seu sistema):

Linux / macOS (bash):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

2. Instale dependências (recomendado usar `requirements.txt` quando disponível):

Se existir `requirements.txt`, instale com:

```bash
pip install -r requirements.txt
```

Caso não tenha `requirements.txt`, instale as dependências manualmente:

```bash
pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-dotenv python-jose
```

3. Configure variáveis de ambiente no `.env` (não commitar este arquivo):

```
SECRET_KEY=uma_chave_secreta_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

4. Rode a aplicação:

```bash
uvicorn main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`.

Documentação interativa

Depois de iniciar a aplicação, a documentação interativa (Swagger UI) fica disponível em:

```
http://127.0.0.1:8000/docs
```

Também há a versão Redoc em:

```
http://127.0.0.1:8000/redoc
```

## Banco de dados
- Este projeto usa SQLite (`banco.db`) conforme `models.py`.
- Se quiser usar Alembic, já há pasta `alembic/` (verifique config em `alembic.ini`).

## Endpoints principais
- POST /admin/criarsindico — cria um usuário do tipo `sindico` (espera `UsuarioSchema`).
- POST /admin/criarcondominio — cria um `Condominio` e o vínculo `SindicoCondominio` usando `idSindico` (parâmetro). Retorna id e nome do condomínio e `sindico_id`.
- POST /sindico/criar/morador — cria usuário do tipo `morador`.
- POST /auth/login — login via JSON (email + senha) que retorna `access_token` e `refresh_token`.
- POST /auth/loginForm — login via formulário (OAuth2PasswordRequestForm), retorna `access_token`.

> Observação: as rotas e formatos de dados usam os schemas definidos em `schemas.py`.

## Segurança e boas práticas
- Não versionar o arquivo `.env` (já incluído em `.gitignore`).
- Mantenha `SECRET_KEY` seguro.
- Se você usa senhas longas, há um tratamento no código para truncar senhas para 72 bytes antes de aplicar bcrypt (limitação do bcrypt).
 - Recomenda-se usar `bcrypt==4.0.1` (versão testada/compatível com este projeto).

## Dicas de Git
- Se `.env` já foi commitado antes de adicionar ao `.gitignore`, remova-o do índice sem apagar localmente:

```bash
git rm --cached .env
git commit -m "Remove .env do repositório"
```

- Para aplicar `.gitignore` em massa (remover do índice arquivos que agora devem ser ignorados):

```bash
git rm -r --cached .
git add .
git commit -m "Aplicar .gitignore"
```

## Como contribuir
- Crie uma branch, faça suas alterações e abra um PR.
- Escreva testes pequenos quando adicionar lógica crítica (autenticação, hashing).

## Observações finais
- Este README é um ponto de partida. Se quiser, eu adiciono exemplos curl ou collection do Postman / HTTPie para os endpoints.
