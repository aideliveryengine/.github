// Em Node: função de ordem superior que embrulha outra.
function comRetry<A extends unknown[], R>(
  fn: (...args: A) => Promise<R>,
  tentativas = 3,
): (...args: A) => Promise<R> {
  return async (...args: A): Promise<R> => {
    for (let i = 1; ; i++) {
      try {
        return await fn(...args);
      } catch (e) {
        if (i >= tentativas) throw e;
      }
    }
  };
}

let falhas = 2;
const buscar = comRetry(async (id: string) => {
  if (falhas-- > 0) throw new Error("timeout");
  return { id };
});

console.log(await buscar("42"));
