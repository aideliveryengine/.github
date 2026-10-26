// Value object em TS: muito boilerplate na mão.
class Dinheiro {
  constructor(
    readonly valor: number,
    readonly moeda: string = "BRL",
  ) {}

  somar(o: Dinheiro): Dinheiro {
    if (o.moeda !== this.moeda) throw new Error("moeda diferente");
    return new Dinheiro(this.valor + o.valor, this.moeda);
  }

  equals(o: Dinheiro): boolean {
    return o.valor === this.valor && o.moeda === this.moeda;
  }

  toString(): string {
    return `${this.moeda} ${this.valor.toFixed(2)}`;
  }
}

const a = new Dinheiro(10.5);
console.log(`${a.somar(a)}`, a.equals(new Dinheiro(10.5)));
