const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function buscar(id: number): Promise<string> {
  await sleep(100);
  return `user ${id}`;
}

// Promise é ANSIOSA: começa a rodar na hora da chamada.
const p = buscar(1);
console.log(await p);

// Paralelo: as três ao mesmo tempo (~100 ms no total).
const todos = await Promise.all([1, 2, 3].map(buscar));
console.log(todos);

// Timeout: corrida entre a tarefa e um timer.
const timeout = (ms: number) =>
  sleep(ms).then(() => Promise.reject(new Error("timeout")));
try {
  await Promise.race([buscar(9), timeout(50)]);
} catch (e) {
  console.log((e as Error).message);
}
// Top-level await: o event loop já está rodando.
