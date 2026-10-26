import { beforeEach, mock, test } from "node:test";
import assert from "node:assert/strict";

// Código sob teste
export const cambio = { cotacao: (): number => 5.4 };
export function frete(kg: number): number {
  if (kg <= 0) throw new RangeError("peso inválido");
  return kg <= 5 ? 10 : 25;
}

let carrinho: string[];
beforeEach(() => {
  carrinho = []; // estado novo por teste
});

for (const [kg, esperado] of [[1, 10], [10, 25]] as const) {
  test(`frete ${kg}kg`, () => assert.equal(frete(kg), esperado));
}

test("cotação mockada", () => {
  mock.method(cambio, "cotacao", () => 5.0);
  assert.equal(cambio.cotacao(), 5.0);
  carrinho.push("x");
});

test("erro", () => assert.throws(() => frete(-1), /peso/));
