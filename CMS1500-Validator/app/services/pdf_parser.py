import re
import json
from pathlib import Path
from  app.services.pdf_extractor import get_flat_data

#Validate the data with the rules and return the array of errors
def validate_fields(data, rules, field_prefix=""):
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


#Get the flat data and validate with the rules
def validate_pdf(filepath):
    flat_data = get_flat_data(filepath)
    rules_path = Path(__file__).resolve().parents[2] / "app" / "CMS-Rules" / "rules.json"
    with open(rules_path, 'r') as f:
        rules = json.load(f)
    errors = validate_fields(flat_data, rules=rules)
    return errors



