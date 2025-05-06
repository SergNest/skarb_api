import httpx
import hashlib
from datetime import date
import xml.etree.ElementTree as ET

from conf.config import settings

async def send_web_push(uid: str, title: str, body: str, type_: str, link: str, message_text: str = "", phone = "") -> dict:
    
    point = settings.point  
    secret = settings.secret

    phash_raw = (point + secret).upper()
    phash = hashlib.md5(phash_raw.encode("utf-8")).hexdigest()
        
    payload = {
        "method": "send_push",
        "uids": uid,
        "title": title,
        "body": title,
        "type": type_,
        "link": "1",
        "self_linked": "1",
        "message_text": message_text,
        "point": point,
        "date_valid": "",
        "codes": "1",
        "phash": phash
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.elombard, data=payload)

            if response.status_code == 200:
                try:
                    root = ET.fromstring(response.text)
                    status = root.findtext("status")

                    if status == "1":
                        # Формуємо JSON на основі XML
                        send_item = root.find(".//send_item")
                        if send_item is not None:
                            json_data = {
                                "uid": send_item.findtext("uid"),
                                "id": send_item.findtext("id"),
                                "channel": "web_push",
                                "phone": phone,
                                "msg": message_text
                            }

                            headers = {"Content-Type": "application/json; charset=utf-8"}
                            response_external_api = await client.post(
                                f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/add_sms_statistic/",
                                json=json_data,
                                headers=headers
                            )

                            return {
                                "success": True,
                                "response": response.text,
                                "external_api_status": response_external_api.status_code
                            }
                        else:
                            return {"success": False, "error": "Missing <send_item> in response"}

                    else:
                        error_text = root.findtext("error") or "Unknown error"
                        return {"success": False, "error": error_text}

                except Exception as parse_error:
                    return {"success": False, "error": f"XML parse error: {parse_error}"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_app_push(phone: str, text: str, title: str) -> dict:
    url = f"https://{settings.homenkopushurl}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {settings.homenkobearer}"
    }

    push_block = {
        "icon": "up",
        "type": "links-accent"
    }

    actions = [
        {
            "action": "https://www.skarb.com.ua/special#spend",
            "title": "ПРО БОНУСИ",
            "icon": "up"
        }
    ]

    row = {
        "phone": phone,
        "title": title,
        "text": text,
        "push": push_block,
        "actions": actions
    }

    payload = {
        "merchant": "1",
        "channels": ["push"],
        "rows": [row]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                resp_json = response.json()
                if not resp_json.get("isError", True):
                    print(response.text)
                    return {"success": True, "response": resp_json.get("data", {})}
                return {"success": False, "error": resp_json.get("message", "Unknown error")}
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
