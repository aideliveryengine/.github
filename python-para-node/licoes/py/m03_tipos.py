from typing import Literal, Protocol, TypedDict


# Protocol = interface ESTRUTURAL (duck typing tipado).
class Repositorio[T](Protocol):
    def buscar(self, id: str) -> T | None: ...


type Status = Literal["ativo", "inativo"]


class Usuario(TypedDict):  # o "type" de um objeto/dict
    id: str
    nome: str
    status: Status


class RepoMemoria:  # sem "implements": basta ter o método
    def __init__(self) -> None:
        self._dados: dict[str, Usuario] = {}

    def buscar(self, id: str) -> Usuario | None:
        return self._dados.get(id)


def primeiro[T](xs: list[T]) -> T | None:
    return xs[0] if xs else None


repo: Repositorio[Usuario] = RepoMemoria()  # mypy confere
print(repo.buscar("1"), primeiro([1, 2]))
