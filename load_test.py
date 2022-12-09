import asyncio

import aiohttp
from flask import Flask, request

app = Flask(__name__)


async def send_http_request(session: aiohttp.ClientSession, timeout: int):
    async with session.get(f"http://127.0.0.1:5000/api/smart?timeout={timeout}") as res:
        return await res.text()


@app.get("/api/smart-load-test")
async def http_client_load_test():
    timeout = int(request.args.get('timeout'))
    rps = int(request.args.get('rps'))
    result = {}
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(send_http_request(session, timeout)) for _ in range(rps)]
        done, _ = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        result["count"] = len(done)
        for i, x in enumerate(done):
            response = x.result()
            result[str(i)] = response
        return result


if __name__ == "__main__":
    app.run(debug=True, port=5001)
