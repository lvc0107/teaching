import asyncio
"""
% time python async_sequential_test1.py                                                                                                                                  26-05-20 - 20:57:50
A started
A done
B started
B done
python async_sequential_test1.py  0.06s user 0.02s system 2% cpu 3.265 total
"""
async def task(name, delay):
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} done")

async def main():
    # Sequential — takes 3 seconds total
    await task("A", 1)
    await task("B", 2)

asyncio.run(main())