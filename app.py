from flask import Flask, jsonify, request
from func_timeout import func_timeout, FunctionTimedOut
import requests
from time import sleep
from random import random
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures import wait
from concurrent.futures import FIRST_COMPLETED
import asyncio
import aiohttp

app = Flask(__name__)


# def get_simple(*args):
#     print(f"GET SIMPLE {args[0]}")
#     res = requests.get("https://exponea-engineering-assignment.appspot.com/api/work")
#     print(f"RES TEXT {args[0]}: {res.text}")
#     return res.text
#
#
# def get_with_sleep(*args):
#     print(f"GET SIMPLE WITH SLEEP {args[0]}")
#     sleep(5)
#     return get_simple(*args)
#
#
# def all_async_functions():
#     with ProcessPoolExecutor(1) as executor:
#         futures = [executor.submit(get_simple, 1), executor.submit(get_with_sleep, 2),
#                    executor.submit(get_with_sleep, 3)]
#         done, not_done = wait(futures, return_when=FIRST_COMPLETED)
#         if len(done) == 0:
#             return "No result"
#         else:
#             # get the future from the done set
#             executor.shutdown(wait=False, cancel_futures=True)
#             future = done.pop()
#             # get the result from the first task to complete
#             result = future.result()
#
#             print(f"FINAL RESULT: {result}")
#             return result


async def get_with_sleep_asyncio(*args, session: aiohttp.ClientSession):
    print(f"GET SIMPLE WITH SLEEP {args[0]}")
    await asyncio.sleep(0.3)
    return await get_simple_asyncio(*args, session=session)


async def get_simple_asyncio(*args, session: aiohttp.ClientSession):
    print(f"GET SIMPLE {args[0]}")
    async with session.get("https://exponea-engineering-assignment.appspot.com/api/work") as res:
        text = await res.text(), res.status
        print(f"RES TEXT {args[0]}: {text}")
        return text


async def all_functions_asyncio():
    async with aiohttp.ClientSession() as session:
        tasks = [get_simple_asyncio(1, session=session)]
        finished, unfinished = await asyncio.wait(tasks, timeout=0.3, return_when=asyncio.FIRST_COMPLETED)
        if finished:
            if list(finished)[0].result()[1] == 200:
                print(f"IN FINISHED: {list(finished)[0].result()[1] == 200}")
                return list(finished)[0].result()
        tasks = list(unfinished) + [get_simple_asyncio(2, session=session), get_simple_asyncio(3, session=session)]
        while tasks:
            finished, unfinished = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for x in finished:
                result = x.result()
                print(f"Finished task produced {result!r}")
                if result[1] == 200:
                    print(f"Cancelling {len(unfinished)} remaining tasks")
                    for task in unfinished:
                        task.cancel()
                    await asyncio.wait(unfinished)
                    return result
            tasks = unfinished
        return "No response", 500


def get_proxy_loop():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    proxy = loop.run_until_complete(all_functions_asyncio())
    loop.close()
    return proxy


@app.get("/api/smart")
def hello_world():
    timeout = request.args.get('timeout')
    # return all_async_functions(int(timeout))
    try:
        res, status = func_timeout(timeout=int(timeout) / 1000, func=get_proxy_loop)
        print(f"RES MAIN {res}, {status}")
        return {"res": res, "status": status}
    except FunctionTimedOut as e:
        print(e)
        return {"message": e.msg}

    # print(f"TIMEOUT: {timeout}")
    # TODO parse to json
    # return res.text


if __name__ == "__main__":
    app.run()
