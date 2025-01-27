from loguru import logger
import requests
import json
import datetime

logger.remove()

loki_url = "http://192.168.11.5:3100/loki/api/v1/push"
headers = {
    "Content-Type": "application/json"
}


async def send_to_loki(message):
    try:
        record = json.loads(message)
    except json.JSONDecodeError:
        record = message

    if isinstance(record, dict):
        level_name = record["level"]["name"]

        log_data = {
            "streams": [
                {
                    "stream": {"job": record.get("job", "skarbapi"), "level": level_name},
                    "values": [
                        [
                            str(int(record["time"].timestamp() * 1000000000)),
                            record["message"]
                        ]
                    ]
                }
            ]
        }
    else:
        log_data = {
            "streams": [
                {
                    "stream": {"job": "skarbapi", "level": "INFO"},
                    "values": [
                        [
                            str(int(datetime.datetime.now().timestamp() * 1000000000)),
                            record
                        ]
                    ]
                }
            ]
        }

    # Виконання POST запиту до Loki
    response = requests.post(loki_url, headers=headers, data=json.dumps(log_data))
    return response.status_code

# Загальний лог-файл для відправки в Loki
logger.add(send_to_loki, level="INFO")


# Логи для окремих маршрутів, також відправляються в Loki
def log_with_job(job_name):
    return lambda record: logger.bind(job=job_name).log("INFO", record["message"])


logger.add(send_to_loki, level="INFO", filter=log_with_job("check_zok_by_phone"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("new_offer"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("new_delay"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("get_vendor"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("new_type"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("dogovorhistory"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("gettype"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("new_vendor"))
logger.add(send_to_loki, level="INFO", filter=log_with_job("get_bonus_withdraw"))
