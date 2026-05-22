import asyncio

"""
% time python async_concurrent_test1.py                                                                                                                                  26-05-20 - 20:56:51
A started
B started
A done
B done
python async_concurrent_test1.py  0.06s user 0.02s system 3% cpu 2.093 total

"""
async def task(name, delay):
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} done")


async def main():
    # Concurrent — takes 2 seconds total (runs simultaneously)
    await asyncio.gather(
        task("A", 1),
        task("B", 2),
    )

asyncio.run(main())

