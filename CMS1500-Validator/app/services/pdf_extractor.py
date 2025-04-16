from pypdf import PdfReader # type: ignore
import json


#Extract all the information from a fillable PDF
def extract_info_pdf(filepath):
    reader = PdfReader(filepath)
    if "/AcroForm" not in reader.trailer["/Root"]:
        return json.dumps({"error": "No AcroForm found. This PDF does not contain fillable fields."}, indent=4)

    fields = reader.get_fields()
    form_data ={}
    for key, field in fields.items():
        value = field.get('/V')
        if value is not None:
            form_data[key] = value
    return form_data

#Convert data into structure map
def reformat_pdf_data(data):
    
    res = {}
    def safe_get(key):
        return data.get(key, '')

    def safe_strip_prefix(val):
        return val[1:] if val and isinstance(val, str) and val.startswith('/') else val
    res['patient'] = {
        "name": safe_get("pt_name"),
        "sex": safe_strip_prefix(safe_get("sex")),
        "dob": f"{safe_get('birth_mm')}/{safe_get('birth_dd')}/{safe_get('birth_yy')}",
        "rti": safe_strip_prefix(safe_get("rel_to_ins")),
        "pt_street": safe_get("pt_street"),
        "pt_city":safe_get("pt_city"),
        "pt_state":safe_get("pt_state"),
        "pt_zip":safe_get("pt_zip"),
        "pt_area_code": safe_get('pt_AreaCode'),
        "pt_phone":safe_get('pt_phone')
    }

    res['insured'] = {
        "name": safe_get('ins_name'),
        "isurance_policy": safe_get('ins_policy'),
        "insurance_id": safe_get('insurance_id'),
        "insurance_type": safe_strip_prefix(safe_get('insurance_type')),
        'insurance_signature': safe_get('ins_signature')
    }

    res['provided'] = {
        "tax_id": safe_get('tax_id'),
        "psignature": safe_get('physician_signature'),
        "pro_address": safe_get('doc_name'),
        "npi": safe_get('pin1'),
        "provide_id": safe_get('local1a')
    }

    res['dianosis'] = {
        "A": safe_get('diagnosis1'),
        "B": safe_get('diagnosis2'),
        "C": safe_get('diagnosis3'),
        "D": safe_get('diagnosis4'),
        "E": safe_get('diagnosis5'),
        "F": safe_get('diagnosis6'),
        "G": safe_get('diagnosis7'),
        "H": safe_get('diagnosis8'),
        "I": safe_get('diagnosis9'),
        "J": safe_get('diagnosis10'),
        "K": safe_get('diagnosis11'),
        "L": safe_get('diagnosis12')
    }

    res["DOS"] = {
        "from": safe_get('sv1_mm_from')+"/"+ safe_get('sv1_dd_from') + "/20" + safe_get('sv1_yy_from'),
        "to": safe_get('sv1_mm_end')+"/"+ safe_get('sv1_dd_end') + "/20" + safe_get('sv1_yy_end'),
        "POS": safe_get('place1'),
        "CPT": safe_get('cpt1'),
        "Modifier": safe_get('mod1'),
        "DP": safe_get('diag1'),
        "Charge": safe_get('ch1'),
        "Days": safe_get('day1')
    }

    return res

#Flatten data from formated data
def get_flat_data(filepath):

    #Extract the data then reformat it
    raw_data = extract_info_pdf(filepath)
    formated_data = reformat_pdf_data(raw_data)

    patient = formated_data["patient"]
    insured = formated_data["insured"]
    provided = formated_data["provided"]
    diagnosis = formated_data["dianosis"]
    dos = formated_data["DOS"]

    #Flatten the data from formated data
    flat_data = {
        "box21": diagnosis.get("A", ""),
        "box24aFROM": dos.get("from", ""),
        "box24aTO": dos.get("to", ""),
        "box24d": dos.get("CPT", ""),
        "modifiers": dos.get("Modifier", ""),
        "box24e": dos.get("DP", ""),
        "box24f": dos.get("Charge", ""),
        "box24j": provided.get("npi", ""),
        "box24g": raw_data.get('day1'),
        "box25": provided.get("tax_id", ""),
        "box31": provided.get("psignature", ""),
        "box33": provided.get("pro_address", ""),
        "box33a": provided.get("npi", ""),
        "box1": insured.get("insurance_type", ""),
        "box1a": insured.get("insurance_id", ""),
        "box2": patient.get("name", ""),
        "box3": patient.get("dob", ""),
        "sex": patient.get("sex", ""),
        "box4": insured.get("name", ""),
        "box5str": patient.get("pt_street", ""),
        "box5city": patient.get("pt_city", ""),
        "box5state": patient.get("pt_state", ""),
        "box5zip": patient.get("pt_zip", ""),
        "box5AC": patient.get("pt_area_code", ""),
        "box5phone": patient.get("pt_phone", ""),
        "box6": patient.get("rti", ""),
        "box11": insured.get("isurance_policy", ""),
        "box13": insured.get("insurance_signature", ""),
        "box24b":dos.get("POS",""),
        "modifier": dos.get("Modifier",""),
        "box24e":dos.get("DP","")
    }
    # print(flat_data)
    return flat_data