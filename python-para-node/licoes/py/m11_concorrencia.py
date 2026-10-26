import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def baixar(url: str) -> str:  # lib síncrona (ex.: requests)
    time.sleep(0.1)
    return url


if __name__ == "__main__":  # obrigatório com processos
    # Threads: o GIL é solto durante I/O, então funciona
    # para chamadas bloqueantes de rede/disco.
    with ThreadPoolExecutor(max_workers=8) as threads:
        print(list(threads.map(baixar, ["a", "b", "c"])))

    # CPU: threads NÃO escalam por causa do GIL.
    # Processos sim (~ worker_threads / cluster).
    with ProcessPoolExecutor() as procs:
        print(list(procs.map(fib, [25, 25, 25, 25])))
