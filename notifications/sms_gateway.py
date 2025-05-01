import base64
import httpx
from xml.dom.minidom import Document

async def send_sms_gateway(phone: str, message: str = "Test message", client_uid: str = "", brand: str = "900000124", alphaname: str = "SkarbComUa", viber: bool = False, image: str = "", msg_type: str = "Шаблон") -> dict:
    doc = Document()

    data = doc.createElement("data")
    doc.appendChild(data)

    brand_el = doc.createElement("brand")
    brand_el.appendChild(doc.createTextNode(brand))
    data.appendChild(brand_el)

    alphaname_el = doc.createElement("alphaname")
    alphaname_el.appendChild(doc.createTextNode(alphaname))
    data.appendChild(alphaname_el)

    viber_el = doc.createElement("viber")
    viber_el.appendChild(doc.createTextNode("1" if viber else "0"))
    data.appendChild(viber_el)

    messages_el = doc.createElement("messages")
    message_el = doc.createElement("message")

    phone_el = doc.createElement("phone")
    phone_el.appendChild(doc.createTextNode("+" + phone if not phone.startswith("+") else phone))
    message_el.appendChild(phone_el)

    text_el = doc.createElement("text")
    cdata = doc.createCDATASection(message)
    text_el.appendChild(cdata)
    message_el.appendChild(text_el)

    uid_el = doc.createElement("uid")
    uid_el.appendChild(doc.createTextNode(client_uid))
    message_el.appendChild(uid_el)

    type_el = doc.createElement("type")
    type_el.appendChild(doc.createTextNode(msg_type))
    message_el.appendChild(type_el)

    messages_el.appendChild(message_el)
    data.appendChild(messages_el)

    # XML буде з UTF-8
    xml_str = doc.toxml(encoding="utf-8").decode("utf-8")
    print("[XML RAW]", xml_str)

    # Але base64 буде на основі байтів у windows-1251
    xml_b64 = base64.b64encode(xml_str.encode("windows-1251")).decode("utf-8")

    payload = {
        "method": "smssend",
        "point": "smsservice",
        "phash": "dbcea636fa23fcd71d36f74b45a3ebad",
        "xml": xml_b64
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://sms.skarb.com.ua/api.php", data=payload)
            if response.status_code == 200:
                return {"success": True, "response": response.text}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}