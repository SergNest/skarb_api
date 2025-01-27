from loguru import logger
import requests
import json
import datetime
import time 

loki_url = "http://192.168.11.5:3100/loki/api/v1/push"
headers = {"Content-Type": "application/json"}

async def send_to_loki(message):
    try:
        record = json.loads(message)  # Loguru тепер видає JSON
    except json.JSONDecodeError:
        record = message  # Якщо JSON не парситься, використовуємо як текст

    # Переконуємося, що Loguru передав `record`
    if isinstance(record, dict) and "record" in record:
        record = record["record"]  # Тепер у нас є `level`, `time`, `extra`
    
    # Витягуємо рівень логування
    level_name = record.get("level", {}).get("name", "INFO")
    timestamp_str = str(int(record["time"]["timestamp"] * 1e9))


    # Витягуємо job або використовуємо дефолтне значення
    job_name = record.get("extra", {}).get("job", "skarbapi")
    log_message = record.get("message", "")

    print("--- DEBUG record ---")
    print(f"Job: {job_name}")
    print(f"Message: {log_message}")
    print("--------------------")

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


# Відлагоджувальний тест
logger.bind(job="test_bind").info("Test log with job field")