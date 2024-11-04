# 物品配置 - 用于管理冒险岛物品相关的设置
ITEM_CONFIG = {
    # API相关配置
    'API': {
        # 冒险岛物品API的基础URL
        'BASE_URL': 'https://maplestory.io/api/CMS/202/item/',
        # API请求参数
        'PARAMS': {
            'overallCategoryFilter': 'Equip',    # 总分类：装备
            'categoryFilter': 'Armor',           # 分类：防具
            'subCategoryFilter': 'Hat',          # 子分类：帽子
        },
        'isCash': True    # 是否为商城物品
    },
    # 文件路径配置
    'PATHS': {
        'IMAGES': 'maplestory-hat',     # 帽子图片存储路径
        'LOGS': 'logs',                 # 日志文件存储路径
        'JSON_BASE': 'maplestory-img'   # JSON数据存储的基础路径
    },
    # 请求相关配置
    'REQUEST': {
        'MAX_RETRIES': 3,    # 请求失败最大重试次数
        'RETRY_DELAY': 2,    # 重试间隔时间(秒)
        'TIMEOUT': 30        # 请求超时时间(秒)
    },
    # 并发配置
    'CONCURRENT': {
        'MAX_WORKERS': 5     # 最大并发工作线程数
    }
}

# NPC配置 - 用于管理游戏中NPC相关的设置
NPC_CONFIG = {
    # TODO: 添加NPC相关配置
}

# 地图配置 - 用于管理游戏地图相关的设置
MAP_CONFIG = {
    # TODO: 添加地图相关配置
}
