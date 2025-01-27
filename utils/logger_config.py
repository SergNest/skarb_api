from loguru import logger
import requests
import json
import datetime

loki_url = "http://192.168.11.5:3100/loki/api/v1/push"
headers = {"Content-Type": "application/json"}

async def send_to_loki(message):
    try:
        record = json.loads(message)  # Тепер "message" буде JSON
    except json.JSONDecodeError:
        record = message

    if isinstance(record, dict) and "level" in record and "time" in record:
        level_name = record["level"]["name"]
        timestamp_str = str(int(record["time"].timestamp() * 1e9))
        job_name = record.get("extra", {}).get("job", "skarbapi")
        log_message = record.get("message", "")
    else:
        level_name = "INFO"
        timestamp_str = str(int(datetime.datetime.now().timestamp() * 1e9))
        job_name = "skarbapi"
        log_message = str(record)

    log_data = {
        "streams": [
            {
                "stream": {
                    "job": job_name,
                    "level": level_name
                },
                "values": [
                    [timestamp_str, log_message]
                ]
            }
        ]
    }

    response = requests.post(loki_url, headers=headers, data=json.dumps(log_data))
    return response.status_code

# Видаляємо усі попередні обробники
logger.remove()

# Додаємо єдиний обробник, який перетворює все на JSON
logger.add(send_to_loki, level="INFO", serialize=True)
