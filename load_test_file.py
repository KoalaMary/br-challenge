import asyncio

import aiohttp
from flask import Flask

app = Flask(__name__)


async def send_http_request(session: aiohttp.ClientSession):
    async with session.get("http://127.0.0.1:5000/api/smart?timeout=1000000") as res:
        return await res.text()


@app.get("/api/smart-load-test")
async def hello_world_load_test():
    result = {}
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(send_http_request(session)) for _ in range(100)]
        done, _ = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        result["count"] = len(done)
        for i, x in enumerate(done):
            response = x.result()
            result[str(i)] = response
        return result


if __name__ == "__main__":
    app.run(debug=True, port=5001)
