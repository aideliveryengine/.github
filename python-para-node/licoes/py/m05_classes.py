from dataclasses import dataclass
from decimal import Decimal
from typing import Self


# frozen = readonly; slots = sem __dict__ (menos memória).
# __init__, __eq__ e __repr__ são GERADOS.
@dataclass(frozen=True, slots=True)
class Dinheiro:
    valor: Decimal
    moeda: str = "BRL"

    def __add__(self, o: Self) -> Self:  # sobrecarga do +
        if o.moeda != self.moeda:
            raise ValueError("moeda diferente")
        return type(self)(self.valor + o.valor, self.moeda)

    def __str__(self) -> str:  # ~ toString()
        return f"{self.moeda} {self.valor:.2f}"


a = Dinheiro(Decimal("10.50"))  # Decimal: nada de 0.1 + 0.2
print(a + a, a == Dinheiro(Decimal("10.50")))
