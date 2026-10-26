import asyncio


async def buscar(id: int) -> str:
    await asyncio.sleep(0.1)  # time.sleep aqui TRAVA o loop
    return f"user {id}"


async def main() -> None:
    # Coroutine é PREGUIÇOSA: só roda quando alguém dá await.
    c = buscar(1)
    print(await c)

    # TaskGroup ~ Promise.all, e cancela as outras se uma falhar.
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(buscar(i)) for i in (1, 2, 3)]
    print([t.result() for t in tasks])

    print(await asyncio.gather(*(buscar(i) for i in (1, 2, 3))))

    try:
        async with asyncio.timeout(0.05):  # ~ Promise.race
            await buscar(9)
    except TimeoutError:
        print("timeout")


asyncio.run(main())  # VOCÊ liga o event loop
