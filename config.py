# 物品配置
ITEM_CONFIG = {
    'API': {
        'BASE_URL': 'https://maplestory.io/api/CMS/202/item/',
        'PARAMS': {
            'overallCategoryFilter': 'Equip',
            'categoryFilter': 'Armor',
            'subCategoryFilter': 'Hat',
        },
        'isCash': True
    },
    'PATHS': {
        'IMAGES': 'maplestory-hat',
        'LOGS': 'logs',
        'JSON_BASE': 'maplestory-img'
    },
    'REQUEST': {
        'MAX_RETRIES': 3,
        'RETRY_DELAY': 2,
        'TIMEOUT': 30
    },
    'CONCURRENT': {
        'MAX_WORKERS': 5
    }
}

# NPC配置
NPC_CONFIG = {

}

# 地图配置
MAP_CONFIG = {

}
