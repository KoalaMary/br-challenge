import asyncio
import logging
from asyncio.exceptions import TimeoutError
from typing import Optional

import aiohttp

logger = logging.getLogger("app")


class HttpClientWithBackup:

    def __init__(self, timeout: int, url: str, delay: Optional[int] = None, backup_count: Optional[int] = None):
        self.__timeout = timeout / 1000
        self.__session = aiohttp.ClientSession()
        self.__url = url
        self.__delay = delay or 0.3
        self.__backup_count = backup_count or 2

    async def send_single_request(self, *args):
        logger.info(f"Send single request {args[0]}")
        async with self.__session.get(url=self.__url) as res:
            res, status = await res.text(), res.status  # TODO text retuns string, need json
            logger.info(f"Single request {args[0]} result: {res, status}")
            return res, status

    async def send_request_with_backups(self):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # Get rid of
        async with self.__session:
            # Sending first request
            tasks = [asyncio.create_task(self.send_single_request(1))]
            done, pending = await asyncio.wait(tasks, timeout=self.__delay, return_when=asyncio.FIRST_COMPLETED)
            if done:
                res, status = done.pop().result()
                if status == 200:
                    logger.info(f"Finished with first request: {res, status}")
                    return res, status

            # Sending 2nd and 3rd requests
            tasks = [asyncio.create_task(self.send_single_request(x)) for x in range(2, self.__backup_count + 2)]
            if pending:
                tasks.append(pending.pop())
            while tasks:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    res, status = task.result()
                    logger.info(f"Finished with backup requests: {res, status}")
                    if status == 200:
                        return res, status

                tasks = pending
            return {"message": "No response"}, 500

    async def send_requests_with_timeout(self):
        task = asyncio.create_task(self.send_request_with_backups())
        try:
            res, status = await asyncio.wait_for(task, timeout=self.__timeout)
            return res, status
        except TimeoutError:
            logger.warning('The task was cancelled due to a timeout')
            return {"message": "Timeout Exception"}, 500
