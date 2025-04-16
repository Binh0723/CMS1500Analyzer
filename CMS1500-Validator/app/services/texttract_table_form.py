import boto3 # type: ignore
from dotenv import load_dotenv  # type: ignore
import os


#Get the data for box24
def get_box_24(filepath):
    all_tables = extract_tables_ocr(filepath)
    tables = clean_textract_tables(all_tables)
    format_table = reformat_cms_table(tables[10])
    box24 = map_box24_table(format_table)

    return box24

#get all data from images
def extract_tables_ocr(imagepath):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    ENV_PATH = os.path.join(BASE_DIR, '.env')
    load_dotenv(dotenv_path=ENV_PATH)
    client = boto3.client('textract',
                      region_name=os.getenv('REGION_NAME'),
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'))
    with open(imagepath, 'rb') as file:
        img_test = file.read()
        bytes_test = bytearray(img_test)

    response = client.analyze_document(
        Document={'Bytes': bytes_test},
        FeatureTypes=["TABLES"]
    )
    tables = extract_tables(response)
    return tables

#Extract important data from tables
def clean_textract_tables(raw_tables):
    formatted_tables = []

    for table in raw_tables:
        clean_table = []
        for row in table[0]: 
            clean_row = [cell.strip() for cell in row if cell.strip() != '']
            clean_table.append(clean_row)
        if clean_table:
            formatted_tables.append(clean_table)

    return formatted_tables

#Reformat the data 
def reformat_cms_table(raw):
    header = raw[0]
    data_rows = raw[1:]

    reformatted = [header]
    current_row = []

    for row in data_rows:
        if len(row) == 1 and row[0].isdigit():
            if current_row:
                reformatted.append(current_row)
            current_row = [row[0]] 
        else:
            # Append the actual row data
            current_row += row

    if current_row:
        reformatted.append(current_row)

    max_len = len(header)
    reformatted = [r + [''] * (max_len - len(r)) for r in reformatted]

    return reformatted

#Get the data of box24 from the extracted tables
def map_box24_table(table):
    header = table[0][1:]  
    mapped_rows = []

    for row in table[1:]:
        if not row or not row[0].isdigit():
            continue  # skip invalid rows

        row_num = row[0]
        data = row[1:]

        if len(data) < len(header):
            data += [''] * (len(header) - len(data))

        row_dict = {'Line': row_num}
        for key, val in zip(header, data):
            row_dict[key.strip()] = val.strip()

        mapped_rows.append(row_dict)

    return mapped_rows

#Convert data from table to key-value map
def map_ocr_to_flat_data(ocr_data, box24):
    print(ocr_data)
    line = box24[0]
    # print(box24)
    box24_map = map_box24_line(line)
    # print(box24_map)
    def first_non_empty(lst):
        return next((item.strip() for item in lst if item.strip()), "")
    
    def get_selected_box1(ocr_data):
        if ocr_data['(Medicare#) '][0] == 'X ':
            return 'Medicare'
        elif  ocr_data['(Medicaid#) '][0] == 'X ':
            return "Medicaid"
        elif  ocr_data['(ID#/DoD#) '][0] == 'X ':
            return "Tricare"
        elif  ocr_data['(Member ID#) '][0] == 'X ':
            return "Champva"
        elif  ocr_data['(ID#) '][0] == 'X ':
            return "Group"
        elif  ocr_data['(ID#) '][1] == 'X ':
            return "Feca"
        elif  ocr_data['(ID#) '][2] == 'X ':
            return "Other"
    flat_data = {
        "box1":get_selected_box1(ocr_data),
        "box1a": first_non_empty(ocr_data.get("1a INSURED'S I.D. NUMBER ", [])).split(")")[1].strip(),
        "box2": first_non_empty(ocr_data.get("2 PATIENT'S NAME (Last Name, First Name, Middle Initial) ", [])),
        "box4": first_non_empty(ocr_data.get("4. INSURED'S NAME (Last Name, First Name, Middle Initial) ", [])),
        "box5str": first_non_empty(ocr_data.get("PATIENT'S ADDRESS (No., Street) ", [])),
        "box5city": first_non_empty(ocr_data.get("CITY ", [])),
        "box5state": first_non_empty(ocr_data.get("STATE ", [])),
        "box5zip": first_non_empty(ocr_data.get("ZIP CODE ", [])),
        "box11": first_non_empty(ocr_data.get("INSURED'S POLICY GROUP OR FECA NUMBER ", [])),
        "box13": first_non_empty(ocr_data.get("SIGNED ", [])),
        "box25": first_non_empty(ocr_data.get("25. FEDERAL TAX I.D. NUMBER ", [])),
        "box33": first_non_empty(ocr_data.get("BILLING PROVIDER INFO & PH # ", [])),
        "box33a": first_non_empty(ocr_data.get("a ", [])), 
        "box21": first_non_empty(ocr_data.get("A ", [])),   
        "box24b": first_non_empty(ocr_data.get("B. ", [])), 
        "box24d": first_non_empty(ocr_data.get("C. ", [])),
        "modifiers": first_non_empty(ocr_data.get("D. ", [])),  
        "box24e": first_non_empty(ocr_data.get("E ", [])),  
        "box24f": first_non_empty(ocr_data.get("F. ", [])), 
        "box24j": first_non_empty(ocr_data.get("a ", [])),  
        "box31": first_non_empty(ocr_data.get("SIGNED ", [])),

        # Telephone split
        "box5AC": "",  # Will extract below
        "box5phone": "",

        # DOB reconstruction from MM/DD/YY format
        "box3": "",

        # Sex
        "sex": "M" if any("X" in s for s in ocr_data.get("M ", [])) else ("F" if any("X" in s for s in ocr_data.get("F ", [])) else ""),

        # Relationship to insured (box6)
        "box6": (
            "S" if any("X" in s for s in ocr_data.get("Self ", [])) else
            "M" if any("X" in s for s in ocr_data.get("Spouse ", [])) else
            "C" if any("X" in s for s in ocr_data.get("Child ", [])) else
            "O" if any("X" in s for s in ocr_data.get("Other ", [])) else ""
        ),
    }
    flat_data.update(box24_map)
    print(flat_data)

    # Extract DOB from MM/DD/YY fields
    mm = first_non_empty(ocr_data.get("MM ", []))
    dd = first_non_empty(ocr_data.get("DD ", []))
    yy = first_non_empty(ocr_data.get("YY ", []))
    if mm and dd and yy:
        flat_data["box3"] = f"{mm.zfill(2)}/{dd.zfill(2)}/{yy.zfill(4)}"

    # Split phone number into area code and phone
    phone_raw = first_non_empty(ocr_data.get("TELEPHONE (Include Area Code) ", []))
    digits = ''.join(filter(str.isdigit, phone_raw))
    if len(digits) >= 10:
        flat_data["box5AC"] = digits[:3]
        flat_data["box5phone"] = f"{digits[3:6]}-{digits[6:10]}"

    return flat_data


#Get the first line of the table to extract the first row of the table
def map_box24_line(line_dict):
    return {
        "box24aFROM": f"{line_dict.get('From DD', '')}/{line_dict.get('DATE(S) YY', '')}/20{line_dict.get('OF SERVICE MM', '')}",
        "box24aTO": f"{line_dict.get('To DD', '')}/{line_dict.get('YY', '')}/20{line_dict.get('B. PLACE OF SERVICE', '')}",
        "box24d": line_dict.get("D. PROCEDURES, (Explain Unusual OPT/HCPCS", ""),
        "modifiers": line_dict.get("SERVICES,", ""),
        "box24e": line_dict.get("OR Circumstances) MODIFIER", ""),
        "box24f": line_dict.get("SUPPLIES", ""),
        "box24g":line_dict.get("E. DIAGNOSIS POINTER", ""),
        "box24j": line_dict.get("G DAYS OR UNITS", ""),  
        "box24b":line_dict.get("C. EMG", ""),  
    }

#Get all the raw data from table
def extract_tables(response):
    blocks = response['Blocks']
    block_map = {block['Id']: block for block in blocks}
    
    tables = []

    for block in blocks:
        if block['BlockType'] == 'TABLE':
            table = []
            for relationship in block.get('Relationships', []):
                if relationship['Type'] == 'CHILD':
                    cells = [block_map[child_id] for child_id in relationship['Ids']
                             if block_map[child_id]['BlockType'] == 'CELL']
                    max_row = max(cell['RowIndex'] for cell in cells)
                    max_col = max(cell['ColumnIndex'] for cell in cells)

                    table_data = [["" for _ in range(max_col)] for _ in range(max_row)]

                    for cell in cells:
                        row_idx = cell['RowIndex'] - 1
                        col_idx = cell['ColumnIndex'] - 1
                        text = ""
                        for rel in cell.get('Relationships', []):
                            if rel['Type'] == 'CHILD':
                                words = [block_map[word_id]['Text'] for word_id in rel['Ids']
                                         if block_map[word_id]['BlockType'] == 'WORD']
                                text = " ".join(words)
                        table_data[row_idx][col_idx] = text
                    table.append(table_data)
            tables.append(table)
    return tables