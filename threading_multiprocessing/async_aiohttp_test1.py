import asyncio
import aiohttp  # async-compatible HTTP library


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main():
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://api.github.com",
    ]
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[fetch(session, url) for url in urls])

    for r in results:
        print(r)  # print first 100 chars of each response
        print(len(r), "chars received")


asyncio.run(main())