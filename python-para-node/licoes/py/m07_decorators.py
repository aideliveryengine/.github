import asyncio
import functools
from collections.abc import Callable, Coroutine
from typing import Any

# "async (...args: A) => Promise<R>" em Python:
type FnAsync[**P, R] = Callable[P, Coroutine[Any, Any, R]]


# Decorator = a MESMA ideia, com açúcar sintático (@).
# **P (ParamSpec) preserva a assinatura, como o A do TS.
def com_retry[**P, R](
    tentativas: int = 3,
) -> Callable[[FnAsync[P, R]], FnAsync[P, R]]:
    def decorator(fn: FnAsync[P, R]) -> FnAsync[P, R]:
        @functools.wraps(fn)  # mantém nome/docstring
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for i in range(1, tentativas + 1):
                try:
                    return await fn(*args, **kwargs)
                except Exception:
                    if i == tentativas:
                        raise
            raise AssertionError("inalcançável")

        return wrapper

    return decorator


falhas = 2


@com_retry(tentativas=3)  # = buscar = com_retry(3)(buscar)
async def buscar(id: str) -> dict[str, str]:
    global falhas
    if falhas > 0:
        falhas -= 1
        raise TimeoutError
    return {"id": id}


print(asyncio.run(buscar("42")))
