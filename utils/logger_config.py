from loguru import logger
import os

log_dir = "/var/log/fastapi"
os.makedirs(log_dir, exist_ok=True)

logger.remove()

# Загальний лог-файл
logger.add(f"{log_dir}/general.json", format="{time} {level} {message} {extra}", serialize=True, rotation="10 MB",
           retention="10 days", compression="zip")

# Логи для окремих маршрутів
logger.add(f"{log_dir}/check_zok_by_phone.json", serialize=True,
           filter=lambda record: "check_zok_by_phone" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/new_delay.json", serialize=True,
           filter=lambda record: "new_delay" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/get_vendor.json", serialize=True,
           filter=lambda record: "get_vendor" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/new_type.json", serialize=True,
           filter=lambda record: "new_type" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/dogovorhistory.json", serialize=True,
           filter=lambda record: "dogovorhistory" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/gettype.json", serialize=True,
           filter=lambda record: "gettype" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/new_vendor.json", serialize=True,
           filter=lambda record: "new_vendor" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/new_offer.json", serialize=True,
           filter=lambda record: "new_offer" in record["extra"], rotation="5 MB", retention="7 days")
logger.add(f"{log_dir}/get_bonus_withdraw.json", serialize=True,
           filter=lambda record: "get_bonus_withdraw" in record["extra"], rotation="5 MB", retention="7 days")
