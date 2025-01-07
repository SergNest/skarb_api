from loguru import logger

logger.remove()

# Загальний лог-файл у JSON форматі
logger.add("logs/general.json", format="{time} {level} {message} {extra}", serialize=True, rotation="10 MB",
           retention="10 days", compression="zip")

# Окремі лог-файли для маршрутів у JSON
logger.add("logs/new_delay.json", serialize=True, filter=lambda record: "new_delay" in record["extra"], rotation="5 MB",
           retention="7 days")
logger.add("logs/get_vendor.json", serialize=True, filter=lambda record: "get_vendor" in record["extra"],
           rotation="5 MB", retention="7 days")
logger.add("logs/new_type.json", serialize=True, filter=lambda record: "new_type" in record["extra"], rotation="5 MB",
           retention="7 days")
logger.add("logs/dogovorhistory.json", serialize=True, filter=lambda record: "dogovorhistory" in record["extra"],
           rotation="5 MB", retention="7 days")
logger.add("logs/gettype.json", serialize=True, filter=lambda record: "gettype" in record["extra"], rotation="5 MB",
           retention="7 days")
logger.add("logs/new_vendor.json", serialize=True, filter=lambda record: "new_vendor" in record["extra"],
           rotation="5 MB", retention="7 days")
logger.add("logs/check_zok_by_phone.json", serialize=True,
           filter=lambda record: "check_zok_by_phone" in record["extra"], rotation="5 MB", retention="7 days")
logger.add("logs/new_offer.json", serialize=True,
           filter=lambda record: "new_offer" in record["extra"], rotation="5 MB", retention="7 days")