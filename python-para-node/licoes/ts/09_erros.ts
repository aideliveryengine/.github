class ErroDominio extends Error {}
class SaldoInsuficiente extends ErroDominio {}

// TS 5.2+: "using" chama [Symbol.dispose]() ao sair do bloco.
function abrirConexao() {
  console.log("abriu");
  return {
    query: (sql: string) => console.log("rodou", sql),
    [Symbol.dispose]: () => console.log("fechou"),
  };
}

function sacar(valor: number): void {
  throw new SaldoInsuficiente(`faltam ${valor}`);
}

{
  using conn = abrirConexao();
  conn.query("select 1");
} // fechou

try {
  sacar(100);
} catch (e) {
  if (!(e instanceof SaldoInsuficiente)) throw e;
  const erro = new Error("saque falhou", { cause: e });
  console.log(erro.message, (erro.cause as Error).message);
} finally {
  console.log("sempre");
}
