import pytest


# Código sob teste
class Cambio:
    def cotacao(self) -> float:
        return 5.4


def frete(kg: float) -> float:
    if kg <= 0:
        raise ValueError("peso inválido")
    return 10 if kg <= 5 else 25


@pytest.fixture  # ~ beforeEach, injetada pelo NOME do parâmetro
def carrinho() -> list[str]:
    return []


@pytest.mark.parametrize(("kg", "esperado"), [(1, 10), (10, 25)])
def test_frete(kg: float, esperado: float) -> None:  # ~ test.each
    assert frete(kg) == esperado  # assert puro, sem expect()


def test_cotacao(monkeypatch: pytest.MonkeyPatch, carrinho: list[str]) -> None:
    monkeypatch.setattr(Cambio, "cotacao", lambda self: 5.0)  # desfeito no fim
    assert Cambio().cotacao() == 5.0
    carrinho.append("x")


def test_erro() -> None:
    with pytest.raises(ValueError, match="peso"):
        frete(-1)
