from uuid import UUID

from pydantic import BaseModel, Field, ValidationError


# pydantic: a CLASSE já é o tipo e o schema ao mesmo tempo.
class Item(BaseModel):
    sku: str
    qtd: int = Field(gt=0)


class Pedido(BaseModel):
    id: UUID
    itens: list[Item] = Field(min_length=1)
    cupom: str | None = None


body = """{"id": "3f2b8c1e-8a6b-4c1d-9f0e-2a7d5b6c4e10",
  "itens": [{"sku": "A1", "qtd": 2}]}"""

p = Pedido.model_validate_json(body)  # ~ Pedido.parse
print(p.itens[0].qtd, type(p.id))  # id virou UUID de verdade

try:
    Pedido.model_validate({"id": "x", "itens": []})
except ValidationError as e:  # ~ safeParse().error
    print(e.error_count(), "erros")
