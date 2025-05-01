import httpx
import hashlib
from datetime import date
import xml.etree.ElementTree as ET

async def send_web_push(uid: str, title: str, body: str, type_: str, link: str, message_text: str = "") -> dict:
    point = "0203"  
    date_valid = date(1, 1, 1).strftime("%Y-%m-%d")
    secret = "5a3e3FGe^3"

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
            response = await client.post("http://e-lombard.com/api.php", data=payload)
           
            if response.status_code == 200:
                try:
                    root = ET.fromstring(response.text)
                    status = root.findtext("status")
                    if status == "1":
                        return {"success": True, "response": response.text}
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
    url = "https://auth.skarb.group/api/v1/notifications-service/send-batch"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTQsImxvZ2luIjoibG9zZW5kIiwiaWF0IjoxNjU5Njg1NjkyfQ.ZKPz77ci46rjHQ8eIiORLmiwIwYBFU2_Eyr8t2Ee6Xs"
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
                    return {"success": True, "response": resp_json.get("data", {})}
                return {"success": False, "error": resp_json.get("message", "Unknown error")}
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
