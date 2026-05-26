import asyncio
import aiohttp  # async-compatible HTTP library


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


urls = [
    "https://example.com",
    "https://httpbin.org/get",
    "https://api.github.com",
]

async def request1():
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[fetch(session, url) for url in urls])

    for r in results:
        print(r)  # print first 100 chars of each response
        print(len(r), "chars received")


async def request2(url):
    print(f"Getting status for {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"Finished getting status from: {url}")
            print("Example.com content length:", response.headers.get("Content-Length"))

            return url, response.status

asyncio.run(request1())
for url in urls:
    asyncio.run(request2(url))


async def main():

    tasks = []
    for url in urls:
        task = asyncio.create_task(request2(url))
        tasks.append(task)

    for task in asyncio.as_completed(tasks):
        try:
            url, code = await task
            print(f"Status code for url: {url} is {code}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")


asyncio.run(main())