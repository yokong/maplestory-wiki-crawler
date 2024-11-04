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
from config import COMMON_CONFIG, ITEM_CONFIG
from urllib.parse import urlparse, parse_qs, unquote
import re

# URL参数与API参数的映射关系
PARAM_MAPPINGS = {
    # 网站URL参数: API参数
    'overallCategory': 'overallCategoryFilter',
    'category': 'categoryFilter',
    'subCategory': 'subCategoryFilter'
}

# 添加URL路径与配置的映射关系
CONFIG_TYPE_MAPPINGS = {
    'item': {
        'url_pattern': r'maplestory\.wiki/CMS/\d+/item',  # URL匹配模式
        'config_key': 'ITEM_CONFIG',                       # 对应的配置键
        'param_path': ['API', 'PARAMS']                    # 配置中参数的路径
    },
    'npc': {
        'url_pattern': r'maplestory\.wiki/CMS/\d+/npc',
        'config_key': 'NPC_CONFIG',
        'param_path': ['API', 'PARAMS']
    },
    'map': {
        'url_pattern': r'maplestory\.wiki/CMS/\d+/map',
        'config_key': 'MAP_CONFIG',
        'param_path': ['API', 'PARAMS']
    }
}


def parse_maplestory_url_params(url: str) -> tuple[dict, bool]:
    """
    从冒险岛物品URL中解析参数配置

    Args:
        url: 完整的冒险岛物品URL
        例如: https://maplestory.wiki/CMS/202/item?overallCategory=Equip&category=One-Handed%20Weapon&subCategory=Chain&cash=true

    Returns:
        tuple: (参数字典, 是否为商城物品)
        例如: (
            {
                'overallCategoryFilter': 'Equip',
                'categoryFilter': 'One-Handed Weapon',
                'subCategoryFilter': 'Chain'
            },
            True
        )
    """
    try:
        parsed_url = urlparse(url)
        query_params = {
            key: unquote(value[0])
            for key, value in parse_qs(parsed_url.query).items()
        }
        print(query_params)
        # 检查是否为商城物品
        is_cash = None  # 默认为None，表示URL中没有指定cash参数
        if 'cash' in query_params:
            is_cash = query_params.pop('cash').lower() == '1'

        # 转换参数名称
        api_params = {}
        for web_param, api_param in PARAM_MAPPINGS.items():
            if web_param in query_params:
                api_params[api_param] = query_params[web_param]

        # 验证必要参数
        required_params = PARAM_MAPPINGS.values()
        missing_params = [
            param for param in required_params if param not in api_params]

        if missing_params:
            raise ValueError(f"URL缺少必要参数: {', '.join(missing_params)}")

        return api_params, is_cash

    except Exception as e:
        raise ValueError(f"URL解析失败: {str(e)}")


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

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
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
    logging.info(f"Logging setup complete. Log file: {log_file}")


def save_base64_image(base64_str, filename):
    """
    保存Base64编码的图像

    Args:
        base64_str: Base64编码的图像字符串
        filename: 保存的文件名

    Returns:
        None
    """
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    image.save(filename)


def get_unique_filename(name: str, original_ext: str = '.png') -> str:
    """
    根据配置策略获取唯一的文件名

    Args:
        name: 原始文件名（不含扩展名）
        original_ext: 文件扩展名，默认为.png

    Returns:
        str: 最终的文件名（包含扩展名）
        None: 当策略为skip且文件存在时返回None
    """
    base_name = name
    ext = original_ext if original_ext.startswith('.') else f'.{original_ext}'
    file_path = os.path.join(
        ITEM_CONFIG['PATHS']['IMAGES'], f"{base_name}{ext}")

    # 如果文件不存在，直接返回原始名称
    if not os.path.exists(file_path):
        return f"{base_name}{ext}"

    # 根据策略处理重复文件
    strategy = COMMON_CONFIG['FILE_HANDLING']['STRATEGY']

    if strategy == 'skip':
        return None
    elif strategy == 'overwrite':
        return f"{base_name}{ext}"
    elif strategy == 'rename':
        index = 1
        while True:
            new_name = COMMON_CONFIG['FILE_HANDLING']['RENAME_PATTERN'].format(
                name=base_name,
                index=index,
                ext=ext
            )
            file_path = os.path.join(ITEM_CONFIG['PATHS']['IMAGES'], new_name)
            if not os.path.exists(file_path):
                return new_name
            index += 1

    return None  # 默认返回None


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

        # logging.info(f"✓ Successfully updated {json_file}")
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

    for attempt in range(COMMON_CONFIG['REQUEST']['MAX_RETRIES']):
        try:
            response = session.get(
                url, params=params, timeout=COMMON_CONFIG['REQUEST']['TIMEOUT'])
            return response
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout) as e:
            if attempt == COMMON_CONFIG['REQUEST']['MAX_RETRIES'] - 1:
                logging.error(f"Failed after {
                              COMMON_CONFIG['REQUEST']['MAX_RETRIES']} attempts: {str(e)}")
                return None
            logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {
                            COMMON_CONFIG['REQUEST']['RETRY_DELAY']} seconds...")
            time.sleep(COMMON_CONFIG['REQUEST']['RETRY_DELAY'])
    return None


def detect_config_type(url: str) -> str:
    """
    根据URL检测配置类型
    """
    for config_type, mapping in CONFIG_TYPE_MAPPINGS.items():
        if re.search(mapping['url_pattern'], url):
            return config_type
    raise ValueError("无法识别的URL类型")
