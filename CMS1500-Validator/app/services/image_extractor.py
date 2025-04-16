import os
import boto3 # type: ignore
import json
from collections import defaultdict
from dotenv import load_dotenv  # type: ignore


def extract_info_ocr(imagepath):

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
        FeatureTypes=["FORMS"]
    )
    blocks = response['Blocks']
    key_map, value_map,block_map = get_kv_map(blocks=blocks)
    kvs = extract_kv_pairs(key_map, value_map, block_map)

    form_data = {}
    for key, value in kvs.items():
        form_data[key] = value
    json_data = json.dumps(form_data, indent=4)
    return json_data

def get_kv_map(blocks):
    key_map = {}
    value_map = {}
    block_map = {}
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block.get('EntityTypes', []):
                key_map[block_id] = block
            else:
                value_map[block_id] = block
    return key_map, value_map, block_map

# Extract key-value pairs
def extract_kv_pairs(key_map, value_map, block_map):
    kvs = defaultdict(list)
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key].append(val)
    return kvs


# Find value block for a given key block
def find_value_block(key_block, value_map):

    if 'Relationships' in key_block:
        for relationship in key_block['Relationships']:
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = value_map[value_id]
    return value_block

def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '

    return text
