import os
import logging
import json
import base64
from PIL import Image
import io
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from datetime import datetime
from config import ITEM_CONFIG


def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")


def get_json_filename():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{ITEM_CONFIG['PATHS']['JSON_BASE']}_{timestamp}.json"


def setup_logging():
    if not os.path.exists(ITEM_CONFIG['PATHS']['LOGS']):
        os.makedirs(ITEM_CONFIG['PATHS']['LOGS'])

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(
        ITEM_CONFIG['PATHS']['LOGS'], f'crawler_{timestamp}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def save_base64_image(base64_str, filename):
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    image.save(filename)


def get_unique_filename(name):
    filename = f"{name}.png"
    file_path = os.path.join(ITEM_CONFIG['PATHS']['IMAGES'], filename)
    counter = 1

    while os.path.exists(file_path):
        filename = f"{name}_{counter}.png"
        file_path = os.path.join(ITEM_CONFIG['PATHS']['IMAGES'], filename)
        counter += 1

    return filename


def update_json_file(item_data, json_file=None):
    if json_file is None:
        json_file = get_json_filename()

    try:
        existing_data = []
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        existing_data = json.loads(content)
            except json.JSONDecodeError:
                logging.warning(
                    "Existing JSON file is invalid or empty, starting fresh")
                existing_data = []

        existing_data.append(item_data)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        logging.info(f"✓ Successfully updated {json_file}")
    except Exception as e:
        logging.error(f"✗ Error updating JSON file: {str(e)}")
        logging.error(f"Attempting to save current item separately...")

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'maplestory-img_backup_{
                item_data["id"]}_{timestamp}.json'
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump([item_data], f, ensure_ascii=False, indent=2)
            logging.info(f"✓ Saved item to backup file: {backup_file}")
        except Exception as backup_error:
            logging.error(f"✗ Failed to save backup: {str(backup_error)}")


def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504, 408, 429],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def safe_request(url, params=None):
    session = create_session()

    for attempt in range(ITEM_CONFIG['REQUEST']['MAX_RETRIES']):
        try:
            response = session.get(
                url, params=params, timeout=ITEM_CONFIG['REQUEST']['TIMEOUT'])
            return response
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout) as e:
            if attempt == ITEM_CONFIG['REQUEST']['MAX_RETRIES'] - 1:
                logging.error(f"Failed after {
                              ITEM_CONFIG['REQUEST']['MAX_RETRIES']} attempts: {str(e)}")
                return None
            logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {
                            ITEM_CONFIG['REQUEST']['RETRY_DELAY']} seconds...")
            time.sleep(ITEM_CONFIG['REQUEST']['RETRY_DELAY'])
    return None
