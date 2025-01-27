from loguru import logger
import requests
import json
import datetime

loki_url = "http://192.168.11.5:3100/loki/api/v1/push"
headers = {"Content-Type": "application/json"}


async def send_to_loki(message):
    """
    Відправляє лог до Loki у форматі JSON.
    """
    try:
        record = json.loads(message)
    except json.JSONDecodeError:
        # Якщо отриманий message не є JSON'ом, розглядаємо його як звичайний рядок
        record = message

    # Якщо ми змогли розпарсити message як dict, і там присутні ключі рівня та часу
    if isinstance(record, dict) and "level" in record and "time" in record:
        level_name = record["level"]["name"]
        timestamp_str = str(int(record["time"].timestamp() * 1e9))
        # Витягуємо job із record["extra"] якщо він там є, інакше ставимо "skarbapi"
        job_name = record.get("extra", {}).get("job", "skarbapi")
        log_message = record.get("message", "")
    else:
        # Якщо структура не відповідає формату, логуватимемо з типом INFO і поточним часом
        level_name = "INFO"
        timestamp_str = str(int(datetime.datetime.now().timestamp() * 1e9))
        job_name = "skarbapi"
        log_message = str(record)
    
    print("--- DEBUG record ---")
    print(record)
    print("--------------------")

    # Формуємо JSON для Loki
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

    # Виконуємо POST-запит до Loki
    response = requests.post(loki_url, headers=headers, data=json.dumps(log_data))
    return response.status_code

# Прибираємо купу фільтрів, замінюємо на єдиний logger.add
logger.remove()  # На випадок, якщо були додані інші "handlers" раніше
logger.add(send_to_loki, level="INFO")
