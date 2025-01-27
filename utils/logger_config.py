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
                    "stream": {"job": record["extra"].get("job", "skarbapi"), "level": level_name},
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
logger.add(send_to_loki, level="INFO", filter=lambda record: "check_zok_by_phone" in record["extra"], extra={"job": "check_zok_by_phone"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "new_offer" in record["extra"], extra={"job": "new_offer"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "new_delay" in record["extra"], extra={"job": "new_delay"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "get_vendor" in record["extra"], extra={"job": "get_vendor"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "new_type" in record["extra"], extra={"job": "new_type"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "dogovorhistory" in record["extra"], extra={"job": "dogovorhistory"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "gettype" in record["extra"], extra={"job": "gettype"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "new_vendor" in record["extra"], extra={"job": "new_vendor"})
logger.add(send_to_loki, level="INFO", filter=lambda record: "get_bonus_withdraw" in record["extra"], extra={"job": "get_bonus_withdraw"})

# from loguru import logger
# import os

# log_dir = "/var/log/fastapi"
# os.makedirs(log_dir, exist_ok=True)

# logger.remove()

# # Загальний лог-файл
# logger.add(f"{log_dir}/general.json", format="{time} {level} {message} {extra}", serialize=True, rotation="10 MB",
#            retention="10 days", compression="zip")

# # Логи для окремих маршрутів
# logger.add(f"{log_dir}/check_zok_by_phone.json", serialize=True,
#            filter=lambda record: "check_zok_by_phone" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/new_delay.json", serialize=True,
#            filter=lambda record: "new_delay" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/get_vendor.json", serialize=True,
#            filter=lambda record: "get_vendor" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/new_type.json", serialize=True,
#            filter=lambda record: "new_type" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/dogovorhistory.json", serialize=True,
#            filter=lambda record: "dogovorhistory" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/gettype.json", serialize=True,
#            filter=lambda record: "gettype" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/new_vendor.json", serialize=True,
#            filter=lambda record: "new_vendor" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/new_offer.json", serialize=True,
#            filter=lambda record: "new_offer" in record["extra"], rotation="5 MB", retention="7 days")
# logger.add(f"{log_dir}/get_bonus_withdraw.json", serialize=True,
#            filter=lambda record: "get_bonus_withdraw" in record["extra"], rotation="5 MB", retention="7 days")
