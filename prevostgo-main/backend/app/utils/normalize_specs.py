import re
from typing import Dict, Optional

_NAMED_SLIDES = {"single": 1, "double": 2, "triple": 3, "quad": 4, "quadruple": 4}

def _parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    # Remove dots used as thousand separators and keep commas
    cleaned = text.replace('.', '')
    m = re.search(r"([\d,]+)", cleaned)
    return int(m.group(1).replace(",", "")) if m else None

def _parse_slide_count(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    t = text.lower()
    for k, v in _NAMED_SLIDES.items():
        if k in t:
            return v
    m = re.search(r"(\d+)\s*slide", t)
    return int(m.group(1)) if m else None

def normalize_specs(specs: Dict[str, str]) -> Dict[str, Optional[object]]:
    """Map raw dealer labels to canonical fields used by the app."""
    model = specs.get("Model") or specs.get("Bus Model") or specs.get("Coach Model")
    chassis = specs.get("Chassis") or specs.get("Chassis Type")

    # Heuristic if chassis omitted but model implies it
    if not chassis and model:
        if "H3" in model.upper():
            chassis = "H3-45"
        elif "X3" in model.upper():
            chassis = "X3-45"

    mileage = _parse_int(specs.get("Mileage") or specs.get("Miles") or specs.get("Odometer"))
    slides_text = specs.get("Slides") or specs.get("Slide Outs") or specs.get("Slideouts") or specs.get("Premium Features")
    slide_count = _parse_slide_count(slides_text)

    price_raw = (specs.get("Price") or "").strip()
    if "contact" in price_raw.lower() or price_raw == "":
        price = None
        price_contact = True
    else:
        price = _parse_int(price_raw)
        price_contact = False

    return {
        "model": model,
        "chassis_type": chassis,
        "mileage": mileage,
        "slide_count": slide_count,
        "price": price,
        "price_contact": price_contact,
    }