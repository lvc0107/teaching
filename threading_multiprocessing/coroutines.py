import asyncio



async def print_names():
    for name in ["Alice", "Bob", "Charlie"]:
        print(name)
        await asyncio.sleep(1)  # Simulate an I/O operation (e.g., network delay)


async def print_ages(min_sleep, max_sleep):
    for age in [30, 25, 35]:
        print(age)
        await asyncio.sleep(0.5)  # Simulate a different I/O operation (e.g., database query)


loop = asyncio.get_event_loop()
# why the following warning?
#DeprecationWarning: There is no current event loop: loop = asyncio.get_event_loop()

#Because in modern Python versions (3.10+),
# the recommended way to run asynchronous code is to use `asyncio.run()`,
# which creates and manages the event loop for you.
# When you call `asyncio.get_event_loop()`
# outside of an asynchronous context, it may raise a `DeprecationWarning`
# because there is no current event loop available.


# why create tasks instead of just calling the coroutines directly?
# When you call a coroutine function (like `print_names()`), it returns a coroutine object,
# but it doesn't start executing until you await it.
# By using `loop.create_task()`,
# you schedule the coroutine to run concurrently with other tasks
# Nevertheles using aynciio.run_until_complete
# with gather directly on the coroutines also works because `asyncio.gather()`
# will handle the scheduling of the coroutines for you.


tasks = [
    loop.create_task(print_names()),
    loop.create_task(print_ages(0.5, 1)),
]
tasks2 = [
    print_names(),
    print_ages(0.5, 1),
]
print("Running tasks concurrently with create_task:")
loop.run_until_complete(asyncio.gather(*tasks))
print("\nRunning tasks concurrently with gather directly:")
loop.run_until_complete(asyncio.gather(*tasks2))

loop.close()
# Why this one? Because we created the event loop manually,
# we should close it to free up resources.
# In modern asyncio code, it's more common to use `asyncio.run()`
# which handles the event loop creation and cleanup automatically,
# so you don't have to worry about closing it yourself.


