import { z } from "zod";

// zod: você escreve o SCHEMA e deriva o tipo dele.
const Item = z.object({
  sku: z.string(),
  qtd: z.number().int().positive(),
});

const Pedido = z.object({
  id: z.string().uuid(),
  itens: z.array(Item).min(1),
  cupom: z.string().optional(),
});

type Pedido = z.infer<typeof Pedido>;

const body = `{"id": "3f2b8c1e-8a6b-4c1d-9f0e-2a7d5b6c4e10",
  "itens": [{"sku": "A1", "qtd": 2}]}`;

const p: Pedido = Pedido.parse(JSON.parse(body));
console.log(p.itens[0].qtd);

const r = Pedido.safeParse({ id: "x", itens: [] });
console.log(r.success); // false, com os erros em r.error
