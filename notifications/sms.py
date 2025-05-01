from notifications.sms_gateway import send_sms_gateway

async def send_sms(phone: str, message: str, client_id: str):
    result = await send_sms_gateway(
        phone=phone,
        message=message,
        client_uid=client_id,
        brand="900000124",
        alphaname="Skarbnica",
        viber=False
    )

    if result.get("success"):
        print("[SMS SUCCESS]", result.get("response"))
    else:
        print("[SMS ERROR]", result.get("error"))
