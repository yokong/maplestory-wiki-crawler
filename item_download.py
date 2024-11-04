import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import json

from config import ITEM_CONFIG
from utils import (
    setup_logging, ensure_directory, get_json_filename,
    get_unique_filename, update_json_file, safe_request
)


def should_process_item(item):
    if ITEM_CONFIG['API']['isCash'] is None:
        return True
    item_is_cash = item.get('isCash', False)
    return item_is_cash == ITEM_CONFIG['API']['isCash']


def process_single_item(item, index, total):
    try:
        item_id = item['id']
        name = item['name']
        is_cash = item.get('isCash', False)

        if not should_process_item(item):
            logging.info(
                f"Skipping {index}/{total}: ID={item_id}, Name={name} (isCash={is_cash})")
            return None

        logging.info(
            f"Processing {index}/{total}: ID={item_id}, Name={name}, isCash={is_cash}")

        detail_url = f'{ITEM_CONFIG["API"]["BASE_URL"]}{item_id}/icon?resize=4'
        detail_response = safe_request(detail_url)

        if detail_response is None:
            logging.error(f"✗ Failed to fetch details for item {
                          item_id} ({name})")
            return {
                'id': item_id,
                'name': name,
                'isCash': is_cash,
                'status': 'failed',
                'reason': 'Network error during fetch'
            }

        try:
            filename = get_unique_filename(name)
            file_path = os.path.join(ITEM_CONFIG['PATHS']['IMAGES'], filename)

            with open(file_path, 'wb') as f:
                f.write(detail_response.content)

            if filename != f"{name}.png":
                logging.info(f"✓ Found duplicate name, saved as: {filename}")
            else:
                logging.info(f"✓ Successfully saved image: {filename}")

            return {
                'id': item_id,
                'name': name,
                'isCash': is_cash,
                'filename': filename,
                'image_url': detail_url,
                'status': 'success'
            }

        except Exception as e:
            logging.error(f"✗ Error saving image {name}: {str(e)}")
            return {
                'id': item_id,
                'name': name,
                'isCash': is_cash,
                'status': 'failed',
                'reason': f'Image save error: {str(e)}'
            }

    except Exception as e:
        logging.error(f"✗ Unexpected error processing item {index}: {str(e)}")
        return {
            'id': item.get('id', 'unknown'),
            'name': item.get('name', 'unknown'),
            'isCash': item.get('isCash', False),
            'status': 'failed',
            'reason': f'Unexpected error: {str(e)}'
        }


def fetch_and_process_items():
    setup_logging()
    ensure_directory(ITEM_CONFIG['PATHS']['IMAGES'])

    json_filename = get_json_filename()
    logging.info(f"Results will be saved to: {json_filename}")

    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump([], f)

    try:
        response = safe_request(
            ITEM_CONFIG['API']['BASE_URL'], params=ITEM_CONFIG['API']['PARAMS'])
        if response is None:
            logging.error("Failed to fetch initial items list")
            return

        items = response.json()
        total_items = len(items)
        logging.info(f"Found {total_items} items to process")

        if ITEM_CONFIG['API']['isCash'] is not None:
            logging.info(f"Filtering items with isCash={
                         ITEM_CONFIG['API']['isCash']}")

        with ThreadPoolExecutor(max_workers=ITEM_CONFIG['CONCURRENT']['MAX_WORKERS']) as executor:
            future_to_item = {
                executor.submit(process_single_item, item, index + 1, total_items): item
                for index, item in enumerate(items)
            }

            for future in concurrent.futures.as_completed(future_to_item):
                try:
                    result = future.result()
                    if result:
                        update_json_file(result, json_filename)
                except Exception as e:
                    logging.error(f"Error processing task: {str(e)}")

        logging.info(f"All tasks completed! Results saved to {json_filename}")

    except Exception as e:
        logging.error(f"Critical error in main process: {str(e)}")
        logging.error(f"Program will exit, but processed items have been saved to {
                      json_filename}")


def start_download():
    fetch_and_process_items()
