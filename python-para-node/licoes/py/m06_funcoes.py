# * = daqui pra frente, só por NOME. É o "options object".
def conectar(host: str, *, porta: int = 5432, ssl: bool = True) -> str:
    return f"{host}:{porta} ssl={ssl}"


conectar("db", ssl=False)


# *args ~ ...rest   |   **kwargs ~ objeto de opções livre
def log(nivel: str, *partes: object, **extra: object) -> None:
    print(nivel, *partes, extra)


base = {"retries": 3}
cfg = {**base, "timeout": 30}  # spread de dict


# ARMADILHA clássica de entrevista: o default é criado UMA vez,
# na definição da função, e compartilhado entre as chamadas.
def add(x: str, lista: list[str] = []) -> list[str]:
    lista.append(x)
    return lista


add("a")
print(add("b"), cfg)  # ['a', 'b'] !!


def add_ok(x: str, lista: list[str] | None = None) -> list[str]:
    lista = [] if lista is None else lista
    lista.append(x)
    return lista
