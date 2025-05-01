import json
from pathlib import Path
from typing import Optional

_templates_cache = None

TEMPLATE_PATH = Path(__file__).parent / "templates.json"

def load_templates():
    global _templates_cache
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        _templates_cache = json.load(f)

def get_template(status: str, channel: str, name: Optional[str] = None) -> dict | str:
    if _templates_cache is None:
        load_templates()

    template = _templates_cache[status][channel]

    if isinstance(template, str):
        return template.replace("ІМ’Я", name or "Клієнте")

    result = {}
    for key, value in template.items():
        if isinstance(value, str):
            result[key] = value.replace("ІМ’Я", name or "Клієнте")
        else:
            result[key] = value
    return result