// "Options object" com defaults: o padrão em Node.
type Opcoes = { porta?: number; ssl?: boolean };

function conectar(host: string, { porta = 5432, ssl = true }: Opcoes = {}) {
  return `${host}:${porta} ssl=${ssl}`;
}
conectar("db", { ssl: false });

// rest params e spread
function log(nivel: string, ...partes: unknown[]): void {
  console.log(nivel, ...partes);
}
const base = { retries: 3 };
const cfg = { ...base, timeout: 30 };

// Em JS o default é avaliado A CADA chamada: sem surpresa.
function add(x: string, lista: string[] = []): string[] {
  lista.push(x);
  return lista;
}
add("a");
console.log(add("b"), cfg); // ["b"]
