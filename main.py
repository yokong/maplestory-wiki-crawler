import json
from config import ITEM_CONFIG, NPC_CONFIG, MAP_CONFIG
import downloader.item_download as item_download
from utils import setup_logging, parse_maplestory_url_params, detect_config_type
import sys
import re


def display_menu():
    """显示主菜单"""
    print("\n=== 冒险岛资源下载器 ===")
    print("1. 下载装备")
    print("2. 下载NPC (Coming soon...)")
    print("3. 下载地图 (Coming soon...)")
    print("0. 退出")
    return input("请选择一个选项 (0-3): ")


def display_config(config):
    """显示当前配置并确认"""
    print("\n当前配置:")
    print(json.dumps(config, indent=2))
    confirm = input(
        "\n是否继续使用当前配置? (y/n): ")
    return confirm.lower() == 'y'


def update_config_from_url():
    """通过URL更新配置"""
    print("\n=== 通过URL更新配置 ===")
    url = input("请粘贴完整的URL: ").strip()

    try:
        # 检测配置类型
        config_type = detect_config_type(url)
        print(f"\n检测到的配置类型: {config_type}")

        # 解析参数
        params, is_cash = parse_maplestory_url_params(url)

        # 显示解析结果
        print("\n解析结果:")
        print("参数:")
        print(json.dumps(params, indent=2))
        if is_cash is not None:
            print(f"isCash: {is_cash}")
        else:
            print("isCash: None")

        # 显示当前配置
        print("\n当前配置:")
        if config_type == 'item':
            print("参数:")
            print(json.dumps(ITEM_CONFIG['API']['PARAMS'], indent=2))
            print(f"isCash: {ITEM_CONFIG['API']['isCash']}")

        # 询问是否更新
        confirm = input(
            "\n是否使用这些参数作为配置? (y/n): ").lower()
        if confirm == 'y':
            # 更新配置
            if config_type == 'item':
                # 更新参数
                ITEM_CONFIG['API']['PARAMS'] = params
                # 只有当URL中指定了cash参数时才更新isCash
                if is_cash is not None:
                    ITEM_CONFIG['API']['isCash'] = is_cash

                # 显示更新后的配置
                print("\n更新后的配置:")
                print("参数:")
                print(json.dumps(ITEM_CONFIG['API']['PARAMS'], indent=2))
                print(f"isCash: {ITEM_CONFIG['API']['isCash']}")

            confirm_final = input(
                "\n继续使用此配置? (y/n): ").lower()
            if confirm_final != 'y':
                print("配置更新取消")
                return False

            print("配置更新成功")
            return True
        else:
            print("配置更新取消")
            return False

    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def main():
    setup_logging()

    # 首先询问是否要更新配置
    print("\n=== 冒险岛资源下载器 ===")
    print("1. 通过URL更新配置")
    print("2. 使用当前配置")
    config_choice = input("\n请选择一个选项 (1/2): ").strip()

    if config_choice == '1':
        if not update_config_from_url():
            confirm = input("\n是否继续使用当前配置? (y/n): ")
            if confirm.lower() != 'y':
                print("\n退出...")
                sys.exit(0)
    elif config_choice != '2':
        print("无效的选项")
        sys.exit(1)

    # 主程序循环
    while True:
        choice = display_menu()

        if choice == '0':
            print("\n再见!")
            break

        elif choice == '1':
            print("\n=== Item Download Selected ===")
            if display_config(ITEM_CONFIG):
                print("\n开始下载装备...")
                item_download.start_download()
            else:
                print("下载取消。")

        elif choice == '2':
            print("\n=== NPC Download Selected ===")
            print("功能尚未实现。")
            # if display_config(NPC_CONFIG):
            #     npc_download.start_download()

        elif choice == '3':
            print("\n=== Map Download Selected ===")
            print("功能尚未实现。")
            # if display_config(MAP_CONFIG):
            #     map_download.start_download()

        else:
            print("\n无效的选项。请重试。")

        input("\n按Enter键继续...")


if __name__ == "__main__":
    main()
