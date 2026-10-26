import {
  Worker, isMainThread, parentPort, workerData,
} from "node:worker_threads";

// I/O: o event loop já é concorrente, nada a fazer.
// CPU pesado: worker_threads (outro isolate do V8).
const fib = (n: number): number =>
  n < 2 ? n : fib(n - 1) + fib(n - 2);

if (isMainThread) {
  const rodar = (n: number) =>
    new Promise<number>((ok, erro) => {
      const w = new Worker(new URL(import.meta.url), {
        workerData: n,
      });
      w.once("message", ok);
      w.once("error", erro);
    });
  console.log(await Promise.all([25, 25, 25, 25].map(rodar)));
} else {
  parentPort!.postMessage(fib(workerData as number));
}
