import logging

from flask import Flask, request

import config
from http_client import HttpClientWithBackup

app = Flask(__name__)
app.config.from_object(config.Config)
app.logger.setLevel(logging.INFO)


@app.get("/api/smart")
async def get_exponea_result():
    timeout = request.args.get('timeout')
    try:
        timeout = int(timeout)
        if timeout < 0:
            raise ValueError
    except ValueError:
        return {"message": f"Invalid timeout {timeout}"}, 400

    client = HttpClientWithBackup(timeout=timeout,
                                  url=app.config["EXPONEA_URL"],
                                  delay=app.config["EXPONEA_BACKUP_DELAY"],
                                  backup_count=app.config["EXPONEA_BACKUP_COUNT"])

    res, status = await client.send_requests_with_timeout()
    return res, status, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run()
