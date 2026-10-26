from collections.abc import Iterator
from contextlib import contextmanager


class ErroDominio(Exception): ...


class SaldoInsuficiente(ErroDominio): ...


@contextmanager  # ~ objeto com [Symbol.dispose]
def abrir_conexao() -> Iterator[str]:
    print("abriu")
    try:
        yield "conn"  # o valor do "as"
    finally:
        print("fechou")


def sacar(valor: int) -> None:
    raise SaldoInsuficiente(f"faltam {valor}")


with abrir_conexao() as conn:  # ~ using
    print("rodou select 1 em", conn)

try:
    sacar(100)
except SaldoInsuficiente as e:  # catch por TIPO
    try:
        raise RuntimeError("saque falhou") from e  # ~ { cause }
    except RuntimeError as erro:
        print(erro, "<-", erro.__cause__)
else:
    print("só roda se NÃO houve exceção")
finally:
    print("sempre")
