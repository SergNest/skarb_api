from notifications.sms_gateway import send_sms_gateway

async def send_viber(phone: str, message: str, client_id: str):
    result = await send_sms_gateway(
        phone=phone,
        message=message,
        client_uid=client_id,
        brand="900000124",
        alphaname="Skarbnica",
        viber=True
    )

    if result.get("success"):
        print("[VIBER SUCCESS]", result.get("response"))
    else:
        print("[VIBER ERROR]", result.get("error"))