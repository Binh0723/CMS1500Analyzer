import json
from pathlib import Path
import re
from app.services.image_extractor import extract_info_ocr
from app.services.texttract_table_form import get_box_24,map_ocr_to_flat_data


def validate_image(filepath,field_prefix=""):
    json_data = extract_info_ocr(filepath)
    ocr_data = json.loads(json_data)
    box24 = get_box_24(filepath)

    data = map_ocr_to_flat_data(ocr_data,box24)
    rules_path = Path(__file__).resolve().parents[2] / "app" / "CMS-Rules" / "rules.json"

    with open(rules_path, 'r') as f:
        rules = json.load(f)
    errors = []
    for field, rule in rules.items():
        full_field = f"{field_prefix}{field}"
        if rule.get("required") and field not in data:
            errors.append({"field": full_field, "error": f"{full_field} is required"})
            continue
        if field in data:
            value = str(data[field]).strip()
            if "pattern" in rule:
                if not re.match(rule["pattern"], value):
                    errors.append({"field": full_field, "error": rule["error"]})
    return errors



# errors = validate_image("image3.png")
# print("errors " + str(errors))







