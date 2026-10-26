from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field


class CriarUsuario(BaseModel):  # o schema do body
    nome: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+$")


class Usuario(CriarUsuario):
    id: int


class RepoUsuarios:
    def __init__(self) -> None:
        self._dados: list[Usuario] = []

    def criar(self, d: CriarUsuario) -> Usuario:
        u = Usuario(**d.model_dump(), id=len(self._dados) + 1)
        self._dados.append(u)
        return u


_repo = RepoUsuarios()


def get_repo() -> RepoUsuarios:  # provider (~ @Injectable do Nest)
    return _repo


app = FastAPI()  # OpenAPI/Swagger em /docs de graça


@app.post("/usuarios", status_code=201)
def criar(
    dados: CriarUsuario,  # body validado: 422 automático
    repo: Annotated[RepoUsuarios, Depends(get_repo)],
) -> Usuario:
    return repo.criar(dados)


# uvicorn m13_api:app --reload   (~ nodemon)
