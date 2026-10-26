from collections.abc import Callable, Iterator
from dataclasses import dataclass


@dataclass
class User:
    id: int
    email: str
    ativo: bool


users = [User(1, "a@x.com", True), User(2, "b@x.com", False)]

ativos = [u.email for u in users if u.ativo]  # filter + map
por_id = {u.id: u for u in users}  # Object.fromEntries
total = sum(u.id for u in users)  # generator: não cria lista


def paginas(api: Callable[[int], list[int]]) -> Iterator[int]:
    p = 1
    while itens := api(p):  # walrus: atribui e testa
        yield from itens  # ~ yield*
        p += 1


def api(p: int) -> list[int]:
    return [p * 10, p * 10 + 1] if p < 3 else []


# Truthiness: [] {} "" 0 None são FALSE em Python.
if not []:
    print("vazio")
print(ativos, por_id[1], total, list(paginas(api)))
