# 通用配置 - 用于管理所有下载任务的通用设置
COMMON_CONFIG = {
    # 请求相关配置
    'REQUEST': {
        'MAX_RETRIES': 3,    # 请求失败最大重试次数
        'RETRY_DELAY': 2,    # 重试间隔时间(秒)
        'TIMEOUT': 30        # 请求超时时间(秒)
    },
    # 并发配置
    'CONCURRENT': {
        'MAX_WORKERS': 3     # 最大并发工作线程数
    },
    # 文件处理策略
    'FILE_HANDLING': {
        # 重复文件处理策略: 'rename'(重命名) 或 'skip'(跳过) 或 'overwrite'(覆盖)
        'STRATEGY': 'rename',
        # 重命名模式，支持 {name}, {index}, {ext}
        'RENAME_PATTERN': '{name}_{index}{ext}'
    }
}

# 物品配置 - 用于管理冒险岛物品相关的设置
ITEM_CONFIG = {
    "API": {
        "BASE_URL": "https://maplestory.io/api/CMS/202/item/",
        "PARAMS": {
            "overallCategoryFilter": "Equip",
            "categoryFilter": "Armor",
            "subCategoryFilter": "Cape"
        },
        "isCash": True
    },
    "PATHS": {
        "IMAGES": "cape_images",
        "LOGS": "logs",
        "JSON_BASE": "cape_result"
    }
}

# 游戏中NPC相关的设置
NPC_CONFIG = {
    # TODO: 添加NPC相关配置
}

# 地图配置 - 用于管理游戏地图相关的设置
MAP_CONFIG = {
    # TODO: 添加地图相关配置
}
