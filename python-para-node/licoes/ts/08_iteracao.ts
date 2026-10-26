type User = { id: number; email: string; ativo: boolean };
const users: User[] = [
  { id: 1, email: "a@x.com", ativo: true },
  { id: 2, email: "b@x.com", ativo: false },
];

const ativos = users.filter((u) => u.ativo).map((u) => u.email);
const porId = Object.fromEntries(users.map((u) => [u.id, u]));
const total = users.reduce((s, u) => s + u.id, 0);

// Generator: produz sob demanda (lazy).
function* paginas(api: (p: number) => number[]) {
  for (let p = 1; ; p++) {
    const itens = api(p);
    if (itens.length === 0) return;
    yield* itens;
  }
}
const api = (p: number) => (p < 3 ? [p * 10, p * 10 + 1] : []);

// Truthiness: [] e {} são TRUE em JS.
if ([].length === 0) console.log("vazio");
console.log(ativos, porId[1], total, [...paginas(api)]);
