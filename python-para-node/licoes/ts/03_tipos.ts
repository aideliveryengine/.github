// Interface: contrato estrutural, apagado em runtime.
interface Repositorio<T> {
  buscar(id: string): T | undefined;
}

type Status = "ativo" | "inativo";

type Usuario = { id: string; nome: string; status: Status };

class RepoMemoria implements Repositorio<Usuario> {
  private dados = new Map<string, Usuario>();

  buscar(id: string): Usuario | undefined {
    return this.dados.get(id);
  }
}

function primeiro<T>(xs: T[]): T | undefined {
  return xs[0];
}

const repo: Repositorio<Usuario> = new RepoMemoria();
console.log(repo.buscar("1"), primeiro([1, 2]));
